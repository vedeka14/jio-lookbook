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
DATASET_DIR = ROOT / "datasets"
MODEL_DIR = ROOT / "models"
SCRIPT_DIR = ROOT / "scripts"

PHOTOS_DIR = DATA_DIR / "photos"
OUTPUT_DIR = DATA_DIR / "output"
CROPS_DIR = DATA_DIR / "crops"
COLOR_CROPS_DIR = DATA_DIR / "color_crops"

# ==================================================
# Files
# ==================================================

WARDROBE_FILE = DATA_DIR / "wardrobe.json"
COLORS_FILE = DATA_DIR / "colors.json"
OWLVIT_OUTPUT = OUTPUT_DIR / "owlvit.json"

# ==================================================
# Device
# ==================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"