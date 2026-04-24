from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import decode_token
from app.database import get_db
from app.models import Order, OrderItem, Product, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Conventional (non-eco) carbon baseline per category (kg CO2e per item)
# Used to estimate how much CO2 the user *avoided* by choosing eco products
CONVENTIONAL_BASELINE: dict[str, float] = {
    "Clothing":    5.5,
    "Shoes":       9.5,
    "Bags":        6.0,
    "Accessories": 3.0,
    "Furniture":  28.0,
    "Home":        5.5,
    "Kitchen":     3.5,
    "Beauty":      2.0,
    "Fitness":     6.0,
    "Tech":        8.5,
    "General":     5.0,
}

EMPTY_STATS = {
    "authenticated": False,
    "has_purchases": False,
    "total_carbon_saved_kg": 0.0,
    "eco_choices_made": 0,
    "better_alternatives_chosen": 0,
    "sustainability_score": 0,
    "monthly_savings_kg": 0.0,
    "best_category": "—",
    "average_eco_score": 0,
    "total_orders": 0,
    "monthly_carbon_data": [0, 0, 0, 0, 0, 0],
}


@router.get("/")
def get_dashboard(token: str | None = None, db: Session = Depends(get_db)):
    # ── Auth ─────────────────────────────────────────────────────────────────
    user: User | None = None
    if token:
        payload = decode_token(token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()

    if not user:
        return {**EMPTY_STATS, "authenticated": False}

    # ── Fetch user's orders ───────────────────────────────────────────────────
    orders = db.query(Order).filter(Order.user_id == user.id).all()

    if not orders:
        return {**EMPTY_STATS, "authenticated": True, "has_purchases": False}

    order_ids = [o.id for o in orders]

    # ── Fetch all order items with their products ─────────────────────────────
    items_with_products: list[tuple[OrderItem, Product | None]] = (
        db.query(OrderItem, Product)
        .outerjoin(Product, OrderItem.product_id == Product.id)
        .filter(OrderItem.order_id.in_(order_ids))
        .all()
    )

    # ── Compute metrics ───────────────────────────────────────────────────────
    total_carbon_saved = 0.0
    eco_items_count = 0
    eco_scores: list[int] = []
    category_counts: dict[str, int] = {}

    for item, product in items_with_products:
        cat = (product.category if product else "General") or "General"
        baseline = CONVENTIONAL_BASELINE.get(cat, 5.0)
        saved = max(0.0, baseline - item.carbon_kg) * item.quantity
        total_carbon_saved += saved

        # "eco choice" = eco_score < 35 or carbon saved > 0
        if product and product.eco_score < 35:
            eco_items_count += item.quantity
            eco_scores.append(product.eco_score)

        category_counts[cat] = category_counts.get(cat, 0) + item.quantity

    best_category = max(category_counts, key=lambda k: category_counts[k]) if category_counts else "—"
    avg_eco_score = round(sum(eco_scores) / len(eco_scores)) if eco_scores else 0

    # Sustainability score: 100 = perfect eco choices, scales down with higher scores
    # eco_score 0 → sustainability 100, eco_score 50+ → sustainability 50
    sustainability_score = max(0, min(100, round(100 - avg_eco_score * 1.0))) if avg_eco_score else 50

    # Monthly carbon saved (last 30 days)
    cutoff = datetime.utcnow() - timedelta(days=30)
    recent_order_ids = {o.id for o in orders if o.created_at >= cutoff}
    monthly_saved = 0.0
    for item, product in items_with_products:
        if item.order_id in recent_order_ids:
            cat = (product.category if product else "General") or "General"
            baseline = CONVENTIONAL_BASELINE.get(cat, 5.0)
            monthly_saved += max(0.0, baseline - item.carbon_kg) * item.quantity

    # Monthly carbon data for bar chart (last 6 months)
    monthly_data: list[float] = []
    now = datetime.utcnow()
    for months_ago in range(5, -1, -1):
        start = (now - timedelta(days=30 * (months_ago + 1))).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = (now - timedelta(days=30 * months_ago)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        month_ids = {o.id for o in orders if start <= o.created_at < end}
        month_saved = sum(
            max(0.0, CONVENTIONAL_BASELINE.get(
                (product.category if product else "General") or "General", 5.0
            ) - item.carbon_kg) * item.quantity
            for item, product in items_with_products
            if item.order_id in month_ids
        )
        monthly_data.append(round(month_saved, 2))

    return {
        "authenticated": True,
        "has_purchases": True,
        "total_carbon_saved_kg": round(total_carbon_saved, 2),
        "eco_choices_made": eco_items_count,
        "better_alternatives_chosen": len(orders),
        "sustainability_score": sustainability_score,
        "monthly_savings_kg": round(monthly_saved, 2),
        "best_category": best_category,
        "average_eco_score": avg_eco_score,
        "total_orders": len(orders),
        "monthly_carbon_data": monthly_data,
    }
