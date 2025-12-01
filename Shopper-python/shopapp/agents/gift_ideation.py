import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class GiftIdeationAgent:
    """
    Gift Ideation Agent

    Responsibilities:
    - Generate concrete product ideas for vague/gift queries
    - Consider recipient profile, occasion, budget
    - Provide 2-4 specific product suggestions
    - Optimize for emotional impact and practicality
    """

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            api_key=api_key
        )

    def generate_gift_ideas(
        self,
        user_request: str,
        intent_data: Dict[str, Any],
        location: str
    ) -> List[str]:
        """
        Generate specific product search queries for gift shopping

        Returns: List of 2-4 specific product search terms
        """
        understanding = intent_data.get("understanding", {})
        constraints = intent_data.get("constraints", {})

        system_prompt = """You are a gift ideation specialist. Generate specific product search queries for gift shopping.

Given the recipient profile and context, suggest 2-4 concrete product ideas that:
1. Match the recipient's interests and style
2. Fit within the budget
3. Are available in the specified location
4. Are thoughtful and meaningful
5. Can be easily found on e-commerce platforms

Return ONLY a JSON array of specific search query strings:
["specific product 1", "specific product 2", "specific product 3"]

Examples:
- Good: "Kindle Paperwhite e-reader", "Yoga mat premium quality", "Coffee subscription gift box"
- Bad: "books", "fitness stuff", "food items"

Make each query specific enough to find actual products."""

        currency = "INR" if location.lower() == "india" else "USD"
        budget_str = f"{currency}{understanding.get('budget_min', 'N/A')}-{currency}{understanding.get('budget_max', 'unlimited')}"

        context = f"""User Request: {user_request}

Recipient Profile: {understanding.get('recipient_profile', 'Not specified')}
Occasion: {understanding.get('occasion', 'General gift')}
Budget: {budget_str}
Key Interests: {', '.join(understanding.get('key_features', []))}
Must Have: {', '.join(constraints.get('must_have', []))}
Avoid: {', '.join(constraints.get('exclude', []))}
Location: {location}

Generate 2-4 specific product search queries for e-commerce."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context)
        ]

        try:
            response = self.llm.invoke(messages)
            content = response.content if isinstance(response, AIMessage) else str(response)

            # Clean and parse JSON
            clean_content = content.strip()
            if clean_content.startswith('```json'):
                clean_content = clean_content[7:]
            if clean_content.startswith('```'):
                clean_content = clean_content[3:]
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3]

            ideas = json.loads(clean_content.strip())

            if isinstance(ideas, list) and len(ideas) > 0:
                return ideas[:4]  # Maximum 4 ideas
            else:
                return [understanding.get('refined_query', user_request)]

        except Exception as e:
            print(f"Gift ideation error: {e}")
            # Fallback to refined query
            return [understanding.get('refined_query', user_request)]

    def enhance_with_context(self, search_queries: List[str], intent_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enhance search queries with additional context

        Returns: List of enhanced query objects
        """
        understanding = intent_data.get("understanding", {})

        enhanced_queries = []
        for idx, query in enumerate(search_queries):
            enhanced_queries.append({
                "query": query,
                "priority": "high" if idx == 0 else "medium",
                "context": {
                    "is_gift": True,
                    "occasion": understanding.get("occasion"),
                    "budget_weight": 0.7,  # Gift focus more on thoughtfulness than price
                    "rating_weight": 0.9  # Important to have good reviews for gifts
                }
            })

        return enhanced_queries
