import os
import subprocess
import sys
import re

# CONFIG
NFT_IMAGES_DIR = "C:/Users/DELL/Desktop/NFT-Brand-Customizer/backend/NFTminting/images"
SIGNER = "testnet-deployer"
NETWORK = "testnet"
CONTRACT_ADDR = "0x8e1e0dc93cf85473"
OUTPUT_DIR = "C:/Users/DELL/Desktop/NFT-Brand-Customizer/backend/NFTminting/output_information"   # ✅ folder for per-NFT logs

# Make sure the output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_command(command):
    """Run a shell command and capture only the final transaction result."""
    print(f"\n>>> Running: {command}")

    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    output = result.stdout

    # ✅ Extract only from "Block ID" onwards
    if "Block ID" in output:
        final_output = output.split("Block ID", 1)[1]
        final_output = "Block ID" + final_output
    else:
        final_output = output

    print(final_output)

    # ✅ Extract NFT ID from output (the "id (UInt64): X" field under Events)
    nft_id = None
    match = re.search(r"- id \(UInt64\): (\d+)", final_output)
    if match:
        nft_id = match.group(1)

    # Save to a per-NFT file
    if nft_id:
        file_path = os.path.join(OUTPUT_DIR, f"{nft_id}.txt")
    else:
        # fallback if ID not found
        file_path = os.path.join(OUTPUT_DIR, "unknown.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_output)

    print(f"✅ Saved transaction info to {file_path}")


def mint_only():
    for idx, filename in enumerate(os.listdir(NFT_IMAGES_DIR), start=1):
        file_path = os.path.join(NFT_IMAGES_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        name = f"My NFT #{idx}"
        description = f"Minted from local file: {filename}"
        image_url = f"file://{os.path.abspath(file_path)}"
        external_url = "https://example.com"

        mint_cmd = (
            f'flow transactions send ./cadence/transactions/mint_nft.cdc '
            f'{CONTRACT_ADDR} "{name}" "{description}" "{image_url}" "{external_url}" '
            f'--network {NETWORK} --signer {SIGNER}'
        )
        run_command(mint_cmd)


if __name__ == "__main__":
    if not os.path.exists(NFT_IMAGES_DIR):
        print(f"❌ Images directory {NFT_IMAGES_DIR} not found")
        sys.exit(1)

    mint_only()
