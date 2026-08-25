# candidate_builder/filters.py
import logging

from metadata.clothing import CLOTHING_META
from metadata.occasions import OCCASIONS
from metadata.weather import WEATHER_PROFILES
from metadata.compatibility import COMPATIBILITY_RULES

def filter_by_gender(wardrobe, user_gender):
    """
    Filters out items that belong strictly to the opposite gender.
    Unisex items are always kept.
    """
    logging.info(f"[Filter] Starting gender filter for gender: {user_gender}")
    filtered = []
    user_g = user_gender.lower()
    
    # Map UI terms to metadata terms
    if user_g == "women" or user_g == "woman":
        user_g = "female"
    elif user_g == "men" or user_g == "man":
        user_g = "male"
        
    for item in wardrobe:
        cat = item.get("category", "").lower()
        meta = CLOTHING_META.get(cat, {})
        item_g = meta.get("gender", "unisex")
        
        if item_g == "unisex" or item_g == user_g:
            filtered.append(item)
    logging.info(f"[Filter] Kept {len(filtered)}/{len(wardrobe)} after gender filter.")
    return filtered

def filter_by_weather(wardrobe, weather_str):
    """
    Removes items that are strictly avoided in the current weather.
    """
    logging.info(f"[Filter] Starting weather filter for: {weather_str}")
    if not weather_str:
        return wardrobe
        
    weather = weather_str.lower()
    weather_prof = None
    if any(w in weather for w in ["hot", "warm", "tropical", "sunny", "humid", "summer"]):
        weather_prof = WEATHER_PROFILES.get("hot")
    elif any(w in weather for w in ["cold", "snow", "freezing", "winter", "chilly"]):
        weather_prof = WEATHER_PROFILES.get("cold")
    elif any(w in weather for w in ["rain", "monsoon", "drizzle", "shower"]):
        weather_prof = WEATHER_PROFILES.get("rainy")
    elif any(w in weather for w in ["mild", "breezy", "pleasant", "spring", "autumn"]):
        weather_prof = WEATHER_PROFILES.get("warm")
        
    if not weather_prof:
        return wardrobe
        
    avoid_list = weather_prof.get("avoid", [])
    filtered = []
    for item in wardrobe:
        cat = item.get("category", "").lower()
        if cat not in avoid_list:
            filtered.append(item)
    logging.info(f"[Filter] Kept {len(filtered)}/{len(wardrobe)} after weather filter.")
    return filtered

def filter_by_occasion(wardrobe, occasion_str):
    """
    Removes items that are completely inappropriate for the occasion.
    """
    logging.info(f"[Filter] Starting occasion filter for: {occasion_str}")
    if not occasion_str:
        return wardrobe
        
    occ = occasion_str.lower()
    occ_prof = OCCASIONS.get(occ, None)
    
    if not occ_prof:
        return wardrobe
        
    avoid_list = occ_prof.get("avoid_items", [])
    filtered = []
    for item in wardrobe:
        cat = item.get("category", "").lower()
        if cat not in avoid_list:
            filtered.append(item)
    logging.info(f"[Filter] Kept {len(filtered)}/{len(wardrobe)} after occasion filter.")
    return filtered
