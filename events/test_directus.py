#!/usr/bin/env python3
import requests
from datetime import datetime

# Test Directus API
DIRECTUS_URL = "https://calapi.buerofalk.de"
DIRECTUS_TOKEN = "APpU898yct7V2VyMFfcJse_7WXktDY-o"

headers = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json"
}

# Test PATCH request
item_id = 1609
update_data = {
    "processed": True,
    "processed_at": datetime.now().isoformat(),
    "processing_status": "processed"
}

url = f"{DIRECTUS_URL}/items/scraped_data/{item_id}"
print(f"Testing PATCH request to: {url}")
print(f"Data: {update_data}")

try:
    response = requests.patch(url, headers=headers, json=update_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    # This is what the analyzer is doing
    response.raise_for_status()
    print("Success! No exception raised.")
    
except requests.exceptions.HTTPError as e:
    print(f"HTTPError: {e}")
    print(f"Response text: {response.text[:500]}")
except Exception as e:
    print(f"Other error: {e}")