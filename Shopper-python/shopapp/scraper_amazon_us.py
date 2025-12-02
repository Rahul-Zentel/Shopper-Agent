import asyncio
import re
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"longitude": -74.0060, "latitude": 40.7128},  # New York, USA
            permissions=["geolocation"]
        )
        page = await context.new_page()

        # Set additional headers and cookies to ensure US experience
        await context.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
        })

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.amazon.com/s?k={encoded_query}"
        print(f"Navigating to: {url}")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Set cookies to force USD currency and US region
            await context.add_cookies([
                {"name": "i18n-prefs", "value": "USD", "domain": ".amazon.com", "path": "/"},
                {"name": "lc-main", "value": "en_US", "domain": ".amazon.com", "path": "/"}
            ])

            # Reload to apply cookies
            await page.reload(wait_until="domcontentloaded")
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

                # Get full card text for extraction (used by multiple strategies)
                card_text = await card.inner_text()

                # Price extraction with comprehensive strategies
                price = None
                price_strategy_used = None

                # Strategy 0: Extract from variant option buttons FIRST (highest priority)
                # These appear in products with multiple size/type options
                try:
                    # Look for variant buttons that contain "option(s) from $XX.XX"
                    variant_buttons = await card.query_selector_all("button, .a-button-inner, [role='button'], li, .a-button-text")
                    for button in variant_buttons:
                        button_text = await button.inner_text()
                        # Normalize whitespace (handle newlines between "from" and price)
                        button_text = " ".join(button_text.split())

                        # Try patterns in order of specificity
                        patterns = [
                            r'\d+\s+options?\s+from\s*\$\s*([\d,]+\.\d{2})',  # "2 options from $14.47"
                            r'\d+\s+options?\s+from\s*\$\s*([\d,]+)',         # "2 options from $14" (no decimals)
                            r'from\s*\$\s*([\d,]+\.\d{2})',                   # "from $15.99"
                            r'from\s*\$\s*([\d,]+)'                           # "from $15" (no decimals)
                        ]

                        for pattern in patterns:
                            variant_match = re.search(pattern, button_text, re.IGNORECASE)
                            if variant_match:
                                price_text = variant_match.group(1).replace(",", "")
                                try:
                                    price = float(price_text)
                                    price_strategy_used = f"Strategy 0: Variant button - {pattern[:30]}"
                                    break
                                except:
                                    continue

                        if price:
                            break
                except Exception as e:
                    pass

                # Strategy 1: Standard hidden price element (a-offscreen within a-price)
                try:
                    price_el = await card.query_selector(".a-price .a-offscreen")
                    if price_el:
                        price_text = await price_el.inner_text()
                        price_text = price_text.replace("$", "").replace(",", "").strip()
                        price = float(price_text)
                        price_strategy_used = "Strategy 1: .a-price .a-offscreen"
                except:
                    pass

                # Strategy 2: Price whole + fraction (e.g. "19" + "99")
                if price is None:
                    try:
                        price_whole = await card.query_selector(".a-price-whole")
                        price_fraction = await card.query_selector(".a-price-fraction")
                        if price_whole:
                            whole_text = await price_whole.inner_text()
                            fraction_text = await price_fraction.inner_text() if price_fraction else "00"
                            whole_text = whole_text.replace(".", "").replace(",", "").strip()
                            fraction_text = fraction_text.replace(".", "").replace(",", "").strip()
                            price = float(f"{whole_text}.{fraction_text}")
                            price_strategy_used = "Strategy 2: .a-price-whole + .a-price-fraction"
                    except:
                        pass

                # Strategy 3: Multiple offscreen selectors
                if price is None:
                    offscreen_selectors = [
                        "span.a-offscreen",
                        ".a-price span.a-offscreen",
                        "span[aria-hidden='true'] + span.a-offscreen"
                    ]
                    for selector in offscreen_selectors:
                        try:
                            price_el = await card.query_selector(selector)
                            if price_el:
                                price_text = await price_el.inner_text()
                                price_text = price_text.replace("$", "").replace(",", "").strip()
                                if price_text and price_text.replace(".", "").isdigit():
                                    price = float(price_text)
                                    price_strategy_used = f"Strategy 3: {selector}"
                                    break
                        except:
                            continue

                # Strategy 4: Look for a-price elements with visible price
                if price is None:
                    try:
                        price_symbols = await card.query_selector_all(".a-price-symbol")
                        for symbol_el in price_symbols:
                            symbol_parent = await symbol_el.evaluate_handle("el => el.parentElement")
                            if symbol_parent:
                                parent_text = await symbol_parent.inner_text()
                                # Extract numeric value
                                numeric = re.search(r'([\d,]+\.?\d*)', parent_text)
                                if numeric:
                                    price_text = numeric.group(1).replace(",", "")
                                    price = float(price_text)
                                    price_strategy_used = "Strategy 4: .a-price-symbol parent"
                                    break
                    except:
                        pass

                # Strategy 4b: Extract price from variant option buttons (for multi-variant products)
                if price is None:
                    try:
                        # Look for variant buttons/options that contain price text
                        variant_selectors = [
                            ".a-button-text",
                            "[data-a-button-text]",
                            ".a-size-base.a-color-base",
                            "li.a-spacing-mini"
                        ]
                        for selector in variant_selectors:
                            variant_els = await card.query_selector_all(selector)
                            for variant_el in variant_els:
                                variant_text = await variant_el.inner_text()
                                # Match patterns like "1 option from $15.99" or "2 options from $14.47"
                                variant_price_match = re.search(r'from\s+\$\s*([\d,]+\.\d{2})', variant_text)
                                if variant_price_match:
                                    price_text = variant_price_match.group(1).replace(",", "")
                                    price = float(price_text)
                                    price_strategy_used = f"Strategy 4b: Variant button - {selector}"
                                    break
                            if price:
                                break
                    except:
                        pass

                # Strategy 5: Regex on full card text - multiple patterns (prioritize variant patterns)
                if price is None:
                    price_patterns = [
                        # Variant patterns (higher priority for multi-option cards)
                        (r'\d+\s+options?\s+from\s+\$\s*([\d,]+\.\d{2})', "Pattern: X option(s) from $XX.XX"),
                        (r'from\s+\$\s*([\d,]+\.\d{2})', "Pattern: from $XX.XX"),
                        # Standard patterns
                        (r'Price:\s*\$\s*([\d,]+\.\d{2})', "Pattern: Price: $XX.XX"),
                        (r'\$\s*([\d,]+\.\d{2})', "Pattern: $XX.XX"),
                        (r'\$\s*([\d,]+)', "Pattern: $XX (no decimals)"),
                        (r'([\d,]+\.\d{2})\s+with', "Pattern: XX.XX with"),
                    ]
                    for pattern, desc in price_patterns:
                        price_match = re.search(pattern, card_text)
                        if price_match:
                            price_text = price_match.group(1).replace(",", "")
                            try:
                                price = float(price_text)
                                price_strategy_used = f"Strategy 5: {desc}"
                                break
                            except:
                                pass

                # Strategy 6: Last resort - find ANY dollar amount in card
                if price is None:
                    all_prices = re.findall(r'\$\s*([\d,]+\.?\d*)', card_text)
                    if all_prices:
                        # Take the first valid price found
                        for price_str in all_prices:
                            try:
                                price_text = price_str.replace(",", "")
                                if float(price_text) > 0:
                                    price = float(price_text)
                                    price_strategy_used = "Strategy 6: First $ amount"
                                    break
                            except:
                                pass

                # Debug output for price extraction
                if price is None:
                    print(f"  WARNING: No price found for card {idx + 1}")
                    print(f"  Card text preview: {card_text[:200]}...")
                else:
                    print(f"  Price extracted: ${price} using {price_strategy_used}")

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
