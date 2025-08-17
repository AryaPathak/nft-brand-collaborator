

import os
import json
import time
import uuid
import requests
from typing import Dict, List, Optional

from fastapi import FastAPI, Body, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

import dotenv

dotenv.load_dotenv()

# =========================
# Config (env-first)
# =========================
OPENSEA_MCP_KEY = os.getenv("OPENSEA_MCP_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =========================
# MCP Client
# =========================
class OpenSeaMCPClient:
    def __init__(self, api_key: str):
        self.base_url = "https://mcp.opensea.io/mcp"
        # IMPORTANT: use the provided api_key, do NOT hardcode
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        self.request_id = 1
        self.session_id: Optional[str] = None
        self.initialize_and_setup_session()

    def handle_sse_response(self, response):
        """Handle Server-Sent Events response"""
        events = []
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    events.append(data)
                except json.JSONDecodeError:
                    events.append({"raw": line[6:]})
        return events

    def send_request(self, method, params=None, use_session_id=True):
        """Send JSON-RPC request"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id,
        }
        if params:
            payload["params"] = params

        headers = self.headers.copy()
        if use_session_id and self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        try:
            response = requests.post(
                self.base_url, json=payload, headers=headers, stream=True, timeout=30
            )
            self.request_id += 1

            if "Mcp-Session-Id" in response.headers:
                self.session_id = response.headers["Mcp-Session-Id"]

            content_type = response.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                return self.handle_sse_response(response)
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def initialize_and_setup_session(self):
        """Initialize connection with proper session handling"""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())

        # Keep your original version if it works for you.
        # If you ever see protocol errors, try: "2024-05-01"
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {},
            },
            "clientInfo": {"name": "Python MCP Client", "version": "1.0"},
        }

        result = self.send_request("initialize", params, use_session_id=True)
        if isinstance(result, dict) and result.get("error"):
            result = self.send_request("initialize", params, use_session_id=False)
            if not self.session_id:
                self.session_id = str(uuid.uuid4())
        return result

    def list_available_tools(self):
        return self.send_request("tools/list")

    def get_collection_data(self, collection_slug: str):
        """Try multiple tool names for better compatibility"""
        collection_tools = [
            ("get_collection", {"slug": collection_slug}),
            ("get_collection_stats", {"collection_slug": collection_slug}),
            ("collection_stats", {"slug": collection_slug}),
            ("get_collection_info", {"collection": collection_slug}),
        ]
        for tool_name, args in collection_tools:
            result = self.send_request(
                "tools/call", {"name": tool_name, "arguments": args}
            )
            # If not an error dict, return it
            if not (isinstance(result, dict) and result.get("error")):
                return result
        return {"error": "No data available"}

    def search_collections(self, query: str):
        search_tools = [
            ("search_collections", {"query": query}),
            ("find_collection", {"name": query}),
            ("collection_search", {"search_term": query}),
        ]
        for tool_name, args in search_tools:
            result = self.send_request(
                "tools/call", {"name": tool_name, "arguments": args}
            )
            if not (isinstance(result, dict) and result.get("error")):
                return result
        return {"error": "Search not available"}


# =========================
# Assistant
# =========================
class NFTCollectionAssistant:
    def __init__(self, opensea_api_key: str, openai_api_key: str):
        self.mcp_client = OpenSeaMCPClient(opensea_api_key)
        self.openai_client = OpenAI(api_key=openai_api_key)

        self.collection_mapping = {
            "cryptopunks": "cryptopunks",
            "crypto punks": "cryptopunks",
            "punks": "cryptopunks",
            "bored ape": "boredapeyachtclub",
            "bored ape yacht club": "boredapeyachtclub",
            "bayc": "boredapeyachtclub",
            "mutant ape": "mutant-ape-yacht-club",
            "mayc": "mutant-ape-yacht-club",
            "azuki": "azuki",
            "doodles": "doodles-official",
            "clone x": "clonex",
            "clonex": "clonex",
            "pudgy penguins": "pudgypenguins",
            "pudgy": "pudgypenguins",
            "art blocks": "art-blocks",
            "moonbirds": "moonbirds",
            "otherdeed": "otherdeeds-for-otherside",
            "world of women": "world-of-women-nft",
            "cool cats": "cool-cats-nft",
        }

    def extract_collection_info(self, data) -> Dict:
        """Extract useful fields from possibly varied tool outputs"""
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        if not isinstance(data, dict):
            return {}

        info = {}
        field_mappings = {
            "name": ["name", "collection.name", "title"],
            "description": ["description", "collection.description", "desc"],
            "floor_price": [
                "floor_price",
                "floorPrice",
                "floor",
                "stats.floor_price",
                "collection.floor_price",
            ],
            "total_supply": [
                "total_supply",
                "totalSupply",
                "supply",
                "stats.total_supply",
                "collection.total_supply",
            ],
            "owners": [
                "owners",
                "num_owners",
                "stats.num_owners",
                "collection.owners",
            ],
            "volume": [
                "total_volume",
                "volume",
                "stats.total_volume",
                "collection.total_volume",
            ],
            "created_date": [
                "created_date",
                "createdDate",
                "created",
                "collection.created_date",
            ],
            "website": ["external_url", "website", "collection.external_url"],
            "discord": ["discord_url", "discord", "collection.discord_url"],
            "twitter": ["twitter_username", "twitter", "collection.twitter_username"],
            "instagram": [
                "instagram_username",
                "instagram",
                "collection.instagram_username",
            ],
            "wiki": ["wiki_url", "wiki", "collection.wiki_url"],
            "banner_image": [
                "banner_image_url",
                "banner",
                "collection.banner_image_url",
            ],
            "featured_image": [
                "featured_image_url",
                "image",
                "collection.featured_image_url",
            ],
            "sales": ["sales", "num_sales", "stats.sales", "stats.num_sales"],
            "average_price": ["average_price", "avg_price", "stats.average_price"],
            "market_cap": ["market_cap", "marketCap", "stats.market_cap"],
            "one_day_volume": ["one_day_volume", "stats.one_day_volume"],
            "seven_day_volume": ["seven_day_volume", "stats.seven_day_volume"],
            "thirty_day_volume": ["thirty_day_volume", "stats.thirty_day_volume"],
        }

        def _get_nested_value(d, field):
            if "." in field:
                keys = field.split(".")
                value = d
                try:
                    for k in keys:
                        value = value[k]
                    return value
                except (KeyError, TypeError):
                    return None
            return d.get(field)

        for key, possible_fields in field_mappings.items():
            for field in possible_fields:
                value = _get_nested_value(data, field)
                if value is not None:
                    info[key] = value
                    break

        return info

    def get_nft_collection_info(self, user_query: str) -> str:
        system_prompt = f"""
You are a comprehensive NFT collection assistant that helps users get detailed information about NFT collections.

Available NFT Collections and their slugs:
{json.dumps(self.collection_mapping, indent=2)}

Your task is to:
1. Parse the user's query to identify which NFT collections they want information about
2. Understand what specific information they're asking for (prices, stats, history, social links, etc.)
3. Return a JSON response with collection slugs to fetch data for
4. If they ask for "popular" or "top" collections, include: cryptopunks, boredapeyachtclub, azuki, doodles-official
5. If they ask for a specific collection, map it to the correct slug
6. If unsure about a collection name, try to find the closest match

Return format:
{{
  "collections": ["slug1", "slug2", ...],
  "user_intent": "detailed description of what specific information the user wants",
  "query_type": "price|stats|comparison|general|social|history"
}}

User query: "{user_query}"
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
                temperature=0.1,
            )
            ai_response = response.choices[0].message.content

            try:
                parsed = json.loads(ai_response)
                collections_to_fetch = parsed.get("collections", [])
                user_intent = parsed.get("user_intent", "Get NFT collection information")
                query_type = parsed.get("query_type", "general")
            except json.JSONDecodeError:
                collections_to_fetch = ["cryptopunks", "boredapeyachtclub", "azuki"]
                user_intent = "Get popular NFT collection information"
                query_type = "general"

            collection_data = []
            for slug in collections_to_fetch:
                raw = self.mcp_client.get_collection_data(slug)
                processed = self.extract_collection_info(raw)

                # Display name from mapping
                display_name = slug
                for name, mapped in self.collection_mapping.items():
                    if mapped == slug:
                        display_name = name.title()
                        break

                processed["display_name"] = display_name
                processed["slug"] = slug
                collection_data.append(processed)
                time.sleep(0.25)

            if collection_data:
                data_summary = json.dumps(collection_data, indent=2, default=str)
                format_prompt = f"""
Based on the user's original query: "{user_query}"
Query type: {query_type}
User intent: {user_intent}

And the comprehensive NFT collection data:
{data_summary}

Provide a detailed, informative response that:
1) Answers the user's question
2) Presents relevant information clearly
3) Includes specific stats when available
4) Acknowledges missing data if any
"""
                out = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a knowledgeable NFT collection analyst.",
                        },
                        {"role": "user", "content": format_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=120,
                )
                return out.choices[0].message.content

            return "I couldn't fetch data for the requested collections."
        except Exception as e:
            return f"Error while fetching NFT collection info: {str(e)}"

    def recommend_collections_for_brand(self, brand_name: str) -> Dict:
        """
        Simple LLM-driven recommender:
        - Map brand tone/industry to 3–5 likely collections (by slug)
        - Try resolving via MCP search if needed
        """
        seed_slugs = list(
            {v for v in self.collection_mapping.values()}
        )  # unique slugs
        sys = f"""
You recommend NFT collections (by slug) for a given brand. Consider brand vibe, audience, art style, and mainstream appeal.
Return a compact JSON object:
{{
  "recommendations": ["slug1", "slug2", ...],
  "rationale": "why these fit the brand"
}}

Valid slugs to consider (not exhaustive):
{json.dumps(seed_slugs, indent=2)}
"""
        try:
            prompt = f'Brand name: "{brand_name}"'
            resp = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            content = resp.choices[0].message.content
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {"recommendations": ["cryptopunks", "boredapeyachtclub", "azuki"], "rationale": "Popular, high-awareness collections with broad cultural fit."}

            # Optionally verify each recommended slug by attempting to fetch data
            verified = []
            for slug in parsed.get("recommendations", [])[:5]:
                data = self.mcp_client.get_collection_data(slug)
                if not (isinstance(data, dict) and data.get("error")):
                    verified.append(slug)
                time.sleep(0.2)

            parsed["verified"] = verified
            return parsed
        except Exception as e:
            return {
                "recommendations": ["cryptopunks", "boredapeyachtclub", "azuki"],
                "rationale": f"Fallback due to error: {str(e)}",
                "verified": [],
            }


