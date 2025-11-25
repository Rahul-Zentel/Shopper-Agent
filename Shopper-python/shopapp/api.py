import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import nest_asyncio

from agent import analyze_prompt
from scraper import flipkart_search_products_async
from ranking import rank_products

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

app = FastAPI(title="Shopper Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. In production, specify the frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    marketplace: str = "flipkart"  # Default to flipkart

class Product(BaseModel):
    title: str
    price: float
    rating: float
    url: str
    image_url: Optional[str] = None
    source: str = "Flipkart"

class SearchResponse(BaseModel):
    products: List[Product]
    analysis: str

@app.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    try:
        user_prompt = request.query
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # 1. Analyze Prompt
        print(f"Analyzing prompt: {user_prompt}")
        try:
            prefs = analyze_prompt(user_prompt)
            analysis_summary = f"Searching for '{prefs.query}'"
            if prefs.min_price: analysis_summary += f", Min Price: {prefs.min_price}"
            if prefs.max_price: analysis_summary += f", Max Price: {prefs.max_price}"
        except Exception as e:
            print(f"Agent analysis failed: {e}, using query as-is")
            from models import ProductSearchPreferences
            prefs = ProductSearchPreferences(query=user_prompt)
            analysis_summary = f"Searching for '{user_prompt}'"
        
        # 2. Scrape
        marketplace = request.marketplace.lower()
        print(f"Scraping {marketplace} for: {prefs.query}")
        print(f"Starting Playwright scraping in separate thread...")
        
        try:
            import asyncio
            
            # Choose scraper based on marketplace
            if marketplace == "amazon":
                from scraper_amazon import amazon_search_products_async
                scraper_func = amazon_search_products_async
            else:  # Default to flipkart
                scraper_func = flipkart_search_products_async
            
            # Run scraper in a separate thread to avoid event loop conflicts
            def run_scraper_sync():
                """Run the async scraper in a new event loop in a separate thread"""
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        scraper_func(prefs.query, max_results=3, headless=True)
                    )
                    return result
                finally:
                    loop.close()
            
            # Execute in thread pool with timeout
            products = await asyncio.wait_for(
                asyncio.to_thread(run_scraper_sync),
                timeout=90.0
            )
            print(f"Scraping completed. Found {len(products)} products")
            
        except asyncio.TimeoutError:
            print("Scraping timed out after 90 seconds")
            products = []
        except Exception as scrape_error:
            print(f"Scraping failed: {scrape_error}")
            import traceback
            print(traceback.format_exc())
            products = []
        # try:
        #     products = await flipkart_search_products_async(prefs.query, max_results=10, headless=True)
        # except Exception as scrape_error:
        #     print(f"Scraping failed: {scrape_error}")
        #     import traceback
        #     print(traceback.format_exc())
        #     # Return mock data if scraping fails
        #     mock_products = [
        #         Product(
        #             title=f"Sample Product for {prefs.query}",
        #             price=999.0,
        #             rating=4.0,
        #             url="https://www.flipkart.com",
        #             image_url=None,
        #             source="Flipkart (Mock Data)"
        #         )
        #     ]
        #     return SearchResponse(
        #         products=mock_products, 
        #         analysis=analysis_summary + ". Note: Using sample data due to scraping issue."
        #     )
        
        if not products:
            return SearchResponse(products=[], analysis=analysis_summary + ". No products found.")

        # 3. Rank
        print("Ranking products...")
        try:
            ranked_products_with_score = rank_products(products, prefs)
        except Exception as rank_error:
            print(f"Ranking failed: {rank_error}, returning unranked products")
            ranked_products_with_score = [(p, 0.0) for p in products]
        
        # Format response
        response_products = []
        for prod, score in ranked_products_with_score:
            # Ensure price is a float
            try:
                price_val = float(prod.price) if prod.price is not None else 0.0
            except (ValueError, TypeError):
                price_val = 0.0

            # Ensure rating is a float
            try:
                rating_val = float(prod.rating) if prod.rating else 0.0
            except (ValueError, TypeError):
                rating_val = 0.0

            response_products.append(Product(
                title=prod.title,
                price=price_val,
                rating=rating_val,
                url=prod.url,
                image_url=getattr(prod, 'thumbnail_url', None),
                source="Flipkart"
            ))

        return SearchResponse(products=response_products, analysis=analysis_summary)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing request: {e}")
        print(f"Full traceback:\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-test")
async def search_test(request: SearchRequest):
    """Test endpoint that skips scraping"""
    try:
        user_prompt = request.query
        print(f"Test search for: {user_prompt}")
        
        # Just do analysis, no scraping
        from agent import analyze_prompt
        prefs = analyze_prompt(user_prompt)
        
        # Return mock data
        mock_products = [
            Product(
                title="Test Product 1",
                price=1000.0,
                rating=4.5,
                url="https://www.flipkart.com/test1",
                image_url=None,
                source="Flipkart"
            )
        ]
        
        analysis = f"Searching for '{prefs.query}'"
        return SearchResponse(products=mock_products, analysis=analysis)
    except Exception as e:
        import traceback
        print(f"Error in test search: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test")
async def test_endpoint(request: SearchRequest):
    return {"message": f"Received query: {request.query}"}

@app.get("/")
async def root():
    return {"message": "Shopper Agent API is running"}
