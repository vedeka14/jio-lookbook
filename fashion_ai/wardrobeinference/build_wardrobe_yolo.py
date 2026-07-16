import json
import cv2
from ultralytics import YOLO
import torch
from extract_colors import detect_color

# ==================================================
# Project Paths
# ==================================================

from config import *

MODEL_PATH = YOLO_MODEL_PATH

IMAGE_PATH = PHOTOS_DIR / "ds07_shirt_v1i_yolo26_t_000013.jpg"

CROP_FOLDER = COLOR_CROPS_DIR

# ==================================================
# Device
# ==================================================

print("=" * 60)
print(f"Running on : {DEVICE.upper()}")

if DEVICE == "cuda":
    print(f"GPU : {torch.cuda.get_device_name(0)}")

print("=" * 60)

# ==================================================
# Load Model
# ==================================================
print("Loading YOLO model...")

model = YOLO(str(MODEL_PATH))
model.to(DEVICE)

# ==================================================
# Read Image
# ==================================================
img = cv2.imread(str(IMAGE_PATH))

if img is None:
    raise FileNotFoundError(f"Image not found:\n{IMAGE_PATH}")

height, width = img.shape[:2]

# ==================================================
# Predict
# ==================================================
print("Running detection...\n")

results = model.predict(
    source=str(IMAGE_PATH),
    conf=0.50,
    device=DEVICE,
    verbose=False
)

result = results[0]

detections = []

# ==================================================
# Process Results
# ==================================================
for i, box in enumerate(result.boxes):

    confidence = float(box.conf[0])

    if confidence < 0.50:
        continue

    class_id = int(box.cls[0])

    x1, y1, x2, y2 = map(int, box.xyxy[0])

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)

    crop = img[y1:y2, x1:x2]

    if crop.size == 0:
        continue

    CROP_FOLDER.mkdir(parents=True, exist_ok=True)
    crop_path = CROP_FOLDER / f"crop_{i}.jpg"
    cv2.imwrite(str(crop_path), crop)

    try:
        color = detect_color(crop)
    except Exception as e:
        print(f"Color detection failed: {e}")
        color = "Unknown"

    item = {
        "category": result.names[class_id],
        "color": color,
        "confidence": round(confidence, 3)
    }

    detections.append(item)

    print("-" * 60)
    print(f"Detection #{i+1}")
    print(f"Category     : {item['category']}")
    print(f"Color        : {item['color']}")
    print(f"Confidence   : {item['confidence']}")
    print(f"Bounding Box : ({x1}, {y1}, {x2}, {y2})")
    print(f"Crop Saved   : {crop_path}")

# ==================================================
# Save JSON
# ==================================================
json_file = COLORS_FILE

# Ensure directory exists
json_file.parent.mkdir(parents=True, exist_ok=True)

with open(json_file, "w") as f:
    json.dump(detections, f, indent=4)

print("\n" + "=" * 60)
print("Finished Successfully")
print("=" * 60)

print(f"JSON Saved : {json_file}")

print(json.dumps(detections, indent=4))
