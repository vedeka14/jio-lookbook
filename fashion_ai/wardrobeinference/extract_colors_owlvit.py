import cv2
import json
import math
from pathlib import Path

from config import *
from extract_colors import detect_color

def main():
    print("=" * 60)
    print("Extracting Colors")
    print("=" * 60)

    # Load OWL-ViT detections to ensure alignment and handle skipped crops
    if OWLVIT_OUTPUT.exists():
        with open(OWLVIT_OUTPUT, "r", encoding="utf-8") as f:
            detections = json.load(f)
    else:
        detections = []

    results = []

    # Keep track of which files exist in CROPS_DIR
    existing_crops = {p.name: p for p in CROPS_DIR.iterdir() if p.is_file()} if CROPS_DIR.exists() else {}

    if detections:
        print(f"Found {len(detections)} detection(s) in owlvit.json\n")
        crop_number = 1
        for detection in detections:
            image_name = detection["image"]
            label = detection["label"]

            # Reconstruct the expected crop name matching crop_detections.py logic
            expected_crop_name = (
                f"{Path(image_name).stem}"
                f"_{label}"
                f"_{crop_number:03d}.jpg"
            )

            if expected_crop_name in existing_crops:
                crop_path = existing_crops[expected_crop_name]
                crop = cv2.imread(str(crop_path))
                if crop is not None:
                    color = detect_color(crop)
                    print(f"{expected_crop_name:<55} {color}")
                    results.append({
                        "crop": expected_crop_name,
                        "color": color
                    })
                else:
                    print(f"{expected_crop_name:<55} Unknown (Read Failed)")
                    results.append({
                        "crop": expected_crop_name,
                        "color": "Unknown"
                    })
                crop_number += 1
            else:
                print(f"Crop skipped or not found for detection: {image_name} ({label})")
                results.append({
                    "crop": None,
                    "color": "Unknown"
                })
    else:
        # Fallback to sorting files alphabetically if owlvit.json doesn't exist
        IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
        crop_paths = sorted([
            p for p in CROPS_DIR.iterdir()
            if p.suffix.lower() in IMAGE_EXTENSIONS
        ]) if CROPS_DIR.exists() else []

        print(f"owlvit.json not found. Found {len(crop_paths)} crop(s) in crops folder.\n")
        for crop_path in crop_paths:
            crop = cv2.imread(str(crop_path))
            if crop is None:
                continue
            color = detect_color(crop)
            print(f"{crop_path.name:<55} {color}")
            results.append({
                "crop": crop_path.name,
                "color": color
            })

    # ==================================================
    # Save JSON
    # ==================================================
    with open(COLORS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print("\n" + "=" * 60)
    print("Color Extraction Complete")
    print("=" * 60)
    print(f"Processed : {len(results)} crops/detections")
    print(f"Saved to  : {COLORS_FILE}")

if __name__ == "__main__":
    main()
