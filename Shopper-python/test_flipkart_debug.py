import asyncio
from playwright.async_api import async_playwright

async def debug_flipkart():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        url = "https://www.flipkart.com/search?q=knee+support"
        await page.goto(url, wait_until="load", timeout=60000)
        await page.wait_for_timeout(6000)

        cards = await page.query_selector_all('div[data-id]')
        print(f"\nFound {len(cards)} cards\n")

        for i, card in enumerate(cards[:3]):
            print(f"=== CARD {i} ===")

            all_links = await card.query_selector_all('a')
            print(f"Links found: {len(all_links)}")

            for j, link in enumerate(all_links[:3]):
                href = await link.get_attribute('href')
                text = await link.inner_text()
                print(f"  Link {j}: href={href[:50] if href else 'None'}...")
                print(f"          text={text[:80] if text else 'EMPTY'}")

            card_text = await card.inner_text()
            lines = card_text.split('\n')[:10]
            print(f"Card text (first 10 lines):")
            for line in lines:
                if line.strip():
                    print(f"  > {line.strip()[:80]}")
            print()

        input("Press Enter to close...")
        await browser.close()

asyncio.run(debug_flipkart())
