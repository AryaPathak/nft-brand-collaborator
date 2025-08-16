from fastapi import FastAPI
import httpx
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import shutil
import os
import base64
import requests
import tempfile
import traceback

from test import edit_image

# Load env variables
load_dotenv()

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENSEA_API_KEY = os.getenv("OPENSEA_API_KEY")

@app.get("/")
def home():
    return {"message": "Backend is running ✅"}


@app.get("/nfts/{username}")
async def get_user_nfts(username: str):
    headers = {
        "accept": "application/json",
        "x-api-key": OPENSEA_API_KEY
    }

    async with httpx.AsyncClient() as client:
        # Get wallet address
        account_url = f"https://api.opensea.io/api/v2/accounts/{username}"
        account_res = await client.get(account_url, headers=headers)
        account_data = account_res.json()

        wallet_address = account_data.get("address")
        if not wallet_address:
            return {"error": "No wallet address found for this username"}

        # Get NFTs for wallet
        nfts_url = f"https://api.opensea.io/api/v2/chain/ethereum/account/{wallet_address}/nfts"
        nfts_res = await client.get(nfts_url, headers=headers)
        nfts_data = nfts_res.json()

        # Return all raw data to frontend
        return {
            "account": account_data,
            "nfts": nfts_data
        }



@app.get("/collection/{collectionName}")
async def get_collection_nfts(collectionName: str):
    headers = {
        "accept": "application/json",
        "x-api-key": OPENSEA_API_KEY
    }

    async with httpx.AsyncClient() as client:
        # Get collection details
        collection_url = f"https://api.opensea.io/api/v2/collection/{collectionName}/nfts"
        collection_res = await client.get(collection_url, headers=headers)
        collection_data = collection_res.json()

        # Get NFTs for collection
        nfts_url = f"https://api.opensea.io/api/v2/collection/{collectionName}/nfts"
        nfts_res = await client.get(nfts_url, headers=headers)
        nfts_data = nfts_res.json()

        # Return all raw data to frontend
        return {
            "collection": collection_data,
            "nfts": nfts_data
        }

        if not wallet_address:
            return {"error": "No wallet address found for this username"}

        # Return all raw data to frontend
        return {
            "account": account_data,
            "nfts": nfts_data
        }




# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/api/edit-nft")
async def edit_nft(
    file_url: str = Form(...),
    brand: str = Form(...),
    metadata_url: str = Form(None)
):
    """
    Edit an NFT given its URL and a brand name.
    If metadata_url is provided, return updated metadata with new image.
    """
    temp_file_path = None
    try:
        # --- 1. Fetch metadata if provided ---
        metadata = {}
        if metadata_url:
            try:
                meta_resp = requests.get(metadata_url)
                meta_resp.raise_for_status()
                metadata = meta_resp.json()
            except Exception as e:
                print("⚠️ Metadata fetch failed:", e)

        # --- 2. Download the NFT image ---
        resp = requests.get(file_url)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(resp.content)
            temp_file_path = temp_file.name

        # --- 3. Call OpenAI image edit ---
        output_path = f"edited_{os.path.basename(temp_file_path)}"
        edit_image(temp_file_path, brand, output_path)

        # --- 4. Encode final image ---
        with open(output_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")

        # --- 5. Return updated metadata if available ---
        if metadata:
            # Replace image field
            metadata["image"] = "data:image/png;base64," + image_base64
            # Add brand attribute
            metadata.setdefault("attributes", []).append({
                "trait_type": "Brand",
                "value": brand
            })
            return JSONResponse({"metadata": metadata})
        else:
            # Just return base64 image if no metadata given
            return JSONResponse({"image_base64": image_base64})

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse({"error": str(e)}, status_code=500)

    finally:
        # --- 6. Clean up temp files ---
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)
