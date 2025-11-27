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
    """
    Async Etsy.com search -> list[Product].
    """
    products: List[Product] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.etsy.com/search?q={encoded_query}"
        print(f"Navigating to: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Etsy uses specific selectors for product listings
            cards = await page.query_selector_all('div[data-search-results-lg] > div')
            if len(cards) == 0:
                # Try alternative selector
                cards = await page.query_selector_all('li.wt-list-unstyled')
            
            print(f"Found {len(cards)} Etsy product cards")
            
            if len(cards) == 0:
                print("No product cards found")
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
                # Get card text for extraction
                card_text = await card.inner_text()
                
                # Skip if card is empty or too short
                if not card_text or len(card_text) < 10:
                    continue
                
                # Title - look for product link
                title = None
                title_link = await card.query_selector('h3')
                if title_link:
                    title = await title_link.inner_text()
                    title = title.strip() if title else None
                
                if not title or len(title) < 5:
                    continue

                # Link - get product URL
                link_el = await card.query_selector('a[href*="/listing/"]')
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

                # Price - extract using regex
                price = None
                import re
                # Look for price pattern like $76.99
                price_match = re.search(r'\$\s*([\d,]+\.?\d*)', card_text)
                if price_match:
                    price_text = price_match.group(1).replace(",", "")
                    try:
                        price = float(price_text)
                    except ValueError:
                        pass

                # Rating - Etsy uses star ratings
                rating = None
                rating_match = re.search(r'(\d+\.?\d*)\s*out\s*of\s*5\s*stars', card_text)
                if rating_match:
                    try:
                        rating = float(rating_match.group(1))
                    except ValueError:
                        pass

                # Image
                thumbnail_url = None
                try:
                    img_el = await card.query_selector("img")
                    if img_el:
                        thumbnail_url = await img_el.get_attribute("src")
                        # Etsy sometimes uses data-src for lazy loading
                        if not thumbnail_url:
                            thumbnail_url = await img_el.get_attribute("data-src")
                except:
                    pass

                product = Product(
                    marketplace="etsy",
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