# =========================
# FastAPI App
# =========================
assistant = NFTCollectionAssistant(OPENSEA_MCP_KEY, OPENAI_API_KEY)

app = FastAPI(title="NFT Brand Customizer Backend", version="1.0.0")

# CORS for local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",  # relax for dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str = Field(..., description="User question about NFT collections")


class ChatResponse(BaseModel):
    answer: str


class RecommendationRequest(BaseModel):
    brand_name: str = Field(..., description="Brand name for personalized recommendation")


class RecommendationResponse(BaseModel):
    recommendations: List[str]
    rationale: str
    verified: List[str]

@app.get("/")
def root():
    return {"msg": "MCP Server is running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tools")
def tools():
    res = assistant.mcp_client.list_available_tools()
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=502, detail=res)
    return res


@app.get("/collection/{slug}")
def collection(slug: str):
    res = assistant.mcp_client.get_collection_data(slug)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=404, detail=res)
    return res


@app.get("/search")
def search(q: str = Query(..., description="Search term for collections")):
    res = assistant.mcp_client.search_collections(q)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=502, detail=res)
    return res


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    answer = assistant.get_nft_collection_info(payload.query)
    return ChatResponse(answer=answer)


@app.post("/recommendations", response_model=RecommendationResponse)
def recommendations(payload: RecommendationRequest):
    rec = assistant.recommend_collections_for_brand(payload.brand_name)
    return RecommendationResponse(
        recommendations=rec.get("recommendations", []),
        rationale=rec.get("rationale", ""),
        verified=rec.get("verified", []),
    )


# Run with: uvicorn server:app --host 0.0.0.0 --port 8002 --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8002, reload=True)



