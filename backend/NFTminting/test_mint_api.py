import requests

API_URL = "http://127.0.0.1:8000/api/mint-nft"
IMAGE_PATH = r"C:\Users\DELL\Desktop\nft-brand-customizer\download.png"  # change to your test NFT image

with open(IMAGE_PATH, "rb") as img:
    files = {"file": img}
    data = {"brand": "TestBrand"}
    resp = requests.post(API_URL, files=files, data=data)

if resp.status_code == 200:
    # Save the response to txt file
    out_path = "minted_nft_info.txt"
    with open(out_path, "wb") as f:
        f.write(resp.content)
    print(f"✅ NFT minted! Info saved to {out_path}")
else:
    print("❌ Error:", resp.text)
