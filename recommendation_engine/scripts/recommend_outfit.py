import csv
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from collections import Counter, defaultdict
from recommendation_engine.scripts.privacy_layer import (
    build_ajio_query,
    save_query,
    display_query
)
from recommendation_engine.config import *

RULES = {
    "weather": {
        "hot": [
            {"category": "shorts", "reason": "Hot weather", "priority": "Medium"},
            {"category": "sandals", "reason": "Stay cool", "priority": "Medium"},
            {"category": "hat", "reason": "Sun protection", "priority": "Low"},
            {"category": "sunglasses", "reason": "Eye protection", "priority": "Low"}
        ],
        "cold": [
            {"category": "jacket", "reason": "Cold weather", "priority": "High"},
            {"category": "sweater", "reason": "Layering", "priority": "Medium"}
        ],
        "rainy": [
            {"category": "raincoat", "reason": "Rain protection", "priority": "High"},
            {"category": "umbrella", "reason": "Rain protection", "priority": "High"}
        ]
    },
    "trip": {
        "mountain": [
            {"category": "boots", "reason": "Mountain terrain", "priority": "High"}
        ],
        "beach": [
            {"category": "sandals", "reason": "Beach environment", "priority": "Medium"}
        ]
    },
    "activities": {
        "snow": [
            {"category": "boots", "reason": "Snow activities", "priority": "High"},
            {"category": "gloves", "reason": "Cold protection", "priority": "High"}
        ],
        "swim": [
            {"category": "swimwear", "reason": "Swimming", "priority": "High"}
        ],
        "trek": [
            {"category": "shoes", "reason": "Trekking", "priority": "High"}
        ]
    }
}

# ==================================================
# Color Compatibility
# ==================================================

COLOR_MATCH = {

    "Black": ["White", "Grey", "Beige"],
    "White": ["Black", "Grey", "Blue"],
    "Grey": ["Black", "White", "Blue"],

    "Beige": ["Brown", "White", "Black"],
    "Brown": ["Beige", "Cream", "White"],
    "Cream": ["Brown", "Beige", "White"],

    "Blue": ["White", "Grey", "Beige"],
    "Sky Blue": ["White", "Brown", "Navy"],
    "Teal": ["White", "Brown", "Black"],

    "Olive": ["Beige", "Brown", "Black"],
    "Mustard": ["Brown", "Black", "White"],

    "Pink": ["White", "Grey"],
    "Lavender": ["White", "Grey"],
    "Purple": ["White", "Grey"]
}

# ==================================================
# Settings
# ==================================================

MIN_CONFIDENCE = 0.50

# ==================================================
# Load Trip Information
# ==================================================

print("=" * 60)
print("Loading Trip Information")
print("=" * 60)

with open(TRIP_CONTEXT_FILE, "r", encoding="utf-8") as f:
    trip = json.load(f)

print("\nTrip Details\n")

for key, value in trip.items():
    print(f"{key:<15}: {value}")

# ==================================================
# Load Wardrobe
# ==================================================

print("\n" + "=" * 60)
print("Loading Wardrobe")
print("=" * 60)

with open(WARDROBE_FILE, "r", encoding="utf-8") as f:
    wardrobe = json.load(f)

filtered_wardrobe = [

    item

    for item in wardrobe

    if item["confidence"] >= MIN_CONFIDENCE

]

print(f"\nFound {len(filtered_wardrobe)} wardrobe item(s).\n")

for item in filtered_wardrobe:

    print(
        f"{item['category']:<18}"
        f"{item['color']:<15}"
        f"{item['confidence']:.2f}"
    )

# ==================================================
# Load AJIO Catalog
# ==================================================

print("\n" + "=" * 60)
print("Loading AJIO Catalog")
print("=" * 60)

with open(CATALOG_FILE, "r", encoding="utf-8") as f:
    catalog = list(csv.DictReader(f))

print(f"\nFound {len(catalog)} catalog item(s).\n")

# ==================================================
# Recommendation Rules
# ==================================================

required_items_dict = {}

weather = trip.get("weather", "").lower()
if "hot" in weather or "humid" in weather or "warm" in weather:
    for item in RULES["weather"]["hot"]:
        required_items_dict[item["category"]] = item
elif "cold" in weather or "snow" in weather or "chill" in weather:
    for item in RULES["weather"]["cold"]:
        required_items_dict[item["category"]] = item
elif "rainy" in weather or "monsoon" in weather or "wet" in weather:
    for item in RULES["weather"]["rainy"]:
        required_items_dict[item["category"]] = item

trip_type = trip.get("trip", "").lower()
if "mountain" in trip_type or "hill" in trip_type:
    for item in RULES["trip"]["mountain"]:
        required_items_dict[item["category"]] = item
elif "beach" in trip_type or "coastal" in trip_type:
    for item in RULES["trip"]["beach"]:
        required_items_dict[item["category"]] = item

activities = trip.get("activities", [])
if isinstance(activities, str):
    activities_str = activities.lower()
else:
    activities_str = " ".join(activities).lower()

if "snow" in activities_str:
    for item in RULES["activities"]["snow"]:
        required_items_dict[item["category"]] = item
