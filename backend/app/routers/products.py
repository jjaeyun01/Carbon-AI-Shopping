import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.services.recommendation import recommend_products

router = APIRouter(prefix="/products", tags=["products"])

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "products.json"


def load_products():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/")
def get_products(
    category: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1)
):
    products = load_products()

    if category:
        products = [
            p for p in products
            if p["category"].lower() == category.lower()
        ]

    if limit:
        products = products[:limit]

    return {"products": products}


@router.get("/{product_id}")
def get_product(product_id: int):
    products = load_products()

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")


@router.get("/{product_id}/recommendations")
def get_product_recommendations(product_id: int):
    products = load_products()

    base_product = next((p for p in products if p["id"] == product_id), None)
    if not base_product:
        raise HTTPException(status_code=404, detail="Product not found")

    recommendations = recommend_products(base_product, products)

    return {
        "base_product_id": product_id,
        "base_product_name": base_product["name"],
        "recommendations": recommendations
    }