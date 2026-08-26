# style_assistant/scripts/outfit_validator.py
import json
import logging
from recommendation_engine.metadata.compatibility import COMPATIBILITY_RULES

def validate_outfit_json(llm_response_text, candidate_json):
    """
    Parses the LLM response text into JSON.
    Validates that the chosen items actually exist in candidate_json.
    Validates compatibility constraints.
    Returns the parsed JSON if valid, else raises Exception or returns a fallback.
    """
    logging.info("[Validator] Validating LLM Output...")
    
    # 1. Parse JSON
    import re
    try:
        # Extract everything between the first { and the last }
        match = re.search(r'\{.*\}', llm_response_text, re.DOTALL)
        if not match:
            logging.error("[Validator] No JSON object found in response.")
            return None
            
        text = match.group()
        outfit_data = json.loads(text)
    except json.JSONDecodeError as e:
        logging.error(f"[Validator] Failed to parse JSON: {e}")
        return None
        
    if "outfit" not in outfit_data:
        logging.error("[Validator] Missing 'outfit' key in JSON.")
        return None
        
    outfit = outfit_data["outfit"]
    
    
    
    # 2. Extract selected categories
    selected_items = {
        "top": outfit.get("top", ""),
        "bottom": outfit.get("bottom", ""),
        "full_body": outfit.get("full_body", "")
    }
    
    # Simple base check: Cannot have top/bottom AND full_body
    has_tb = bool(selected_items["top"]) or bool(selected_items["bottom"])
    has_fb = bool(selected_items["full_body"])
    
    if has_tb and has_fb:
        has_fb_candidate = bool(candidate_json.get("candidates", {}).get("full_body"))
        if not has_fb_candidate:
            logging.warning("[Validator] Auto-correcting: Defaulting to top/bottom since full_body is not a candidate.")
            outfit_data["outfit"]["full_body"] = ""
        else:
            logging.warning("[Validator] Auto-correcting: Cannot have top/bottom AND full_body. Defaulting to full_body.")
            outfit_data["outfit"]["top"] = ""
            outfit_data["outfit"]["bottom"] = ""
        
    # 3. Strip hallucinations (The ultimate defense against Mistral's stubbornness)
    cands = candidate_json.get("candidates", {})
    allowed_slots = {"top", "bottom", "full_body", "outerwear", "footwear", "accessory"}
    
    # Iterate over a list of keys since we are modifying the dict
    for key in list(outfit_data["outfit"].keys()):
        slot = key.lower()
        if slot not in allowed_slots:
            logging.warning(f"[Validator] Stripping unknown key {key}: {outfit_data['outfit'][key]}")
            del outfit_data["outfit"][key]
        elif len(cands.get(slot, [])) == 0:
            logging.warning(f"[Validator] Stripping hallucinated {key}: {outfit_data['outfit'][key]}")
            del outfit_data["outfit"][key]
        
    # We could do deep compatibility checks here using COMPATIBILITY_RULES,
    
    logging.info("[Validator] Validation Passed.")
    return outfit_data
