"""
Batch-scrape product URLs and MERGE into data/products.json (by source_url).

- Skips URLs already present (normalized source_url).
- Assigns new ids after max existing id.
- Polite delay between requests (--delay).

Run from repo root:
  cd backend && python -m app.scripts.build_products_dataset
  cd backend && python -m app.scripts.build_products_dataset --dry-run

Then restart the API so sync_products_from_json() picks up new rows.

Do not point this at entire merchant catalogs without permission; use curated URL lists.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from app.services.carbon_calculator import estimate_carbon, infer_shipping_type
from app.services.product_scraper import scrape_product_page


BASE_DIR = Path(__file__).resolve().parent.parent
URLS_PATH = BASE_DIR / "data" / "product_urls.txt"
OUTPUT_PATH = BASE_DIR / "data" / "products.json"


def _norm_source(u: str | None) -> str:
    if not u or not isinstance(u, str):
        return ""
    return u.strip().rstrip("/")


def _load_existing() -> tuple[list[dict], dict[str, int], int]:
    if not OUTPUT_PATH.exists():
        return [], {}, 0
    data = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    seen: dict[str, int] = {}
    for p in data:
        key = _norm_source(p.get("source_url"))
        if key:
            seen[key] = int(p["id"])
    next_id = max((int(p["id"]) for p in data), default=0) + 1
    return data, seen, next_id


def build_dataset(*, delay_s: float, dry_run: bool, timeout: int, url_file: Path | None) -> None:
    path = url_file or URLS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    urls = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    results, seen_urls, next_id = _load_existing()
    initial_count = len(results)

    for url in urls:
        key = _norm_source(url)
        if key and key in seen_urls:
            print(f"[SKIP] already in catalog: {url}")
            continue

        if dry_run:
            print(f"[DRY] would scrape: {url}")
            continue

        try:
            scraped = scrape_product_page(url, timeout=timeout)
            su = _norm_source(scraped.source_url)
            if su and su in seen_urls:
                print(f"[SKIP] duplicate after redirect: {scraped.source_url}")
                continue

            shipping_type = infer_shipping_type(scraped.brand + " " + scraped.source_url)
            carbon = estimate_carbon(
                category=scraped.category,
                title=scraped.title,
                material_text=scraped.material_text,
                shipping_type=shipping_type,
            )

            item = {
                "id": next_id,
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
            if su:
                seen_urls[su] = next_id
            next_id += 1
            print(f"[OK] {scraped.title} (id={item['id']})")

        except Exception as e:
            print(f"[ERROR] {url} -> {e}")

        if delay_s > 0:
            time.sleep(delay_s)

    if dry_run:
        print("\nDry run: no files written.")
        return

    OUTPUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    added = len(results) - initial_count
    print(f"\nWrote {len(results)} products to {OUTPUT_PATH} ({added} new)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge scraped products into products.json")
    parser.add_argument(
        "--urls-file",
        type=Path,
        default=None,
        help=f"Defaults to {URLS_PATH}",
    )
    parser.add_argument("--delay", type=float, default=2.5, help="Seconds between HTTP requests")
    parser.add_argument("--timeout", type=int, default=45, help="Per-request timeout seconds")
    parser.add_argument("--dry-run", action="store_true", help="List URLs only, no network")
    args = parser.parse_args()

    build_dataset(
        delay_s=args.delay,
        dry_run=args.dry_run,
        timeout=args.timeout,
        url_file=args.urls_file,
    )


if __name__ == "__main__":
    main()
