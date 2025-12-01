import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shopapp.scraper import flipkart_search_products_async

async def test_flipkart_visible():
    """Test Flipkart scraper with visible browser to see what's happening"""
    print("Testing Flipkart scraper with VISIBLE browser...")
    print("This will help us see what's going wrong.\n")
    
    products = await flipkart_search_products_async("laptop", max_results=6, headless=False)
    
    print(f"\n{'='*60}")
    print(f"RESULTS: Found {len(products)} products from Flipkart")
    print(f"{'='*60}\n")
    
    if len(products) == 0:
        print("❌ NO PRODUCTS FOUND - Scraper is failing!")
        print("Check the browser window to see what happened.")
    else:
        print("✓ Products found:")
        for i, p in enumerate(products, 1):
            print(f"{i}. {p.title[:60]}...")
            print(f"   Price: ₹{p.price} | Rating: ⭐{p.rating}")
            print(f"   URL: {p.url[:80]}...")
            print()

if __name__ == "__main__":
    asyncio.run(test_flipkart_visible())
