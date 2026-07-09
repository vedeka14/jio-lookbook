import json
# ----------------------------
# Project Root
# ----------------------------
from config import *

# ----------------------------
# Load wardrobe database
# ----------------------------

with open(WARDROBE_FILE, "r", encoding="utf-8") as f:
    wardrobe = json.load(f)

# ----------------------------
# Display wardrobe
# ----------------------------
print("\n========== MY WARDROBE ==========\n")

for item in wardrobe:
    print(f"Image      : {item['image']}")
    print(f"Category   : {item['category']}")
    print(f"Color      : {item['color']}")
    print(f"Confidence : {item['confidence']:.3f}")
    print("-" * 40)

print(f"\nTotal Items: {len(wardrobe)}")