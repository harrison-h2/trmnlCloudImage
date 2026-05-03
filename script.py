import os
import cloudinary
from cloudinary.api import resources_by_tag
import random
import requests

# 1. Configure Cloudinary credentials via Environment Variables
cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key = os.environ.get("CLOUDINARY_API_KEY"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
    secure = True
)

def update_trmnl_display():
    tag_name = "mono" # Change this if your tag is different
    
    try:
        print(f"Fetching images tagged with: {tag_name}")
        response = resources_by_tag(tag_name, max_results=100)
        images = response.get("resources", [])
        
        if not images:
            print(f"No images found with tag: {tag_name}")
            return

        chosen_image = random.choice(images)
        public_id = chosen_image["public_id"]

        # Generate TRMNL-optimized URL (800x480, grayscale)
        optimized_url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            width=980,
            height=720,
            crop="fill",
            effect="grayscale",
            border="30px_solid_white",
            format="jpg"
        )
        
        print(f"Selected Image URL: {optimized_url}")

        # Push to TRMNL Webhook
        plugin_uuid = os.environ.get("TRMNL_PLUGIN_UUID")
        trmnl_webhook_url = f"https://trmnl.com/api/custom_plugins/{plugin_uuid}"
        trmnl_api_key = os.environ.get("TRMNL_API_KEY")
        
        headers = {
            "Authorization": f"Bearer {trmnl_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "merge_variables": {
                "image_url": optimized_url
            }
        }
        
        trmnl_response = requests.post(trmnl_webhook_url, json=payload, headers=headers)
        
        if trmnl_response.status_code == 200:
            print("Successfully pushed new image to TRMNL!")
        else:
            print(f"Failed to push to TRMNL: {trmnl_response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_trmnl_display()
