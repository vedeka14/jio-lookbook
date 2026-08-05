from pathlib import Path

# ==================================================
# Project Paths
# ==================================================

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / "data"
PROMPTS_DIR = ROOT / "prompts"

# ==================================================
# Existing Project Outputs
# ==================================================

TRAVEL_CONTEXT_FILE = (
    ROOT.parent
    / "travel_context_ai"
    / "data"
    / "output"
    / "travel_context.json"
)

WARDROBE_FILE = (
    ROOT.parent
    / "fashion_ai"
    / "wardrobeinference"
    / "data"
    / "wardrobe.json"
)

AJIO_QUERY_FILE = (
    ROOT.parent
    / "recommendation_engine"
    / "data"
    / "ajio_query.json"
)

# ==================================================
# Style Assistant Files
# ==================================================

USER_PROFILE_FILE = DATA_DIR / "user_profile.json"
PROMPT_FILE = PROMPTS_DIR / "stylist_prompt.txt"