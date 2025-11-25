import asyncio
import sys
sys.path.insert(0, 'c:/Users/Admin/Desktop/shpop/shopapp')

from scraper import flipkart_search_products_async

async def test_in_api_context():
    """Simulate the API environment"""
    try:
        print("Testing scraper in API-like context...")
        products = await asyncio.wait_for(
            flipkart_search_products_async("redmi phones", max_results=3, headless=True),
            timeout=60.0
        )
        print(f"Success! Found {len(products)} products")
        for p in products[:3]:
            print(f"- {p.title[:50]}... | ₹{p.price}")
    except Exception as e:
        import traceback
        print(f"Failed: {e}")
        print(traceback.format_exc())

# Run with asyncio
asyncio.run(test_in_api_context())
