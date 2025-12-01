import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import nest_asyncio

try:
    from .agent import analyze_prompt, generate_quick_notes
    from .scraper import flipkart_search_products_async
    from .ranking import rank_products
    from .deep_agent import DeepShoppingAgent
except ImportError:
    # Fallback for when running directly from shopapp directory
    import sys
    import os
    # Add parent dir to path to allow absolute import of shopapp
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from shopapp.agent import analyze_prompt, generate_quick_notes
    from shopapp.scraper import flipkart_search_products_async
    from shopapp.ranking import rank_products
    from shopapp.deep_agent import DeepShoppingAgent

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
    mode: str = "scraper"  # "scraper" or "deep-agent"

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
    quick_notes: Optional[str] = None

@app.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    try:
        user_prompt = request.query
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if request.mode == "deep-agent":
            return await search_deep_agent(request)

        # 1. Analyze Prompt
        print(f"Analyzing prompt: {user_prompt}")
        try:
            prefs = analyze_prompt(user_prompt)
            analysis_summary = f"Searching for '{prefs.query}'"
            if prefs.min_price: analysis_summary += f", Min Price: {prefs.min_price}"
            if prefs.max_price: analysis_summary += f", Max Price: {prefs.max_price}"
        except Exception as e:
            print(f"Agent analysis failed: {e}, using query as-is")
            try:
                from .models import ProductSearchPreferences
            except ImportError:
                from shopapp.models import ProductSearchPreferences
            prefs = ProductSearchPreferences(query=user_prompt)
            analysis_summary = f"Searching for '{user_prompt}'"
        
        # 2. Scrape based on location
        location = request.marketplace.lower()  # Using marketplace field for location temporarily
        print(f"Scraping for location: {location}, query: {prefs.query}")
        
        all_products = []
        
        try:
            import asyncio
            
            # Run scraper in a separate thread to avoid event loop conflicts
            def run_scraper_sync(scraper_func, source_name):
                """Run the async scraper in a new event loop in a separate thread"""
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        scraper_func(prefs.query, max_results=3, headless=True)
                    )
                    # Add source to each product
                    for prod in result:
                        prod.marketplace = source_name
                    return result
                except Exception as e:
                    print(f"Error in {source_name} scraper: {e}")
                    return []
                finally:
                    loop.close()
            
            # Determine which scrapers to use based on location
            if location == "india":
                print("Scraping Indian retailers: Flipkart, Amazon.in")
                try:
                    from .scraper import flipkart_search_products_async
                    from .scraper_amazon import amazon_search_products_async
                except ImportError:
                    from shopapp.scraper import flipkart_search_products_async
                    from shopapp.scraper_amazon import amazon_search_products_async
                
                scrapers = [
                    (flipkart_search_products_async, "Flipkart"),
                    (amazon_search_products_async, "Amazon.in"),
                ]
            else:  # USA
                print("Scraping US retailers: Walmart, Target, Amazon.com, Etsy, Best Buy")
                try:
                    from .scraper_walmart import walmart_search_products_async
                    from .scraper_target import target_search_products_async
                    from .scraper_amazon_us import amazon_us_search_products_async
                    from .scraper_etsy import etsy_search_products_async
                    from .scraper_bestbuy import bestbuy_search_products_async
                except ImportError:
                    from shopapp.scraper_walmart import walmart_search_products_async
                    from shopapp.scraper_target import target_search_products_async
                    from shopapp.scraper_amazon_us import amazon_us_search_products_async
                    from shopapp.scraper_etsy import etsy_search_products_async
                    from shopapp.scraper_bestbuy import bestbuy_search_products_async
                
                scrapers = [
                    (walmart_search_products_async, "Walmart"),
                    (target_search_products_async, "Target"),
                    (amazon_us_search_products_async, "Amazon.com"),
                    (etsy_search_products_async, "Etsy"),
                    (bestbuy_search_products_async, "Best Buy"),
                ]
            
            # Run all scrapers concurrently with timeout
            scraper_tasks = []
            for scraper_func, source_name in scrapers:
                task = asyncio.to_thread(run_scraper_sync, scraper_func, source_name)
                scraper_tasks.append(task)
            
            # Wait for all scrapers with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*scraper_tasks, return_exceptions=True),
                timeout=120.0
            )
            
            # Combine results from all scrapers
            for result in results:
                if isinstance(result, list):
                    all_products.extend(result)
                elif isinstance(result, Exception):
                    print(f"Scraper failed with exception: {result}")
            
            print(f"Total products scraped: {len(all_products)}")
            
        except asyncio.TimeoutError:
            print("Scraping timed out after 120 seconds")
        except Exception as scrape_error:
            print(f"Scraping failed: {scrape_error}")
            import traceback
            print(traceback.format_exc())
        
        if not all_products:
            return SearchResponse(products=[], analysis=analysis_summary + ". No products found.")

        # 3. Rank
        print("Ranking products...")
        try:
            ranked_products_with_score = rank_products(all_products, prefs)
        except Exception as rank_error:
            print(f"Ranking failed: {rank_error}, returning unranked products")
            ranked_products_with_score = [(p, 0.0) for p in all_products]
        
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
                source=prod.marketplace
            ))

        # Generate Quick Notes
        print("Generating quick notes...")
        quick_notes = generate_quick_notes(response_products)

        return SearchResponse(products=response_products, analysis=analysis_summary, quick_notes=quick_notes)

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

@app.post("/search-deep-agent")
async def search_deep_agent(request: SearchRequest):
    try:
        user_prompt = request.query
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        location = request.marketplace.lower()
        print(f"Deep Agent Mode - Processing: {user_prompt}, Location: {location}")

        deep_agent = DeepShoppingAgent()
        result = await deep_agent.process_shopping_request(user_prompt, location)

        products = []
        for prod_data in result.get("products", []):
            price_str = prod_data.get("price", "0")
            try:
                price_val = float(price_str.replace("₹", "").replace("$", "").replace(",", "").strip())
            except (ValueError, AttributeError):
                price_val = 0.0

            rating_str = prod_data.get("rating", "0")
            try:
                rating_val = float(rating_str) if rating_str else 0.0
            except (ValueError, TypeError):
                rating_val = 0.0

            products.append(Product(
                title=prod_data.get("title", "Unknown Product"),
                price=price_val,
                rating=rating_val,
                url=prod_data.get("url", ""),
                image_url=prod_data.get("image_url"),
                source=prod_data.get("source", "Web Search")
            ))

        analysis = result.get("query_understanding", {}).get("notes", "Analysis completed")
        quick_notes = result.get("quick_notes", "")

        return SearchResponse(
            products=products,
            analysis=analysis,
            quick_notes=quick_notes
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in deep agent: {e}")
        print(f"Full traceback:\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Shopper Agent API is running"}
