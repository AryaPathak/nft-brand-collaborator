# backend/mcp/server.py
import os
import requests

import json
import uuid
import time
from openai import OpenAI
from typing import Dict, List, Optional
import dotenv 
import os

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
# Ensure mint.py exists in the same directory or adjust the import path accordingly
from NFTminting.mint import mint_image, NFT_IMAGES_DIR


dotenv.load_dotenv()
OPENSEA_MCP_KEY = os.getenv("OPENSEA_MCP_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenSeaMCPClient:
    def __init__(self, api_key):
        self.base_url = "https://mcp.opensea.io/mcp"
        self.headers = {
            "Authorization": f"Bearer {OPENSEA_MCP_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        self.request_id = 1
        self.session_id = None
        self.initialize_and_setup_session()
    
    def handle_sse_response(self, response):
        """Handle Server-Sent Events response"""
        events = []
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
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
            "id": self.request_id
        }
        
        if params:
            payload["params"] = params
        
        headers = self.headers.copy()
        if use_session_id and self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        
        try:
            response = requests.post(self.base_url, 
                                   json=payload,
                                   headers=headers,
                                   stream=True,
                                   timeout=30)
            
            self.request_id += 1
            
            if 'Mcp-Session-Id' in response.headers:
                self.session_id = response.headers['Mcp-Session-Id']
            
            content_type = response.headers.get('content-type', '')
            
            if 'text/event-stream' in content_type:
                return self.handle_sse_response(response)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def initialize_and_setup_session(self):
        """Initialize connection with proper session handling"""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "Python MCP Client",
                "version": "1.0"
            }
        }
        
        result = self.send_request("initialize", params, use_session_id=True)
        
        if isinstance(result, dict) and result.get('error'):
            result = self.send_request("initialize", params, use_session_id=False)
            if not self.session_id:
                self.session_id = str(uuid.uuid4())
        
        return result
    
    def list_available_tools(self):
        """Get available tools from the MCP server"""
        return self.send_request("tools/list")
    
    def get_collection_data(self, collection_slug):
        """Get comprehensive collection data"""
        collection_tools = [
            ("get_collection", {"slug": collection_slug}),
            ("get_collection_stats", {"collection_slug": collection_slug}),
            ("collection_stats", {"slug": collection_slug}),
            ("get_collection_info", {"collection": collection_slug})
        ]
        
        for tool_name, args in collection_tools:
            result = self.send_request("tools/call", {
                "name": tool_name,
                "arguments": args
            })
            
            if not (isinstance(result, dict) and result.get('error')):
                return result
        
        return {"error": "No data available"}
    
    def search_collections(self, query):
        """Search for collections"""
        search_tools = [
            ("search_collections", {"query": query}),
            ("find_collection", {"name": query}),
            ("collection_search", {"search_term": query})
        ]
        
        for tool_name, args in search_tools:
            result = self.send_request("tools/call", {
                "name": tool_name,
                "arguments": args
            })
            
            if not (isinstance(result, dict) and result.get('error')):
                return result
        
        return {"error": "Search not available"}

from fastmcp import FastMCP
import dotenv

# Load .env
dotenv.load_dotenv()


OPENSEA_MCP_KEY = os.getenv("OPENSEA_MCP_KEY")
if not OPENSEA_MCP_KEY:
    print("⚠️  WARNING: OpenSea API key not found in .env. Please set OPENSEA_MCP_KEY.")
HEADERS = {"X-API-KEY": OPENSEA_MCP_KEY} if OPENSEA_MCP_KEY else {}

# Initialize MCP server
mcp = FastMCP("opensea-mcp")

# Tool: fetch floor price for a collection
def _get_floor_price_raw(collection_slug: str):
    """Raw function to fetch floor price directly"""
    if not OPENSEA_MCP_KEY:
        return {"error": "Missing OpenSea API key. Set OPENSEA_MCP_KEY in .env"}

    url = f"https://api.opensea.io/api/v2/collections/{collection_slug}/stats"
    resp = requests.get(url, headers=HEADERS)
    
    if resp.status_code == 401:
        return {"error": "Invalid OpenSea API key. Check your OPENSEA_MCP_KEY"}
    elif resp.status_code == 200:
        data = resp.json()
        return {"floor_price": data.get("total", {}).get("floor_price")}
    else:
        return {"error": f"Request failed with status {resp.status_code}: {resp.text}"}

@mcp.tool()
def get_floor_price(collection_slug: str):
    return _get_floor_price_raw(collection_slug)

# Direct test function
def fetch_floor_price_direct(collection_slug: str):
    return _get_floor_price_raw(collection_slug)

if __name__ == "__main__":
    print("Starting MCP server... (Press Ctrl+C to stop)")
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nMCP server stopped.")



@app.post("/api/mint-nft")
async def mint_nft(file: UploadFile, brand: str = Form(...)):
    try:
        # Save uploaded file temporarily
        save_path = os.path.join(NFT_IMAGES_DIR, file.filename)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call mint logic
        file_path, nft_id, tx_output = mint_image(save_path, name=brand, description=f"Branded NFT {brand}")

        if not nft_id:
            return JSONResponse({"error": "Minting failed"}, status_code=500)

        # Return log file to download
        return FileResponse(
            file_path,
            media_type="text/plain",
            filename=f"{nft_id}.txt"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)