from collections import Counter, OrderedDict
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, UserAction

router = APIRouter(prefix="/user-actions", tags=["user-actions"])


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
    user_id: int | None = None


def product_row_to_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "price": p.price,
        "material": p.material,
        "eco_score": p.eco_score,
        "carbon_kg": p.carbon_kg,
        "tag": p.tag,
        "image_url": p.image_url or "",
    }


@router.get("/")
def get_user_actions(db: Session = Depends(get_db)):
    actions = db.query(UserAction).order_by(UserAction.created_at.desc()).limit(500).all()
    return {
        "actions": [
            {
                "id": a.id,
                "action_type": a.action_type,
                "product_id": a.product_id,
                "source_product_id": a.source_product_id,
                "query": a.query,
                "created_at": a.created_at.isoformat(),
            }
            for a in actions
        ],
        "count": len(actions),
    }


@router.post("/")
def create_user_action(payload: UserActionCreate, db: Session = Depends(get_db)):
    action = UserAction(
        user_id=payload.user_id,
        action_type=payload.action_type,
        product_id=payload.product_id,
        source_product_id=payload.source_product_id,
        query=payload.query,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return {"message": "Action recorded", "action_id": action.id}


@router.get("/recent-products")
def get_recent_products(limit: int = 4, db: Session = Depends(get_db)):
    actions = (
        db.query(UserAction)
        .filter(UserAction.action_type == "view_product", UserAction.product_id.isnot(None))
        .order_by(UserAction.created_at.desc())
        .limit(200)
        .all()
    )

    seen: OrderedDict[int, dict] = OrderedDict()
    for action in actions:
        pid = action.product_id
        if pid not in seen:
            product = db.query(Product).filter(Product.id == pid).first()
            if product:
                seen[pid] = product_row_to_dict(product)
        if len(seen) >= limit:
            break

    return {"products": list(seen.values()), "count": len(seen)}


@router.get("/most-viewed-products")
def get_most_viewed_products(limit: int = 4, db: Session = Depends(get_db)):
    actions = (
        db.query(UserAction)
        .filter(
            UserAction.action_type.in_(["view_product", "view_recommendation"]),
            UserAction.product_id.isnot(None),
        )
        .all()
    )

    counter: Counter = Counter(a.product_id for a in actions)
    ranked = []
    for pid, count in counter.most_common(limit):
        product = db.query(Product).filter(Product.id == pid).first()
        if product:
            ranked.append({**product_row_to_dict(product), "view_count": count})

    return {"products": ranked, "count": len(ranked)}
