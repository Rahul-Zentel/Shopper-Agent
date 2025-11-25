import asyncio
import os
from dotenv import load_dotenv
from agent import analyze_prompt
from scraper import flipkart_search_products_async
from ranking import rank_products

# Load environment variables
load_dotenv()

async def main():
    print("--- Flipkart Scraper Agent ---")
    
    # User Input
    import sys
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = input("Enter what you are looking for (e.g., 'Best gaming laptop under 80k'): ").strip()
    
    if not user_prompt:
        print("Please provide a prompt.")
        return

    # Agent Analysis
    prefs = analyze_prompt(user_prompt)
    print(f"\nAgent understood: Searching for '{prefs.query}'")
    if prefs.min_price: print(f"Min Price: {prefs.min_price}")
    if prefs.max_price: print(f"Max Price: {prefs.max_price}")
    if prefs.prefer_brands: print(f"Preferred Brands: {prefs.prefer_brands}")

    # Scrape
    products = await flipkart_search_products_async(prefs.query, max_results=10, headless=False)

    if not products:
        print("No products found.")
        return

    # Rank
    ranked_products = rank_products(products, prefs)

    # Display
    print(f"\nFound {len(products)} products. Top results:")
    print("-" * 60)
    for i, (prod, score) in enumerate(ranked_products, 1):
        print(f"{i}. {prod.title}")
        print(f"   Price: Rs. {prod.price} | Rating: {prod.rating}")
        print(f"   Score: {score:.2f}")
        print(f"   Link: {prod.url}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(main())
