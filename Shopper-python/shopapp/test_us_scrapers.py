import asyncio
from .scraper_etsy import etsy_search_products_async
from .scraper_bestbuy import bestbuy_search_products_async
from .scraper_walmart import walmart_search_products_async
from .scraper_target import target_search_products_async

async def test_scrapers():
    print("Testing Walmart Scraper...")
    try:
        walmart_products = await walmart_search_products_async("laptop", max_results=3, headless=True)
        print(f"Walmart found {len(walmart_products)} products")
        for p in walmart_products:
            print(f"- {p.title} (${p.price}) [Image: {'Yes' if p.thumbnail_url else 'No'}]")
    except Exception as e:
        print(f"Walmart failed: {e}")

    print("\nTesting Target Scraper...")
    try:
        target_products = await target_search_products_async("headphones", max_results=3, headless=True)
        print(f"Target found {len(target_products)} products")
        for p in target_products:
            print(f"- {p.title} (${p.price}) [Image: {'Yes' if p.thumbnail_url else 'No'}]")
    except Exception as e:
        print(f"Target failed: {e}")

    print("\nTesting Etsy Scraper...")
    try:
        etsy_products = await etsy_search_products_async("handmade jewelry", max_results=3, headless=True)
        print(f"Etsy found {len(etsy_products)} products")
        for p in etsy_products:
            print(f"- {p.title} (${p.price}) [Image: {'Yes' if p.thumbnail_url else 'No'}]")
    except Exception as e:
        print(f"Etsy failed: {e}")

    print("\nTesting Best Buy Scraper...")
    try:
        bb_products = await bestbuy_search_products_async("laptop", max_results=3, headless=True)
        print(f"Best Buy found {len(bb_products)} products")
        for p in bb_products:
            print(f"- {p.title} (${p.price}) [Image: {'Yes' if p.thumbnail_url else 'No'}]")
    except Exception as e:
        print(f"Best Buy failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
