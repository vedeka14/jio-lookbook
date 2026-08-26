import json
import sys
import logging

from recommendation_engine.candidate_builder.filters import filter_by_gender, filter_by_weather, filter_by_occasion
from recommendation_engine.candidate_builder.scorer import score_and_sort_candidates
from recommendation_engine.candidate_builder.selector import build_candidate_json

def recommend(wardrobe, trip, silent=False):
    """
    The main orchestrator for the constraint engine.
    Takes the raw YOLO wardrobe and the trip context.
    Returns the strict Candidate JSON.
    """
    logging.info("=" * 60)
    logging.info("Starting Candidate Builder Orchestration")
    logging.info("=" * 60)

    occasion_str = trip.get("trip", "everyday / casual day")
    weather_str = trip.get("weather", "")
    gender_str = trip.get("gender", "women")
    vibe_str = trip.get("vibe", "")
    
    # Extract strict template
    occ_key_map = {
        "Travel": "travel",
        "Cafe": "cafe",
        "Office": "office",
        "Wedding": "wedding",
        "Party": "party",
        "Casual": "casual day"
    }
    occ_key = occ_key_map.get(occasion_str, "default")
    
    from recommendation_engine.metadata.outfit_presets import OUTFIT_PRESETS
    preset_template = None
    if occ_key in OUTFIT_PRESETS:
        if gender_str in OUTFIT_PRESETS[occ_key]:
            if vibe_str in OUTFIT_PRESETS[occ_key][gender_str]:
                preset_template = OUTFIT_PRESETS[occ_key][gender_str][vibe_str]
    
    # 1. Filter
    filtered_w = filter_by_gender(wardrobe, gender_str)
    filtered_w = filter_by_weather(filtered_w, weather_str)
    filtered_w = filter_by_occasion(filtered_w, occasion_str)
    
    # 2. Score & Sort
    scored_w = score_and_sort_candidates(filtered_w, occasion_str, weather_str)
    
    # 3. Select & Group (Build JSON)
    candidate_json = build_candidate_json(scored_w, occasion_str, weather_str, vibe_str, preset_template)
    
    # Generate privacy safe ajio query
    from recommendation_engine.scripts.privacy_layer import build_ajio_query
    # preferred_colors could just be an empty list or extracted from something if needed. Here we just use an empty list or a default color if needed, but since it's just a demo we can use [] or the occasion name as a dummy.
    # Actually, let's use an empty list for colors since it's not strictly available here
    ajio_query = build_ajio_query(candidate_json.get("missing_items", []), [])
    candidate_json["ajio_query"] = ajio_query
    # demo.py also expects "recommendations", we can just put an empty dict for now, or the candidates
    candidate_json["recommendations"] = candidate_json.get("candidates", {})
    
    if not silent:
        print(json.dumps(candidate_json, indent=2))
        
    return candidate_json