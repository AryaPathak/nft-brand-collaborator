# backend/mcp/test_prices.py
from server import fetch_floor_price_direct

# Replace with the collection slug you want to check
collection_slug = "cryptopunks"

# Fetch the floor price
result = fetch_floor_price_direct(collection_slug)

# Print the result
print(f"Floor price for '{collection_slug}':", result)