if "swim" in activities_str:
    for item in RULES["activities"]["swim"]:
        required_items_dict[item["category"]] = item
if "trek" in activities_str or "hik" in activities_str:
    for item in RULES["activities"]["trek"]:
        required_items_dict[item["category"]] = item

if not required_items_dict:
    default_items = [
        {"category": "jeans", "reason": "Casual wear", "priority": "Low"},
        {"category": "tshirt", "reason": "Casual wear", "priority": "Low"}
    ]
    for item in default_items:
        required_items_dict[item["category"]] = item

required_items = list(required_items_dict.values())

print("\n" + "=" * 60)
print("Combined Requirements")
print("=" * 60)

for item in required_items:
    print(f"{item['category'].title()} ({item['priority']}): {item['reason']}")

# ==================================================
# Already Owned
# ==================================================

owned_categories = {

    item["category"].lower()

    for item in filtered_wardrobe

}

print("\n" + "=" * 60)
print("Already Owned")
print("=" * 60)

for category in sorted(owned_categories):
    print(category)

# ==================================================
# Favorite Colors
# ==================================================

color_counter = Counter()

for item in filtered_wardrobe:
    color_counter[item["color"]] += 1

favorite_colors = [

    color

    for color, count in color_counter.most_common(3)

]

print("\n" + "=" * 60)
print("Favorite Colors")
print("=" * 60)

for color in favorite_colors:
    print(color)

# ==================================================
# Preferred Colors
# ==================================================

preferred_colors = set()

for color in favorite_colors:

    preferred_colors.add(color)

    if color in COLOR_MATCH:
        preferred_colors.update(COLOR_MATCH[color])

print("\n" + "=" * 60)
print("Preferred Colors")
print("=" * 60)

for color in sorted(preferred_colors):
    print(color)

# ==================================================
# Missing Items
# ==================================================

missing_items = [

    item

    for item in required_items

    if item["category"].lower() not in owned_categories

]

print("\n" + "=" * 60)
print("Items to Recommend")
print("=" * 60)

if missing_items:

    for item in missing_items:
        print(f"{item['category'].title()} ({item['priority']})")

else:

    print("No additional items needed.")


# ==================================================
# Privacy Layer
# ==================================================

print("\n" + "=" * 60)
print("Privacy Layer")
print("=" * 60)

ajio_query = build_ajio_query(
    missing_items,
    preferred_colors
)

save_query(
    ajio_query,
    AJIO_QUERY_FILE
)

display_query(missing_items, preferred_colors)

print("\nPrivacy Check")

try:
    print("✓ User photos are NOT shared")
    print("✓ OCR travel documents are NOT shared")
    print("✓ Wardrobe images are NOT shared")
    print("✓ Only clothing requirements are shared")
except UnicodeEncodeError:
    print("[OK] User photos are NOT shared")
    print("[OK] OCR travel documents are NOT shared")
    print("[OK] Wardrobe images are NOT shared")
    print("[OK] Only clothing requirements are shared")

# ==================================================
# Find Matching Products
# ==================================================

missing_categories = {

    item["category"].lower()

    for item in missing_items

}

recommended_products = []

for product in catalog:

    if (

        product["category"].lower() in missing_categories

        and

        product["color"] in preferred_colors

    ):

        recommended_products.append(product)

# ==================================================
# Group Recommendations
# ==================================================

recommendations = defaultdict(list)

for product in recommended_products:
    recommendations[product["category"]].append(product)

print("\n" + "=" * 60)
print(f"Recommended Outfit")
print("=" * 60)

if recommendations:
    for category, products in recommendations.items():
        if products:
            top_product = products[0]
            try:
                print(f"✓ {top_product['color']} {category.title()}")
            except UnicodeEncodeError:
                print(f"[OK] {top_product['color']} {category.title()}")
else:
    print("No outfit recommendations needed.")

print("\n" + "=" * 60)
print("Recommended Products")
print("=" * 60)

if recommendations:

    for category, products in recommendations.items():

        print(f"\n{category.upper()}")

        for product in products[:2]:

            print(
                f"  {product['color']:<10} Rs. {product['price']}"
            )

else:

    print("No matching products found.")

# ==================================================
# Recommendation Summary
# ==================================================

print("\n" + "=" * 60)
print("Trip Summary")
print("=" * 60)

print(f"Destination : {trip.get('destination', 'N/A')}")
print(f"Trip Type   : {trip.get('trip', 'N/A')}")
print(f"Weather     : {trip.get('weather', 'N/A')}")

print("\nWardrobe")
try:
    print(f"\n✓ {len(owned_categories)} Clothing Categories")
except UnicodeEncodeError:
    print(f"\n[OK] {len(owned_categories)} Clothing Categories")

print("\nNeed\n")
for item in missing_items:
    try:
        print(f"✓ {item['category'].title()}")
    except UnicodeEncodeError:
        print(f"[OK] {item['category'].title()}")

print("\nCatalog Matches")
try:
    print(f"\n✓ {len(recommended_products)} Products Found")
except UnicodeEncodeError:
    print(f"\n[OK] {len(recommended_products)} Products Found")