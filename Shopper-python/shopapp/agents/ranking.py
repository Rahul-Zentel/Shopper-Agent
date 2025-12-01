import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class IntelligentRankingAgent:
    """
    Intelligent Ranking Agent (Enhanced)

    Responsibilities:
    - Rank products using multi-factor analysis
    - Integrate seller reputation scores
    - Consider deal quality
    - Personalize to user requirements
    - Provide detailed reasoning for each rank
    """

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=api_key
        )

    def rank_products(
        self,
        products: List[Any],
        intent_data: Dict[str, Any],
        reputation_data: Dict[int, Dict[str, Any]],
        deal_data: Dict[int, Dict[str, Any]],
        location: str
    ) -> List[Dict[str, Any]]:
        """
        Rank products using comprehensive analysis

        Returns: List of ranked product dictionaries with metadata
        """
        if not products:
            return []

        understanding = intent_data.get("understanding", {})
        constraints = intent_data.get("constraints", {})

        # Prepare product summaries for LLM
        product_summaries = []
        for idx, prod in enumerate(products[:15]):  # Limit to 15 for LLM context
            rep = reputation_data.get(idx, {})
            deal = deal_data.get(idx, {})

            # Safe float conversion
            try:
                price = float(prod.price) if prod.price is not None else 0.0
            except (ValueError, TypeError):
                price = 0.0

            try:
                rating = float(prod.rating) if prod.rating is not None else 0.0
            except (ValueError, TypeError):
                rating = 0.0

            summary = {
                "index": idx,
                "title": prod.title[:100] if prod.title else "Unknown Product",
                "price": price,
                "rating": rating,
                "source": prod.marketplace if hasattr(prod, 'marketplace') else "Unknown",
                "seller_trust_score": rep.get("trust_score", 50),
                "seller_risk_level": rep.get("risk_level", "medium"),
                "deal_quality": deal.get("deal_quality", "average"),
                "value_score": deal.get("value_score", 50),
                "is_lowest_price": deal.get("is_lowest_price", False),
                "deal_tags": deal.get("tags", []),
                "has_warnings": len(rep.get("red_flags", [])) > 0
            }
            product_summaries.append(summary)

        # Get LLM ranking
        ranked_data = self._get_llm_ranking(
            product_summaries, understanding, constraints, location
        )

        # Combine LLM ranking with algorithmic scoring
        final_rankings = self._combine_rankings(
            ranked_data, product_summaries, understanding
        )

        # Build final result
        results = []
        for rank_info in final_rankings:
            idx = rank_info["product_index"]
            if idx < len(products):
                prod = products[idx]
                rep = reputation_data.get(idx, {})
                deal = deal_data.get(idx, {})

                results.append({
                    "product": prod,
                    "rank": rank_info["rank"],
                    "overall_score": rank_info["overall_score"],
                    "reasoning": rank_info["reasoning"],
                    "match_score": rank_info.get("match_score", 50),
                    "value_assessment": rank_info.get("value_assessment", "average"),
                    "recommendation": rank_info.get("recommendation", ""),
                    "seller_reputation": rep,
                    "deal_info": deal,
                    "highlights": self._generate_highlights(prod, rep, deal)
                })

        return results

    def _get_llm_ranking(
        self,
        product_summaries: List[Dict],
        understanding: Dict[str, Any],
        constraints: Dict[str, Any],
        location: str
    ) -> List[Dict[str, Any]]:
        """Get intelligent ranking from LLM"""
        system_prompt = """You are an expert shopping advisor. Rank these products based on user requirements.

For each product, consider:
1. How well it matches user requirements (features, category)
2. Price vs value (deal quality, value score)
3. Seller trustworthiness (trust score, risk level)
4. Product quality (ratings)
5. Overall value proposition

Return ONLY a JSON array ranked from best to worst:
[
  {
    "product_index": original_index,
    "rank": new_rank_1_to_N,
    "overall_score": 0-100,
    "match_score": 0-100,
    "value_assessment": "excellent|good|average|poor",
    "reasoning": "concise 1-2 sentence explanation",
    "recommendation": "brief actionable recommendation",
    "key_strengths": ["strength1", "strength2"],
    "concerns": ["concern1"] or []
  }
]

Prioritize:
- Seller trust and safety (avoid high-risk sellers)
- Value for money (good ratings + fair price)
- Match with user requirements
- Deal quality (best deals rank higher)"""

        currency = "₹" if location.lower() == "india" else "$"

        context = f"""User Requirements:
- Category: {understanding.get('product_category', 'general')}
- Budget: {currency}{understanding.get('budget_min', 'N/A')} - {currency}{understanding.get('budget_max', 'unlimited')}
- Key Features: {', '.join(understanding.get('key_features', []))}
- Must Have: {', '.join(constraints.get('must_have', []))}
- Avoid: {', '.join(constraints.get('exclude', []))}
- Is Gift: {understanding.get('is_gift', False)}
- Urgency: {understanding.get('urgency', 'medium')}

Products to rank:
{json.dumps(product_summaries, indent=2)}

Rank these products based on overall value, safety, and user requirements."""

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

            rankings = json.loads(clean_content.strip())
            return rankings if isinstance(rankings, list) else []

        except Exception as e:
            print(f"LLM ranking error: {e}")
            # Fallback to algorithmic ranking
            return self._algorithmic_fallback(product_summaries)

    def _algorithmic_fallback(self, product_summaries: List[Dict]) -> List[Dict[str, Any]]:
        """Fallback algorithmic ranking if LLM fails"""
        scored = []

        for prod in product_summaries:
            score = 0
            score += prod.get("seller_trust_score", 50) * 0.3
            score += prod.get("value_score", 50) * 0.3
            score += (prod.get("rating", 0) / 5.0) * 100 * 0.2
            score += (100 - (prod.get("price", 1000) / 50)) * 0.2  # Simple price scoring

            scored.append({
                "product_index": prod["index"],
                "overall_score": score,
                "match_score": 50,
                "value_assessment": "average",
                "reasoning": "Automatically scored based on multiple factors",
                "recommendation": "Review product details before purchase"
            })

        scored.sort(key=lambda x: x["overall_score"], reverse=True)

        for rank, item in enumerate(scored, 1):
            item["rank"] = rank

        return scored

    def _combine_rankings(
        self,
        llm_rankings: List[Dict],
        product_summaries: List[Dict],
        understanding: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Combine LLM ranking with algorithmic boosts

        Adjustments:
        - Boost lowest price products
        - Boost highest trust products
        - Penalize high-risk sellers
        """
        combined = []

        for rank_info in llm_rankings:
            idx = rank_info["product_index"]
            prod_summary = next((p for p in product_summaries if p["index"] == idx), None)

            if not prod_summary:
                continue

            score = rank_info.get("overall_score", 50)

            # Apply boosts and penalties
            if prod_summary.get("is_lowest_price"):
                score += 5

            if prod_summary.get("seller_trust_score", 50) >= 85:
                score += 5
            elif prod_summary.get("seller_risk_level") == "high":
                score -= 15

            if prod_summary.get("deal_quality") == "excellent":
                score += 8
            elif prod_summary.get("deal_quality") == "good":
                score += 4

            if prod_summary.get("has_warnings"):
                score -= 10

            rank_info["overall_score"] = max(0, min(100, score))
            combined.append(rank_info)

        # Re-sort by adjusted score
        combined.sort(key=lambda x: x["overall_score"], reverse=True)

        # Update ranks
        for new_rank, item in enumerate(combined, 1):
            item["rank"] = new_rank

        return combined

    def _generate_highlights(
        self,
        product: Any,
        reputation: Dict[str, Any],
        deal: Dict[str, Any]
    ) -> List[str]:
        """Generate bullet point highlights for product"""
        highlights = []

        # Deal highlights
        if deal.get("is_best_deal"):
            highlights.append(f"Top {deal.get('deal_rank', '')} Best Deal")

        deal_tags = deal.get("tags", [])
        if deal_tags:
            highlights.extend(deal_tags[:2])

        # Reputation highlights
        if reputation.get("trust_score", 0) >= 85:
            highlights.append("Trusted Seller")

        rep_recs = reputation.get("recommendations", [])
        if rep_recs:
            highlights.append(rep_recs[0][:50])

        # Product highlights
        try:
            rating = float(product.rating) if product.rating is not None else 0.0
            if rating >= 4.5:
                highlights.append(f"{rating} ⭐ Rating")
        except (ValueError, TypeError):
            pass

        return highlights[:4]  # Max 4 highlights
