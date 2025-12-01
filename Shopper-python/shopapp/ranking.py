from typing import List, Tuple
import math
from .models import Product, ProductSearchPreferences

def score_product(prod: Product, prefs: ProductSearchPreferences) -> float:
    """
    Compute a numeric score for a single product given user preferences.
    """
    score = 0.0

    # 1. Price band
    if prod.price is not None:
        if prefs.min_price is not None and prod.price < prefs.min_price:
            score -= 100
        if prefs.max_price is not None and prod.price > prefs.max_price:
            score -= 100

        if prefs.min_price is not None and prefs.max_price is not None:
            center = (prefs.min_price + prefs.max_price) / 2
            dist = abs(prod.price - center) / max(center, 1e-6)
            score -= dist * 10

    # 2. Rating & popularity (ENHANCED for top-rated products)
    if prod.rating is not None:
        # Quality threshold: Penalize products below 3.5 stars heavily
        if prod.rating < 3.5:
            score -= 50  # Heavy penalty for low-rated products
        elif prod.rating < prefs.min_rating:
            score -= 30
        else:
            # Significantly increased weight for high ratings
            score += (prod.rating - prefs.min_rating) * 20  # Increased from 8 to 20
            
            # Exponential bonus for excellent products (4+ stars)
            if prod.rating >= 4.0:
                score += 30  # Extra boost for top-rated products
            
            # Additional bonus for near-perfect ratings (4.5+ stars)
            if prod.rating >= 4.5:
                score += 20  # Even more boost for exceptional products

    # Amplified review count impact for credibility
    if prod.rating_count is not None and prod.rating_count > 0:
        # Increased max impact from 10 to 25 points
        score += min(math.log10(prod.rating_count + 1) * 5, 25)
        
        # Combined quality score: Rating × Review Count factor
        # Products with both high ratings AND many reviews get extra boost
        if prod.rating is not None and prod.rating >= 4.0:
            quality_factor = prod.rating * math.log10(prod.rating_count + 1) * 3
            score += min(quality_factor, 30)  # Cap at 30 points

    # 3. Sponsorship penalty
    if prod.is_sponsored:
        score -= 5

    # 4. Brand preferences
    title_lower = prod.title.lower()
    for b in prefs.prefer_brands:
        if b.lower() in title_lower:
            score += 10

    for b in prefs.exclude_brands:
        if b.lower() in title_lower:
            score -= 50

    # 5. Features
    features_blob = (prod.title + " " + " ".join(prod.primary_features)).lower()

    for feat in prefs.must_have_features:
        if feat.lower() in features_blob:
            score += 15
        else:
            score -= 20

    for feat in prefs.nice_to_have_features:
        if feat.lower() in features_blob:
            score += 5

    return score

def rank_products(
    products: List[Product],
    prefs: ProductSearchPreferences,
    top_k: int = 10,
) -> List[Tuple[Product, float]]:
    """
    Rank a list of products according to preferences.
    """
    scored: List[Tuple[Product, float]] = []
    for p in products:
        s = score_product(p, prefs)
        scored.append((p, s))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
