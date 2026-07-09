"""
verify_dataset.py
Draw YOLO bounding boxes on a few images from each dataset split to visually
verify that labels were merged correctly.

Usage:
    python verify_dataset.py
"""

from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from config import *

ROOT = DATASET_DIR / "merged_dataset"
OUT = ROOT / "verify_samples"

SPLITS = ("train", "valid", "test")
SAMPLES_PER_SPLIT = 2
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_names() -> dict[int, str]:
    with open(ROOT / "data.yaml", "r", encoding="utf8") as f:
        cfg = yaml.safe_load(f)
    names = cfg["names"]
    if isinstance(names, dict):
        return {int(k): v for k, v in names.items()}
    return {i: n for i, n in enumerate(names)}


def yolo_to_box(w: int, h: int, cx: float, cy: float, bw: float, bh: float):
    x1 = max(0, int((cx - bw / 2) * w))
    y1 = max(0, int((cy - bh / 2) * h))
    x2 = min(w - 1, int((cx + bw / 2) * w))
    y2 = min(h - 1, int((cy + bh / 2) * h))
    return x1, y1, x2, y2


def get_font():
    for font_name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(font_name, 16)
        except OSError:
            pass
    return ImageFont.load_default()


FONT = get_font()


def draw_sample(img_path: Path, names: dict[int, str]):
    label_path = img_path.parent.parent / "labels" / f"{img_path.stem}.txt"

    try:
        img = Image.open(img_path).convert("RGB")
    except (UnidentifiedImageError, OSError) as e:
        print(f"Skipping unreadable image: {img_path.name} ({e})")
        return None

    draw = ImageDraw.Draw(img)
    w, h = img.size

    if not label_path.exists():
        print(f"No label found: {img_path.name}")

    else:
        for line in label_path.read_text(encoding="utf8").splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue

            cls = int(parts[0])
            cx, cy, bw, bh = map(float, parts[1:5])

            box = yolo_to_box(w, h, cx, cy, bw, bh)
            label = names.get(cls, str(cls))

            draw.rectangle(box, outline="lime", width=3)

            left, top, right, bottom = draw.textbbox((0, 0), label, font=FONT)
            tw = right - left
            th = bottom - top

            tx = box[0]
            ty = max(0, box[1] - th - 6)

            draw.rectangle((tx, ty, tx + tw + 6, ty + th + 4), fill="lime")
            draw.text((tx + 3, ty + 2), label, fill="black", font=FONT)

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{img_path.parent.parent.name}_{img_path.name}"
    img.save(out)
    return out


def main():
    if not ROOT.exists():
        raise FileNotFoundError(f"Dataset not found:\n{ROOT.resolve()}")

    data_yaml = ROOT / "data.yaml"
    if not data_yaml.exists():
        raise FileNotFoundError(f"Missing data.yaml:\n{data_yaml.resolve()}")

    names = load_names()
    saved = []

    for split in SPLITS:
        img_dir = ROOT / split / "images"
        if not img_dir.exists():
            print(f"Skipping missing split: {split}")
            continue

        count = 0
        for img_path in sorted(img_dir.iterdir(), key=lambda p: p.name.lower()):
            if img_path.suffix.lower() not in IMAGE_EXTS:
                continue

            result = draw_sample(img_path, names)
            if result:
                saved.append(result)

            count += 1
            if count >= SAMPLES_PER_SPLIT:
                break

    print(f"\nSaved {len(saved)} verification images:")
    for p in saved:
        print("  ", p.name)

    print(f"\nOutput folder:\n{OUT.resolve()}")


if __name__ == "__main__":
    main()
