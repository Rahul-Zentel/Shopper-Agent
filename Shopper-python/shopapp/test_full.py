import requests
import json
import time

url = "http://127.0.0.1:8000/search"
payload = {"query": "redmi phones under 30000"}

print("Sending search request...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload)}")

start = time.time()
try:
    response = requests.post(url, json=payload, timeout=120)
    elapsed = time.time() - start
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Time taken: {elapsed:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nProducts found: {len(data['products'])}")
        print(f"Analysis: {data['analysis']}")
        
        for i, product in enumerate(data['products'][:3], 1):
            print(f"\n{i}. {product['title']}")
            print(f"   Price: ₹{product['price']}")
            print(f"   Rating: {product['rating']}")
            print(f"   URL: {product['url'][:60]}...")
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.Timeout:
    print("Request timed out after 120 seconds")
except Exception as e:
    print(f"Request failed: {e}")
