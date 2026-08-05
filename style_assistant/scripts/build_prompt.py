import json
import os
from collections import defaultdict

from style_assistant.config import (
    TRAVEL_CONTEXT_FILE,
    WARDROBE_FILE,
    AJIO_QUERY_FILE,
    USER_PROFILE_FILE,
    PROMPT_FILE,
)

# ==================================================
# Load JSON Safely
# ==================================================

def load_json_safe(filepath, default_val):
    if not os.path.exists(filepath):
        return default_val
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default_val

trip = load_json_safe(TRAVEL_CONTEXT_FILE, {})
wardrobe = load_json_safe(WARDROBE_FILE, [])
missing_items = load_json_safe(AJIO_QUERY_FILE, [])
profile = load_json_safe(USER_PROFILE_FILE, {})

if os.path.exists(PROMPT_FILE):
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        template = f.read()
else:
    template = (
        "User Trip:\nDestination: {destination}\nWeather: {weather}\nActivities:\n{activities}\n\n"
        "Wardrobe:\n{wardrobe}\n\n"
        "Missing/Needed Items:\n{missing_items}\n\n"
        "User Profile:\nGender: {gender}\nAge: {age}\nSkin Tone: {skin_tone}\nBody Type: {body_type}\n"
        "Height: {height}\nBudget: {budget}\nPreferred Style: {preferred_style}\n"
        "Favorite Colors: {favorite_colors}\nColors to Avoid: {avoid_colors}\n"
    )

# ==================================================
# Wardrobe Groups
# ==================================================

CATEGORY_GROUPS = {

    "Base Layers": {
        "shirt",
        "tshirt",
        "t-shirt",
        "kurti",
        "blouse",
        "top"
    },

    "Bottoms": {
        "jeans",
        "pants",
        "shorts",
        "trousers",
        "leggings",
        "skirt"
    },

    "Outerwear": {
        "jacket",
        "coat",
        "blazer",
        "cardigan",
        "shrug",
        "overcoat",
        "sweater",
        "hoodie",
        "pullover"
    },

    "Traditional Wear": {
        "saree",
        "lehenga",
        "kurta",
        "salwar",
        "dress",
        "gown"
    },

    "Footwear": {
        "sandals",
        "shoes",
        "heels",
        "slippers",
        "sneakers",
        "boots",
        "flats"
    },

    "Accessories": {
        "bag",
        "handbag",
        "cap",
        "hat",
        "belt",
        "watch",
        "sunglasses",
        "scarf",
        "jewelry",
        "necklace"
    }
}

# ==================================================
# Format Wardrobe
# ==================================================

grouped = defaultdict(list)

for item in wardrobe:
    
    category = item.get("category", "unknown").lower()
    color = item.get("color", "unknown color")
    
    placed = False

    for group_name, categories in CATEGORY_GROUPS.items():
        if category in categories:
            grouped[group_name].append(f"{color} {category}")
            placed = True
            break

    if not placed:
        grouped["Other"].append(f"{color} {category}")

wardrobe_text = ""

group_order = [
    "Base Layers",
    "Bottoms",
    "Outerwear",
    "Traditional Wear",
    "Footwear",
    "Accessories",
    "Other"
]

for group in group_order:
    if grouped[group]:
        wardrobe_text += f"{group}\n"
        for item in sorted(grouped[group]):
            wardrobe_text += f"- {item}\n"
        wardrobe_text += "\n"
    elif group in ["Footwear", "Accessories", "Outerwear"]:
        wardrobe_text += f"{group}\n"
        wardrobe_text += "- None\n\n"

if not wardrobe:
    wardrobe_text = "No wardrobe items detected.\n\n"

# ==================================================
# Format Missing Items
# ==================================================

missing_text = ""

for item in missing_items:
    cat = item.get("category", "unknown")
    prio = item.get("priority", "medium")
    reason = item.get("reason", "none")
    missing_text += (
        f"- {cat}\n"
        f"  Priority: {prio}\n"
        f"  Reason: {reason}\n\n"
    )

if not missing_items:
    missing_text = "No missing items required.\n\n"

# ==================================================
# Build Prompt
# ==================================================

activities_list = trip.get("activities", [])
if activities_list:
    activities_text = "\n".join([f"- {act}" for act in activities_list])
else:
    activities_text = "- None"

prompt = template.format(
    destination=trip.get("destination", "Unknown Destination"),
    weather=trip.get("weather", "Unknown Weather"),
    activities=activities_text,

    wardrobe=wardrobe_text,
    missing_items=missing_text,

    gender=profile.get("gender", "Unknown"),
    age=profile.get("age", "Unknown"),
    skin_tone=profile.get("skin_tone", "Unknown"),
    body_type=profile.get("body_type", "Unknown"),
    height=profile.get("height", "Unknown"),
    budget=profile.get("budget", "Unknown"),
    preferred_style=profile.get("preferred_style", "Unknown"),
    favorite_colors=", ".join(profile.get("favorite_colors", [])),
    avoid_colors=", ".join(profile.get("avoid_colors", [])),
)

# ==================================================
# Public Function
# ==================================================

def build_prompt():
    return prompt

# ==================================================
# Preview Prompt
# ==================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LLM Prompt")
    print("=" * 60)
    print(build_prompt())