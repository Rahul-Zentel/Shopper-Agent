import requests

test_queries = [
    "lipstick",
    "t-shirt for men", 
    "face cream",
    "jeans"
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Testing API: {query}")
    print('='*60)
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/search",
            json={"query": query, "marketplace": "flipkart"},
            timeout=120
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Products found: {len(data['products'])}")
            print(f"Analysis: {data['analysis']}")
            
            for i, p in enumerate(data['products'][:2], 1):
                print(f"\n{i}. {p['title'][:60]}...")
                print(f"   Price: ₹{p['price']} | Rating: {p['rating']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")
