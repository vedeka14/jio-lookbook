from ultralytics import YOLO
import torch
import cv2
import json
from pathlib import Path

from extract_colors import detect_color

# ==================================================
# Project Paths
# ==================================================
PROJECT_DIR = Path(__file__).resolve().parent

MODEL_PATH = PROJECT_DIR / "models" / "best.pt"

IMAGE_PATH = PROJECT_DIR / "photos" / "ds07_shirt_v1i_yolo26_t_000013.jpg"

CROP_FOLDER = PROJECT_DIR / "color_crops"
CROP_FOLDER.mkdir(exist_ok=True)

OUTPUT_FOLDER = PROJECT_DIR / "output"
OUTPUT_FOLDER.mkdir(exist_ok=True)

# ==================================================
# Device
# ==================================================
device = "cuda" if torch.cuda.is_available() else "cpu"

print("=" * 50)
print(f"Running on : {device}")
print("=" * 50)

# ==================================================
# Load YOLO Model
# ==================================================
model = YOLO(str(MODEL_PATH))
model.to(device)

# ==================================================
# Read Image
# ==================================================
img = cv2.imread(str(IMAGE_PATH))

if img is None:
    raise FileNotFoundError(
        f"Could not read image:\n{IMAGE_PATH}"
    )

# ==================================================
# Run YOLO Detection
# ==================================================
results = model.predict(
    source=str(IMAGE_PATH),
    device=device,
    conf=0.50,
    verbose=False
)

result = results[0]

output = []

# ==================================================
# Process Detections
# ==================================================
for i, box in enumerate(result.boxes):

    class_id = int(box.cls[0])
    confidence = float(box.conf[0])

    if confidence < 0.50:
        continue

    x1, y1, x2, y2 = map(int, box.xyxy[0])

    crop = img[y1:y2, x1:x2]

    if crop.size == 0:
        continue

    # ----------------------------------------------
    # Save Crop
    # ----------------------------------------------
    crop_path = CROP_FOLDER / f"crop_{i}.jpg"

    cv2.imwrite(str(crop_path), crop)

    # ----------------------------------------------
    # Detect Color
    # ----------------------------------------------
    color = detect_color(crop)

    # ----------------------------------------------
    # Save Result
    # ----------------------------------------------
    output.append(
        {
            "category": result.names[class_id],
            "color": color,
            "confidence": round(confidence, 3)
        }
    )

    # ----------------------------------------------
    # Console Output
    # ----------------------------------------------
    print("-" * 50)
    print(f"Detection {i + 1}")
    print("-" * 50)
    print("Category     :", result.names[class_id])
    print("Color        :", color)
    print("Confidence   :", round(confidence, 3))
    print("Bounding Box :", (x1, y1, x2, y2))
    print("Crop Shape   :", crop.shape)
    print("Crop Saved   :", crop_path)

# ==================================================
# Save JSON
# ==================================================
json_path = OUTPUT_FOLDER / "colors.json"

with open(json_path, "w") as f:
    json.dump(output, f, indent=4)

print("\n" + "=" * 50)
print("Finished Successfully")
print("=" * 50)
print(f"Results saved to : {json_path}")
print(json.dumps(output, indent=4))