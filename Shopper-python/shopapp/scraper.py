import asyncio
import urllib.parse
from typing import List
from playwright.async_api import async_playwright
from .models import Product

async def flipkart_search_products_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    """
    Async Flipkart search -> list[Product].
    Works for ALL product categories (electronics, cosmetics, clothes, etc.)
    """
    products: List[Product] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.flipkart.com/search?q={encoded_query}"
        print(f"Navigating to: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)  # Wait for dynamic content (increased to 3s)
            
            # Updated selectors for 2024 Flipkart structure
            cards = []
            card_selectors = ["a.wjcEIp", "a.k7wcnx", "div.yKfJKb", "div.tUxRFH", "a.CGtC98"]
            
            for selector in card_selectors:
                cards = await page.query_selector_all(selector)
                if len(cards) > 0:
                    print(f"✓ Found {len(cards)} Flipkart cards using selector: {selector}")
                    break
            
            if len(cards) == 0:
                print("❌ No Flipkart product cards found with any selector")
                await browser.close()
                return []
                
        except Exception as e:
            print(f"Error loading page: {e}")
            await browser.close()
            return []

        for card in cards:
            if len(products) >= max_results:
                break

            try:
                # Get link - for div cards, find 'a' inside; for 'a' cards, use the card itself
                link_el = None
                if await card.evaluate("el => el.tagName") == "A":
                    link_el = card
                else:
                    link_el = await card.query_selector("a")
                
                if not link_el:
                    continue
                
                rel_link = await link_el.get_attribute("href")
                prod_url = "https://www.flipkart.com" + rel_link if rel_link and rel_link.startswith("/") else rel_link
                if not prod_url or prod_url == "https://www.flipkart.com":
                    continue

                # Get all card text for extraction
                card_text = await card.inner_text()
                lines = [l.strip() for l in card_text.split('\n') if l.strip()]
                
                # Title - try specific selector first, then fallback to text extraction
                title = None
                title_el = await card.query_selector("div.KzDlHZ, div.IRpwTa, div.s1Q9rs")
                if title_el:
                    title = await title_el.inner_text()
                    title = title.strip() if title else None
                
                # Fallback: first substantial line that's not a price
                if not title:
                    for line in lines:
                        if line and not line.startswith('₹') and len(line) > 10 and not line.replace('.', '').replace('(', '').replace(')', '').isdigit():
                            title = line
                            break
                
                if not title or len(title.strip()) < 5:
                    continue

                # Price - try specific selector first, then regex
                price = None
                import re
                price_el = await card.query_selector("div.Nx9bqj, div._30jeq3")
                if price_el:
                    price_text = await price_el.inner_text()
                    price_match = re.search(r'₹\s*([\d,]+)', price_text)
                    if price_match:
                        try:
                            price = float(price_match.group(1).replace(",", ""))
                        except ValueError:
                            pass
                
                # Fallback: extract from card text
                if not price:
                    price_match = re.search(r'₹\s*([\d,]+)', card_text)
                    if price_match:
                        try:
                            price = float(price_match.group(1).replace(",", ""))
                        except ValueError:
                            pass

                # Rating - try specific selector first, then regex
                rating = None
                rating_el = await card.query_selector("div.XQDdHH, div._3LWZlK")
                if rating_el:
                    rating_text = await rating_el.inner_text()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                        except ValueError:
                            pass
                
                # Fallback: look for pattern like "4.5(123)" or "4.5 (123)"
                if not rating:
                    rating_match = re.search(r'(\d+\.?\d*)\s*\(\d+\)', card_text)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                        except ValueError:
                            pass

                product = Product(
                    marketplace="flipkart",
                    title=title.strip(),
                    url=prod_url,
                    price=price,
                    currency="INR",
                    rating=rating,
                    rating_count=None,
                    is_sponsored=False,
                    thumbnail_url=None,
                    primary_features=[],
                )
                products.append(product)
                print(f"Added: {title[:40]}... | ₹{price} | ⭐{rating}")

            except Exception as e:
                print(f"Error parsing card: {e}")
                import traceback
                traceback.print_exc()
                continue

        await browser.close()

    return products
