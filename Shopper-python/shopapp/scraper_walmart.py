import asyncio
import urllib.parse
from typing import List, Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from .models import Product
from .scrapingbee_client import fetch_html_with_scrapingbee, ScrapingBeeError


async def _walmart_search_direct_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    """
    Direct Playwright scraping for Walmart (no ScrapingBee).
    Returns empty list if it fails.
    """
    products: List[Product] = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://www.walmart.com/search?q={encoded_query}"
            print(f"[Walmart] Trying direct scraping: {url}")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)  # Wait for dynamic content
                
                html = await page.content()
                await browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("[data-item-id]")
                
                if len(cards) == 0:
                    print("[Walmart] Direct scraping found 0 products")
                    return []
                
                print(f"[Walmart] Direct scraping found {len(cards)} product cards")
                products = _parse_walmart_cards(soup, max_results)
                return products
                
            except Exception as e:
                print(f"[Walmart] Direct scraping failed: {e}")
                await browser.close()
                return []
                
    except Exception as e:
        print(f"[Walmart] Direct scraping error: {e}")
        return []


def _walmart_search_scrapingbee_sync(
    query: str,
    max_results: int = 10,
) -> List[Product]:
    """
    Fallback: Walmart.com search using ScrapingBee -> list[Product].
    """
    products: List[Product] = []

    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.walmart.com/search?q={encoded_query}"
    print(f"[Walmart] Fallback to ScrapingBee: {url}")

    try:
        # Use US geo-targeting and stealth proxy for walmart.com
        html = fetch_html_with_scrapingbee(url, country_code="US", params={"stealth_proxy": "true"})
    except ScrapingBeeError as e:
        print(f"[Walmart] ScrapingBee error: {e}")
        return []
    except Exception as e:
        print(f"[Walmart] Unexpected error fetching page: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    products = _parse_walmart_cards(soup, max_results)
    return products


def _parse_walmart_cards(soup: BeautifulSoup, max_results: int) -> List[Product]:
    """
    Parse Walmart product cards from BeautifulSoup object.
    """
    products: List[Product] = []
    
    # Walmart uses data-item-id for product cards
    cards = soup.select("[data-item-id]")
    print(f"[Walmart] Found {len(cards)} product cards")

    if not cards:
        print("[Walmart] No product cards found in HTML")
        return []

    import re

    for idx, card in enumerate(cards):
        if len(products) >= max_results:
            break

        try:
            # Get card text for extraction
            card_text = card.get_text(" ", strip=True)

            # Title - look for product link text
            title = None
            title_link = card.select_one('a[link-identifier*="product"]')
            if not title_link:
                title_link = card.select_one("a span")
            if title_link:
                title = title_link.get_text(" ", strip=True)

            if not title or len(title) < 5:
                continue

            # Link - get product URL
            link_el = card.select_one('a[href*="/ip/"]')
            if not link_el:
                link_el = card.select_one("a")
            if not link_el:
                continue

            rel_link = link_el.get("href")
            if not rel_link:
                continue

            if rel_link.startswith("/"):
                prod_url = "https://www.walmart.com" + rel_link
            else:
                prod_url = rel_link

            # Price - extract using regex
            price = None
            # Look for price pattern like $76.99 or $76,990.00
            price_match = re.search(r"\$\s*([\d,]+\.?\d*)", card_text)
            if price_match:
                price_text = price_match.group(1).replace(",", "")
                try:
                    price = float(price_text)
                except ValueError:
                    price = None

            # Rating - look for pattern like "4.5 out of 5"
            rating = None
            rating_match = re.search(r"(\d+\.?\d*)\s+out\s+of\s+5", card_text)
            if rating_match:
                try:
                    rating = float(rating_match.group(1))
                except ValueError:
                    rating = None

            # Image
            thumbnail_url = None
            img_el = card.select_one("img")
            if img_el:
                thumbnail_url = img_el.get("src")

            product = Product(
                marketplace="walmart",
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
            print(f"[Walmart] Added: {title[:50]}... | ${price} | ⭐{rating}")

        except Exception as e:
            print(f"[Walmart] Error parsing card {idx + 1}: {e}")
            import traceback

            traceback.print_exc()
            continue

    return products


async def walmart_search_products_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    """
    Async Walmart.com search with fallback mechanism.
    Tries direct scraping first, falls back to ScrapingBee if it fails.
    """
    # Try direct scraping first
    print("[Walmart] Attempting direct scraping...")
    products = await _walmart_search_direct_async(query, max_results, headless)
    
    # If direct scraping succeeded, return results
    if len(products) > 0:
        print(f"[Walmart] Direct scraping successful! Found {len(products)} products")
        return products
    
    # Fallback to ScrapingBee
    print("[Walmart] Direct scraping failed or found 0 products, falling back to ScrapingBee...")
    loop = asyncio.get_running_loop()
    products = await loop.run_in_executor(
        None, _walmart_search_scrapingbee_sync, query, max_results
    )
    
    if len(products) > 0:
        print(f"[Walmart] ScrapingBee fallback successful! Found {len(products)} products")
    else:
        print("[Walmart] Both direct scraping and ScrapingBee failed")
    
    return products
