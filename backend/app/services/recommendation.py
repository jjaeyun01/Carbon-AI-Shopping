from typing import Any


def load_price_similarity_score(base_price: float, candidate_price: float) -> float:
    if base_price == 0:
        return 0.0
    diff_ratio = abs(base_price - candidate_price) / base_price
    return max(0.0, 1.0 - diff_ratio)


def compute_similarity(base: dict[str, Any], candidate: dict[str, Any]) -> float:
    score = 0.0

    if base["category"] == candidate["category"]:
        score += 0.5

    price_score = load_price_similarity_score(base["price"], candidate["price"])
    score += 0.3 * price_score

    if base["material"].lower() == candidate["material"].lower():
        score += 0.2
    elif any(
        word in candidate["material"].lower()
        for word in base["material"].lower().split()
    ):
        score += 0.1

    return round(score, 3)


def recommend_products(
    base_product: dict[str, Any], all_products: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    recommendations = []

    for product in all_products:
        if product["id"] == base_product["id"]:
            continue

        if product["category"] != base_product["category"]:
            continue

        similarity = compute_similarity(base_product, product)
        eco_gain = base_product["eco_score"] - product["eco_score"]

        if eco_gain <= 0:
            continue

        recommendations.append(
            {
                "id": product["id"],
                "name": product["name"],
                "category": product["category"],
                "price": product["price"],
                "material": product["material"],
                "eco_score": product["eco_score"],
                "carbon_kg": product["carbon_kg"],
                "esg_rating": product["esg_rating"],
                "shipping_type": product["shipping_type"],
                "tag": product["tag"],
                "image_url": product.get("image_url", ""),
                "description": product.get("description", ""),
                "similarity_score": similarity,
                "eco_gain_score": eco_gain,
            }
        )

    recommendations.sort(
        key=lambda x: (-x["similarity_score"], -x["eco_gain_score"])
    )

    return recommendations[:4]