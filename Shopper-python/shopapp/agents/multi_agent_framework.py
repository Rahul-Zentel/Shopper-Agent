import os
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

from .orchestrator import OrchestratorAgent
from .gift_ideation import GiftIdeationAgent
from .seller_reputation import SellerReputationAgent
from .deal_detection import DealDetectionAgent
from .ranking import IntelligentRankingAgent

load_dotenv()

class MultiAgentShoppingFramework:
    """
    Multi-Agent Shopping Framework

    Coordinates all specialized agents to provide intelligent product recommendations

    Agents:
    1. Orchestrator + Intent Agent (merged)
    2. Gift Ideation Agent (conditional)
    3. Scraper Agent (external - uses existing scrapers)
    4. Seller Reputation Agent
    5. Deal Detection Agent
    6. Intelligent Ranking Agent
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")

        # Initialize all agents
        self.orchestrator = OrchestratorAgent(api_key)
        self.gift_agent = GiftIdeationAgent(api_key)
        self.reputation_agent = SellerReputationAgent()
        self.deal_agent = DealDetectionAgent()
        self.ranking_agent = IntelligentRankingAgent(api_key)

    async def process_shopping_request(
        self,
        user_query: str,
        location: str = "india"
    ) -> Dict[str, Any]:
        """
        Main processing pipeline

        Phase 1: Intent Analysis & Planning (parallel)
        Phase 2: Product Scraping (parallel with gift ideation if needed)
        Phase 3: Analysis (seller reputation + deal detection)
        Phase 4: Ranking & Formatting
        """
        print(f"\n=== Multi-Agent Framework Processing ===")
        print(f"Query: {user_query}")
        print(f"Location: {location}")

        # PHASE 1: Intent Analysis
        print("\n[Phase 1] Analyzing intent...")
        intent_data = self.orchestrator.analyze_intent(user_query, location)
        print(f"Intent: {intent_data['routing']['query_type']}")
        print(f"Needs gift ideation: {intent_data['routing']['needs_gift_ideation']}")

        # PHASE 2: Product Discovery
        print("\n[Phase 2] Product discovery...")

        search_queries = []
        if intent_data['routing']['needs_gift_ideation']:
            print("Running Gift Ideation Agent...")
            gift_queries = self.gift_agent.generate_gift_ideas(
                user_query, intent_data, location
            )
            search_queries = gift_queries
            print(f"Generated {len(search_queries)} gift ideas: {search_queries}")
        else:
            refined_query = intent_data['understanding']['refined_query']
            search_queries = [refined_query]
            print(f"Direct search: {refined_query}")

        # Scrape products
        print(f"Scraping products for {len(search_queries)} queries...")
        all_products = await self._scrape_products(search_queries, location)
        print(f"Scraped {len(all_products)} products")

        if not all_products:
            return self._empty_response(user_query, intent_data)

        # PHASE 3: Analysis (parallel execution)
        print("\n[Phase 3] Running analysis agents...")

        # Run reputation and deal detection in parallel
        reputation_task = asyncio.create_task(
            asyncio.to_thread(self.reputation_agent.batch_analyze, all_products)
        )
        deal_task = asyncio.create_task(
            asyncio.to_thread(self.deal_agent.analyze_deals, all_products, location)
        )

        reputation_data, deal_data = await asyncio.gather(reputation_task, deal_task)

        print(f"Reputation analysis: {len(reputation_data)} products scored")
        print(f"Deal detection: {len(deal_data)} deals analyzed")
        print(f"DEBUG: reputation_data type: {type(reputation_data)}, keys: {list(reputation_data.keys()) if isinstance(reputation_data, dict) else 'N/A'}")
        print(f"DEBUG: deal_data type: {type(deal_data)}, keys: {list(deal_data.keys()) if isinstance(deal_data, dict) else 'N/A'}")

        # Filter out high-risk products
        safe_indices = self.reputation_agent.filter_risky_products(
            all_products, reputation_data, max_risk_level="medium"
        )
        print(f"Filtered to {len(safe_indices)} safe products")
        print(f"DEBUG: safe_indices: {safe_indices}")
        print(f"DEBUG: all_products type: {type(all_products)}, length: {len(all_products)}")

        # Filter products and their metadata with robust error handling
        safe_products = []
        for i in safe_indices:
            try:
                if isinstance(all_products, list):
                    if 0 <= i < len(all_products):
                        safe_products.append(all_products[i])
                    else:
                        print(f"WARNING: Index {i} out of range for all_products (length: {len(all_products)})")
                elif isinstance(all_products, dict):
                    if i in all_products:
                        safe_products.append(all_products[i])
                    else:
                        print(f"WARNING: Key {i} not found in all_products dict")
                else:
                    print(f"ERROR: all_products is neither list nor dict, it's {type(all_products)}")
            except Exception as e:
                print(f"ERROR: Failed to access all_products[{i}]: {e}")

        safe_reputation = {new_idx: reputation_data.get(old_idx, {}) if isinstance(reputation_data, dict)
                          else (reputation_data[old_idx] if old_idx < len(reputation_data) else {})
                          for new_idx, old_idx in enumerate(safe_indices) if old_idx in safe_indices}
        safe_deals = {new_idx: deal_data.get(old_idx, {}) if isinstance(deal_data, dict)
                     else (deal_data[old_idx] if old_idx < len(deal_data) else {})
                     for new_idx, old_idx in enumerate(safe_indices) if old_idx in safe_indices}
                     
        # PHASE 4: Intelligent Ranking
        print("\n[Phase 4] Intelligent ranking...")
        ranked_products = self.ranking_agent.rank_products(
            safe_products,
            intent_data,
            safe_reputation,
            safe_deals,
            location
        )
        print(f"Ranked {len(ranked_products)} products")

        # PHASE 5: Format Response
        print("\n[Phase 5] Formatting response...")
        return self._format_response(
            user_query,
            intent_data,
            ranked_products,
            deal_data,
            location
        )

    async def _scrape_products(
        self,
        search_queries: List[str],
        location: str
    ) -> List[Any]:
        """Scrape products from multiple marketplaces"""
        try:
            if location.lower() == "india":
                try:
                    from shopapp.scraper import flipkart_search_products_async
                    from shopapp.scraper_amazon import amazon_search_products_async
                except ImportError:
                    from ..scraper import flipkart_search_products_async
                    from ..scraper_amazon import amazon_search_products_async

                scrapers = [
                    (flipkart_search_products_async, "Flipkart"),
                    (amazon_search_products_async, "Amazon.in"),
                ]
            else:
                try:
                    from shopapp.scraper_walmart import walmart_search_products_async
                    from shopapp.scraper_target import target_search_products_async
                    from shopapp.scraper_amazon_us import amazon_us_search_products_async
                except ImportError:
                    from ..scraper_walmart import walmart_search_products_async
                    from ..scraper_target import target_search_products_async
                    from ..scraper_amazon_us import amazon_us_search_products_async

                scrapers = [
                    (walmart_search_products_async, "Walmart"),
                    (target_search_products_async, "Target"),
                    (amazon_us_search_products_async, "Amazon.com"),
                ]

            all_products = []

            # Scrape for each search query
            for query in search_queries[:2]:  # Max 2 queries to control latency
                def run_scraper_sync(scraper_func, source_name, search_query):
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(
                            scraper_func(search_query, max_results=10, headless=True)
                        )
                        for prod in result:
                            prod.marketplace = source_name
                        return result
                    except Exception as e:
                        print(f"Scraper error {source_name}: {e}")
                        import traceback
                        traceback.print_exc()
                        return []
                    finally:
                        loop.close()

                scraper_tasks = []
                for scraper_func, source_name in scrapers:
                    task = asyncio.to_thread(run_scraper_sync, scraper_func, source_name, query)
                    scraper_tasks.append(task)

                results = await asyncio.wait_for(
                    asyncio.gather(*scraper_tasks, return_exceptions=True),
                    timeout=90.0
                )

                for result in results:
                    if isinstance(result, list):
                        all_products.extend(result)

            return all_products

        except Exception as e:
            print(f"Scraping error: {e}")
            return []

    def _format_response(
        self,
        user_query: str,
        intent_data: Dict[str, Any],
        ranked_products: List[Dict[str, Any]],
        deal_data: Dict[int, Dict[str, Any]],
        location: str
    ) -> Dict[str, Any]:
        """Format final response for API"""
        understanding = intent_data.get("understanding", {})
        currency = "₹" if location.lower() == "india" else "$"

        # Generate analysis
        category = understanding.get("product_category", "products")
        budget_min = understanding.get("budget_min")
        budget_max = understanding.get("budget_max")

        budget_str = ""
        if budget_min or budget_max:
            budget_str = f" Budget: {currency}{budget_min or 0}-{currency}{budget_max or 'unlimited'}."

        analysis = f"Found {len(ranked_products)} {category}"
        if understanding.get("is_gift"):
            analysis += " (gift recommendations)"
        analysis += f".{budget_str} Analyzed for seller reputation, deals, and value."

        # Generate quick notes with agent insights
        quick_notes = self._generate_quick_notes(ranked_products[:3])

        # Get deal summary
        deal_summary = self.deal_agent.get_summary(deal_data)

        # Format products
        formatted_products = []
        for item in ranked_products[:12]:
            prod = item["product"]
            rep = item.get("seller_reputation", {})
            deal = item.get("deal_info", {})

            formatted_products.append({
                "title": prod.title,
                "price": str(prod.price) if prod.price else "0",
                "currency": prod.currency,
                "url": prod.url,
                "source": prod.marketplace,
                "rating": str(prod.rating) if prod.rating else None,
                "image_url": getattr(prod, 'thumbnail_url', None),
                "rank": item["rank"],
                "overall_score": item.get("overall_score", 0),
                "reasoning": item.get("reasoning", ""),
                "value_assessment": item.get("value_assessment", "average"),
                "recommendation": item.get("recommendation", ""),
                "highlights": item.get("highlights", []),
                "seller_trust_score": rep.get("trust_score", 0),
                "seller_risk_level": rep.get("risk_level", "unknown"),
                "deal_quality": deal.get("deal_quality", "average"),
                "deal_tags": deal.get("tags", []),
                "is_best_deal": deal.get("is_best_deal", False)
            })

        return {
            "query_understanding": {
                "original_request": user_query,
                "inferred_budget_range": f"{budget_min or 'N/A'}-{budget_max or 'unlimited'}",
                "notes": analysis
            },
            "products": formatted_products,
            "quick_notes": quick_notes,
            "deal_summary": deal_summary,
            "agent_metadata": {
                "total_analyzed": len(ranked_products),
                "gift_mode": understanding.get("is_gift", False),
                "location": location,
                "framework_version": "multi-agent-v1"
            }
        }

    def _generate_quick_notes(self, top_products: List[Dict[str, Any]]) -> str:
        """Generate quick notes from top products"""
        if not top_products:
            return "No products found matching criteria."

        notes = []
        for idx, item in enumerate(top_products, 1):
            prod = item["product"]
            reasoning = item.get("reasoning", "")

            note = f"{idx}. {prod.title[:60]}..."
            if reasoning:
                note += f" - {reasoning}"
            notes.append(note)

        return "\n".join(notes)

    def _empty_response(self, user_query: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return empty response when no products found"""
        return {
            "query_understanding": {
                "original_request": user_query,
                "inferred_budget_range": None,
                "notes": "No products found. Try refining your search query."
            },
            "products": [],
            "quick_notes": "No products available. Please try a different search term or location.",
            "deal_summary": {},
            "agent_metadata": {
                "total_analyzed": 0,
                "gift_mode": intent_data.get("understanding", {}).get("is_gift", False),
                "location": "unknown",
                "framework_version": "multi-agent-v1"
            }
        }
