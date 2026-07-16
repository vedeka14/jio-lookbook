from pathlib import Path
import torch

# ==================================================
# Root
# ==================================================

ROOT = Path(__file__).resolve().parent

# ==================================================
# Directories
# ==================================================

DATA_DIR = ROOT / "data"
PHOTOS_DIR = DATA_DIR / "photos"
OUTPUT_DIR = DATA_DIR / "output"
CROPS_DIR = DATA_DIR / "crops"
COLOR_CROPS_DIR = DATA_DIR / "color_crops"

# ==================================================
# External Pipeline Inputs
# ==================================================

OWLVIT_DIR = ROOT.parent / "owl_vit"
OWLVIT_OUTPUT = OWLVIT_DIR / "data" / "output" / "owlvit.json"

YOLO_DIR = ROOT.parent / "yolo11"
YOLO_MODEL_PATH = YOLO_DIR / "models" / "best.pt"

# ==================================================
# Files
# ==================================================

WARDROBE_FILE = DATA_DIR / "wardrobe.json"
COLORS_FILE = DATA_DIR / "colors.json"

# ==================================================
# Device
# ==================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
