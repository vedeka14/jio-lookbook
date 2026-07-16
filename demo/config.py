from pathlib import Path

ROOT = Path(__file__).resolve().parent

TRAVEL_CONTEXT = ROOT.parent / "travel_context_ai"

RECOMMENDATION_ENGINE = ROOT.parent / "recommendation_engine"

WARDROBE_FILE = RECOMMENDATION_ENGINE / "data" / "wardrobe.json"