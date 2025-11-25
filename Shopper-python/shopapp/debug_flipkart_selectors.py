import asyncio
from playwright.async_api import async_playwright

async def debug_flipkart_selectors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test with lipstick
        await page.goto("https://www.flipkart.com/search?q=lipstick", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Try different card selectors
        selectors = [
            "a.CGtC98",  # Old selector
            "div._75nlfW",  # New grid item
            "div._1sdMkc",  # Product card
            "a.rPDeLR",  # Product link
            "div.tUxRFH",  # Another variant
        ]
        
        for sel in selectors:
            elements = await page.query_selector_all(sel)
            print(f"{sel}: {len(elements)} elements")
        
        # Get page HTML snippet
        html = await page.content()
        # Find first product-like div
        if "lipstick" in html.lower():
            print("\n✓ Page loaded with lipstick results")
        
        await browser.close()

asyncio.run(debug_flipkart_selectors())
