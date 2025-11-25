import asyncio
from playwright.async_api import async_playwright

async def find_working_selectors():
    """Find what selectors actually work on Amazon"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.amazon.in/s?k=laptop"
        print(f"Loading: {url}\n")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)  # Wait for page to fully load
        
        # Get HTML of first result to analyze
        card = await page.query_selector("div[data-component-type='s-search-result']")
        if card:
            html = await card.inner_html()
            print("First 500 chars of card HTML:")
            print(html[:500])
            print("\n" + "="*80 + "\n")
            
            # Try to find any h2
            h2_elements = await card.query_selector_all("h2")
            print(f"Found {len(h2_elements)} h2 elements")
            for i, h2 in enumerate(h2_elements[:2]):
                text = await h2.inner_text()
                print(f"  h2[{i}]: {text[:80]}...")
            
            # Try to find any span with price-like text
            all_spans = await card.query_selector_all("span")
            print(f"\nFound {len(all_spans)} span elements, checking for price-like content...")
            for span in all_spans[:20]:
                text = await span.inner_text()
                if text and ("₹" in text or text.replace(",", "").replace(".", "").isdigit()):
                    print(f"  Potential price: {text}")
        
        await browser.close()

asyncio.run(find_working_selectors())
