from ultralytics import YOLO
import cv2
import json
import math

# ==================================================
# Project Configuration
# ==================================================
from config import *

MODEL_PATH = MODEL_DIR / "best.pt"
IMAGE_PATH = PHOTOS_DIR / "ds07_shirt_v1i_yolo26_t_000013.jpg"

CROP_FOLDER = COLOR_CROPS_DIR
CROP_FOLDER.mkdir(parents=True, exist_ok=True)


# ==================================================
# HSV Color Database
# ==================================================
COLOR_DATABASE = {
    "Black": (0, 0, 20),
    "White": (0, 0, 255),
    "Grey": (0, 0, 140),

    "Red": (0, 255, 255),
    "Maroon": (175, 255, 120),

    "Orange": (15, 255, 255),
    "Coral": (10, 180, 255),

    "Yellow": (30, 255, 255),
    "Mustard": (25, 220, 180),

    "Green": (60, 255, 255),
    "Olive": (45, 180, 120),
    "Mint": (55, 120, 255),

    "Cyan": (90, 255, 255),
    "Teal": (90, 180, 180),

    "Blue": (120, 255, 255),
    "Sky Blue": (105, 120, 255),
    "Navy": (120, 255, 100),

    "Purple": (145, 255, 180),
    "Lavender": (145, 80, 255),

    "Pink": (170, 120, 255),

    "Brown": (15, 180, 120),
    "Beige": (20, 50, 220),
    "Cream": (25, 30, 255)
}


# ==================================================
# Find Closest Color
# ==================================================
def find_closest_color(h, s, v):
    best_color = None
    best_distance = float("inf")

    for color_name, (H, S, V) in COLOR_DATABASE.items():
        distance = math.sqrt(
            (h - H) ** 2 +
            (s - S) ** 2 +
            (v - V) ** 2
        )

        if distance < best_distance:
            best_distance = distance
            best_color = color_name

    return best_color


# ==================================================
# Function Used by build_wardrobe.py
# ==================================================
def detect_color(crop):
    """
    Detect the dominant clothing color from a cropped BGR image.
    """

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    hue, saturation, value = hsv.mean(axis=(0, 1))

    return find_closest_color(hue, saturation, value)


# ==================================================
# Standalone Testing
# ==================================================
if __name__ == "__main__":

    print("=" * 60)
    print(f"Running on : {DEVICE.upper()}")
    print("=" * 60)

    model = YOLO(str(MODEL_PATH))
    model.to(DEVICE)

    img = cv2.imread(str(IMAGE_PATH))

    if img is None:
        raise FileNotFoundError(f"Image not found:\n{IMAGE_PATH}")

    results = model.predict(
        source=str(IMAGE_PATH),
        device=DEVICE,
        conf=0.50,
        verbose=False
    )

    result = results[0]

    output = []

    for i, box in enumerate(result.boxes):

        confidence = float(box.conf[0])

        if confidence < 0.50:
            continue

        class_id = int(box.cls[0])

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        crop = img[y1:y2, x1:x2]

        if crop.size == 0:
            continue

        crop_path = CROP_FOLDER / f"{IMAGE_PATH.stem}_crop_{i}.jpg"

        cv2.imwrite(str(crop_path), crop)

        color = detect_color(crop)

        print("-" * 40)
        print(f"Category   : {result.names[class_id]}")
        print(f"Color      : {color}")
        print(f"Confidence : {confidence:.3f}")

        output.append({
            "category": result.names[class_id],
            "color": color,
            "confidence": round(confidence, 3)
        })

    with open(COLORS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("Finished Successfully")
    print("=" * 60)
    print(f"Results saved to:\n{COLORS_FILE}")

    print("\nJSON Output:\n")
    print(json.dumps(output, indent=4, ensure_ascii=False))