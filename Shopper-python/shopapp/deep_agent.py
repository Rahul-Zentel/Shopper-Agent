import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from .agents.multi_agent_framework import MultiAgentShoppingFramework

load_dotenv()

class DeepShoppingAgent:
    """
    Deep Shopping Agent - Multi-Agent Framework Wrapper

    This class wraps the multi-agent framework for backward compatibility
    with existing API

    The framework coordinates 6 specialized agents:
    1. Orchestrator + Intent Agent - Query analysis and routing
    2. Gift Ideation Agent - Gift recommendations for vague queries
    3. Scraper Agent - Multi-marketplace product scraping
    4. Seller Reputation Agent - Trust scoring and risk assessment
    5. Deal Detection Agent - Price analysis and deal identification
    6. Intelligent Ranking Agent - AI-powered product ranking

    Features:
    - Seller trust scoring
    - Deal detection and price comparison
    - Gift ideation for vague queries
    - Intelligent ranking with reasoning
    - Risk filtering (removes high-risk sellers)
    - Multi-factor analysis (price, rating, trust, deals)
    """

    def __init__(self):
        self.framework = MultiAgentShoppingFramework()
        print("Deep Shopping Agent initialized with Multi-Agent Framework")

    async def process_shopping_request(self, user_request: str, location: str = "india") -> Dict[str, Any]:
        """
        Process shopping request using Multi-Agent Framework

        Execution Flow:
        Phase 1: Intent Analysis (500ms)
           - Parse query, extract requirements, determine routing

        Phase 2: Product Discovery (15-30s - parallel)
           - Gift ideation if needed (800ms, parallel)
           - Multi-marketplace scraping (15-30s)

        Phase 3: Analysis (1s - parallel)
           - Seller reputation scoring (300ms)
           - Deal detection (300ms)

        Phase 4: Ranking (1s)
           - AI-powered intelligent ranking
           - Multi-factor optimization

        Phase 5: Response Formatting (100ms)
           - Structure final JSON response

        Total Latency: 17-33s (mostly scraping)

        Returns:
        {
            "query_understanding": {...},
            "products": [...],  # Ranked with metadata
            "quick_notes": "...",
            "deal_summary": {...},
            "agent_metadata": {...}
        }
        """
        return await self.framework.process_shopping_request(user_request, location)
