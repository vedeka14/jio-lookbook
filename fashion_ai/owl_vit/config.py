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

# ==================================================
# Files
# ==================================================

OWLVIT_OUTPUT = OUTPUT_DIR / "owlvit.json"

# ==================================================
# Device
# ==================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
