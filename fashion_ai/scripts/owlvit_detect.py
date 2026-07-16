import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

import json
import torch
from PIL import Image
from transformers import Owlv2Processor, Owlv2ForObjectDetection

from fashion_ai.config import *

# ==================================================
# Load OWL-ViT
# ==================================================

print("=" * 60)
print("Loading OWL-ViT Processor...")
print("=" * 60)

processor = Owlv2Processor.from_pretrained(
    "google/owlv2-base-patch16-ensemble"
)

print("Processor Loaded!")

print("\nLoading OWL-ViT Model...")

model = Owlv2ForObjectDetection.from_pretrained(
    "google/owlv2-base-patch16-ensemble"
).to(DEVICE)

print(f"Model Loaded on {DEVICE}")

# ==================================================
# Clothing Queries
# ==================================================

TEXT_QUERIES = [[
    "churidaar",
    "dhoti",
    "hijab",
    "jeans",
    "maxi dress",
    "pants",
    "saree",
    "shorts",
    "t shirt",
    "kurta",
    "shirt",
    "jacket",
    "dress",
    "skirt",
    "dupatta",
    "kameez",
    "shalwar",
    "design sherwani",
    "plain sherwani",
    "lehenga",
    "anarkali",
    "sharara",
    "lungi",
    "handbag",
    "shoes",
    "hoodie"
]]

# ==================================================
# Read Images
# ==================================================

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

image_paths = sorted(
    [
        p for p in PHOTOS_DIR.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    ]
)

print("\n" + "=" * 60)
print(f"Found {len(image_paths)} image(s)")
print("=" * 60)

# ==================================================
# Store All Detections
# ==================================================

all_detections = []

# ==================================================
# Run OWL-ViT
# ==================================================

for image_path in image_paths:

    print("\n" + "=" * 60)
    print(f"Processing: {image_path.name}")
    print("=" * 60)

    image = Image.open(image_path).convert("RGB")

    inputs = processor(
        text=TEXT_QUERIES,
        images=image,
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs)

    target_sizes = torch.tensor(
        [image.size[::-1]],
        device=DEVICE
    )

    results = processor.post_process_grounded_object_detection(
        outputs=outputs,
        target_sizes=target_sizes,
        threshold=0.25
    )[0]

    boxes = results["boxes"]
    scores = results["scores"]
    labels = results["labels"]

    if len(boxes) == 0:
        print("No objects detected.")
        continue

    print("\nDetected Objects:\n")

    for box, score, label in zip(boxes, scores, labels):

        box = [round(x, 2) for x in box.tolist()]
        label_name = TEXT_QUERIES[0][label]

        print(
            f"{label_name:20}"
            f"Score: {score:.2f} "
            f"Box: {box}"
        )

        all_detections.append(
            {
                "image": image_path.name,
                "label": label_name,
                "score": round(float(score), 3),
                "bbox": box
            }
        )

# ==================================================
# Save JSON
# ==================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(OWLVIT_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(all_detections, f, indent=4)

print("\n" + "=" * 60)
print("Finished processing all images.")
print("=" * 60)

print(f"Saved {len(all_detections)} detections")
print(f"Output file:\n{OWLVIT_OUTPUT}")