from typing import List, Dict, Any

class SellerReputationAgent:
    """
    Seller Reputation Agent

    Responsibilities:
    - Score seller trustworthiness
    - Flag potential scam indicators
    - Provide seller ratings
    - Warn about risky purchases
    """

    # Trusted marketplace ratings (based on reputation, buyer protection, return policies)
    MARKETPLACE_TRUST_SCORES = {
        "flipkart": 85,
        "amazon.in": 90,
        "amazon.com": 92,
        "walmart": 88,
        "target": 87,
        "best buy": 86,
        "etsy": 75,
        "croma": 80,
        "reliance digital": 82,
    }

    # Red flags for products
    RED_FLAGS = {
        "price_too_low": "Price significantly below market average",
        "no_rating": "Product has no customer ratings",
        "very_low_rating": "Product rating below 3.0",
        "few_reviews": "Less than 5 customer reviews",
        "new_seller": "New or unverified seller",
    }

    def analyze_seller(self, product: Any, all_products: List[Any]) -> Dict[str, Any]:
        """
        Analyze seller reputation for a single product

        Returns:
        {
            "trust_score": 0-100,
            "marketplace_score": 0-100,
            "risk_level": "low|medium|high",
            "red_flags": [],
            "warnings": [],
            "recommendations": []
        }
        """
        marketplace = getattr(product, 'marketplace', '').lower()

        # Safe conversions
        try:
            price = float(product.price) if product.price is not None else 0.0
        except (ValueError, TypeError):
            price = 0.0

        try:
            rating = float(product.rating) if product.rating is not None else 0.0
        except (ValueError, TypeError):
            rating = 0.0

        try:
            rating_count = int(getattr(product, 'rating_count', 0) or 0)
        except (ValueError, TypeError):
            rating_count = 0

        # Base marketplace trust score
        marketplace_score = self.MARKETPLACE_TRUST_SCORES.get(marketplace, 50)

        # Calculate price anomaly
        avg_price = self._calculate_average_price(all_products, product.title)
        price_anomaly = self._detect_price_anomaly(price, avg_price)

        # Detect red flags
        red_flags = []
        warnings = []

        if price_anomaly == "too_low":
            red_flags.append(self.RED_FLAGS["price_too_low"])

        if rating == 0:
            red_flags.append(self.RED_FLAGS["no_rating"])
        elif rating < 3.0:
            red_flags.append(self.RED_FLAGS["very_low_rating"])

        if rating_count and rating_count < 5:
            warnings.append(self.RED_FLAGS["few_reviews"])

        # Calculate overall trust score
        trust_score = marketplace_score

        # Adjust based on product rating
        if rating > 0:
            rating_boost = (rating - 3.0) * 10  # +10 per star above 3.0
            trust_score += rating_boost
        else:
            trust_score -= 15  # penalty for no rating

        # Adjust based on review count
        if rating_count:
            if rating_count < 5:
                trust_score -= 10
            elif rating_count > 100:
                trust_score += 10
            elif rating_count > 500:
                trust_score += 15

        # Adjust for price anomaly
        if price_anomaly == "too_low":
            trust_score -= 20
            warnings.append("Verify product authenticity before purchase")
        elif price_anomaly == "too_high":
            trust_score -= 5
            warnings.append("Price higher than average - check for additional features")

        # Cap trust score
        trust_score = max(0, min(100, trust_score))

        # Determine risk level
        if trust_score >= 75:
            risk_level = "low"
        elif trust_score >= 50:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Generate recommendations
        recommendations = self._generate_recommendations(
            marketplace_score, rating, rating_count, price_anomaly
        )

        return {
            "trust_score": round(trust_score, 1),
            "marketplace_score": marketplace_score,
            "risk_level": risk_level,
            "red_flags": red_flags,
            "warnings": warnings,
            "recommendations": recommendations,
            "details": {
                "marketplace": marketplace,
                "has_rating": rating > 0,
                "rating_value": rating,
                "review_count": rating_count,
                "price_status": price_anomaly
            }
        }

    def _calculate_average_price(self, all_products: List[Any], product_title: str) -> float:
        """Calculate average price for similar products"""
        prices = []
        for prod in all_products:
            if prod.price:
                try:
                    prices.append(float(prod.price))
                except:
                    pass

        if not prices:
            return 0

        return sum(prices) / len(prices)

    def _detect_price_anomaly(self, price: float, avg_price: float) -> str:
        """Detect if price is anomalously high or low"""
        if avg_price == 0 or price == 0:
            return "normal"

        ratio = price / avg_price

        if ratio < 0.5:  # More than 50% below average
            return "too_low"
        elif ratio > 1.5:  # More than 50% above average
            return "too_high"
        else:
            return "normal"

    def _generate_recommendations(
        self,
        marketplace_score: int,
        rating: float,
        rating_count: int,
        price_anomaly: str
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if marketplace_score >= 85:
            recommendations.append("Trusted marketplace with buyer protection")

        if rating >= 4.5 and rating_count and rating_count > 100:
            recommendations.append("Highly rated product with substantial reviews")

        if rating > 0 and rating < 3.5:
            recommendations.append("Consider alternative products with better ratings")

        if price_anomaly == "too_low":
            recommendations.append("Verify seller authenticity and product details")

        if not rating_count or rating_count < 10:
            recommendations.append("New product - check for detailed specifications")

        return recommendations

    def batch_analyze(self, products: List[Any]) -> Dict[int, Dict[str, Any]]:
        """Analyze seller reputation for all products"""
        results = {}

        for idx, product in enumerate(products):
            results[idx] = self.analyze_seller(product, products)

        return results

    def filter_risky_products(
        self,
        products: List[Any],
        reputation_data: Dict[int, Dict[str, Any]],
        max_risk_level: str = "medium"
    ) -> List[int]:
        """
        Filter out high-risk products

        Returns indices of products to keep
        """
        risk_order = {"low": 0, "medium": 1, "high": 2}
        max_risk = risk_order.get(max_risk_level, 1)

        safe_indices = []
        for idx, rep_data in reputation_data.items():
            risk_level = rep_data.get("risk_level", "high")
            if risk_order.get(risk_level, 2) <= max_risk:
                safe_indices.append(idx)

        return safe_indices
