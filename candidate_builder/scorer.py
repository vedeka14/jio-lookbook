# candidate_builder/scorer.py
import logging
from metadata.occasions import OCCASIONS
from metadata.weather import WEATHER_PROFILES
from metadata.colors import COLOR_MATCH
from collections import Counter

def score_item(item, occasion_str, weather_str, favorite_colors=None):
    """
    Computes a fitness score for a wardrobe item.
    Higher score = better fit.
    """
    if favorite_colors is None:
        favorite_colors = []
        
    score = 0
    cat = item.get("category", "").lower()
    color = item.get("color", "").title()
    
    # 1. Weather Scoring
    if weather_str:
        weather = weather_str.lower()
        weather_prof = None
        if "hot" in weather or "warm" in weather:
            weather_prof = WEATHER_PROFILES.get("hot")
        elif "cold" in weather or "snow" in weather:
            weather_prof = WEATHER_PROFILES.get("cold")
        elif "rain" in weather or "monsoon" in weather:
            weather_prof = WEATHER_PROFILES.get("rainy")
            
        if weather_prof:
            if cat in weather_prof.get("prefer", []):
                score += 3
                
    # 2. Occasion Scoring
    # Wait, occasion styling is handled by matching user's favorite styles maybe?
    # Or just giving points if it's the right vibe. We can skip complex logic for now and just score +2 for favored items.
    # YOLO output doesn't have native "styles" yet unless we map them.
    # Let's keep it simple.
    
    # 3. Color Scoring
    if color in favorite_colors:
        score += 2
        
    # Check if color is complementary to a favorite color
    for fav in favorite_colors:
        if fav in COLOR_MATCH and color in COLOR_MATCH[fav]:
            score += 1
            
    return score

def score_and_sort_candidates(wardrobe, occasion_str, weather_str):
    """
    Takes a filtered wardrobe, scores each item, and sorts descending.
    Extracts favorite colors automatically based on frequency in wardrobe.
    """
    logging.info("[Scorer] Scoring candidates...")
    color_counter = Counter([i.get("color", "").title() for i in wardrobe])
    favorite_colors = [c for c, count in color_counter.most_common(3)]
    
    scored_items = []
    for item in wardrobe:
        s = score_item(item, occasion_str, weather_str, favorite_colors)
        item_copy = item.copy()
        item_copy["score"] = s
        scored_items.append(item_copy)
        
    # Sort by score descending
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    return scored_items
