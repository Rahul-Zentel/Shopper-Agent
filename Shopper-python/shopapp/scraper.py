import asyncio
import urllib.parse
import re
from typing import List
from playwright.async_api import async_playwright
from .models import Product

async def flipkart_search_products_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    products: List[Product] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page = await context.new_page()

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.flipkart.com/search?q={encoded_query}"

        try:
            await page.goto(url, wait_until="load", timeout=60000)
            await page.wait_for_timeout(6000)

            cards = await page.query_selector_all('div[data-id]')

            for idx, card in enumerate(cards):
                if len(products) >= max_results:
                    break

                try:
                    all_links = await card.query_selector_all('a')

                    product_link = None
                    raw_url = None
                    title = None

                    for link in all_links:
                        href = await link.get_attribute('href')
                        if href and '/p/' in href and 'itm' in href:
                            raw_url = href
                            product_link = link

                            link_text = await link.inner_text()
                            if link_text:
                                lines = [l.strip() for l in link_text.split('\n') if l.strip()]
                                for line in lines:
                                    if (len(line) > 15 and
                                        not line.startswith('₹') and
                                        not line.startswith('Buy ') and
                                        not line.lower().startswith('save ') and
                                        not line.lower().startswith('off ') and
                                        'items' not in line.lower() and
                                        'extra' not in line.lower()):
                                        title = line
                                        break

                            if title and len(title) > 15:
                                break

                    if not product_link or not raw_url:
                        continue

                    if not title:
                        card_text = await card.inner_text()
                        lines = [l.strip() for l in card_text.split('\n') if l.strip()]

                        for line in lines:
                            if (len(line) > 15 and
                                not line.startswith('₹') and
                                not line.startswith('Buy ') and
                                not line.lower().startswith('save ') and
                                not line.lower().startswith('off ') and
                                not line.lower().startswith('get ') and
                                'items' not in line.lower() and
                                'extra' not in line.lower() and
                                'delivery' not in line.lower() and
                                'out of 5' not in line.lower()):
                                title = line
                                break

                    if not title or len(title) < 10:
                        continue

                    if raw_url.startswith('/'):
                        full_url = f"https://www.flipkart.com{raw_url}"
                    elif raw_url.startswith('http'):
                        full_url = raw_url
                    else:
                        full_url = f"https://www.flipkart.com/{raw_url}"

                    parsed = urllib.parse.urlparse(full_url)
                    path = parsed.path

                    query_params = urllib.parse.parse_qs(parsed.query)
                    pid = query_params.get('pid', [None])[0]

                    if pid:
                        clean_url = f"https://www.flipkart.com{path}?pid={pid}"
                    else:
                        clean_url = f"https://www.flipkart.com{path}"

                    card_html = await card.inner_html()

                    price = None
                    price_matches = re.findall(r'₹([\d,]+)', card_html)
                    if price_matches:
                        try:
                            price = float(price_matches[0].replace(',', ''))
                        except:
                            pass

                    rating = None
                    rating_match = re.search(r'(\d\.\d)\s*★', card_html)
                    if not rating_match:
                        rating_match = re.search(r'(\d\.\d)\s*<', card_html)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                        except:
                            pass

                    thumbnail_url = None
                    img = await card.query_selector('img')
                    if img:
                        thumbnail_url = await img.get_attribute('src')

                    product = Product(
                        marketplace="Flipkart",
                        title=title,
                        url=clean_url,
                        price=price,
                        currency="INR",
                        rating=rating,
                        rating_count=None,
                        is_sponsored=False,
                        thumbnail_url=thumbnail_url,
                        primary_features=[],
                    )
                    products.append(product)

                except Exception:
                    continue

        except Exception:
            pass
        finally:
            await browser.close()

    return products
