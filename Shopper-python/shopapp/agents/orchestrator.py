import os
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class OrchestratorAgent:
    """
    Orchestrator + Intent Analysis Agent (merged for performance)

    Responsibilities:
    - Parse and understand user query
    - Extract intent, budget, features, recipient profile
    - Route to appropriate agent workflow
    - Manage overall execution flow
    """

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=api_key
        )

    def analyze_intent(self, user_query: str, location: str) -> Dict[str, Any]:
        """
        Analyze user query and extract structured intent
        Fast single LLM call with comprehensive analysis
        """
        system_prompt = """You are a shopping orchestrator that analyzes queries and plans execution.

Analyze the user's shopping request and extract:
1. Product category and specific requirements
2. Budget constraints (extract numbers, infer if not mentioned)
3. Key features they care about
4. Whether this is a gift or personal purchase
5. Urgency level
6. Query complexity (simple/moderate/complex)

Also determine routing:
- needs_gift_ideation: true if query is vague or mentions gift
- needs_research: true if asking "how to choose" or buying advice
- query_type: "direct_search" | "gift_shopping" | "product_research" | "comparison"

Return ONLY valid JSON:
{
  "understanding": {
    "refined_query": "optimized search query for e-commerce",
    "product_category": "category name",
    "budget_min": number or null,
    "budget_max": number or null,
    "key_features": ["feature1", "feature2"],
    "is_gift": true/false,
    "occasion": "string or null",
    "recipient_profile": "string or null",
    "urgency": "low|medium|high"
  },
  "routing": {
    "needs_gift_ideation": true/false,
    "needs_research": true/false,
    "query_type": "direct_search|gift_shopping|product_research|comparison",
    "complexity": "simple|moderate|complex",
    "estimated_search_queries": number
  },
  "constraints": {
    "must_have": ["feature1"],
    "nice_to_have": ["feature2"],
    "exclude": ["unwanted1"]
  }
}"""

        currency = "INR" if location.lower() == "india" else "USD"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User query: {user_query}\nLocation: {location}\nCurrency: {currency}")
        ]

        response = self.llm.invoke(messages)
        content = response.content if isinstance(response, AIMessage) else str(response)

        try:
            clean_content = content.strip()
            if clean_content.startswith('```json'):
                clean_content = clean_content[7:]
            if clean_content.startswith('```'):
                clean_content = clean_content[3:]
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3]

            result = json.loads(clean_content.strip())
            return result
        except Exception as e:
            print(f"Intent analysis error: {e}")
            return {
                "understanding": {
                    "refined_query": user_query,
                    "product_category": "general",
                    "budget_min": None,
                    "budget_max": None,
                    "key_features": [],
                    "is_gift": False,
                    "occasion": None,
                    "recipient_profile": None,
                    "urgency": "medium"
                },
                "routing": {
                    "needs_gift_ideation": False,
                    "needs_research": False,
                    "query_type": "direct_search",
                    "complexity": "simple",
                    "estimated_search_queries": 1
                },
                "constraints": {
                    "must_have": [],
                    "nice_to_have": [],
                    "exclude": []
                }
            }

    def plan_execution(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create execution plan based on intent analysis
        Determines which agents to invoke and in what order
        """
        routing = intent.get("routing", {})
        understanding = intent.get("understanding", {})

        plan = {
            "phase_1_parallel": [],
            "phase_2_sequential": [],
            "phase_3_finalization": []
        }

        # Phase 1: Parallel execution (can run simultaneously)
        if routing.get("needs_gift_ideation"):
            plan["phase_1_parallel"].append("gift_ideation_agent")

        plan["phase_1_parallel"].append("scraper_agent")

        # Phase 2: Sequential execution (needs phase 1 results)
        plan["phase_2_sequential"].append("seller_reputation_agent")
        plan["phase_2_sequential"].append("deal_detection_agent")
        plan["phase_2_sequential"].append("ranking_agent")

        # Phase 3: Finalization
        plan["phase_3_finalization"].append("response_formatter")

        return plan
