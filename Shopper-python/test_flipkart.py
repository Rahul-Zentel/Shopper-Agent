import asyncio
from playwright.async_api import async_playwright
import re

async def test_flipkart():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page = await context.new_page()

        url = "https://www.flipkart.com/search?q=knee+support"
        print(f"\nNavigating to: {url}")

        await page.goto(url, wait_until="load", timeout=60000)
        await page.wait_for_timeout(8000)

        print(f"\nPage Title: {await page.title()}")
        print(f"Current URL: {page.url}")

        html = await page.content()
        print(f"HTML Length: {len(html)}")

        if 'captcha' in html.lower():
            print("⚠️ CAPTCHA DETECTED!")
        if 'robot' in html.lower():
            print("⚠️ BOT DETECTION!")

        print("\n=== Testing Selectors ===")
        selectors = [
            'div[data-id]',
            'div._1AtVbE',
            'a._1fQZEK',
            'div.tUxRFH',
            'div.cPHDOP',
            'a.CGtC98',
            'div._75nlfW',
            'a.s1Q9rs',
            'div > a',
        ]

        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                print(f"{selector}: {len(elements)} elements")
                if len(elements) > 0 and len(elements) < 100:
                    first = elements[0]
                    text = await first.inner_text()
                    print(f"  Sample text: {text[:100]}")
            except Exception as e:
                print(f"{selector}: ERROR - {e}")

        print("\n=== Looking for Product Links ===")
        all_links = await page.query_selector_all('a')
        product_links = []
        for link in all_links[:50]:
            href = await link.get_attribute('href')
            if href and '/p/' in href:
                product_links.append(href)
                text = await link.inner_text()
                print(f"Found product link: {text[:50]}")

        print(f"\nTotal product links found: {len(product_links)}")

        print("\n=== Saving Debug Files ===")
        await page.screenshot(path="flipkart_test.png", full_page=True)
        with open("flipkart_test.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Screenshot: flipkart_test.png")
        print("HTML: flipkart_test.html")

        print("\n=== Looking for Prices ===")
        prices = re.findall(r'₹\s*([\d,]+)', html)
        print(f"Found {len(prices)} prices: {prices[:10]}")

        input("\nPress Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_flipkart())
