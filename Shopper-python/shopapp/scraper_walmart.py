import asyncio
import urllib.parse
import re
import json
from typing import List
from playwright.async_api import async_playwright
from .models import Product

async def walmart_search_products_async(
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
        url = f"https://www.walmart.com/search?q={encoded_query}"

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(3000)

            script_content = await page.content()
            json_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">({.+?})</script>', script_content)

            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    items = data.get('props', {}).get('pageProps', {}).get('initialData', {}).get('searchResult', {}).get('itemStacks', [{}])[0].get('items', [])

                    for item in items[:max_results]:
                        try:
                            title = item.get('name', '')
                            if not title or len(title) < 5:
                                continue

                            product_id = item.get('usItemId', '')
                            if not product_id:
                                continue

                            prod_url = f"https://www.walmart.com/ip/{product_id}"

                            price_info = item.get('priceInfo', {})
                            current_price = price_info.get('currentPrice', {})
                            price = current_price.get('price')

                            rating_info = item.get('averageRating')
                            rating = float(rating_info) if rating_info else None

                            image_info = item.get('imageInfo', {})
                            thumbnail_url = image_info.get('thumbnailUrl', '')

                            product = Product(
                                marketplace="Walmart",
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

            if len(products) == 0:
                cards = await page.query_selector_all('[data-item-id]')

                for card in cards[:max_results]:
                    try:
                        title_el = await card.query_selector('span[data-automation-id="product-title"]')
                        if not title_el:
                            title_el = await card.query_selector('a span')

                        if not title_el:
                            continue

                        title = await title_el.inner_text()
                        title = title.strip()
                        if len(title) < 5:
                            continue

                        link_el = await card.query_selector('a[href*="/ip/"]')
                        if not link_el:
                            link_el = await card.query_selector('a')
                        if not link_el:
                            continue

                        href = await link_el.get_attribute('href')
                        if not href:
                            continue

                        if href.startswith('/'):
                            prod_url = f"https://www.walmart.com{href}"
                        else:
                            prod_url = href

                        parsed = urllib.parse.urlparse(prod_url)
                        prod_url = f"https://www.walmart.com{parsed.path}"

                        card_html = await card.inner_html()

                        price = None
                        price_match = re.search(r'\$\s*([\d,]+\.?\d*)', card_html)
                        if price_match:
                            try:
                                price = float(price_match.group(1).replace(',', ''))
                            except:
                                pass

                        rating = None
                        rating_match = re.search(r'(\d\.\d)\s+out\s+of\s+5', card_html, re.IGNORECASE)
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
                            marketplace="Walmart",
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
