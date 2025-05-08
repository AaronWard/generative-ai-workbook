import base64
import os
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path


OLLAMA_API = 'http://localhost:11434/api/generate'
MODEL_NAME = 'llava'
IMAGE_DIR = './img'  # <-- change this to your dataset folder

# Set your dataset directory here
DATASET_DIR = Path("img")
DATASET_DIR.mkdir(exist_ok=True)

# Supported image formats
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# Collect and sort all image files
image_files = sorted([f for f in DATASET_DIR.iterdir() if f.suffix.lower() in VALID_EXTENSIONS])

# Rename and create empty .txt files
for idx, image_path in enumerate(image_files, 1):
    # Format filename as pollock01.jpg, pollock02.jpg, ...
    new_image_name = f"pollock{idx:02d}.jpg"
    new_image_path = DATASET_DIR / new_image_name

    # Convert to .jpg if needed
    if image_path.suffix.lower() != ".jpg":
        img = Image.open(image_path).convert("RGB")
        img.save(new_image_path)
        image_path.unlink()  # Delete the old file
    else:
        image_path.rename(new_image_path)

    # Create matching empty .txt caption file
    txt_path = new_image_path.with_suffix(".txt")
    txt_path.touch()

    print(f"Renamed {image_path.name} → {new_image_path.name} and created {txt_path.name}")


def encode_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")  # ensure compatibility
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_caption(base64_image):
    payload = {
        "model": MODEL_NAME,
        "prompt": "Generate a detailed caption describing this image. Start with the word: pollockdrip.",
        "images": [base64_image],
        "stream": False 
    }

    response = requests.post(OLLAMA_API, json=payload)
    try:
        data = response.json()
        return data.get("response", "").strip()
    except requests.exceptions.JSONDecodeError as e:
        print("Failed to parse response:", response.text)
        raise

def caption_all_images():
    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(IMAGE_DIR, filename)
            txt_path = os.path.splitext(image_path)[0] + ".txt"

            print(f"Captioning: {filename}")
            b64_img = encode_image(image_path)
            caption = generate_caption(b64_img)
        
            # Trigger word: pollockdrip
            caption = f"pollockdrip, {caption}"  # Append filename to caption

            with open(txt_path, "w") as f:
                f.write(caption)

            print(f"Saved caption to {txt_path}")

if __name__ == "__main__":
    caption_all_images()
