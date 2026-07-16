from pathlib import Path
import torch

# ==================================================
# Root
# ==================================================

ROOT = Path(__file__).resolve().parent

# ==================================================
# Directories
# ==================================================

DATASET_DIR = ROOT / "datasets"
MODEL_DIR = ROOT / "models"

# ==================================================
# Device
# ==================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
