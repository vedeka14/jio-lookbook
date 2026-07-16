import csv
import json
from collections import Counter, defaultdict

from recommendation_engine.config import *

# ==================================================
# Trip Requirements
# ==================================================

TRIP_REQUIREMENTS = {

    "Beach": [
        "shirt",
        "shorts",
        "sandals",
        "hat",
        "sunglasses"
    ],

    "Mountain": [
        "hoodie",
        "jacket",
        "pants",
        "shoes"
    ],

    "City": [
        "shirt",
        "pants",
        "shoes"
    ]
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
# Trip Requirements
# ==================================================

trip_type = trip.get("trip", "Unknown")

required_items = TRIP_REQUIREMENTS.get(trip_type, [])

print("\n" + "=" * 60)
print(f"{trip_type} Trip Requirements")
print("=" * 60)

for item in required_items:
    print(item)

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

    if item.lower() not in owned_categories

]

print("\n" + "=" * 60)
print("Items to Recommend")
print("=" * 60)

if missing_items:

    for item in missing_items:
        print(item)

else:

    print("No additional items needed.")

# ==================================================
# Find Matching Products
# ==================================================

missing_categories = {

    item.lower()

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
print("Recommendation Summary")
print("=" * 60)

print(f"Destination : {trip.get('destination')}")
print(f"Trip        : {trip.get('trip')}")
print(f"Weather     : {trip.get('weather')}")
print(f"Own Items   : {len(owned_categories)}")
print(f"Need Items  : {len(missing_items)}")
print(f"Suggestions : {len(recommended_products)}")