# backend/mcp/server.py
from mcp.server.fastmcp import FastMCP
import requests
import os

# Init MCP server
mcp = FastMCP("opensea-mcp")

# Load API key from env
OPENSEA_API_KEY = os.getenv("OPENSEA_API_KEY")
HEADERS = {"X-API-KEY": OPENSEA_API_KEY} if OPENSEA_API_KEY else {}

# Tool: fetch floor price for a collection
@mcp.tool()
def get_floor_price(collection_slug: str):
    """
    Get the current floor price of a given collection from OpenSea.
    """
    url = f"https://api.opensea.io/api/v2/collections/{collection_slug}/stats"
    resp = requests.get(url, headers=HEADERS)

    if resp.status_code == 200:
        data = resp.json()
        return {"floor_price": data.get("total", {}).get("floor_price")}
    else:
        return {"error": resp.text}

if __name__ == "__main__":
    mcp.run()
