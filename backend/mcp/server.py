# backend/mcp/server.py
import os
import requests
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
