"""
Batch-import eco products from Shopify stores via their public products.json API.

Shopify exposes GET /products.json?limit=250&page=N on all stores by default.
No authentication required.

Usage:
    cd backend
    python -m app.scripts.scrape_shopify_stores                # all stores, default limit
    python -m app.scripts.scrape_shopify_stores --limit 100    # 100 per store
    python -m app.scripts.scrape_shopify_stores --stores earthhero.com
    python -m app.scripts.scrape_shopify_stores --dry-run

Then restart uvicorn so sync_products_from_json() picks up the new rows.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "products.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

# Eco-friendly Shopify stores with verified public products.json access
SHOPIFY_STORES: dict[str, str] = {
    "earthhero.com": "https://earthhero.com",
    "packagefreeshop.com": "https://packagefreeshop.com",
    "zerowastestore.com": "https://zerowastestore.com",
    "ecoroots.us": "https://ecoroots.us",
    "pela.earth": "https://pela.earth",
}

# ── Category mapping ─────────────────────────────────────────────────────────
# Maps fragments from Shopify product_type / tags → our category system

CATEGORY_KEYWORDS: list[tuple[list[str], str]] = [
    (["sneaker", "shoe", "boot", "sandal", "footwear", "slipper", "runner"], "Shoes"),
    (["shampoo", "conditioner", "face wash", "moisturizer", "serum", "sunscreen",
      "deodorant", "lip balm", "toothbrush", "body wash", "skincare", "soap bar",
      "castile", "dry shampoo", "makeup", "mascara", "foundation"], "Beauty"),
    (["yoga mat", "gym", "resistance band", "workout", "fitness", "sport bottle",
      "exercise", "kettlebell", "dumbbell"], "Fitness"),
    (["sheet set", "duvet", "comforter", "bedding", "pillowcase", "bath towel",
      "hand towel", "bath rug", "throw", "blanket", "mattress", "pillow"], "Home"),
    (["frying pan", "cookware", "bento", "lunch box", "food storage", "dish soap",
      "glass cleaner", "cleaning", "food wrap", "beeswax", "silicone bag",
      "cutting board", "coffee filter", "dish brush", "kitchen", "utensil",
      "container", "reusable bag", "produce bag", "beeswax wrap"], "Kitchen"),
    (["desk", "chair", "table", "sofa", "shelf", "bookcase", "dresser",
      "bed frame", "couch", "sectional", "wardrobe", "cabinet"], "Furniture"),
    (["shirt", "tee", "t-shirt", "jacket", "hoodie", "pants", "dress", "sweater",
      "sweatshirt", "legging", "shorts", "skirt", "sock", "flannel", "jeans",
      "denim", "cardigan", "pullover", "blazer", "coat", "parka", "fleece",
      "top", "bottom", "activewear", "underwear", "bra", "brief", "boxer"], "Clothing"),
    (["bag", "backpack", "tote", "purse", "handbag", "duffel", "messenger",
      "crossbody", "rucksack", "satchel", "wallet", "clutch", "pack"], "Bags"),
    (["watch", "cap", "hat", "belt", "sunglasses", "jewelry", "bracelet",
      "ring", "necklace", "water bottle", "insulated bottle", "beanie",
      "scarf", "gloves", "phone case", "case"], "Accessories"),
    (["laptop", "keyboard", "mouse", "monitor", "cable", "charger", "tablet",
      "speaker", "headphone", "earphone", "laptop stand", "charging"], "Tech"),
]


def _infer_category(product_type: str, tags: list[str], title: str, body: str) -> str:
    text = " ".join([product_type, title, body[:300], *tags]).lower()
    for keywords, category in CATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            return category
    return "General"


# ── Material extraction ───────────────────────────────────────────────────────

MATERIAL_PATTERNS = [
    r"(organic cotton)",
    r"(recycled polyester)",
    r"(recycled nylon)",
    r"(recycled cotton)",
    r"(recycled wool)",
    r"(merino wool)",
    r"(organic linen)",
    r"(eucalyptus fiber)",
    r"(plant.based|plant fiber)",
    r"(reclaimed wood)",
    r"\b(bamboo)\b",
    r"\b(hemp)\b",
    r"\b(cork)\b",
    r"\b(silicone)\b",
    r"\b(glass)\b",
    r"\b(linen)\b",
    r"\b(cotton)\b",
    r"\b(polyester)\b",
    r"\b(nylon)\b",
    r"\b(wool)\b",
    r"\b(wood)\b",
    r"\b(metal|stainless steel|steel)\b",
    r"\b(aluminum|aluminium)\b",
    r"\b(plastic)\b",
]


def _extract_material(body_html: str, tags: list[str]) -> str:
    text = (BeautifulSoup(body_html or "", "html.parser").get_text(" ") + " " + " ".join(tags)).lower()
    for pattern in MATERIAL_PATTERNS:
        m = re.search(pattern, text)
        if m:
            found = m.group(1).strip()
            # normalise "plant-based" → "plant fiber"
            if "plant" in found:
                return "plant fiber"
            # normalise "stainless steel" → "metal"
            if "stainless" in found or "steel" in found:
                return "metal"
            return found
    return "unknown"


def _strip_html(html: str) -> str:
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)[:300]


def _lowest_price(variants: list[dict]) -> float:
    prices = []
    for v in variants:
        try:
            prices.append(float(v.get("price", 0) or 0))
        except (ValueError, TypeError):
            pass
    return min(prices) if prices else 0.0


# ── Pagination ───────────────────────────────────────────────────────────────

def _fetch_all_products(base_url: str, max_products: int, delay: float) -> list[dict]:
    results: list[dict] = []
    page = 1
    while len(results) < max_products:
        url = f"{base_url}/products.json?limit=250&page={page}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
        except Exception as e:
            print(f"  [NET ERROR] page {page}: {e}")
            break
        if r.status_code != 200:
            print(f"  [HTTP {r.status_code}] stopping pagination")
            break
        batch = r.json().get("products", [])
        if not batch:
            break
        results.extend(batch)
        print(f"  fetched page {page} ({len(batch)} products, total so far: {len(results)})")
        if len(batch) < 250:
            break
        page += 1
        time.sleep(delay)
    return results[:max_products]


# ── Main ─────────────────────────────────────────────────────────────────────

def _norm(url: str | None) -> str:
    if not url or not isinstance(url, str):
        return ""
    return url.strip().rstrip("/")


def run(stores: list[str], max_per_store: int, delay: float, dry_run: bool) -> None:
    from app.services.carbon_calculator import estimate_carbon, infer_shipping_type

    # Load existing catalog
    existing: list[dict] = []
    if OUTPUT_PATH.exists():
        existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    seen_urls: set[str] = {_norm(p.get("source_url")) for p in existing if p.get("source_url")}
    next_id = max((int(p["id"]) for p in existing), default=0) + 1

    new_products: list[dict] = []
    total_added = 0

    for store_key in stores:
        base_url = SHOPIFY_STORES.get(store_key)
        if not base_url:
            print(f"[SKIP] unknown store: {store_key}")
            continue

        print(f"\n── {store_key} ──────────────────────────────────")

        if dry_run:
            print("  [DRY RUN] skipping network calls")
            continue

        raw_products = _fetch_all_products(base_url, max_per_store, delay)
        print(f"  Processing {len(raw_products)} raw products...")

        added_this_store = 0
        for p in raw_products:
            handle = p.get("handle", "")
            source_url = _norm(f"{base_url}/products/{handle}")

            if source_url in seen_urls:
                continue

            title = (p.get("title") or "").strip()
            if not title:
                continue

            vendor = p.get("vendor") or store_key
            body_html = p.get("body_html") or ""
            product_type = p.get("product_type") or ""
            tags = p.get("tags") or []
            price = _lowest_price(p.get("variants") or [])
            image_url = ""
            if p.get("images"):
                image_url = p["images"][0].get("src", "")

            category = _infer_category(product_type, tags, title, body_html)
            # Skip if we can't categorize (usually irrelevant items)
            if category == "General" and not any(k in title.lower() for k in ["eco", "organic", "recycled", "natural", "sustainable", "bamboo", "hemp"]):
                continue

            material_text = _extract_material(body_html, tags)
            description = _strip_html(body_html)
            shipping_type = infer_shipping_type(vendor + " " + source_url)

            carbon = estimate_carbon(
                category=category,
                title=title,
                material_text=material_text,
                shipping_type=shipping_type,
            )

            item = {
                "id": next_id,
                "name": title,
                "category": category,
                "price": price,
                "material": carbon.material.title(),
                "eco_score": carbon.eco_score,
                "carbon_kg": carbon.total_carbon_kg,
                "esg_rating": carbon.esg_rating,
                "shipping_type": shipping_type.title(),
                "tag": "Eco-Certified",
                "image_url": image_url,
                "description": description,
                "source_url": source_url,
                "carbon_breakdown": json.dumps({
                    "estimated_weight_kg": carbon.estimated_weight_kg,
                    "material_carbon_kg": carbon.material_carbon_kg,
                    "shipping_carbon_kg": carbon.shipping_carbon_kg,
                }),
            }

            new_products.append(item)
            seen_urls.add(source_url)
            next_id += 1
            added_this_store += 1

        print(f"  Added {added_this_store} new products from {store_key}")
        total_added += added_this_store
        time.sleep(delay)

    if dry_run:
        print("\nDry run complete. No files written.")
        return

    if not new_products:
        print("\nNo new products to add.")
        return

    all_products = existing + new_products
    OUTPUT_PATH.write_text(json.dumps(all_products, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print summary by category
    cats: dict[str, int] = {}
    for p in new_products:
        cats[p["category"]] = cats.get(p["category"], 0) + 1

    print(f"\n── Done: added {total_added} products (catalog now has {len(all_products)}) ──")
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {n}")
    print("\nRestart uvicorn to sync with the database.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import eco products from Shopify stores")
    parser.add_argument(
        "--stores",
        nargs="+",
        default=list(SHOPIFY_STORES.keys()),
        choices=list(SHOPIFY_STORES.keys()),
        help="Which stores to scrape (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Max products to fetch per store (default: 500)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds between paginated requests (default: 1.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any requests",
    )
    args = parser.parse_args()
    run(
        stores=args.stores,
        max_per_store=args.limit,
        delay=args.delay,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
