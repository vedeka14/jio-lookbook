from pathlib import Path
import torch
PROJECT_NAME = "Fashion_Project"
# Project root
ROOT = Path(__file__).resolve().parent.parent

# Directories
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
DATASET_DIR = ROOT / "datasets"

PHOTOS_DIR = DATA_DIR / "photos"
OUTPUT_DIR = DATA_DIR / "output"
COLOR_CROPS_DIR = DATA_DIR / "color_crops"
CROPS_DIR = DATA_DIR / "crops"

WARDROBE_FILE = DATA_DIR / "wardrobe.json"
COLORS_FILE = DATA_DIR / "colors.json"

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

