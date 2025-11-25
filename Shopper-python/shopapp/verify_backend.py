import requests
import json

url = "http://127.0.0.1:8000/search"
payload = {"query": "test product"}
headers = {"Content-Type": "application/json"}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response:", json.dumps(response.json(), indent=2)[:200] + "...")
    else:
        print("Error Response:", response.text)
except Exception as e:
    print(f"Connection failed: {e}")
