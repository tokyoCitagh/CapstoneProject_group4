import cloudinary.api

try:
    result = cloudinary.api.resources(type='upload', prefix='service_attachments/', max_results=50)
    print(f'Found {len(result.get("resources", []))} files on Cloudinary:')
    for r in result.get('resources', []):
        print(f'  {r["public_id"]} - {r["secure_url"]}')
except Exception as e:
    print(f'Error: {e}')
