"""
Demo seed: creates two verified test accounts with realistic order history.

Account 1 — 기존 계정 (wodbs0101@gmail.com)
  - 6개월치 구매 내역 (활발한 eco shopper)

Account 2 — 신규 테스트 계정 (demo@novera.eco / password: demo1234)
  - 최근 2개월 구매 내역 (입문 eco shopper)

Usage:
    cd backend && python3 -m app.scripts.seed_demo_data
"""

import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from app.auth import hash_password
from app.database import Base, SessionLocal, engine, run_migrations
from app.models import EmailVerificationToken, Order, OrderItem, Product, User

run_migrations()
Base.metadata.create_all(bind=engine)
db = SessionLocal()


def _order(user_id: int, items: list[dict], days_ago: int) -> None:
    """items = [{"product_id": int, "qty": int}]"""
    created_at = datetime.utcnow() - timedelta(days=days_ago)
    order_id = str(uuid.uuid4())[:12]

    total_price = 0.0
    total_carbon = 0.0
    order_items = []

    for item in items:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            continue
        qty = item["qty"]
        total_price += product.price * qty
        total_carbon += product.carbon_kg * qty
        order_items.append(OrderItem(
            order_id=order_id,
            product_id=product.id,
            name=product.name,
            price=product.price,
            quantity=qty,
            material=product.material,
            carbon_kg=product.carbon_kg,
        ))

    if not order_items:
        return

    order = Order(
        id=order_id,
        user_id=user_id,
        status="confirmed",
        total_price=round(total_price, 2),
        total_carbon_kg=round(total_carbon, 3),
        shipping_info=json.dumps({"address": "Seoul, Korea", "method": "standard"}),
        created_at=created_at,
    )
    db.add(order)
    for oi in order_items:
        db.add(oi)


# ── 계정 1: wodbs0101@gmail.com ──────────────────────────────────────────────
user1 = db.query(User).filter(User.email == "wodbs0101@gmail.com").first()
if not user1:
    user1 = User(
        email="wodbs0101@gmail.com",
        username="jaeyoon",
        full_name="Jaeyoon Lee",
        hashed_password=hash_password("password123"),
        is_active=True,
        is_verified=True,
    )
    db.add(user1)
    db.flush()
else:
    # Mark as verified, ensure full_name
    user1.is_verified = True
    if not user1.full_name:
        user1.full_name = "Jaeyoon Lee"
    # Remove any pending verification tokens
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user1.id
    ).delete()

db.flush()

# Delete existing orders for clean re-seed
for o in db.query(Order).filter(Order.user_id == user1.id).all():
    db.query(OrderItem).filter(OrderItem.order_id == o.id).delete()
    db.delete(o)
db.flush()

# 6 months of purchases (eco_score mostly 15-28)
_order(user1.id, [{"product_id": 1,  "qty": 2},   # Patagonia tee x2
                  {"product_id": 5,  "qty": 1}],   # Tentree tee
       days_ago=168)

_order(user1.id, [{"product_id": 88, "qty": 1},   # Blueland cleaning kit
                  {"product_id": 94, "qty": 1}],   # Bamboo cutting board
       days_ago=140)

_order(user1.id, [{"product_id": 37, "qty": 1},   # Nisolo sneaker
                  {"product_id": 105, "qty": 2}],  # Dr. Bronner's soap x2
       days_ago=112)

_order(user1.id, [{"product_id": 117, "qty": 1},  # Manduka yoga mat
                  {"product_id": 106, "qty": 1}],  # Ursa Major face wash
       days_ago=80)

_order(user1.id, [{"product_id": 2,  "qty": 1},   # Patagonia Capilene shirt
                  {"product_id": 80, "qty": 1}],   # Bamboo sheet set
       days_ago=45)

_order(user1.id, [{"product_id": 89, "qty": 2},   # Grove glass cleaner x2
                  {"product_id": 107, "qty": 1},   # Biodegradable face wipes
                  {"product_id": 119, "qty": 1}],  # Jade Harmony yoga mat
       days_ago=12)

print(f"User 1 ({user1.email}): 6 orders seeded")


# ── 계정 2: demo@novera.eco ──────────────────────────────────────────────────
user2 = db.query(User).filter(User.email == "demo@novera.eco").first()
if not user2:
    user2 = User(
        email="demo@novera.eco",
        username="novera_demo",
        full_name="Demo User",
        hashed_password=hash_password("demo1234"),
        is_active=True,
        is_verified=True,
    )
    db.add(user2)
    db.flush()
else:
    user2.is_verified = True
    for o in db.query(Order).filter(Order.user_id == user2.id).all():
        db.query(OrderItem).filter(OrderItem.order_id == o.id).delete()
        db.delete(o)
    db.flush()

# 2 months of purchases (newer eco shopper)
_order(user2.id, [{"product_id": 5,  "qty": 1},   # Tentree tee
                  {"product_id": 89, "qty": 1}],   # Grove cleaner
       days_ago=55)

_order(user2.id, [{"product_id": 118, "qty": 1},  # Manduka PROlite mat
                  {"product_id": 105, "qty": 1}],  # Dr. Bronner's soap
       days_ago=18)

print(f"User 2 ({user2.email}): 2 orders seeded")

db.commit()
db.close()

print("\n──────────────────────────────────────")
print("Demo accounts ready:")
print("  Email : wodbs0101@gmail.com  | PW: (기존 비밀번호)")
print("  Email : demo@novera.eco      | PW: demo1234")
print("──────────────────────────────────────")
