from pathlib import Path

# ==================================================
# Root
# ==================================================

ROOT = Path(__file__).resolve().parent

# ==================================================
# Directories
# ==================================================

DATA_DIR = ROOT / "data"
SCRIPT_DIR = ROOT / "scripts"

CATALOG_DIR = DATA_DIR / "catalog"

# ==================================================
# Files
# ==================================================

CATALOG_FILE = CATALOG_DIR / "ajio_catalog.csv"

WARDROBE_FILE = DATA_DIR / "wardrobe.json"

TRIP_CONTEXT_FILE = DATA_DIR / "trip_context.json"