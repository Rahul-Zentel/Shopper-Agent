import asyncio
from scraper import flipkart_search_products_async
from scraper_amazon import amazon_search_products_async

async def test_different_categories():
    categories = [
        "lipstick",
        "t-shirt for men",
        "face cream",
        "jeans"
    ]
    
    for category in categories:
        print(f"\n{'='*60}")
        print(f"Testing: {category}")
        print('='*60)
        
        # Test Flipkart
        print("\n[FLIPKART]")
        try:
            products = await flipkart_search_products_async(category, max_results=2, headless=True)
            print(f"Found {len(products)} products")
            for p in products[:2]:
                print(f"  - {p.title[:50]}... | ₹{p.price}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test Amazon
        print("\n[AMAZON]")
        try:
            products = await amazon_search_products_async(category, max_results=2, headless=True)
            print(f"Found {len(products)} products")
            for p in products[:2]:
                print(f"  - {p.title[:50]}... | ₹{p.price}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_different_categories())
