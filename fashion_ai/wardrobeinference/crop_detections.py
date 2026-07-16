import json
import shutil
from pathlib import Path
from PIL import Image

from config import *

# ==================================================
# Clean Previous Crops
# ==================================================

if CROPS_DIR.exists():
    shutil.rmtree(CROPS_DIR)

CROPS_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# Load OWL-ViT Detections
# ==================================================

print("=" * 60)
print("Loading OWL-ViT Detections...")
print("=" * 60)

with open(OWLVIT_OUTPUT, "r", encoding="utf-8") as f:
    detections = json.load(f)

print(f"Loaded {len(detections)} detections.")

# ==================================================
# Crop All Detections
# ==================================================

crop_number = 1

for detection in detections:

    image_name = detection["image"]
    label = detection["label"]
    bbox = detection["bbox"]

    image_path = PHOTOS_DIR / image_name

    if not image_path.exists():
        print(f"Image not found: {image_name}")
        continue

    image = Image.open(image_path).convert("RGB")

    x1, y1, x2, y2 = map(int, bbox)

    # Keep coordinates inside image
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(image.width, x2)
    y2 = min(image.height, y2)

    if x2 <= x1 or y2 <= y1:
        print(f"Skipping invalid bounding box for {image_name}")
        continue

    crop = image.crop((x1, y1, x2, y2))

    crop_name = (
        f"{Path(image_name).stem}"
        f"_{label}"
        f"_{crop_number:03d}.jpg"
    )

    crop_path = CROPS_DIR / crop_name

    crop.save(crop_path)

    print(f"Saved: {crop_name}")

    crop_number += 1

# ==================================================
# Finished
# ==================================================

print("\n" + "=" * 60)
print("Cropping Complete")
print("=" * 60)
print(f"Saved {crop_number - 1} crops")
print(f"Crops saved to:\n{CROPS_DIR}")
