import asyncio
from playwright.async_api import async_playwright

async def test_h2_extraction():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://www.amazon.in/s?k=laptop", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        cards = await page.query_selector_all("div[data-component-type='s-search-result']")
        print(f"Found {len(cards)} cards\n")
        
        for i, card in enumerate(cards[:3]):
            print(f"=== Card {i+1} ===")
            
            # Method 1: Query all h2
            h2_list = await card.query_selector_all("h2")
            print(f"h2 elements found: {len(h2_list)}")
            for j, h2 in enumerate(h2_list):
                try:
                    text = await h2.inner_text()
                    print(f"  h2[{j}] text: {text[:80] if text else 'EMPTY'}...")
                except Exception as e:
                    print(f"  h2[{j}] error: {e}")
            
            # Method 2: Try direct selector
            h2_direct = await card.query_selector("h2")
            if h2_direct:
                try:
                    text = await h2_direct.inner_text()
                    print(f"Direct h2 text: {text[:80]}...")
                except Exception as e:
                    print(f"Direct h2 error: {e}")
            else:
                print("Direct h2: NOT FOUND")
            
            # Method 3: Get all text
            all_text = await card.inner_text()
            lines = all_text.split('\n')
            print(f"First 3 lines of card text:")
            for line in lines[:3]:
                if line.strip():
                    print(f"  {line.strip()[:80]}...")
            print()
        
        await browser.close()

asyncio.run(test_h2_extraction())
