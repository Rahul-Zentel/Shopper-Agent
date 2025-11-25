import asyncio
from playwright.async_api import async_playwright

async def debug_amazon():
    """Debug Amazon page structure"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.amazon.in/s?k=laptop"
        print(f"Loading: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for results
        try:
            await page.wait_for_selector("div[data-component-type='s-search-result']", timeout=10000)
            print("✓ Found search results")
        except:
            print("✗ Could not find search results")
            await browser.close()
            return
        
        # Get first card
        card = await page.query_selector("div[data-component-type='s-search-result']")
        if not card:
            print("No card found")
            await browser.close()
            return
        
        print("\n=== Debugging First Product Card ===")
        
        # Try different title selectors
        print("\nTitle selectors:")
        title1 = await card.query_selector("h2 a span")
        print(f"  h2 a span: {await title1.inner_text() if title1 else 'NOT FOUND'}")
        
        title2 = await card.query_selector("h2 span")
        print(f"  h2 span: {await title2.inner_text() if title2 else 'NOT FOUND'}")
        
        title3 = await card.query_selector("h2")
        print(f"  h2: {await title3.inner_text() if title3 else 'NOT FOUND'}")
        
        # Try link
        print("\nLink selectors:")
        link = await card.query_selector("h2 a")
        if link:
            href = await link.get_attribute("href")
            print(f"  h2 a href: {href[:80] if href else 'NO HREF'}...")
        else:
            print(f"  h2 a: NOT FOUND")
        
        # Try price
        print("\nPrice selectors:")
        price1 = await card.query_selector("span.a-price-whole")
        print(f"  span.a-price-whole: {await price1.inner_text() if price1 else 'NOT FOUND'}")
        
        price2 = await card.query_selector("span.a-price span.a-offscreen")
        print(f"  span.a-price span.a-offscreen: {await price2.inner_text() if price2 else 'NOT FOUND'}")
        
        # Try rating
        print("\nRating selectors:")
        rating1 = await card.query_selector("span.a-icon-alt")
        print(f"  span.a-icon-alt: {await rating1.inner_text() if rating1 else 'NOT FOUND'}")
        
        rating2 = await card.query_selector("i.a-icon-star-small span")
        print(f"  i.a-icon-star-small span: {await rating2.inner_text() if rating2 else 'NOT FOUND'}")
        
        await browser.close()

asyncio.run(debug_amazon())
