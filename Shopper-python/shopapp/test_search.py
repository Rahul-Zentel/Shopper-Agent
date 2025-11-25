import requests

url = "http://127.0.0.1:8000/search-test"
payload = {"query": "gaming laptop"}

try:
    print(f"Testing /search-test endpoint...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Products: {len(data['products'])}")
        print(f"Analysis: {data['analysis']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Failed: {e}")
