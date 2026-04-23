import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.models import Product
from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.orders import router as orders_router
from app.routers.products import router as products_router
from app.routers.user_actions import router as user_actions_router

PRODUCTS_JSON = Path(__file__).resolve().parent / "data" / "products.json"


def sync_products_from_json() -> None:
    """Upsert products from products.json so new catalog items appear after a server restart."""
    if not PRODUCTS_JSON.exists():
        return
    with open(PRODUCTS_JSON, "r", encoding="utf-8") as f:
        products = json.load(f)

    db = SessionLocal()
    try:
        for p in products:
            breakdown = p.get("carbon_breakdown")
            payload = {
                "name": p["name"],
                "category": p["category"],
                "price": float(p["price"]),
                "material": p["material"],
                "eco_score": int(p["eco_score"]),
                "carbon_kg": float(p["carbon_kg"]),
                "esg_rating": p["esg_rating"],
                "shipping_type": p["shipping_type"],
                "tag": p["tag"],
                "image_url": p.get("image_url") if isinstance(p.get("image_url"), str) else "",
                "description": p.get("description", ""),
                "source_url": p.get("source_url", ""),
                "carbon_breakdown": json.dumps(breakdown) if breakdown else None,
            }
            row = db.query(Product).filter(Product.id == p["id"]).first()
            if row:
                for key, val in payload.items():
                    setattr(row, key, val)
            else:
                db.add(Product(id=int(p["id"]), **payload))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    sync_products_from_json()
    yield


app = FastAPI(title="Novera API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(dashboard_router)
app.include_router(user_actions_router)
app.include_router(orders_router)


@app.get("/")
def root():
    return {"message": "Novera backend is running"}
