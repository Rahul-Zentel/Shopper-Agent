from typing import List, Dict, Any
import statistics

class DealDetectionAgent:
    """
    Deal Detection Agent

    Responsibilities:
    - Identify discounts and deals
    - Compare prices across marketplaces
    - Flag best value products
    - Detect pricing anomalies
    - Calculate savings potential
    """

    def analyze_deals(self, products: List[Any], location: str) -> Dict[int, Dict[str, Any]]:
        """
        Analyze all products for deals and value

        Returns dict mapping product index to deal data
        """
        if not products:
            return {}

        # Extract prices for analysis
        prices = []
        for prod in products:
            try:
                if prod.price is not None:
                    price_val = float(prod.price)
                    if price_val > 0:  # Only include positive prices
                        prices.append(price_val)
            except (ValueError, TypeError, AttributeError):
                pass

        if not prices:
            return {}

        # Calculate price statistics
        avg_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        min_price = min(prices)
        max_price = max(prices)

        currency = "₹" if location.lower() == "india" else "$"

        results = {}
        for idx, product in enumerate(products):
            try:
                price = float(product.price) if product.price is not None else 0.0
            except (ValueError, TypeError, AttributeError):
                price = 0.0

            if price <= 0:
                continue

            # Calculate deal score
            deal_analysis = self._analyze_single_product(
                price, avg_price, median_price, min_price, max_price,
                product, currency
            )

            results[idx] = deal_analysis

        # Identify best deals
        best_deals = self._identify_best_deals(results)
        for idx in best_deals:
            results[idx]["is_best_deal"] = True
            results[idx]["deal_rank"] = best_deals.index(idx) + 1

        return results

    def _analyze_single_product(
        self,
        price: float,
        avg_price: float,
        median_price: float,
        min_price: float,
        max_price: float,
        product: Any,
        currency: str
    ) -> Dict[str, Any]:
        """Analyze a single product for deal potential"""

        # Calculate percentile
        price_percentile = self._calculate_percentile(price, min_price, max_price)

        # Calculate savings vs average
        savings_vs_avg = avg_price - price
        savings_percent_avg = (savings_vs_avg / avg_price * 100) if avg_price > 0 else 0

        # Calculate savings vs median
        savings_vs_median = median_price - price
        savings_percent_median = (savings_vs_median / median_price * 100) if median_price > 0 else 0

        # Determine deal quality
        deal_quality = self._determine_deal_quality(price_percentile, savings_percent_avg)

        # Calculate value score (price + rating)
        try:
            rating = float(product.rating) if product.rating is not None else 0.0
        except (ValueError, TypeError):
            rating = 0.0
        value_score = self._calculate_value_score(price_percentile, rating)

        # Generate deal tags
        tags = self._generate_deal_tags(
            price_percentile, savings_percent_avg, rating, price == min_price
        )

        # Check for potential discount indicators
        title_lower = product.title.lower()
        has_discount_keyword = any(word in title_lower for word in ['sale', 'off', 'deal', 'discount', 'clearance'])

        return {
            "price": price,
            "currency": currency,
            "price_percentile": round(price_percentile, 1),
            "savings_vs_average": round(savings_vs_avg, 2),
            "savings_percent": round(savings_percent_avg, 1),
            "deal_quality": deal_quality,
            "value_score": round(value_score, 1),
            "tags": tags,
            "is_lowest_price": price == min_price,
            "is_best_deal": False,
            "deal_rank": None,
            "price_position": self._get_price_position(price_percentile),
            "has_discount_keyword": has_discount_keyword,
            "recommendation": self._generate_deal_recommendation(
                deal_quality, value_score, price == min_price
            )
        }

    def _calculate_percentile(self, price: float, min_price: float, max_price: float) -> float:
        """Calculate where price falls in the range (0-100)"""
        if max_price == min_price:
            return 50.0

        percentile = ((price - min_price) / (max_price - min_price)) * 100
        return 100 - percentile  # Invert so lower price = higher percentile

    def _determine_deal_quality(self, price_percentile: float, savings_percent: float) -> str:
        """Determine overall deal quality"""
        if price_percentile >= 80 or savings_percent >= 20:
            return "excellent"
        elif price_percentile >= 60 or savings_percent >= 10:
            return "good"
        elif price_percentile >= 40 or savings_percent >= 5:
            return "fair"
        else:
            return "average"

    def _calculate_value_score(self, price_percentile: float, rating: float) -> float:
        """
        Calculate value score combining price and quality

        Formula: (price_percentile * 0.6) + (rating/5 * 100 * 0.4)
        """
        if rating == 0:
            return price_percentile * 0.8

        rating_score = (rating / 5.0) * 100
        value_score = (price_percentile * 0.6) + (rating_score * 0.4)

        return value_score

    def _generate_deal_tags(
        self,
        price_percentile: float,
        savings_percent: float,
        rating: float,
        is_lowest: bool
    ) -> List[str]:
        """Generate descriptive tags for the deal"""
        tags = []

        if is_lowest:
            tags.append("Lowest Price")

        if savings_percent >= 30:
            tags.append("Hot Deal")
        elif savings_percent >= 20:
            tags.append("Great Deal")
        elif savings_percent >= 10:
            tags.append("Good Deal")

        if price_percentile >= 80:
            tags.append("Best Value")
        elif price_percentile >= 60:
            tags.append("Good Value")

        if rating >= 4.5:
            tags.append("Top Rated")
        elif rating >= 4.0:
            tags.append("Highly Rated")

        if rating >= 4.0 and price_percentile >= 70:
            tags.append("Quality + Price")

        return tags

    def _get_price_position(self, percentile: float) -> str:
        """Get human-readable price position"""
        if percentile >= 80:
            return "Very Low"
        elif percentile >= 60:
            return "Below Average"
        elif percentile >= 40:
            return "Average"
        elif percentile >= 20:
            return "Above Average"
        else:
            return "High"

    def _generate_deal_recommendation(
        self,
        deal_quality: str,
        value_score: float,
        is_lowest: bool
    ) -> str:
        """Generate recommendation text"""
        if deal_quality == "excellent" and value_score >= 80:
            return "Outstanding value - highly recommended"
        elif deal_quality == "excellent":
            return "Excellent price - great deal"
        elif deal_quality == "good" and value_score >= 70:
            return "Good value for money"
        elif is_lowest:
            return "Lowest price available"
        elif deal_quality == "fair":
            return "Fair deal - consider alternatives"
        else:
            return "Compare with other options"

    def _identify_best_deals(self, deal_data: Dict[int, Dict[str, Any]]) -> List[int]:
        """Identify top 3 best deals by value score"""
        if not deal_data:
            return []

        # Sort by value score
        sorted_deals = sorted(
            deal_data.items(),
            key=lambda x: x[1].get("value_score", 0),
            reverse=True
        )

        # Return top 3 indices
        return [idx for idx, _ in sorted_deals[:3]]

    def get_summary(self, deal_data: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """Get overall deal summary"""
        if not deal_data:
            return {
                "total_products": 0,
                "best_deals_count": 0,
                "avg_savings_percent": 0,
                "price_range": None
            }

        savings = [d["savings_percent"] for d in deal_data.values()]
        prices = [d["price"] for d in deal_data.values()]

        best_deals = sum(1 for d in deal_data.values() if d.get("is_best_deal", False))

        return {
            "total_products": len(deal_data),
            "best_deals_count": best_deals,
            "avg_savings_percent": round(statistics.mean(savings), 1) if savings else 0,
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": round(statistics.mean(prices), 2) if prices else 0
            },
            "deal_quality_distribution": self._get_quality_distribution(deal_data)
        }

    def _get_quality_distribution(self, deal_data: Dict[int, Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of deal qualities"""
        distribution = {"excellent": 0, "good": 0, "fair": 0, "average": 0}

        for data in deal_data.values():
            quality = data.get("deal_quality", "average")
            distribution[quality] = distribution.get(quality, 0) + 1

        return distribution
