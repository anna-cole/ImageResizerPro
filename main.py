import os
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Configuration
INPUT_FILE = "input_urls.xlsx"  # Excel file with image URLs
OUTPUT_FILE = "output_urls.xlsx"  # Output file with new image URLs
RESIZED_FOLDER = "resized_images"  # Temporary folder for resized images
NEW_IMAGE_SIZE = (1000, 1000)  # Resize dimensions (Width, Height)

# Create output folder if it doesn't exist
os.makedirs(RESIZED_FOLDER, exist_ok=True)

# Read Excel file
df = pd.read_excel(INPUT_FILE)

# Ensure the correct column name
if 'URL' not in df.columns:
    raise ValueError("Excel file must contain a column named 'URL'")

new_urls = []

for index, row in df.iterrows():
    image_url = row['URL']
    
    try:
        # Download image
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise error for bad responses
        img = Image.open(BytesIO(response.content))

        # Resize image
        img_resized = img.resize(NEW_IMAGE_SIZE)

        # Save resized image temporarily
        new_filename = os.path.join(RESIZED_FOLDER, f"image_{index}.jpg")
        img_resized.save(new_filename, "JPEG")

        # Upload resized image to Cloudinary
        upload_result = cloudinary.uploader.upload(new_filename, folder="resized_images")

        # Get the Cloudinary URL
        new_url = upload_result.get("secure_url", "Failed")
        new_urls.append(new_url)

        print(f"Processed: {image_url} -> {new_url}")

    except Exception as e:
        print(f"Failed to process {image_url}: {e}")
        new_urls.append("Failed")

# Save the new URLs to an Excel file
df["New URL"] = new_urls
df.to_excel(OUTPUT_FILE, index=False)

print(f"Processing complete. New URLs saved in {OUTPUT_FILE}")
