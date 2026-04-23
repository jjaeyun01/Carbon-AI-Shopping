import json
import re
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


@dataclass
class ScrapedProduct:
    source_url: str
    brand: str
    title: str
    price: float
    image_url: str
    description: str
    material_text: str
    category: str
    raw_text_excerpt: str


BRAND_MAP = {
    "amazon": "Amazon",
    "ikea": "IKEA",
    "patagonia": "Patagonia",
    "rei": "REI",
    "everlane": "Everlane",
    "amazon": "Amazon",
    "target": "Target",
    "walmart": "Walmart",
    "wayfair": "Wayfair",
    "zara": "Zara",
    "hm": "H&M",
    "uniqlo": "Uniqlo",
    "gap": "Gap",
    "nordstrom": "Nordstrom",
    "macys": "Macy's",
    "etsy": "Etsy",
    "pranaclothing": "Prana",
    "allbirds": "Allbirds",
    "tentree": "Tentree",
    "outerknown": "Outerknown",
    "thirdlove": "ThirdLove",
    "brooklinen": "Brooklinen",
}


def detect_brand_from_url(url: str) -> str:
    netloc = urlparse(url).netloc.lower().replace("www.", "")
    for key, brand in BRAND_MAP.items():
        if key in netloc:
            return brand
    parts = netloc.split(".")
    return parts[0].capitalize() if parts else netloc


def infer_category(title: str, description: str) -> str:
    text = f"{title} {description}".lower()

    if any(k in text for k in ["desk", "chair", "table", "sofa", "shelf", "bookcase", "dresser", "cabinet", "wardrobe"]):
        return "Furniture"
    if any(k in text for k in ["shirt", "tee", "t-shirt", "jacket", "hoodie", "pants", "dress", "sweater", "sweatshirt", "legging", "shorts", "skirt", "sock", "sneaker", "shoe", "boot"]):
        return "Clothing"
    if any(k in text for k in ["bag", "backpack", "pack", "tote", "purse", "handbag", "clutch", "duffel"]):
        return "Bags"
    if any(k in text for k in ["watch", "cap", "hat", "wallet", "belt", "sunglasses", "jewelry", "bracelet", "ring", "necklace"]):
        return "Accessories"
    if any(k in text for k in ["laptop", "stand", "keyboard", "mouse", "monitor", "cable", "charger", "phone", "tablet", "speaker", "headphone", "earphone"]):
        return "Tech"

    return "General"


def extract_json_ld(soup: BeautifulSoup) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        if not tag.string:
            continue
        try:
            parsed = json.loads(tag.string)
            if isinstance(parsed, list):
                results.extend([x for x in parsed if isinstance(x, dict)])
            elif isinstance(parsed, dict):
                results.append(parsed)
        except Exception:
            continue
    return results


def absolutize_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    if u.startswith("//"):
        return f"https:{u}"
    return u


def pick_image_from_json_ld(product_json: dict[str, Any]) -> str:
    """Resolve schema.org Product image which may be str, list, or ImageObject dict."""
    image_val = product_json.get("image")
    if isinstance(image_val, str):
        return absolutize_url(image_val)
    if isinstance(image_val, list) and image_val:
        first = image_val[0]
        if isinstance(first, str):
            return absolutize_url(first)
        if isinstance(first, dict):
            u = first.get("url") or first.get("contentUrl")
            if isinstance(u, str):
                return absolutize_url(u)
            if isinstance(u, list) and u and isinstance(u[0], str):
                return absolutize_url(u[0])
    if isinstance(image_val, dict):
        u = image_val.get("url") or image_val.get("contentUrl")
        if isinstance(u, str):
            return absolutize_url(u)
    return ""


def find_product_json_ld(items: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    for item in items:
        item_type = item.get("@type")
        if item_type == "Product":
            return item
        if isinstance(item_type, list) and "Product" in item_type:
            return item
    return None


def extract_price_from_text(text: str) -> float:
    match = re.search(r"\$?\s?(\d+(?:\.\d{1,2})?)", text.replace(",", ""))
    if match:
        return float(match.group(1))
    return 0.0


def extract_material_text(full_text: str) -> str:
    lowered = full_text.lower()

    patterns = [
        r"(materials?:\s*[^\n\.]+)",
        r"(made from\s+[^\n\.]+)",
        r"(fabric:\s*[^\n\.]+)",
        r"(shell:\s*[^\n\.]+)",
        r"(composition:\s*[^\n\.]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return match.group(1)

    material_keywords = [
        "cotton",
        "organic cotton",
        "recycled cotton",
        "polyester",
        "recycled polyester",
        "linen",
        "wool",
        "bamboo",
        "wood",
        "reclaimed wood",
        "mdf",
        "particleboard",
        "plastic",
        "metal",
        "steel",
        "aluminum",
        "nylon",
        "recycled nylon",
        "plant fiber",
    ]

    found = [kw for kw in material_keywords if kw in lowered]
    if found:
        return ", ".join(found)

    return "unknown"


def scrape_product_page(url: str) -> ScrapedProduct:
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    excerpt = page_text[:1200]

    brand = detect_brand_from_url(url)

    json_ld_items = extract_json_ld(soup)
    product_json = find_product_json_ld(json_ld_items)

    title = ""
    price = 0.0
    image_url = ""
    description = ""

    if product_json:
        title = product_json.get("name", "") or ""
        description = product_json.get("description", "") or ""

        image_url = pick_image_from_json_ld(product_json)

        offers = product_json.get("offers")
        if isinstance(offers, dict):
            price_str = str(offers.get("price", "")).strip()
            if price_str:
                try:
                    price = float(price_str)
                except ValueError:
                    price = 0.0

    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else "Unknown Product"

    if not description:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"].strip()

    if not image_url:
        og_image = soup.find("meta", attrs={"property": "og:image"})
        if og_image and og_image.get("content"):
            image_url = absolutize_url(og_image["content"].strip())

    netloc = urlparse(url).netloc.lower()
    if not image_url and "amazon." in netloc:
        landing = soup.select_one("#landingImage, #imgBlkFront, #main-image")
        if landing and landing.get("src"):
            image_url = absolutize_url(landing["src"].strip())
        if not image_url:
            hi_res = soup.select_one("#landingImage[data-a-dynamic-image]")
            raw = hi_res.get("data-a-dynamic-image") if hi_res else None
            if raw:
                try:
                    dyn = json.loads(raw)
                    if isinstance(dyn, dict) and dyn:
                        image_url = absolutize_url(next(iter(dyn.keys())))
                except (json.JSONDecodeError, StopIteration):
                    pass

    if price == 0.0:
        price = extract_price_from_text(page_text)

    material_text = extract_material_text(page_text)
    category = infer_category(title, description)

    return ScrapedProduct(
        source_url=url,
        brand=brand,
        title=title,
        price=price,
        image_url=image_url,
        description=description,
        material_text=material_text,
        category=category,
        raw_text_excerpt=excerpt,
    )