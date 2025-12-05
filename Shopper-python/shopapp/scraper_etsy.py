import asyncio
import urllib.parse
from typing import List
from playwright.async_api import async_playwright
from .models import Product

async def etsy_search_products_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    products: List[Product] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York"
        )
        page = await context.new_page()

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.etsy.com/search?q={encoded_query}"
        print(f"Navigating to: {url}")

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)

            selectors_to_try = [
                'div[data-search-results-lg] > div',
                'li.wt-list-unstyled',
                'div.v2-listing-card',
                'div[data-listing-id]',
                'ol.wt-grid > li'
            ]

            cards = []
            for selector in selectors_to_try:
                cards = await page.query_selector_all(selector)
                if len(cards) > 0:
                    print(f"Found {len(cards)} Etsy product cards using selector: {selector}")
                    break

            if len(cards) == 0:
                print("No product cards found with any selector")
                await browser.close()
                return []

        except Exception as e:
            print(f"Error loading Etsy page: {e}")
            await browser.close()
            return []

        for idx, card in enumerate(cards):
            if len(products) >= max_results:
                break

            try:
                card_text = await card.inner_text()

                if not card_text or len(card_text) < 10:
                    continue

                title = None
                title_selectors = [
                    'h3.wt-text-caption',
                    'h3',
                    'h2',
                    'a.listing-link',
                    'div.v2-listing-card__title'
                ]
                for selector in title_selectors:
                    title_el = await card.query_selector(selector)
                    if title_el:
                        title = await title_el.inner_text()
                        title = title.strip() if title else None
                        if title and len(title) >= 5:
                            break

                if not title or len(title) < 5:
                    continue

                link_el = await card.query_selector('a[href*="/listing/"]')
                if not link_el:
                    link_el = await card.query_selector('a.listing-link')
                if not link_el:
                    link_el = await card.query_selector('a')
                if not link_el:
                    continue

                rel_link = await link_el.get_attribute("href")
                if not rel_link:
                    continue

                if rel_link.startswith("/"):
                    prod_url = "https://www.etsy.com" + rel_link
                elif not rel_link.startswith("http"):
                    prod_url = "https://www.etsy.com" + "/" + rel_link
                else:
                    prod_url = rel_link

                price = None
                import re

                price_selectors = [
                    'span.currency-value',
                    'span.currency-symbol + span',
                    'div.n-listing-card__price span',
                    'p.wt-text-title-01'
                ]

                for selector in price_selectors:
                    price_el = await card.query_selector(selector)
                    if price_el:
                        price_text = await price_el.inner_text()
                        price_match = re.search(r'\$?\s*([\d,]+\.?\d*)', price_text)
                        if price_match:
                            try:
                                price = float(price_match.group(1).replace(",", ""))
                                break
                            except:
                                pass

                if price is None:
                    price_patterns = [
                        r'USD\s+\$?\s*([\d,]+\.\d{2})',
                        r'\$\s*([\d,]+\.\d{2})',
                        r'\$\s*([\d,]+)'
                    ]
                    for pattern in price_patterns:
                        price_match = re.search(pattern, card_text, re.IGNORECASE)
                        if price_match:
                            try:
                                price = float(price_match.group(1).replace(",", ""))
                                break
                            except:
                                pass

                rating = None
                rating_patterns = [
                    r'(\d+\.?\d*)\s*out\s*of\s*5\s*stars',
                    r'(\d+\.?\d*)\s+stars',
                    r'rating:\s*(\d+\.?\d*)'
                ]
                for pattern in rating_patterns:
                    rating_match = re.search(pattern, card_text, re.IGNORECASE)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                            if 0 <= rating <= 5:
                                break
                        except:
                            pass

                thumbnail_url = None
                try:
                    img_el = await card.query_selector("img")
                    if img_el:
                        thumbnail_url = await img_el.get_attribute("src")
                        if not thumbnail_url or thumbnail_url == "":
                            thumbnail_url = await img_el.get_attribute("data-src")
                except:
                    pass

                product = Product(
                    marketplace="Etsy",
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
                print(f"Added: {title[:50]}... | ${price} | ⭐{rating}")

            except Exception as e:
                print(f"Error parsing Etsy card {idx + 1}: {e}")
                import traceback
                traceback.print_exc()
                continue

        await browser.close()

    return products
