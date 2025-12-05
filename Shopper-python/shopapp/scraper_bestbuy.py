import asyncio
import urllib.parse
import re
from typing import List
from playwright.async_api import async_playwright
from .models import Product

async def bestbuy_search_products_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    products: List[Product] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.bestbuy.com/site/searchpage.jsp?st={encoded_query}"

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(3000)

            cards = await page.query_selector_all('li.sku-item')

            for card in cards[:max_results]:
                try:
                    title_el = await card.query_selector('h4.sku-title a, h4.sku-header a')
                    if not title_el:
                        continue

                    title = await title_el.inner_text()
                    title = title.strip()
                    if len(title) < 5:
                        continue

                    href = await title_el.get_attribute('href')
                    if not href:
                        continue

                    if href.startswith('/'):
                        prod_url = f"https://www.bestbuy.com{href}"
                    else:
                        prod_url = href

                    parsed = urllib.parse.urlparse(prod_url)
                    clean_path = parsed.path.split('?')[0]
                    prod_url = f"https://www.bestbuy.com{clean_path}"

                    card_html = await card.inner_html()

                    price = None
                    price_el = await card.query_selector('[data-testid="customer-price"]')
                    if price_el:
                        price_text = await price_el.inner_text()
                        price_match = re.search(r'\$\s*([\d,]+\.?\d*)', price_text)
                        if price_match:
                            try:
                                price = float(price_match.group(1).replace(',', ''))
                            except:
                                pass

                    if not price:
                        price_match = re.search(r'\$\s*([\d,]+\.?\d*)', card_html)
                        if price_match:
                            try:
                                price = float(price_match.group(1).replace(',', ''))
                            except:
                                pass

                    rating = None
                    rating_el = await card.query_selector('[class*="c-review"]')
                    if rating_el:
                        rating_text = await rating_el.get_attribute('aria-label')
                        if rating_text:
                            rating_match = re.search(r'(\d\.\d)', rating_text)
                            if rating_match:
                                try:
                                    rating = float(rating_match.group(1))
                                except:
                                    pass

                    thumbnail_url = None
                    img = await card.query_selector('img.product-image, img')
                    if img:
                        thumbnail_url = await img.get_attribute('src')

                    product = Product(
                        marketplace="Best Buy",
                        title=title,
                        url=prod_url,
                        price=price,
                        currency="USD",
                        rating=rating,
                        rating_count=None,
                        is_sponsored=False,
                        thumbnail_url=thumbnail_url,
                        primary_features=[],
                    )
                    products.append(product)
                except:
                    continue

        except:
            pass
        finally:
            await browser.close()

    return products
