"""
Run once to regenerate backend/app/data/products.json with 150+ curated eco products.

Usage:
    cd backend
    python -m app.scripts.generate_eco_catalog
"""
import json
import sys  # noqa: E402
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.services.carbon_calculator import estimate_carbon

PRODUCTS_JSON = Path(__file__).resolve().parent.parent / "data" / "products.json"

# Each entry: name, brand, category, price, material_text, shipping_type, description
RAW_CATALOG = [
    # ── CLOTHING (25) ───────────────────────────────────────────────────────
    {"name": "Men's P-6 Logo Responsibili-Tee", "brand": "Patagonia", "category": "Clothing", "price": 35.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Classic graphic tee made with 100% organic cotton, certified Fair Trade."},
    {"name": "Men's Capilene Cool Daily Shirt", "brand": "Patagonia", "category": "Clothing", "price": 55.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Ultralight moisture-wicking shirt made from 100% recycled polyester."},
    {"name": "Women's Better Sweater Fleece Jacket", "brand": "Patagonia", "category": "Clothing", "price": 139.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Classic fleece jacket made from 100% recycled polyester fleece."},
    {"name": "Men's Nano Puff Jacket", "brand": "Patagonia", "category": "Clothing", "price": 199.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Ultralight insulation jacket with recycled PrimaLoft Gold fill."},
    {"name": "Men's Classic Cotton T-Shirt", "brand": "Tentree", "category": "Clothing", "price": 38.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Everyday tee in 100% GOTS-certified organic cotton. Plants 10 trees per purchase."},
    {"name": "Women's Organic French Terry Hoodie", "brand": "Tentree", "category": "Clothing", "price": 98.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Relaxed hoodie in 100% organic cotton French terry. Plants 10 trees per purchase."},
    {"name": "Women's Organic Cotton Box-Cut Tee", "brand": "Everlane", "category": "Clothing", "price": 28.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Relaxed boxy tee made with 100% GOTS-certified organic cotton."},
    {"name": "The Straight Organic Jean", "brand": "Everlane", "category": "Clothing", "price": 68.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Classic straight-leg jean in 100% organic cotton denim."},
    {"name": "Organic Cotton Crew Sweatshirt", "brand": "Everlane", "category": "Clothing", "price": 88.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Classic crewneck made with 100% GOTS organic cotton."},
    {"name": "Organic Cotton Basic Tee", "brand": "Organic Basics", "category": "Clothing", "price": 25.00, "material_text": "organic cotton", "shipping_type": "international", "description": "Minimalist essential tee in GOTS-certified organic cotton. Low-impact production."},
    {"name": "Recycled Nylon Sports Bra", "brand": "Organic Basics", "category": "Clothing", "price": 35.00, "material_text": "recycled nylon", "shipping_type": "international", "description": "High-support sports bra made with ECONYL regenerated nylon from ocean waste."},
    {"name": "Paloma Sports Bra", "brand": "Girlfriend Collective", "category": "Clothing", "price": 54.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Made from 79% RPET recycled plastic bottles. Supportive and sustainable."},
    {"name": "High-Rise Bike Short", "brand": "Girlfriend Collective", "category": "Clothing", "price": 68.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Compressive bike short made from 87% recycled plastic bottles."},
    {"name": "Hemp Blend Pant", "brand": "Prana", "category": "Clothing", "price": 85.00, "material_text": "hemp", "shipping_type": "regional", "description": "Versatile everyday pant in hemp and organic cotton blend."},
    {"name": "Men's Hemp Tee", "brand": "Prana", "category": "Clothing", "price": 55.00, "material_text": "hemp", "shipping_type": "regional", "description": "Soft and breathable tee in hemp and organic cotton blend."},
    {"name": "Bamboo Stripe T-Shirt", "brand": "Thought Clothing", "category": "Clothing", "price": 42.00, "material_text": "bamboo", "shipping_type": "international", "description": "Classic striped tee in organic bamboo. Naturally antibacterial and moisture-wicking."},
    {"name": "Fair Trade Organic Cotton Tee", "brand": "People Tree", "category": "Clothing", "price": 38.00, "material_text": "organic cotton", "shipping_type": "international", "description": "100% GOTS organic cotton, certified Fair Trade by artisans in developing countries."},
    {"name": "Organic Cotton Sundress", "brand": "People Tree", "category": "Clothing", "price": 75.00, "material_text": "organic cotton", "shipping_type": "international", "description": "Lightweight summer dress in GOTS-certified organic cotton. Fair Trade certified."},
    {"name": "Organic Linen Wide-Leg Pant", "brand": "Eileen Fisher", "category": "Clothing", "price": 148.00, "material_text": "linen", "shipping_type": "regional", "description": "Relaxed wide-leg pant in breathable organic linen. Timeless and sustainably made."},
    {"name": "Classic Organic Jersey Tee", "brand": "Alternative Apparel", "category": "Clothing", "price": 35.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Super-soft tee made from 100% organic cotton jersey."},
    {"name": "Eco-Fleece Hoodie", "brand": "Alternative Apparel", "category": "Clothing", "price": 72.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Cozy hoodie made from 50% recycled polyester and 46% organic cotton."},
    {"name": "Organic Cotton Jogger Pant", "brand": "Bhumi", "category": "Clothing", "price": 65.00, "material_text": "organic cotton", "shipping_type": "international", "description": "Relaxed jogger pants in GOTS-certified organic cotton."},
    {"name": "Men's S.E.A. Jean", "brand": "Outerknown", "category": "Clothing", "price": 98.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Classic 5-pocket jean in 100% organic cotton. Bluesign-certified denim."},
    {"name": "Swell Flannel Shirt", "brand": "Outerknown", "category": "Clothing", "price": 98.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Comfortable flannel in GOTS-certified organic cotton."},
    {"name": "USA-Made Organic Tee", "brand": "Harvest & Mill", "category": "Clothing", "price": 68.00, "material_text": "organic cotton", "shipping_type": "local", "description": "100% USDA organic cotton grown and sewn in California. Zero-waste production."},

    # ── SHOES (12) ──────────────────────────────────────────────────────────
    {"name": "Men's Tree Runners", "brand": "Allbirds", "category": "Shoes", "price": 110.00, "material_text": "eucalyptus fiber", "shipping_type": "regional", "description": "Lightweight sneaker made from sustainable eucalyptus tree fiber. Carbon neutral."},
    {"name": "Women's Wool Runners", "brand": "Allbirds", "category": "Shoes", "price": 120.00, "material_text": "merino wool", "shipping_type": "regional", "description": "The original Allbirds sneaker in ZQ-certified merino wool."},
    {"name": "Men's Tree Dasher 2", "brand": "Allbirds", "category": "Shoes", "price": 125.00, "material_text": "eucalyptus fiber", "shipping_type": "regional", "description": "Running shoe in sustainable eucalyptus tree fiber. Certified carbon neutral."},
    {"name": "V-10 Organic Cotton Sneaker", "brand": "Veja", "category": "Shoes", "price": 150.00, "material_text": "organic cotton", "shipping_type": "international", "description": "Iconic sneaker in organic cotton canvas with wild rubber from the Amazon."},
    {"name": "Campo Chromefree Sneaker", "brand": "Veja", "category": "Shoes", "price": 160.00, "material_text": "recycled polyester", "shipping_type": "international", "description": "Clean leather-free sneaker made from B-mesh recycled plastic bottles."},
    {"name": "OCA Low Canvas Sneaker", "brand": "Cariuma", "category": "Shoes", "price": 79.00, "material_text": "bamboo", "shipping_type": "international", "description": "Low-top canvas sneaker in bamboo and sugarcane. Carbon negative."},
    {"name": "IBI High Knit Sneaker", "brand": "Cariuma", "category": "Shoes", "price": 169.00, "material_text": "recycled polyester", "shipping_type": "international", "description": "High-top knit sneaker in recycled polyester yarn. Carbon negative."},
    {"name": "Recycled Women's Lace-Up Sneaker", "brand": "Nothing New", "category": "Shoes", "price": 145.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Classic sneaker made from 100% recycled materials including bottles and fishing nets."},
    {"name": "Men's Classic Recycled Sneaker", "brand": "Nothing New", "category": "Shoes", "price": 149.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Timeless sneaker in recycled plastic bottles and natural rubber."},
    {"name": "Nile Organic Canvas Sneaker", "brand": "Po-Zu", "category": "Shoes", "price": 110.00, "material_text": "organic cotton", "shipping_type": "international", "description": "Everyday sneaker with organic cotton, natural rubber and coconut husk midsole."},
    {"name": "Pinatex Vegan Chelsea Boot", "brand": "Po-Zu", "category": "Shoes", "price": 145.00, "material_text": "plant fiber", "shipping_type": "international", "description": "Classic chelsea boot in Pinatex pineapple leaf fiber. Vegan and sustainable."},
    {"name": "Go-To Slip-On Sneaker", "brand": "Nisolo", "category": "Shoes", "price": 128.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Versatile leather-free sneaker in a Climate Neutral certified supply chain."},

    # ── BAGS (12) ───────────────────────────────────────────────────────────
    {"name": "Black Hole Pack 32L", "brand": "Patagonia", "category": "Bags", "price": 130.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Durable daypack in 100% recycled polyester body fabric. Bluesign approved."},
    {"name": "Fieldsmith Lid Pack 28L", "brand": "Patagonia", "category": "Bags", "price": 119.00, "material_text": "recycled nylon", "shipping_type": "regional", "description": "Versatile commuter pack in 100% recycled nylon ripstop."},
    {"name": "Kanken Classic Backpack", "brand": "Fjallraven", "category": "Bags", "price": 80.00, "material_text": "recycled polyester", "shipping_type": "international", "description": "Iconic Swedish backpack in Vinylon F water-resistant material."},
    {"name": "Standard Reusable Tote", "brand": "BAGGU", "category": "Bags", "price": 16.00, "material_text": "recycled nylon", "shipping_type": "regional", "description": "Packable reusable tote bag made from 40% recycled ripstop nylon."},
    {"name": "Classic Messenger Bag", "brand": "Timbuk2", "category": "Bags", "price": 89.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Iconic messenger bag in recycled TPU coated fabric. Made in San Francisco."},
    {"name": "Allpa 42L Travel Pack", "brand": "Cotopaxi", "category": "Bags", "price": 210.00, "material_text": "recycled nylon", "shipping_type": "regional", "description": "Durable travel pack in 100% recycled nylon. Repurposed fabric design."},
    {"name": "Vegan Leather Tote", "brand": "Matt & Nat", "category": "Bags", "price": 145.00, "material_text": "recycled polyester", "shipping_type": "international", "description": "Stylish vegan tote. Lining made from 100% recycled plastic bottles."},
    {"name": "Waterproof Recycled Rucksack", "brand": "Rains", "category": "Bags", "price": 90.00, "material_text": "recycled polyester", "shipping_type": "international", "description": "Minimalist waterproof backpack in recycled polyester."},
    {"name": "Recycled Duffel Bag 45L", "brand": "Patagonia", "category": "Bags", "price": 99.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Versatile duffel in 100% recycled polyester. Bluesign approved."},
    {"name": "Organic Cotton Market Tote", "brand": "Tentree", "category": "Bags", "price": 28.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Simple and spacious market tote in 100% organic cotton canvas."},
    {"name": "Hemp Canvas Shoulder Bag", "brand": "Rawganique", "category": "Bags", "price": 75.00, "material_text": "hemp", "shipping_type": "international", "description": "Durable shoulder bag in 100% organic hemp canvas. Chemical-free."},
    {"name": "Recycled Plastic Crossbody Bag", "brand": "Patagonia", "category": "Bags", "price": 69.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Compact crossbody bag made from 100% recycled polyester ripstop."},

    # ── ACCESSORIES (12) ────────────────────────────────────────────────────
    {"name": "Organic Cotton Toque Beanie", "brand": "Tentree", "category": "Accessories", "price": 28.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Classic winter beanie in 100% organic cotton. Plants 10 trees per purchase."},
    {"name": "Recycled Wool Cap", "brand": "Patagonia", "category": "Accessories", "price": 38.00, "material_text": "recycled wool", "shipping_type": "regional", "description": "Classic beanie in recycled wool yarn. Bluesign approved."},
    {"name": "Compostable iPhone Case", "brand": "Pela", "category": "Accessories", "price": 49.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "100% compostable phone case in flax shive and biopolymers. Climate neutral."},
    {"name": "Classic Insulated Water Bottle 20oz", "brand": "Klean Kanteen", "category": "Accessories", "price": 35.00, "material_text": "metal", "shipping_type": "regional", "description": "Stainless steel insulated bottle. BPA-free, reusable, made to last a lifetime."},
    {"name": "Triple-Insulated Water Bottle 17oz", "brand": "S'well", "category": "Accessories", "price": 35.00, "material_text": "metal", "shipping_type": "regional", "description": "Triple-insulated stainless steel bottle. Cold 24h, hot 12h."},
    {"name": "Natural Cork Slim Wallet", "brand": "Corkor", "category": "Accessories", "price": 45.00, "material_text": "cork", "shipping_type": "international", "description": "Minimalist wallet in natural cork. Vegan, sustainable, water-resistant."},
    {"name": "Organic Hemp Bifold Wallet", "brand": "Rawganique", "category": "Accessories", "price": 35.00, "material_text": "hemp", "shipping_type": "international", "description": "Durable wallet in organic hemp canvas. No chemicals, no plastic."},
    {"name": "Ocean Plastic Sunglasses", "brand": "Sea2See", "category": "Accessories", "price": 89.00, "material_text": "recycled polyester", "shipping_type": "international", "description": "Frames made from 100% recycled marine plastic collected from oceans."},
    {"name": "Solar-Powered Swiss Watch", "brand": "Solios", "category": "Accessories", "price": 195.00, "material_text": "metal", "shipping_type": "international", "description": "Swiss-made solar watch with sapphire crystal. Carbon neutral, no battery waste."},
    {"name": "Recycled Rubber Webbing Belt", "brand": "Alchemy Goods", "category": "Accessories", "price": 38.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Durable belt made from recycled inner tubes and seat belts."},
    {"name": "Organic Cotton Headband Set 2pk", "brand": "Girlfriend Collective", "category": "Accessories", "price": 18.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Set of 2 headbands in organic cotton and recycled elastane."},
    {"name": "Bamboo Fiber Sun Hat", "brand": "Thought Clothing", "category": "Accessories", "price": 32.00, "material_text": "bamboo", "shipping_type": "international", "description": "Breathable hat in organic bamboo fiber. UPF 50+ sun protection."},

    # ── FURNITURE (12) ──────────────────────────────────────────────────────
    {"name": "BILLY Bookcase White", "brand": "IKEA", "category": "Furniture", "price": 69.99, "material_text": "particleboard", "shipping_type": "regional", "description": "Classic bookcase in FSC-certified particleboard with wood veneer."},
    {"name": "NORDLI 6-Drawer Chest", "brand": "IKEA", "category": "Furniture", "price": 299.00, "material_text": "particleboard", "shipping_type": "regional", "description": "Modern drawer chest in FSC-certified particleboard. Modular design."},
    {"name": "KALLAX 4x2 Shelf Unit", "brand": "IKEA", "category": "Furniture", "price": 139.00, "material_text": "particleboard", "shipping_type": "regional", "description": "Versatile shelf unit in particleboard. Holds up to 29 lbs per compartment."},
    {"name": "MICKE Study Desk", "brand": "IKEA", "category": "Furniture", "price": 89.99, "material_text": "particleboard", "shipping_type": "regional", "description": "Compact desk in FSC-certified particleboard with honeycomb paper fill."},
    {"name": "The Bed Frame - Queen", "brand": "Floyd", "category": "Furniture", "price": 595.00, "material_text": "wood", "shipping_type": "regional", "description": "Simple bed frame in FSC-certified birch plywood. Designed to last a lifetime."},
    {"name": "The Platform Bed - Queen", "brand": "Floyd", "category": "Furniture", "price": 1295.00, "material_text": "reclaimed wood", "shipping_type": "regional", "description": "Low-profile platform bed in sustainable birch plywood. Tool-free assembly."},
    {"name": "Bank 2-Seat Sofa", "brand": "Burrow", "category": "Furniture", "price": 1295.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Modular sofa with FSC-certified hardwood frame. Kiln-dried for lasting strength."},
    {"name": "Essential 3-Seat Sofa", "brand": "Sabai", "category": "Furniture", "price": 1495.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Sofa made from recycled plastic bottles. Climate Pledge Friendly certified."},
    {"name": "Oslo Lounge Chair", "brand": "Medley", "category": "Furniture", "price": 895.00, "material_text": "wood", "shipping_type": "regional", "description": "Handcrafted chair with solid wood frame and GOTS organic upholstery."},
    {"name": "Reclaimed Wood Dining Table", "brand": "Great Lakes Woodworking", "category": "Furniture", "price": 899.00, "material_text": "reclaimed wood", "shipping_type": "local", "description": "Hand-crafted dining table from reclaimed barn wood. One-of-a-kind."},
    {"name": "Bamboo Height-Adjustable Desk", "brand": "FlexiSpot", "category": "Furniture", "price": 599.00, "material_text": "bamboo", "shipping_type": "regional", "description": "Electric standing desk with bamboo desktop. Adjustable 27-47 inches."},
    {"name": "Slope Lounge Chair", "brand": "Burrow", "category": "Furniture", "price": 695.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Modern chair with FSC-certified hardwood frame and recycled upholstery."},

    # ── HOME (14) ───────────────────────────────────────────────────────────
    {"name": "Organic Jersey Sheet Set - Full", "brand": "Coyuchi", "category": "Home", "price": 185.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Ultra-soft jersey sheets in 100% GOTS-certified organic cotton."},
    {"name": "Organic Waffle Bath Towel", "brand": "Coyuchi", "category": "Home", "price": 28.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Lightweight waffle-weave towel in 100% organic cotton. Quick-drying."},
    {"name": "Signature Hemmed Sheet Set - Queen", "brand": "Boll & Branch", "category": "Home", "price": 290.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Buttery-soft sheets in 100% Fair Trade Certified organic cotton."},
    {"name": "Cloud Recycled Comforter", "brand": "Buffy", "category": "Home", "price": 175.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Ultra-soft comforter filled with 100% recycled plastic bottles."},
    {"name": "Organic Mattress Protector - Queen", "brand": "Avocado", "category": "Home", "price": 99.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Waterproof mattress protector in organic cotton with natural wool filling."},
    {"name": "Linen Core Sheet Set - Queen", "brand": "Brooklinen", "category": "Home", "price": 235.00, "material_text": "linen", "shipping_type": "regional", "description": "100% European linen sheets. Gets softer with every wash. OEKO-TEX certified."},
    {"name": "Bamboo Lyocell Sheet Set - Queen", "brand": "Ettitude", "category": "Home", "price": 155.00, "material_text": "bamboo", "shipping_type": "regional", "description": "Ultra-soft sheets in 100% organic bamboo lyocell. Naturally cooling."},
    {"name": "Organic Cotton Bath Towel", "brand": "Pact", "category": "Home", "price": 28.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Plush bath towel in 100% GOTS-certified organic cotton."},
    {"name": "Organic Sateen Sheet Set - King", "brand": "Parachute", "category": "Home", "price": 189.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Classic sateen sheets in 100% GOTS-certified long-staple organic cotton."},
    {"name": "French Linen Pillowcase", "brand": "West Elm", "category": "Home", "price": 29.00, "material_text": "linen", "shipping_type": "regional", "description": "Relaxed linen pillowcase from ethically sourced European flax."},
    {"name": "Organic Cotton Blanket", "brand": "SOL Organics", "category": "Home", "price": 98.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Cozy blanket in 100% GOTS-certified organic cotton. OEKO-TEX 100."},
    {"name": "Hemp Pillow Case Set", "brand": "Rawganique", "category": "Home", "price": 35.00, "material_text": "hemp", "shipping_type": "international", "description": "Pillowcases in 100% organic hemp. No chemicals, pesticide-free."},
    {"name": "Recycled Fleece Throw Blanket", "brand": "Patagonia", "category": "Home", "price": 119.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Soft throw in 100% recycled fleece. Bluesign certified."},
    {"name": "Organic Wool Duvet Insert", "brand": "Avocado", "category": "Home", "price": 349.00, "material_text": "wool", "shipping_type": "regional", "description": "Cozy duvet with 100% GOTS-certified organic wool fill. Temperature-regulating."},

    # ── KITCHEN (15) ────────────────────────────────────────────────────────
    {"name": "Multi-Surface Starter Kit", "brand": "Blueland", "category": "Kitchen", "price": 39.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Refillable cleaning kit with reusable bottles and dissolvable plant-based tablets."},
    {"name": "Glass Cleaner Concentrate", "brand": "Grove", "category": "Kitchen", "price": 8.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Plant-based glass cleaner concentrate. Dilute with water, eliminates plastic waste."},
    {"name": "Silicone Reusable Sandwich Bags 4pk", "brand": "Stasher", "category": "Kitchen", "price": 33.00, "material_text": "silicone", "shipping_type": "regional", "description": "Reusable silicone bags replacing plastic zip bags. Dishwasher and microwave safe."},
    {"name": "Beeswax Wrap Variety Pack", "brand": "Bee's Wrap", "category": "Kitchen", "price": 22.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Plastic-free food wrap in organic cotton, beeswax, jojoba oil and tree resin."},
    {"name": "Stainless Steel Bento Box 3-Tier", "brand": "ECOlunchbox", "category": "Kitchen", "price": 28.00, "material_text": "metal", "shipping_type": "regional", "description": "Stainless steel lunchbox with no plastic. Leak-proof and durable."},
    {"name": "Ceramic Nonstick Fry Pan 10in", "brand": "GreenPan", "category": "Kitchen", "price": 40.00, "material_text": "metal", "shipping_type": "regional", "description": "Ceramic-coated pan. Free of PFAS, PFOA, lead and cadmium."},
    {"name": "Organic Bamboo Cutting Board", "brand": "Bambu", "category": "Kitchen", "price": 32.00, "material_text": "bamboo", "shipping_type": "regional", "description": "Cutting board in certified organic bamboo. Harder than wood, antimicrobial."},
    {"name": "Plant-Based Dish Soap Refill", "brand": "Common Good", "category": "Kitchen", "price": 9.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Concentrated dish soap in plant-based ingredients. Plastic-free packaging."},
    {"name": "Bamboo Dish Brush Set", "brand": "Full Circle", "category": "Kitchen", "price": 10.00, "material_text": "bamboo", "shipping_type": "regional", "description": "Kitchen brush with bamboo handle and plant-based bristles. Compostable."},
    {"name": "Plant-Based Dish Soap", "brand": "Method", "category": "Kitchen", "price": 4.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Plant-based dish soap in 100% recycled plastic bottle. Biodegradable formula."},
    {"name": "Borosilicate Glass Food Storage Set", "brand": "Pyrex", "category": "Kitchen", "price": 55.00, "material_text": "glass", "shipping_type": "regional", "description": "Glass containers with BPA-free lids. Replaces plastic food storage."},
    {"name": "Stainless Steel Coffee Filter", "brand": "Goldtone", "category": "Kitchen", "price": 8.00, "material_text": "metal", "shipping_type": "regional", "description": "Reusable mesh filter. Eliminates paper filter waste. 1 filter = 1000+ uses."},
    {"name": "Coconut Fiber Kitchen Scrubber", "brand": "EcoTools", "category": "Kitchen", "price": 8.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Kitchen scrub brush with coconut fiber bristles and FSC-certified wood handle."},
    {"name": "Beeswax Food Wrap Set", "brand": "Etee", "category": "Kitchen", "price": 26.00, "material_text": "organic cotton", "shipping_type": "regional", "description": "Handmade food wraps in organic cotton, beeswax and natural pine resin."},
    {"name": "Compostable Parchment Bags", "brand": "If You Care", "category": "Kitchen", "price": 5.00, "material_text": "plant fiber", "shipping_type": "international", "description": "Unbleached chlorine-free parchment bags. Certified compostable."},

    # ── BEAUTY (14) ─────────────────────────────────────────────────────────
    {"name": "Solid Shampoo Bar - Mintasy", "brand": "Ethique", "category": "Beauty", "price": 15.00, "material_text": "plant fiber", "shipping_type": "international", "description": "Solid shampoo bar equivalent to 3 plastic bottles. 100% compostable packaging."},
    {"name": "Solid Conditioner Bar", "brand": "Ethique", "category": "Beauty", "price": 15.00, "material_text": "plant fiber", "shipping_type": "international", "description": "Solid conditioner bar replacing 2-3 plastic conditioner bottles."},
    {"name": "Pure Castile Soap 32oz", "brand": "Dr. Bronner's", "category": "Beauty", "price": 17.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Organic fair-trade multi-purpose Castile soap. Use for body, hair, and cleaning."},
    {"name": "Natural Gentle Face Wash", "brand": "Ursa Major", "category": "Beauty", "price": 26.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Natural face wash with aloe vera and green tea. Free of synthetic chemicals."},
    {"name": "Biodegradable Face Wipes", "brand": "Ursa Major", "category": "Beauty", "price": 24.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Biodegradable face wipes with natural clean ingredients. No synthetics."},
    {"name": "Activated Charcoal Face Soap", "brand": "Meow Meow Tweet", "category": "Beauty", "price": 16.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Vegan face soap with activated charcoal. Minimal plastic-free packaging."},
    {"name": "Rosewater Moisture Cream", "brand": "Herbivore", "category": "Beauty", "price": 54.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Lightweight moisturizer with rosewater and coconut water. Natural and cruelty-free."},
    {"name": "Natural Coconut + Vanilla Deodorant", "brand": "Each & Every", "category": "Beauty", "price": 14.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Clean deodorant with plant-based ingredients. Aluminum-free, recyclable packaging."},
    {"name": "Charcoal Magnesium Deodorant", "brand": "Schmidt's", "category": "Beauty", "price": 10.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Plant-based deodorant with activated charcoal. Certified natural ingredients."},
    {"name": "Mineral SPF 40 Sport Sunscreen", "brand": "Badger", "category": "Beauty", "price": 18.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Mineral sunscreen with certified organic ingredients. Reef and ocean safe."},
    {"name": "Zero Waste Solid Lip Balm", "brand": "Ethique", "category": "Beauty", "price": 9.00, "material_text": "plant fiber", "shipping_type": "international", "description": "Solid lip balm in compostable packaging. Replaces 5 plastic tubes."},
    {"name": "Bamboo Charcoal Toothbrush 4pk", "brand": "Brush with Bamboo", "category": "Beauty", "price": 12.00, "material_text": "bamboo", "shipping_type": "regional", "description": "Toothbrush with bamboo handle and bio-based nylon bristles. Compostable handle."},
    {"name": "Refillable Solid Moisturizer", "brand": "Attitude", "category": "Beauty", "price": 18.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Concentrated solid face moisturizer in refillable aluminum tin. Zero plastic waste."},
    {"name": "Natural Clay Dry Shampoo", "brand": "Primally Pure", "category": "Beauty", "price": 22.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Dry shampoo in organic arrowroot and clay. No aerosols, compostable packaging."},

    # ── FITNESS (10) ────────────────────────────────────────────────────────
    {"name": "PRO Yoga Mat 6mm", "brand": "Manduka", "category": "Fitness", "price": 120.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Professional-grade yoga mat. PVC-free materials with a lifetime guarantee."},
    {"name": "PROlite Yoga Mat 4mm", "brand": "Manduka", "category": "Fitness", "price": 80.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Lightweight performance yoga mat with closed-cell surface."},
    {"name": "Harmony Natural Rubber Yoga Mat", "brand": "Jade Yoga", "category": "Fitness", "price": 80.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "Natural rubber yoga mat. Plants a tree with every mat sold."},
    {"name": "Alignment Yoga Mat", "brand": "Liforme", "category": "Fitness", "price": 150.00, "material_text": "plant fiber", "shipping_type": "international", "description": "Eco-polyurethane yoga mat with alignment markings. Biodegradable natural rubber base."},
    {"name": "Wide-Mouth Insulated Bottle 32oz", "brand": "Hydroflask", "category": "Fitness", "price": 45.00, "material_text": "metal", "shipping_type": "regional", "description": "Insulated stainless steel bottle. TempShield keeps drinks cold 24h."},
    {"name": "Organic Sports Tank", "brand": "Patagonia", "category": "Fitness", "price": 45.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Lightweight sports tank in recycled polyester and organic cotton blend."},
    {"name": "Compressive High-Rise Legging", "brand": "Girlfriend Collective", "category": "Fitness", "price": 88.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "High-performance legging from recycled plastic bottles. 79% RPET."},
    {"name": "Natural Latex Resistance Band Set", "brand": "MOUS", "category": "Fitness", "price": 30.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "5 resistance bands in natural latex rubber. Compostable packaging."},
    {"name": "Cork Yoga Block 2pk", "brand": "Hugger Mugger", "category": "Fitness", "price": 28.00, "material_text": "cork", "shipping_type": "regional", "description": "Yoga blocks in natural cork. Antimicrobial, sustainable, and firm support."},
    {"name": "Recycled Gym Bag 22L", "brand": "Patagonia", "category": "Fitness", "price": 75.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Packable gym bag in 100% recycled polyester. 22L capacity."},

    # ── TECH (8) ────────────────────────────────────────────────────────────
    {"name": "Compostable iPhone 15 Case", "brand": "Pela", "category": "Tech", "price": 49.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "100% compostable case in flax shive and biopolymers. Carbon neutral."},
    {"name": "Compostable Samsung Galaxy Case", "brand": "Pela", "category": "Tech", "price": 49.00, "material_text": "plant fiber", "shipping_type": "regional", "description": "100% compostable Galaxy case in flax shive and biopolymers. Carbon neutral."},
    {"name": "Recycled Plastic 30W Fast Charger", "brand": "Nimble", "category": "Tech", "price": 35.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "USB-C fast charger in 50% recycled plastic housing. B Corp certified."},
    {"name": "Recycled Braided USB-C Cable 6ft", "brand": "Nimble", "category": "Tech", "price": 20.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Durable USB-C cable with casing from 70% recycled plastic."},
    {"name": "Bamboo Ergonomic Laptop Stand", "brand": "Bureo", "category": "Tech", "price": 45.00, "material_text": "bamboo", "shipping_type": "regional", "description": "Ergonomic laptop stand in reclaimed bamboo. Adjustable angles."},
    {"name": "Recycled Wireless Keyboard and Mouse", "brand": "Logitech", "category": "Tech", "price": 69.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Wireless peripherals in certified post-consumer recycled plastic."},
    {"name": "Solar Portable Charging Bank", "brand": "Goal Zero", "category": "Tech", "price": 59.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Portable solar panel and power bank. Charge devices with clean solar energy."},
    {"name": "Recycled Plastic Monitor Stand", "brand": "Fellowes", "category": "Tech", "price": 55.00, "material_text": "recycled polyester", "shipping_type": "regional", "description": "Monitor riser in 100% recycled plastic with built-in cable management."},
]


def generate() -> None:
    products = []
    for idx, raw in enumerate(RAW_CATALOG, start=1):
        carbon = estimate_carbon(
            category=raw["category"],
            title=raw["name"],
            material_text=raw["material_text"],
            shipping_type=raw["shipping_type"],
        )
        products.append({
            "id": idx,
            "name": raw["name"],
            "category": raw["category"],
            "price": raw["price"],
            "material": carbon.material.title(),
            "eco_score": carbon.eco_score,
            "carbon_kg": carbon.total_carbon_kg,
            "esg_rating": carbon.esg_rating,
            "shipping_type": raw["shipping_type"].title(),
            "tag": "Eco-Certified",
            "image_url": raw.get("image_url", ""),
            "description": raw.get("description", ""),
            "source_url": raw.get("source_url", ""),
            "carbon_breakdown": json.dumps({
                "estimated_weight_kg": carbon.estimated_weight_kg,
                "material_carbon_kg": carbon.material_carbon_kg,
                "shipping_carbon_kg": carbon.shipping_carbon_kg,
            }),
        })

    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    cats: dict[str, int] = {}
    for p in products:
        cats[p["category"]] = cats.get(p["category"], 0) + 1

    print(f"Generated {len(products)} eco products:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    generate()
