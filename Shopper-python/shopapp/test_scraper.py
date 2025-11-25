import asyncio
from scraper import flipkart_search_products_async

async def test():
    print("Testing scraper...")
    try:
        products = await flipkart_search_products_async("redmi phones under 30000", max_results=3, headless=True)
        print(f"\nFound {len(products)} products:")
        for i, p in enumerate(products, 1):
            print(f"\n{i}. {p.title}")
            print(f"   Price: {p.price}")
            print(f"   Rating: {p.rating}")
            print(f"   URL: {p.url}")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())

asyncio.run(test())
