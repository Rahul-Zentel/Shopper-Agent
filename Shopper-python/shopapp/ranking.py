from typing import List, Tuple
import math
from models import Product, ProductSearchPreferences

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

    # 2. Rating & popularity
    if prod.rating is not None:
        if prod.rating < prefs.min_rating:
            score -= 30
        else:
            score += (prod.rating - prefs.min_rating) * 8

    if prod.rating_count is not None and prod.rating_count > 0:
        score += min(math.log10(prod.rating_count + 1) * 2, 10)

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
