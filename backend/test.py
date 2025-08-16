import base64
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import os

# Load .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key, timeout=120)

def edit_image(image_path: str, brand_name: str, output_path: str = "edited_image.png"):
    """
    Convert image to RGBA, create a mask, and edit the image via OpenAI.
    """
    # Open original image
    img = Image.open(image_path).convert("RGBA")  # Convert to RGBA

    # Save RGBA temporary image
    temp_rgba_path = image_path.replace(".png", "_rgba.png")
    img.save(temp_rgba_path)

    # Create fully opaque mask (255 = keep everything)
    mask = Image.new("L", img.size, 255)  
    mask_path = image_path.replace(".png", "_mask.png")
    mask.save(mask_path)

    prompt = (
        f"Take this image and create a promotional version featuring the brand '{brand_name}'. "
        "Retain the original art style, colors, and composition, but integrate the brand naturally. "
        "The character in the original image should be using the product '{brand_name}'."
        "The correct use is important, and not like only merchandise."
    )

    print("Sending edit request to OpenAI...")
    with open(temp_rgba_path, "rb") as img_file, open(mask_path, "rb") as mask_file:
        response = client.images.edit(
            model="gpt-image-1",
            image=img_file,
            mask=mask_file,
            prompt=prompt,
            size="1024x1024"
        )

    # Decode returned image
    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    # Clean up temp files
    os.remove(temp_rgba_path)
    os.remove(mask_path)

    print(f"Edited image saved to {output_path}")
