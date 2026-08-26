# candidate_builder/selector.py
import logging
from recommendation_engine.metadata.clothing import CLOTHING_META
from recommendation_engine.metadata.templates import OUTFIT_TEMPLATES
from recommendation_engine.metadata.occasions import OCCASIONS

def build_candidate_json(scored_items, occasion_str, weather_str="", vibe_str="", preset_template=None):
    """
    Groups scored items by type (top, bottom, full_body, footwear, accessory).
    Checks against OUTFIT_TEMPLATES to determine if required slots are missing.
    Returns the Candidate JSON object.
    """
    logging.info("[Selector] Building Candidate JSON...")
    
    candidates = {
        "top": [],
        "bottom": [],
        "full_body": [],
        "outerwear": [],
        "footwear": [],
        "accessory": []
    }
    
    for item in scored_items:
        cat = item.get("category", "").lower()
        meta = CLOTHING_META.get(cat, {})
        ctype = meta.get("type", "other")
        
        if ctype in candidates:
            # Format nicely for the LLM
            color = item.get("color", "").title()
            display_name = f"{color} {cat.title()}"
            candidates[ctype].append({
                "item": display_name,
                "score": item.get("score", 0),
                "category": cat.lower()
            })
            
    # Check templates for missing required slots
    occ = occasion_str.lower() if occasion_str else "default"
    template = OUTFIT_TEMPLATES.get(occ, OUTFIT_TEMPLATES["default"])
    
    missing = []
    
    if preset_template:
        # If we have a strict preset template, skip the generic required_options logic
        for slot in ["top", "bottom", "full_body", "outerwear", "footwear", "accessory"]:
            if slot in preset_template:
                valid_options = preset_template[slot]
                filtered_cands = []
                for c in candidates[slot]:
                    cat_lower = c["category"].lower()
                    if any(opt.lower() in cat_lower or cat_lower in opt.lower() for opt in valid_options):
                        filtered_cands.append(c)
                candidates[slot] = filtered_cands
                
                if len(candidates[slot]) == 0:
                    missing.append({
                        "category": " or ".join(valid_options).title(),
                        "priority": "High",
                        "reason": f"Required for curated {occ} look."
                    })
            else:
                candidates[slot] = []
    else:
        # We must satisfy at least one required_options array, or the "required" array
        satisfied = False
        chosen_path = None
        if "required_options" in template:
            best_path = None
            max_cands_in_path = -1

            # Check if any path is satisfied (e.g. top+bottom OR full_body)
            for req_path in template["required_options"]:
                path_satisfied = True
                cands_count = 0
                for slot in req_path:
                    slot_cands = len(candidates[slot])
                    cands_count += slot_cands
                    if slot_cands == 0:
                        path_satisfied = False
                
                if path_satisfied:
                    satisfied = True
                    chosen_path = req_path
                    break
                
                if cands_count > max_cands_in_path:
                    max_cands_in_path = cands_count
                    best_path = req_path
                    
            if not satisfied:
                # If no path is satisfied, default to the path where the user has the most items
                chosen_path = best_path
                for slot in chosen_path:
                    if len(candidates[slot]) == 0:
                        missing.append({
                            "category": slot.title(),
                            "priority": "High",
                            "reason": f"Required for {occ} outfit."
                        })
                        
            # WIPE candidates that belong to mutually exclusive paths
            # So the LLM doesn't try to use them both
            all_options = set()
            for p in template["required_options"]:
                all_options.update(p)
            for opt in all_options:
                if opt not in chosen_path:
                    candidates[opt] = []
        else:
            # Standard required array
            for slot in template.get("required", []):
                if len(candidates[slot]) == 0:
                    missing.append({
                        "category": slot.title(),
                        "priority": "High",
                        "reason": f"Required for {occ} outfit."
                    })

    valid_top_bottom_pairs = []
    if len(candidates["top"]) > 0 and len(candidates["bottom"]) > 0:
        from recommendation_engine.metadata.compatibility import COMPATIBILITY_RULES
        for t in candidates["top"]:
            t_cat = t["category"]
            rules = COMPATIBILITY_RULES.get(t_cat, {})
            avoid = rules.get("avoid_pair_with", [])
            for b in candidates["bottom"]:
                b_cat = b["category"]
                if b_cat not in avoid:
                    valid_top_bottom_pairs.append({
                        "top": t["item"],
                        "bottom": b["item"]
                    })
        if len(valid_top_bottom_pairs) > 0:
            # Wipe independent arrays so LLM doesn't mix and match independently
            candidates["top"] = []
            candidates["bottom"] = []
        else:
            # No valid pairs found! Clear bottoms so we are forced to buy a compatible bottom
            logging.warning("[Selector] No compatible top/bottom pairs found. Clearing bottoms.")
            candidates["bottom"] = []
            missing.append({
                "category": "Bottom",
                "priority": "High",
                "reason": "None of your bottoms matched your tops."
            })
        
    preferred_styles = []
    if occasion_str:
        occ_prof = OCCASIONS.get(occasion_str.lower(), {})
        preferred_styles = occ_prof.get("preferred_styles", [])

    candidate_json = {
        "occasion": occasion_str,
        "weather": weather_str,
        "vibe": vibe_str,
        "preferred_styles": preferred_styles,
        "valid_top_bottom_pairs": valid_top_bottom_pairs,
        "preset_template": preset_template,
        "candidates": candidates,
        "missing_items": missing
    }
    
    logging.info(f"[Selector] Missing items identified: {len(missing)}")
    return candidate_json
