import json

from config import *

# ==================================================
# Load Files
# ==================================================

print("=" * 60)
print("Building Wardrobe Database")
print("=" * 60)

with open(OWLVIT_OUTPUT, "r", encoding="utf-8") as f:
    detections = json.load(f)

with open(COLORS_FILE, "r", encoding="utf-8") as f:
    colors = json.load(f)

# ==================================================
# Verify
# ==================================================

if len(detections) != len(colors):
    raise ValueError(
        f"Mismatch:\n"
        f"Detections : {len(detections)}\n"
        f"Colors     : {len(colors)}"
    )

# ==================================================
# Build Wardrobe
# ==================================================

best_detections = {}

for detection, color_info in zip(detections, colors):
    category = detection["label"]
    color = color_info["color"]
    confidence = detection["score"]
    image = detection["image"]

    key = (category.lower(), color.lower())

    if key not in best_detections or confidence > best_detections[key]["confidence"]:
        best_detections[key] = {
            "image": image,
            "category": category,
            "color": color,
            "confidence": confidence
        }

# Convert back to list and sort by category and color
wardrobe = sorted(best_detections.values(), key=lambda x: (x["category"], x["color"]))

# ==================================================
# Save JSON
# ==================================================

with open(WARDROBE_FILE, "w", encoding="utf-8") as f:
    json.dump(wardrobe, f, indent=4)

# ==================================================
# Display
# ==================================================

print("\nWardrobe Items\n")

for item in wardrobe:

    print(
        f"{item['image']:<45}"
        f"{item['category']:<18}"
        f"{item['color']:<15}"
        f"{item['confidence']:.2f}"
    )

print("\n" + "=" * 60)
print("Wardrobe Complete")
print("=" * 60)
print(f"Items: {len(wardrobe)}")
print(f"Saved to:\n{WARDROBE_FILE}")
