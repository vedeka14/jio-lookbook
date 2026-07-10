from pathlib import Path
import torch

# ==================================================
# Project
# ==================================================

PROJECT_NAME = "Jio_Lookbook"

# Project root
ROOT = Path(__file__).resolve().parent.parent

# ==================================================
# Directories
# ==================================================

DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
DATASET_DIR = ROOT / "datasets"

PHOTOS_DIR = DATA_DIR / "photos"
TICKETS_DIR = DATA_DIR / "tickets"

OUTPUT_DIR = DATA_DIR / "output"
COLOR_CROPS_DIR = DATA_DIR / "color_crops"
CROPS_DIR = DATA_DIR / "crops"

# ==================================================
# Files
# ==================================================

WARDROBE_FILE = DATA_DIR / "wardrobe.json"
COLORS_FILE = DATA_DIR / "colors.json"

TICKET_IMAGE = TICKETS_DIR / "goa-flight-ticket.jpg"
OCR_OUTPUT = OUTPUT_DIR / "ocr.json"

# ==================================================
# Device
# ==================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"