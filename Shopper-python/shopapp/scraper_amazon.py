import asyncio
import urllib.parse
from typing import List
from playwright.async_api import async_playwright
from .models import Product

async def amazon_search_products_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    """
    Async Amazon.in search -> list[Product].
    Rewritten with working selectors.
    """
    products: List[Product] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.amazon.in/s?k={encoded_query}"
        print(f"Navigating to: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # Wait a bit for dynamic content
            await page.wait_for_timeout(2000)
            # Wait for product cards
            await page.wait_for_selector("div[data-component-type='s-search-result']", timeout=10000)
        except Exception as e:
            print(f"Error loading Amazon page: {e}")
            await browser.close()
            return []

        cards = await page.query_selector_all("div[data-component-type='s-search-result']")
        print(f"Found {len(cards)} Amazon product cards")

        for idx, card in enumerate(cards):
            if len(products) >= max_results:
                break

            try:
                # Title - get from h2
                title = None
                h2 = await card.query_selector("h2")
                if h2:
                    title = await h2.inner_text()
                    title = title.strip() if title else None
                
                if not title or len(title) < 5:
                    continue

                # Link - get from any link with /dp/ (product link)
                link_el = await card.query_selector("a[href*='/dp/']")
                if not link_el:
                    # Fallback to any link
                    link_el = await card.query_selector("a.a-link-normal")
                if not link_el:
                    continue
                    
                rel_link = await link_el.get_attribute("href")
                if not rel_link:
                    continue
                    
                if rel_link.startswith("/"):
                    prod_url = "https://www.amazon.in" + rel_link
                else:
                    prod_url = rel_link

                # Price - look for spans with ₹ symbol
                price = None
                card_text = await card.inner_text()
                import re
                # Look for price pattern like ₹76,990 or ₹76990
                price_match = re.search(r'₹\s*([\d,]+)', card_text)
                if price_match:
                    price_text = price_match.group(1).replace(",", "")
                    try:
                        price = float(price_text)
                    except:
                        pass

                # Rating - look for text like "4.5 out of 5"
                rating = None
                rating_match = re.search(r'(\d+\.?\d*)\s+out\s+of\s+5', card_text)
                if rating_match:
                    try:
                        rating = float(rating_match.group(1))
                    except:
                        pass

                # Image
                thumbnail_url = None
                try:
                    img_el = await card.query_selector("img")
                    if img_el:
                        thumbnail_url = await img_el.get_attribute("src")
                except:
                    pass

                product = Product(
                    marketplace="amazon",
                    title=title,
                    url=prod_url,
                    price=price,
                    currency="INR",
                    rating=rating,
                    rating_count=None,
                    is_sponsored=False,
                    thumbnail_url=thumbnail_url,
                    primary_features=[],
                )
                products.append(product)
                print(f"Added: {title[:50]}... | Rs.{price} | Rating:{rating}")

            except Exception as e:
                print(f"Error parsing Amazon card {idx + 1}: {e}")
                import traceback
                traceback.print_exc()
                continue

        await browser.close()

    return products
