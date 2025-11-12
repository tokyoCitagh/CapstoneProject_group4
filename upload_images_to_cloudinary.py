#!/usr/bin/env python
"""Upload static images to Cloudinary and generate environment variable commands"""

import cloudinary
import cloudinary.uploader
import os
import sys

# Try to get credentials from .env or use Railway URL
cloudinary_url = os.environ.get('CLOUDINARY_URL')

if cloudinary_url:
    # Parse cloudinary://api_key:api_secret@cloud_name
    cloudinary.config(cloudinary_url=cloudinary_url)
else:
    # Fallback to individual credentials
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'dey547z7d'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    )

images = {
    'imj2': '/Users/mac/Documents/EcomApp/store/static/images/imj2.jpg',
    'imj3': '/Users/mac/Documents/EcomApp/store/static/images/imj3.jpg',
    'imj4': '/Users/mac/Documents/EcomApp/store/static/images/imj4.jpg',
}

print("Uploading images to Cloudinary...\n")

for name, path in images.items():
    try:
        result = cloudinary.uploader.upload(
            path,
            public_id=f'static/{name}',
            overwrite=True,
            resource_type='image'
        )
        url = result['secure_url']
        print(f"✅ Uploaded {name}.jpg")
        print(f"   URL: {url}")
        print(f"   Railway command: railway variables --set STATIC_CLOUDINARY_{name.upper()}_URL=\"{url}\"\n")
    except Exception as e:
        print(f"❌ Error uploading {name}: {e}\n")

print("\n📋 Summary of Railway commands to run:")
print("=" * 60)
