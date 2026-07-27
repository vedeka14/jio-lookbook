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

WARDROBE_FILE = ROOT.parent / "fashion_ai" / "wardrobeinference" / "data" / "wardrobe.json"

TRIP_CONTEXT_FILE = ROOT.parent / "travel_context_ai" / "data" / "output" / "travel_context.json"
AJIO_QUERY_FILE = DATA_DIR / "ajio_query.json"
