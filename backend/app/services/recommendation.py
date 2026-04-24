from typing import Any

# Categories that are considered "related" — recommendations can cross group boundaries
# when no same-category eco alternatives exist.
CATEGORY_GROUPS: dict[str, str] = {
    "Clothing": "wearables",
    "Shoes": "wearables",
    "Bags": "carry",
    "Accessories": "carry",
    "Furniture": "home_living",
    "Home": "home_living",
    "Kitchen": "home_living",
    "Beauty": "personal_care",
    "Fitness": "personal_care",
    "Tech": "tech",
    "General": "general",
}


def _price_score(base: float, candidate: float) -> float:
    if base == 0:
        return 0.0
    diff = abs(base - candidate) / base
    return max(0.0, 1.0 - diff)


def _compute_similarity(base: dict[str, Any], candidate: dict[str, Any]) -> float:
    score = 0.0

    if base["category"] == candidate["category"]:
        score += 0.5
    elif CATEGORY_GROUPS.get(base["category"]) == CATEGORY_GROUPS.get(candidate["category"]):
        # Related category (e.g., Clothing ↔ Shoes)
        score += 0.2

    score += 0.3 * _price_score(base["price"], candidate["price"])

    b_mat = base["material"].lower()
    c_mat = candidate["material"].lower()
    if b_mat == c_mat:
        score += 0.2
    elif any(word in c_mat for word in b_mat.split()):
        score += 0.1

    return round(score, 3)


def recommend_products(
    base_product: dict[str, Any],
    all_products: list[dict[str, Any]],
    max_results: int = 4,
) -> list[dict[str, Any]]:
    """
    Return up to `max_results` eco-friendlier alternatives to base_product.

    Strategy:
    1. Prefer exact-category matches with positive eco_gain.
    2. If fewer than max_results found, expand to related-category matches.
    3. If still short, pull any product with a significantly better eco_score
       (eco_gain >= 5) regardless of category.
    """
    base_eco = base_product["eco_score"]
    base_group = CATEGORY_GROUPS.get(base_product["category"], "general")

    def _as_recommendation(p: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "price": p["price"],
            "material": p["material"],
            "eco_score": p["eco_score"],
            "carbon_kg": p["carbon_kg"],
            "esg_rating": p["esg_rating"],
            "shipping_type": p["shipping_type"],
            "tag": p["tag"],
            "image_url": p.get("image_url", ""),
            "description": p.get("description", ""),
            "similarity_score": _compute_similarity(base_product, p),
            "eco_gain_score": base_eco - p["eco_score"],
        }

    # ── Pass 1: same category, eco_gain > 0 ──────────────────────────────
    same_cat = [
        _as_recommendation(p)
        for p in all_products
        if p["id"] != base_product["id"]
        and p["category"] == base_product["category"]
        and base_eco - p["eco_score"] > 0
    ]
    same_cat.sort(key=lambda x: (-x["similarity_score"], -x["eco_gain_score"]))

    results: list[dict[str, Any]] = same_cat[:max_results]

    # ── Pass 2: related category group, eco_gain > 0 ─────────────────────
    if len(results) < max_results:
        seen_ids = {r["id"] for r in results}
        related = [
            _as_recommendation(p)
            for p in all_products
            if p["id"] != base_product["id"]
            and p["id"] not in seen_ids
            and CATEGORY_GROUPS.get(p["category"]) == base_group
            and base_eco - p["eco_score"] > 0
        ]
        related.sort(key=lambda x: (-x["eco_gain_score"], -x["similarity_score"]))
        results.extend(related[: max_results - len(results)])

    # ── Pass 3: any category with significantly better eco_score ─────────
    if len(results) < max_results:
        seen_ids = {r["id"] for r in results}
        fallback = [
            _as_recommendation(p)
            for p in all_products
            if p["id"] != base_product["id"]
            and p["id"] not in seen_ids
            and base_eco - p["eco_score"] >= 5
        ]
        fallback.sort(key=lambda x: -x["eco_gain_score"])
        results.extend(fallback[: max_results - len(results)])

    return results
