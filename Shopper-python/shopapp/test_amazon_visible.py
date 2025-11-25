import asyncio
from scraper_amazon import amazon_search_products_async

async def test():
    print("Testing Amazon scraper with visible browser...")
    try:
        # Run with headless=False to see what's happening
        products = await amazon_search_products_async("laptop", max_results=3, headless=False)
        print(f"\nFound {len(products)} products:")
        for i, p in enumerate(products, 1):
            print(f"\n{i}. {p.title[:60]}...")
            print(f"   Price: ₹{p.price}")
            print(f"   Rating: {p.rating}")
            print(f"   URL: {p.url[:80]}...")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())

asyncio.run(test())
