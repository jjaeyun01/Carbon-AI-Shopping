import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.services.carbon_calculator import estimate_carbon, infer_shipping_type
from app.services.product_scraper import scrape_product_page
from app.services.recommendation import recommend_products

router = APIRouter(prefix="/products", tags=["products"])


class ScrapeRequest(BaseModel):
    url: str


def _source_url_variants(url: str) -> list[str]:
    u = url.strip()
    if not u:
        return []
    out = {u, u.rstrip("/"), u.rstrip("/") + "/"}
    return list(out)


def _find_product_by_source_url(db: Session, url: str) -> Product | None:
    variants = _source_url_variants(url)
    row = db.query(Product).filter(Product.source_url.in_(variants)).first()
    if row:
        return row
    norm = url.strip().rstrip("/")
    for p in db.query(Product).all():
        if p.source_url and p.source_url.strip().rstrip("/") == norm:
            return p
    return None


def _scrape_and_create_product(db: Session, url: str) -> Product:
    scraped = scrape_product_page(url)
    shipping_type = infer_shipping_type(scraped.brand + " " + scraped.source_url)
    carbon = estimate_carbon(
        category=scraped.category,
        title=scraped.title,
        material_text=scraped.material_text,
        shipping_type=shipping_type,
    )
    breakdown = {
        "estimated_weight_kg": carbon.estimated_weight_kg,
        "material_carbon_kg": carbon.material_carbon_kg,
        "shipping_carbon_kg": carbon.shipping_carbon_kg,
    }
    product = Product(
        name=scraped.title,
        category=scraped.category,
        price=scraped.price,
        material=carbon.material.title(),
        eco_score=carbon.eco_score,
        carbon_kg=carbon.total_carbon_kg,
        esg_rating=carbon.esg_rating,
        shipping_type=shipping_type.title(),
        tag="AI Estimated",
        image_url=scraped.image_url,
        description=scraped.description or scraped.raw_text_excerpt[:220],
        source_url=scraped.source_url,
        carbon_breakdown=json.dumps(breakdown),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def product_to_dict(p: Product) -> dict:
    breakdown = None
    if p.carbon_breakdown:
        try:
            breakdown = json.loads(p.carbon_breakdown)
        except Exception:
            breakdown = None
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "price": p.price,
        "material": p.material,
        "eco_score": p.eco_score,
        "carbon_kg": p.carbon_kg,
        "esg_rating": p.esg_rating,
        "shipping_type": p.shipping_type,
        "tag": p.tag,
        "image_url": p.image_url or "",
        "description": p.description or "",
        "source_url": p.source_url or "",
        "carbon_breakdown": breakdown,
    }


@router.get("/")
def get_products(
    category: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1),
    sort: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category and category.lower() != "all":
        query = query.filter(Product.category.ilike(category))
    if sort == "eco_score_asc":
        query = query.order_by(Product.eco_score.asc())
    elif sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    products = query.all()
    if limit:
        products = products[:limit]
    return {"products": [product_to_dict(p) for p in products]}


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    rows = db.query(Product.category).distinct().all()
    categories = sorted({r[0] for r in rows if r[0]})
    return {"categories": ["All"] + categories}


@router.post("/compare-from-url")
def compare_from_url(body: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Scrape a product URL (or reuse if already saved), estimate footprint, and return
    greener alternatives from the catalog when available.
    """
    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    existing = _find_product_by_source_url(db, url)
    if existing:
        product = existing
        already_exists = True
    else:
        try:
            product = _scrape_and_create_product(db, url)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not analyze this URL: {e}")
        already_exists = False

    all_products = [product_to_dict(p) for p in db.query(Product).all()]
    base = product_to_dict(product)
    recommendations = recommend_products(base, all_products)

    return {
        "base_product": base,
        "recommendations": recommendations,
        "already_exists": already_exists,
    }


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_to_dict(product)


@router.get("/{product_id}/recommendations")
def get_product_recommendations(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    all_products = [product_to_dict(p) for p in db.query(Product).all()]
    base = product_to_dict(product)
    recommendations = recommend_products(base, all_products)

    return {
        "base_product_id": product_id,
        "base_product_name": product.name,
        "recommendations": recommendations,
    }


@router.post("/scrape")
def scrape_and_add_product(body: ScrapeRequest, db: Session = Depends(get_db)):
    if _find_product_by_source_url(db, body.url):
        raise HTTPException(status_code=409, detail="Product with this URL already exists")

    try:
        product = _scrape_and_create_product(db, body.url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Scraping failed: {e}")

    return product_to_dict(product)
