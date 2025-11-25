import requests
import json

# Test the test endpoint
url = "http://127.0.0.1:8000/test"
payload = {"query": "test product"}

try:
    print(f"Testing /test endpoint...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Test endpoint failed: {e}")

# Test root endpoint
try:
    print(f"\nTesting / endpoint...")
    response = requests.get("http://127.0.0.1:8000/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Root endpoint failed: {e}")
