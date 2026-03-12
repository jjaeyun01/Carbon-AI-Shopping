import json
from collections import Counter, OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/user-actions", tags=["user-actions"])

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "user_actions.json"
PRODUCTS_PATH = Path(__file__).resolve().parent.parent / "data" / "products.json"


class UserActionCreate(BaseModel):
    action_type: Literal[
        "view_product",
        "view_recommendation",
        "search_products",
        "open_product_from_grid",
    ]
    product_id: int | None = None
    source_product_id: int | None = None
    query: str | None = None


def load_actions() -> list[dict]:
    if not DATA_PATH.exists():
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_actions(actions: list[dict]) -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(actions, f, ensure_ascii=False, indent=2)


def load_products() -> list[dict]:
    if not PRODUCTS_PATH.exists():
        return []

    with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/")
def get_user_actions():
    actions = load_actions()
    return {"actions": actions, "count": len(actions)}


@router.post("/")
def create_user_action(payload: UserActionCreate):
    actions = load_actions()

    new_action = {
        "id": len(actions) + 1,
        "action_type": payload.action_type,
        "product_id": payload.product_id,
        "source_product_id": payload.source_product_id,
        "query": payload.query,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    actions.append(new_action)
    save_actions(actions)

    return {"message": "Action recorded", "action": new_action}


@router.get("/recent-products")
def get_recent_products(limit: int = 4):
    actions = load_actions()

    recent_view_actions = [
        action
        for action in actions
        if action["action_type"] == "view_product" and action["product_id"] is not None
    ]

    products = load_products()
    product_map = {product["id"]: product for product in products}

    ordered_recent = OrderedDict()

    for action in reversed(recent_view_actions):
        product_id = action["product_id"]
        if product_id in product_map and product_id not in ordered_recent:
            ordered_recent[product_id] = product_map[product_id]

        if len(ordered_recent) >= limit:
            break

    return {
        "products": list(ordered_recent.values()),
        "count": len(ordered_recent),
    }


@router.get("/most-viewed-products")
def get_most_viewed_products(limit: int = 4):
    actions = load_actions()

    counted_action_types = {
        "view_product",
        "view_recommendation",
    }

    product_counter = Counter()

    for action in actions:
        action_type = action.get("action_type")
        product_id = action.get("product_id")

        if action_type in counted_action_types and product_id is not None:
            product_counter[product_id] += 1

    products = load_products()
    product_map = {product["id"]: product for product in products}

    ranked_products = []
    for product_id, view_count in product_counter.most_common(limit):
        product = product_map.get(product_id)
        if product:
            ranked_products.append({**product, "view_count": view_count})

    return {
        "products": ranked_products,
        "count": len(ranked_products),
    }