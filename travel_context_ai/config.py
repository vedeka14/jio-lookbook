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

TICKETS_DIR = DATA_DIR / "tickets"
OUTPUT_DIR = DATA_DIR / "output"

# ==================================================
# Files
# ==================================================

TICKET_IMAGE = TICKETS_DIR / "goa-flight-ticket.jpg"

TRIP_CONTEXT_FILE = OUTPUT_DIR / "trip_context.json"
OCR_OUTPUT = OUTPUT_DIR / "ocr.json"

# ==================================================
# Device
# ==================================================

DEVICE = "cpu"