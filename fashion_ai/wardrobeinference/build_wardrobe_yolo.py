import json
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import cv2
from ultralytics import YOLO
import torch
from tqdm import tqdm
from collections import Counter

# ==================================================
# Project Paths & Modules
# ==================================================
from .config import *
from .extract_colors import detect_color


def main():
    print("=" * 60)
    print(f"Running YOLO Wardrobe Inference on : {DEVICE.upper()}")
    if DEVICE == "cuda":
        print(f"GPU : {torch.cuda.get_device_name(0)}")
    print("=" * 60)

    # ==================================================
    # Load Model
    # ==================================================
    print("Loading YOLO model...")
    model = YOLO(str(YOLO_MODEL_PATH))
    model.to(DEVICE)

    # ==================================================
    # Read Images
    # ==================================================
    image_extensions = {".jpg", ".jpeg", ".png"}
    image_paths = sorted(
        [
            p for p in PHOTOS_DIR.iterdir()
            if p.suffix.lower() in image_extensions
        ]
    )

    print("\n" + "=" * 60)
    print(f"Found {len(image_paths)} image(s) in {PHOTOS_DIR.name}")
    print("=" * 60)

    all_detections = []
    COLOR_CROPS_DIR.mkdir(parents=True, exist_ok=True)

    # ==================================================
    # Run Detection & Color Extraction
    # ==================================================
    for image_path in tqdm(image_paths, desc="Processing Photos", unit="img"):
        img = cv2.imread(str(image_path))

        if img is None:
            continue

        height, width = img.shape[:2]

        results = model.predict(
            source=str(image_path),
            conf=0.50,
            device=DEVICE,
            verbose=False
        )
        result = results[0]

        if len(result.boxes) == 0:
            continue

        for i, box in enumerate(result.boxes):
            confidence = float(box.conf[0])
            if confidence < 0.50:
                continue

            class_id = int(box.cls[0])
            category = result.names[class_id]

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(width, x2)
            y2 = min(height, y2)

            crop = img[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            crop_name = f"{image_path.stem}_{category}_{i+1:03d}.jpg"
            crop_path = COLOR_CROPS_DIR / crop_name
            cv2.imwrite(str(crop_path), crop)

            try:
                color = detect_color(crop)
            except Exception:
                color = "Unknown"

            item = {
                "image": image_path.name,
                "category": category,
                "color": color,
                "confidence": round(confidence, 3),
                "crop": crop_name,
                "bbox": [x1, y1, x2, y2]
            }
            all_detections.append(item)

    # ==================================================
    # Save Raw Detections (COLORS_FILE)
    # ==================================================
    COLORS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COLORS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_detections, f, indent=4)

    # ==================================================
    # Build Deduplicated Wardrobe Database (WARDROBE_FILE)
    # ==================================================
    best_detections = {}
    for item in all_detections:
        category = item["category"]
        color = item["color"]
        confidence = item["confidence"]
        image = item["image"]

        key = (category.lower(), color.lower())
        if key not in best_detections or confidence > best_detections[key]["confidence"]:
            best_detections[key] = {
                "image": image,
                "category": category,
                "color": color,
                "confidence": confidence
            }

    wardrobe = sorted(best_detections.values(), key=lambda x: (x["category"], x["color"]))

    with open(WARDROBE_FILE, "w", encoding="utf-8") as f:
        json.dump(wardrobe, f, indent=4)

    # ==================================================
    # Summary
    # ==================================================
    cat_counts = Counter(item["category"] for item in wardrobe)

    print("\n" + "=" * 60)
    print("Wardrobe Summary")
    print("=" * 60)
    print(f"Images Processed  : {len(image_paths)}")
    print(f"Unique Categories : {len(cat_counts)}")

    print("\nDetected Items\n")
    for category, count in sorted(cat_counts.items(), key=lambda x: (-x[1], x[0])):
        display_cat = category
        if display_cat.lower() == "tshirt":
            display_cat = "T-Shirt"
        if count != 1 and not display_cat.endswith("s"):
            display_cat += "s"
        try:
            print(f"✓ {count} {display_cat}\n")
        except UnicodeEncodeError:
            print(f"[OK] {count} {display_cat}\n")

    print("\n" + "=" * 60)
    print("YOLO Wardrobe Inference Complete")
    print("=" * 60)
    print(f"Total Detections : {len(all_detections)} (saved to {COLORS_FILE.name})")
    print(f"Unique Items     : {len(wardrobe)} (saved to {WARDROBE_FILE.name})")


if __name__ == "__main__":
    main()
