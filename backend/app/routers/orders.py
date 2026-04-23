import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderItem

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderItemSchema(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    material: str
    carbon_kg: float


class ShippingInfo(BaseModel):
    full_name: str
    email: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str = "United States"


class PlaceOrderRequest(BaseModel):
    items: list[OrderItemSchema]
    shipping: ShippingInfo
    user_id: int | None = None


@router.post("/")
def place_order(body: PlaceOrderRequest, db: Session = Depends(get_db)):
    total_price = sum(i.price * i.quantity for i in body.items)
    total_carbon = sum(i.carbon_kg * i.quantity for i in body.items)
    order_id = str(uuid.uuid4())[:8].upper()

    order = Order(
        id=order_id,
        user_id=body.user_id,
        status="confirmed",
        total_price=round(total_price, 2),
        total_carbon_kg=round(total_carbon, 2),
        shipping_info=json.dumps(body.shipping.model_dump()),
        created_at=datetime.utcnow(),
    )
    db.add(order)

    for item in body.items:
        db.add(OrderItem(
            order_id=order_id,
            product_id=item.product_id,
            name=item.name,
            price=item.price,
            quantity=item.quantity,
            material=item.material,
            carbon_kg=item.carbon_kg,
        ))

    db.commit()

    return {
        "order_id": order_id,
        "status": "confirmed",
        "total_price": order.total_price,
        "total_carbon_kg": order.total_carbon_kg,
        "message": "Order placed successfully",
    }


@router.get("/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id.upper()).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    shipping = json.loads(order.shipping_info) if order.shipping_info else {}
    return {
        "id": order.id,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "total_price": order.total_price,
        "total_carbon_kg": order.total_carbon_kg,
        "shipping": shipping,
        "items": [
            {
                "product_id": i.product_id,
                "name": i.name,
                "price": i.price,
                "quantity": i.quantity,
                "material": i.material,
                "carbon_kg": i.carbon_kg,
            }
            for i in order.items
        ],
    }
