import re
from dataclasses import dataclass


@dataclass
class CarbonResult:
    material: str
    estimated_weight_kg: float
    material_carbon_kg: float
    shipping_carbon_kg: float
    total_carbon_kg: float
    eco_score: int
    esg_rating: str


# 대략적인 relative carbon factors (kg CO2e per kg material)
# 정확한 LCA 값이 아니라 포트폴리오용 상대 비교 모델
MATERIAL_FACTORS = {
    "cotton": 5.0,
    "organic cotton": 3.5,
    "recycled cotton": 2.5,
    "polyester": 9.0,
    "recycled polyester": 4.5,
    "linen": 2.8,
    "organic linen": 2.2,
    "wool": 12.0,
    "merino wool": 9.0,
    "recycled wool": 5.5,
    "bamboo": 2.2,
    "wood": 2.0,
    "reclaimed wood": 1.2,
    "mdf": 3.8,
    "particleboard": 4.0,
    "plastic": 6.5,
    "metal": 7.5,
    "steel": 6.8,
    "aluminum": 11.0,
    "nylon": 8.5,
    "recycled nylon": 4.2,
    "plant fiber": 2.0,
    "hemp": 1.5,
    "cork": 1.0,
    "glass": 3.0,
    "silicone": 4.0,
    "tencel": 2.5,
    "eucalyptus fiber": 2.5,
    "unknown": 5.5,
}

SHIPPING_FACTORS = {
    "local": 0.2,
    "regional": 0.6,
    "international": 1.6,
}


def normalize_material(raw_text: str) -> str:
    text = raw_text.lower().strip()

    candidates = [
        "organic cotton",
        "recycled cotton",
        "recycled polyester",
        "reclaimed wood",
        "recycled nylon",
        "recycled wool",
        "merino wool",
        "organic linen",
        "eucalyptus fiber",
        "plant fiber",
        "particleboard",
        "polyester",
        "aluminum",
        "silicone",
        "tencel",
        "plastic",
        "cotton",
        "bamboo",
        "linen",
        "nylon",
        "steel",
        "metal",
        "glass",
        "cork",
        "hemp",
        "wool",
        "wood",
        "mdf",
    ]

    for material in candidates:
        if material in text:
            return material

    return "unknown"


def infer_weight_kg(category: str, title: str, material: str) -> float:
    """
    아주 러프한 무게 추정.
    실제 무게 데이터가 없을 때 relative comparison용.
    """
    c = category.lower()
    t = title.lower()

    if c == "clothing":
        if "jacket" in t or "hoodie" in t:
            return 0.8
        if "shirt" in t or "button-down" in t:
            return 0.35
        if "tee" in t or "t-shirt" in t:
            return 0.25
        return 0.4

    if c == "bags":
        return 0.9

    if c == "accessories":
        if "watch" in t:
            return 0.15
        return 0.2

    if c == "tech":
        return 0.3

    if c == "furniture":
        if "desk" in t:
            return 18.0
        if "chair" in t:
            return 8.0
        if "table" in t:
            return 14.0
        return 10.0

    # material heuristic fallback
    if material in {"wood", "reclaimed wood", "mdf", "particleboard"}:
        return 10.0

    return 1.0


def infer_shipping_type(brand_or_url: str) -> str:
    text = brand_or_url.lower()

    if any(x in text for x in ["ikea", "patagonia", "rei", "everlane"]):
        return "regional"

    return "international"


def calculate_esg_rating(total_carbon_kg: float) -> str:
    if total_carbon_kg <= 1.0:
        return "AAA"
    if total_carbon_kg <= 2.0:
        return "AA"
    if total_carbon_kg <= 3.0:
        return "A"
    if total_carbon_kg <= 5.0:
        return "B+"
    if total_carbon_kg <= 7.0:
        return "B"
    if total_carbon_kg <= 10.0:
        return "C"
    return "C-"


def calculate_eco_score(total_carbon_kg: float) -> int:
    """
    낮을수록 친환경.
    0~100 범위로 clamp.
    """
    raw = round(total_carbon_kg * 10)
    return max(1, min(raw, 100))


def estimate_carbon(
    *,
    category: str,
    title: str,
    material_text: str,
    shipping_type: str,
) -> CarbonResult:
    material = normalize_material(material_text)
    weight = infer_weight_kg(category, title, material)

    material_factor = MATERIAL_FACTORS.get(material, MATERIAL_FACTORS["unknown"])
    shipping_factor = SHIPPING_FACTORS.get(shipping_type, SHIPPING_FACTORS["international"])

    material_carbon = round(weight * material_factor, 2)
    shipping_carbon = round(shipping_factor, 2)
    total = round(material_carbon + shipping_carbon, 2)

    eco_score = calculate_eco_score(total)
    esg_rating = calculate_esg_rating(total)

    return CarbonResult(
        material=material,
        estimated_weight_kg=weight,
        material_carbon_kg=material_carbon,
        shipping_carbon_kg=shipping_carbon,
        total_carbon_kg=total,
        eco_score=eco_score,
        esg_rating=esg_rating,
    )