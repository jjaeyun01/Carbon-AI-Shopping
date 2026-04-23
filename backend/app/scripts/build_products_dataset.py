import json
from pathlib import Path

from app.services.carbon_calculator import estimate_carbon, infer_shipping_type
from app.services.product_scraper import scrape_product_page


BASE_DIR = Path(__file__).resolve().parent.parent
URLS_PATH = BASE_DIR / "data" / "product_urls.txt"
OUTPUT_PATH = BASE_DIR / "data" / "products.json"


def build_dataset() -> None:
    if not URLS_PATH.exists():
        raise FileNotFoundError(f"Missing file: {URLS_PATH}")

    urls = [
        line.strip()
        for line in URLS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    results = []

    for idx, url in enumerate(urls, start=1):
        try:
            scraped = scrape_product_page(url)
            shipping_type = infer_shipping_type(scraped.brand + " " + scraped.source_url)

            carbon = estimate_carbon(
                category=scraped.category,
                title=scraped.title,
                material_text=scraped.material_text,
                shipping_type=shipping_type,
            )

            item = {
                "id": idx,
                "name": scraped.title,
                "category": scraped.category,
                "price": scraped.price,
                "material": carbon.material.title(),
                "eco_score": carbon.eco_score,
                "carbon_kg": carbon.total_carbon_kg,
                "esg_rating": carbon.esg_rating,
                "shipping_type": shipping_type.title(),
                "tag": "AI Estimated",
                "image_url": scraped.image_url,
                "description": scraped.description or scraped.raw_text_excerpt[:220],
                "source_url": scraped.source_url,
                "carbon_breakdown": {
                    "estimated_weight_kg": carbon.estimated_weight_kg,
                    "material_carbon_kg": carbon.material_carbon_kg,
                    "shipping_carbon_kg": carbon.shipping_carbon_kg,
                },
            }

            results.append(item)
            print(f"[OK] {scraped.title}")

        except Exception as e:
            print(f"[ERROR] {url} -> {e}")

    OUTPUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {len(results)} products to {OUTPUT_PATH}")


if __name__ == "__main__":
    build_dataset()