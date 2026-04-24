"""
스크랩 제품의 잘못된 카테고리를 단어 경계(word-boundary) 정규식으로 재분류합니다.

기존 버그: 'bra' → 'bracelet' 매칭, 'coat' → 'coated' 매칭, 'top' → 'laptop' 매칭 등

Usage:
    cd backend && python3 -m app.scripts.fix_categories
    python3 -m app.scripts.fix_categories --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_JSON = BASE_DIR / "data" / "products.json"

# 우선순위 순서로 정의 — 먼저 매칭될수록 우선
# 각 규칙: (category, [regex_patterns])  — 모두 word-boundary 적용
RULES: list[tuple[str, list[str]]] = [
    ("Shoes", [
        r"\b(sneaker|sneakers|shoe|shoes|boot|boots|sandal|sandals|footwear|slipper|loafer|heel|heels|trainer|trainers)\b",
    ]),
    ("Beauty", [
        r"\b(shampoo|conditioner|moisturizer|moisturiser|serum|sunscreen|sunblock|deodorant|toothbrush|toothpaste|skincare|cleanser|toner|mascara|foundation|concealer|blush|eyeshadow|lipstick|lip\s*balm|lip\s*gloss|body\s*wash|face\s*wash|face\s*cream|hair\s*care|face\s*mask|body\s*lotion|body\s*oil|perfume|cologne|nail\s*polish|dry\s*shampoo|castile\s*soap)\b",
    ]),
    ("Accessories", [
        r"\b(wallet|wallets|money\s*clip|belt|belts|watch|watches|sunglasses|jewelry|jewellery|necklace|necklaces|bracelet|bracelets|earring|earrings|anklet|brooch|broaches|ring\b(?!\s*binder)|beanie|beanies|cap\b|caps\b|hat\b|hats\b|scarf|scarves|glove|gloves|phone\s*case|keychain|key\s*chain|clutch\s*purse|coin\s*purse)\b",
    ]),
    ("Fitness", [
        r"\b(yoga\s*mat|exercise\s*mat|gym\s*bag|resistance\s*band|kettlebell|dumbbell|barbell|workout|fitness\s*equipment|foam\s*roller|jump\s*rope|pull[- ]up\s*bar)\b",
    ]),
    ("Home", [
        r"\b(sheet\s*set|duvet|comforter|bedding|pillowcase|pillow\s*case|bath\s*towel|hand\s*towel|throw\s*blanket|blanket\b|mattress|pillow\b|pillows\b|bath\s*rug|area\s*rug|curtain|duvet\s*cover|quilt|bed\s*skirt)\b",
    ]),
    ("Kitchen", [
        r"\b(frying\s*pan|sauce\s*pan|cookware|bento|lunch\s*box|lunchbox|dish\s*soap|cutting\s*board|kitchen\b|utensil|food\s*storage|food\s*wrap|beeswax\s*wrap|silicone\s*bag|reusable\s*wrap|dish\s*brush|produce\s*bag|straw\b(?!\s*hat))\b",
    ]),
    ("Furniture", [
        r"\b(desk\b|desks\b|chair\b|chairs\b|sofa\b|sofas\b|couch\b|shelf\b|shelves\b|bookcase|bookshelf|dresser|bed\s*frame|wardrobe|cabinet|dining\s*table|coffee\s*table|side\s*table|nightstand)\b",
    ]),
    ("Bags", [
        r"\b(backpack|back\s*pack|tote\s*bag|handbag|duffel|duffle|messenger\s*bag|crossbody|cross-body|rucksack|satchel|fanny\s*pack|diaper\s*bag|laptop\s*bag|camera\s*bag|gym\s*bag|travel\s*bag|weekender)\b",
    ]),
    ("Tech", [
        r"\b(laptop\b|keyboard\b|mouse\b|monitor\b|charger\b|charging|usb\s*cable|usb-c|lightning\s*cable|speaker\b|headphone|earphone|earbuds|webcam|laptop\s*stand|monitor\s*stand|phone\s*stand|solar\s*charger)\b",
    ]),
    ("Clothing", [
        r"\b(t-shirt|tee\s*shirt|graphic\s*tee|hoodie|sweatshirt|sweatpants|jogger|legging|leggings|crop\s*top|tank\s*top|sports\s*bra|bikini\s*top|blouse|flannel|denim|jeans|cardigan|pullover|blazer|trench\s*coat|parka|anorak|windbreaker|fleece\s*jacket|down\s*jacket|button-down|button\s*up|polo\s*shirt|dress\b|skirt\b|romper|jumpsuit|bodysuit|underwear|boxers|briefs\b|bralette)\b",
        r"\b(men's|women's|unisex)\s+(t-shirt|shirt|tee|hoodie|pant|jacket|top|dress|shorts|socks)",
    ]),
]


def infer_category(name: str, description: str) -> str | None:
    """정규식 word-boundary로 카테고리 추론. 확실하지 않으면 None 반환."""
    text = f"{name} {description}".lower()
    for category, patterns in RULES:
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return category
    return None


def run(dry_run: bool) -> None:
    products: list[dict] = json.loads(PRODUCTS_JSON.read_text(encoding="utf-8"))

    # 큐레이션 제품(source_url 없음)은 건드리지 않음
    to_fix = [p for p in products if p.get("source_url")]
    curated_count = len(products) - len(to_fix)
    print(f"재분류 대상: {len(to_fix)}개 (큐레이션 {curated_count}개 제외)\n")

    changes: list[tuple[int, str, str, str]] = []  # (id, name, old, new)

    for p in to_fix:
        new_cat = infer_category(p["name"], p.get("description") or "")
        if new_cat and new_cat != p["category"]:
            changes.append((p["id"], p["name"], p["category"], new_cat))

    # 변경 요약
    summary: dict[str, dict[str, int]] = {}
    for _, _, old, new in changes:
        summary.setdefault(old, {}).setdefault(new, 0)
        summary[old][new] += 1

    print(f"총 {len(changes)}개 카테고리 변경:")
    for old_cat, moves in sorted(summary.items()):
        for new_cat, count in sorted(moves.items(), key=lambda x: -x[1]):
            print(f"  {old_cat:12} → {new_cat:12}: {count}개")

    if dry_run:
        print("\n--- 변경 예시 (처음 20개) ---")
        for pid, name, old, new in changes[:20]:
            print(f"  [{pid}] {name[:50]}: {old} → {new}")
        print("\nDry-run. 저장 없이 종료.")
        return

    # 실제 적용
    id_map = {p["id"]: p for p in products}
    for pid, _, _, new_cat in changes:
        id_map[pid]["category"] = new_cat

    PRODUCTS_JSON.write_text(
        json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # 최종 카테고리 분포
    cats: dict[str, int] = {}
    for p in products:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    print("\n적용 후 카테고리 분포:")
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {n}개")

    print(f"\n✓ products.json 저장 완료. 서버 재시작 후 반영됩니다.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="변경 내용만 출력, 저장 안 함")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
