import requests

print("=== Testing Flipkart ===")
response = requests.post("http://127.0.0.1:8000/search", 
    json={"query": "cricket bats under 2000", "marketplace": "flipkart"},
    timeout=120
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Products: {len(data['products'])}")
    for p in data['products'][:3]:
        print(f"  - {p['title'][:60]}... | ₹{p['price']}")
else:
    print(f"Error: {response.text}")

print("\n=== Testing Amazon ===")
response = requests.post("http://127.0.0.1:8000/search", 
    json={"query": "cricket bats under 2000", "marketplace": "amazon"},
    timeout=120
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Products: {len(data['products'])}")
    for p in data['products'][:3]:
        print(f"  - {p['title'][:60]}... | ₹{p['price']}")
else:
    print(f"Error: {response.text}")
