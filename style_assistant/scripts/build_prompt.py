# style_assistant/scripts/build_prompt.py
import json
from recommendation_engine.metadata.styles import STYLE_PROFILES

def build_prompt_from_candidates(candidate_json):
    """
    Constructs the prompt for the LLM using the pre-computed Candidate JSON.
    Forces the LLM to output ONLY a JSON object.
    """
    
    # We serialize the candidate json to a formatted string
    candidates_str = json.dumps(candidate_json, indent=2)
    
    occasion = candidate_json.get("occasion", "").lower()
    occasion_rules = ""
    if "party" in occasion:
        occasion_rules = (
            "PARTY SPECIFIC RULES:\n"
            "- If you are styling an outfit for a MAN (inferred by available men's items or unisex), you MUST strongly prioritize suggesting White Pants, a Black Polo T-Shirt, and a Gold Chain. If they are missing, suggest them as purchases.\n"
            "- If you are styling an outfit for a WOMAN (inferred by available dresses/heels), you MUST strongly prioritize suggesting a Black Short Dress, Black Heels, Gold/Silver Earrings, and a Bracelet. If they are missing, suggest them as purchases.\n\n"
        )
        
    # Dynamically build the expected JSON format based on available options
    json_format = '{\n  "outfit": {\n'
    cands = candidate_json.get("candidates", {})
    has_cands = any(len(lst) > 0 for lst in cands.values())
    missing_items = candidate_json.get("missing_items", [])
    
    parts = [
        '    "top": "Name of Top (from candidates, or invent one if missing)"',
        '    "bottom": "Name of Bottom (from candidates, or invent one if missing)"',
        '    "full_body": "Name of Full Body Item (optional, use instead of top/bottom)"',
        '    "outerwear": "Name of Outerwear (optional, from candidates or invent)"',
        '    "footwear": "Name of Footwear (from candidates, or invent if missing)"',
        '    "accessory": "Name of Accessory (from candidates, or invent if missing)"'
    ]

    json_format += ",\n".join(parts) + "\n"
    json_format += (
        '  },\n'
        '  "missing": [\n'
        '    "Category: Specific Suggestion (e.g. Footwear: Brown Leather Loafers)"\n'
        '  ],\n'
        '  "reason": "Explain why this outfit combination works best for the user\'s criteria. Do NOT include styling tips for items not in the outfit."\n'
        '}'
    )

    preferred_styles = candidate_json.get("preferred_styles", [])
    style_rules = ""
    
    if preferred_styles:
        style_rules = "STYLE REQUIREMENTS:\n"
        style_rules += f"The user prefers these styles for the occasion: {', '.join(preferred_styles)}.\n"
        style_rules += "To achieve this, strongly prefer candidates matching these color/fabric palettes:\n"
        
        for style in preferred_styles:
            if style in STYLE_PROFILES:
                colors = ", ".join(STYLE_PROFILES[style].get("colors", []))
                style_rules += f"- {style.title()}: Colors ({colors})\n"
        style_rules += "\n"

    system_prompt = (
        "You are an expert AI Fashion Stylist.\n"
        "Your job is to select the BEST outfit from a pre-approved list of candidates.\n\n"
        "RULES:\n"
        "1. You MUST build a complete, cohesive outfit containing a Top, Bottom, Footwear, and Accessory (or a Full Body item instead of Top/Bottom).\n"
        "2. You MUST prioritize using items from the 'candidates' arrays. However, if 'candidates' is missing an item for a required slot (like a top or bottom), you MUST invent an ideal item for that slot to complete the outfit.\n"
        "3. You MUST output EXACTLY the keys shown in the JSON OUTPUT FORMAT. DO NOT ADD ANY OTHER KEYS to the 'outfit' object.\n"
        "4. AESTHETICS: Do not match the exact same color for top and bottom unless it is a coordinated suit or set. Ensure the outfit is cohesive.\n"
        "5. CRITICAL: If you invent any items because they were missing from the candidates, you MUST include them in your 'outfit' AND ALSO list them in the 'missing' array formatted as 'Category: Specific Suggestion' (e.g., 'Footwear: White Sneakers').\n"
        "6. CRITICAL: Do not layer tops and bottoms under a full body outfit.\n"
        "7. You MUST output ONLY valid JSON. Do not include markdown blocks like ```json or any conversational text outside the JSON.\n\n"
        f"{occasion_rules}"
        f"{style_rules}"
        "JSON OUTPUT FORMAT:\n"
        f"{json_format}"
    )
    
    vibe_str = candidate_json.get('vibe', '')
    vibe_line = f"- Vibe: {vibe_str.title()}\n" if vibe_str else ""
    
    user_prompt = (
        f"CONTEXT:\n"
        f"- Occasion: {occasion.title()}\n"
        f"- Weather: {candidate_json.get('weather', '').title()}\n"
        f"{vibe_line}\n"
        f"Here are the candidates and missing items:\n\n"
        f"{candidates_str}\n\n"
        f"Generate the JSON outfit now. In your 'reason' field, make sure to explain why the outfit works for this specific occasion, weather, and vibe."
    )
    
    return system_prompt, user_prompt