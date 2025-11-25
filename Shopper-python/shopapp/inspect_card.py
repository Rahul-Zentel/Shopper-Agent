import asyncio
from playwright.async_api import async_playwright

async def inspect_card_structure():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://www.flipkart.com/search?q=lipstick", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        cards = await page.query_selector_all("div._75nlfW")
        print(f"Found {len(cards)} cards\n")
        
        if len(cards) > 0:
            first_card = cards[0]
            
            # Get the full HTML
            html = await first_card.inner_html()
            print("First 500 chars of card HTML:")
            print(html[:500])
            print("\n" + "="*60 + "\n")
            
            # Try to find link
            link = await first_card.query_selector("a")
            if link:
                href = await link.get_attribute("href")
                print(f"Link found: {href[:80] if href else 'None'}...")
            
            # Get all text
            text = await first_card.inner_text()
            print(f"\nCard text:\n{text[:200]}...")
        
        await browser.close()

asyncio.run(inspect_card_structure())
