import asyncio
from scraper_amazon import amazon_search_products_async

async def test():
    print("Testing Amazon scraper with max_results=1...")
    try:
        products = await amazon_search_products_async("laptop", max_results=1, headless=True)
        print(f"\n=== RESULT ===")
        print(f"Found {len(products)} products")
        for i, p in enumerate(products, 1):
            print(f"\n{i}. {p.title}")
            print(f"   Price: ₹{p.price}")
            print(f"   Rating: {p.rating}")
            print(f"   URL: {p.url}")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

asyncio.run(test())
