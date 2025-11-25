import requests
import json

print("Testing FLIPKART...")
response = requests.post("http://127.0.0.1:8000/search", 
    json={"query": "laptop", "marketplace": "flipkart"},
    timeout=120
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Products: {len(data['products'])}")
    for p in data['products'][:2]:
        print(f"  - {p['title'][:50]}... | ₹{p['price']}")

print("\n" + "="*80 + "\n")

print("Testing AMAZON...")
response = requests.post("http://127.0.0.1:8000/search", 
    json={"query": "laptop", "marketplace": "amazon"},
    timeout=120
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Products: {len(data['products'])}")
    for p in data['products'][:2]:
        print(f"  - {p['title'][:50]}... | ₹{p['price']}")
