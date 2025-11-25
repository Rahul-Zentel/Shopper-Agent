import asyncio
from playwright.async_api import async_playwright

async def find_link():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://www.amazon.in/s?k=laptop", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        card = await page.query_selector("div[data-component-type='s-search-result']")
        if card:
            print("Testing link selectors:")
            
            # Try different selectors
            selectors = [
                "h2 a",
                "a.a-link-normal",
                "a[href*='/dp/']",
                "a",
            ]
            
            for sel in selectors:
                elem = await card.query_selector(sel)
                if elem:
                    href = await elem.get_attribute("href")
                    print(f"  {sel}: {href[:80] if href else 'NO HREF'}...")
                else:
                    print(f"  {sel}: NOT FOUND")
        
        await browser.close()

asyncio.run(find_link())
