import asyncio
import urllib.parse
from typing import List
from playwright.async_api import async_playwright
from .models import Product

async def amazon_us_search_products_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    """
    Async Amazon.com (US) search -> list[Product].
    """
    products: List[Product] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.amazon.com/s?k={encoded_query}"
        print(f"Navigating to: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(2000)
            await page.wait_for_selector("div[data-component-type='s-search-result']", timeout=10000)
        except Exception as e:
            print(f"Error loading Amazon.com page: {e}")
            await browser.close()
            return []

        cards = await page.query_selector_all("div[data-component-type='s-search-result']")
        print(f"Found {len(cards)} Amazon.com product cards")

        for idx, card in enumerate(cards):
            if len(products) >= max_results:
                break

            try:
                # Title
                title = None
                h2 = await card.query_selector("h2")
                if h2:
                    title = await h2.inner_text()
                    title = title.strip() if title else None
                
                if not title or len(title) < 5:
                    continue

                # Link
                link_el = await card.query_selector("a[href*='/dp/']")
                if not link_el:
                    link_el = await card.query_selector("a.a-link-normal")
                if not link_el:
                    continue
                    
                rel_link = await link_el.get_attribute("href")
                if not rel_link:
                    continue
                    
                if rel_link.startswith("/"):
                    prod_url = "https://www.amazon.com" + rel_link
                else:
                    prod_url = rel_link

                # Price
                price = None
                
                # Strategy 1: Standard hidden price element
                price_el = await card.query_selector(".a-price .a-offscreen")
                
                # Strategy 2: Price whole + fraction (e.g. "19" + "99")
                if not price_el:
                    price_whole = await card.query_selector(".a-price-whole")
                    price_fraction = await card.query_selector(".a-price-fraction")
                    if price_whole:
                        whole_text = await price_whole.inner_text()
                        fraction_text = await price_fraction.inner_text() if price_fraction else "00"
                        # Remove punctuation like '.' from whole text if present
                        whole_text = whole_text.replace(".", "").replace(",", "").strip()
                        try:
                            price = float(f"{whole_text}.{fraction_text}")
                        except:
                            pass

                # Strategy 3: Generic offscreen span
                if price is None and not price_el:
                    price_el = await card.query_selector("span.a-offscreen")

                # Process Strategy 1 & 3 result
                if price is None and price_el:
                    price_text = await price_el.inner_text()
                    # Clean up: remove '$', commas, and whitespace
                    price_text = price_text.replace("$", "").replace(",", "").strip()
                    try:
                        price = float(price_text)
                    except:
                        pass
                
                # Strategy 4: Regex on full card text (Fallback)
                if price is None:
                    card_text = await card.inner_text()
                    import re
                    # Look for "options from $X" or just "$X"
                    # Matches: $19.99, $1,200.00, $ 19.99
                    price_match = re.search(r'\$\s*([\d,]+\.?\d*)', card_text)
                    if price_match:
                        price_text = price_match.group(1).replace(",", "")
                        try:
                            price = float(price_text)
                        except:
                            pass

                # Rating
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
                    marketplace="amazon_us",
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
                print(f"Added: {title[:50]}... | ${price} | Rating:{rating}")

            except Exception as e:
                print(f"Error parsing Amazon.com card {idx + 1}: {e}")
                import traceback
                traceback.print_exc()
                continue

        await browser.close()

    return products
