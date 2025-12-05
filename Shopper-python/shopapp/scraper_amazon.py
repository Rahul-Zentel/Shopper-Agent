import asyncio
import re
import urllib.parse
from typing import List
from playwright.async_api import async_playwright
from .models import Product

async def amazon_search_products_async(
    query: str,
    max_results: int = 10,
    headless: bool = True,
) -> List[Product]:
    products: List[Product] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            geolocation={"longitude": 77.2090, "latitude": 28.6139},
            permissions=["geolocation"]
        )
        page = await context.new_page()

        await context.set_extra_http_headers({
            "Accept-Language": "en-IN,en;q=0.9",
        })

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.amazon.in/s?k={encoded_query}"
        print(f"Navigating to: {url}")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            await context.add_cookies([
                {"name": "i18n-prefs", "value": "INR", "domain": ".amazon.in", "path": "/"},
                {"name": "lc-main", "value": "en_IN", "domain": ".amazon.in", "path": "/"}
            ])

            await page.reload(wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.wait_for_selector("div[data-component-type='s-search-result']", timeout=10000)
        except Exception as e:
            print(f"Error loading Amazon.in page: {e}")
            await browser.close()
            return []

        cards = await page.query_selector_all("div[data-component-type='s-search-result']")
        print(f"Found {len(cards)} Amazon product cards")

        for idx, card in enumerate(cards):
            if len(products) >= max_results:
                break

            try:
                title = None
                h2 = await card.query_selector("h2")
                if h2:
                    title = await h2.inner_text()
                    title = title.strip() if title else None

                if not title or len(title) < 5:
                    continue

                link_el = await card.query_selector("a[href*='/dp/']")
                if not link_el:
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

                card_text = await card.inner_text()

                price = None
                price_strategy_used = None

                try:
                    variant_buttons = await card.query_selector_all("button, .a-button-inner, [role='button'], li, .a-button-text")
                    for button in variant_buttons:
                        button_text = await button.inner_text()
                        button_text = " ".join(button_text.split())

                        patterns = [
                            r'\d+\s+options?\s+from\s*₹\s*([\d,]+)',
                            r'from\s*₹\s*([\d,]+)'
                        ]

                        for pattern in patterns:
                            variant_match = re.search(pattern, button_text, re.IGNORECASE)
                            if variant_match:
                                price_text = variant_match.group(1).replace(",", "")
                                try:
                                    price = float(price_text)
                                    price_strategy_used = f"Strategy 0: Variant button"
                                    break
                                except:
                                    continue

                        if price:
                            break
                except Exception as e:
                    pass

                if price is None:
                    try:
                        price_el = await card.query_selector(".a-price .a-offscreen")
                        if price_el:
                            price_text = await price_el.inner_text()
                            price_text = price_text.replace("₹", "").replace(",", "").strip()
                            price = float(price_text)
                            price_strategy_used = "Strategy 1: .a-price .a-offscreen"
                    except:
                        pass

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
                                price_text = price_text.replace("₹", "").replace(",", "").strip()
                                if price_text and price_text.replace(".", "").isdigit():
                                    price = float(price_text)
                                    price_strategy_used = f"Strategy 3: {selector}"
                                    break
                        except:
                            continue

                if price is None:
                    price_patterns = [
                        (r'\d+\s+options?\s+from\s+₹\s*([\d,]+)', "Pattern: X option(s) from ₹XX"),
                        (r'from\s+₹\s*([\d,]+)', "Pattern: from ₹XX"),
                        (r'Price:\s*₹\s*([\d,]+)', "Pattern: Price: ₹XX"),
                        (r'₹\s*([\d,]+)', "Pattern: ₹XX"),
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

                if price is None:
                    all_prices = re.findall(r'₹\s*([\d,]+)', card_text)
                    if all_prices:
                        for price_str in all_prices:
                            try:
                                price_text = price_str.replace(",", "")
                                if float(price_text) > 0:
                                    price = float(price_text)
                                    price_strategy_used = "Strategy 6: First ₹ amount"
                                    break
                            except:
                                pass

                rating = None
                rating_match = re.search(r'(\d+\.?\d*)\s+out\s+of\s+5', card_text)
                if rating_match:
                    try:
                        rating = float(rating_match.group(1))
                    except:
                        pass

                thumbnail_url = None
                try:
                    img_el = await card.query_selector("img")
                    if img_el:
                        thumbnail_url = await img_el.get_attribute("src")
                except:
                    pass

                product = Product(
                    marketplace="Amazon.in",
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
                print(f"Added: {title[:50]}... | Rs.{price} | ⭐{rating}")

            except Exception as e:
                print(f"Error parsing Amazon card {idx + 1}: {e}")
                import traceback
                traceback.print_exc()
                continue

        await browser.close()

    return products
