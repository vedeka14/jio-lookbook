
import os
import json
import base64
import requests
from pathlib import Path
from fashion_ai.wardrobeinference.config import PHOTOS_DIR, WARDROBE_FILE

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def enrich_metadata(cat):
    c = cat.lower()
    if c in ["saree", "lehenga", "kurta", "kurti", "churidaar", "anarkali", "sherwani"]:
        return {"style": "traditional/ethnic", "occasion": ["wedding", "festival", "traditional"], "weather": "all", "fit": "relaxed"}
    if c in ["shirt", "trousers", "blazer", "suit", "pants"]:
        return {"style": "versatile/smart-casual", "occasion": ["office", "dinner", "business", "casual day"], "weather": "all", "fit": "tailored"}
    if c in ["t-shirt", "jeans", "shorts", "skirt", "sneakers", "polo", "hoodie"]:
        return {"style": "casual/street", "occasion": ["travel", "sightseeing", "casual day", "cafe"], "weather": "all", "fit": "regular"}
    if c in ["dress", "maxi", "midi", "gown"]:
        return {"style": "elegant/chic", "occasion": ["dinner", "party", "date", "resort"], "weather": "warm", "fit": "flowy"}
    if c in ["jacket", "coat", "sweater", "cardigan"]:
        return {"style": "layering/cozy", "occasion": ["travel", "outdoor", "evening"], "weather": "cold", "fit": "relaxed"}
    return {"style": "versatile", "occasion": ["casual day"], "weather": "all", "fit": "regular"}

def ask_llava(img_b64):
    payload = {
        "model": "llava",
        "messages": [
            {
                "role": "user",
                "content": "You are a strict fashion AI. Output ONLY a raw JSON array containing a list of clothing items worn in this image. For each item, give the \"category\" (e.g. Jeans, Blazer, Skirt, T-Shirt) and the \"color\". Do not use markdown. Example: [{\"category\": \"Jeans\", \"color\": \"Blue\"}]",
                "images": [img_b64]
            }
        ],
        "stream": False
    }
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload)
        content = response.json().get("message", {}).get("content", "")
        content = content.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(content)
        except:
            # Sometime it might prefix with something, try to find bracket
            idx = content.find("[")
            edx = content.rfind("]")
            if idx != -1 and edx != -1:
                return json.loads(content[idx:edx+1])
            return []
    except Exception as e:
        print("LLaVA Error:", e)
        return []

def build_wardrobe(silent=False):
    if not silent:
        print("="*60)
        print("Building Wardrobe using LLaVA (Vision LLM)")
        print("="*60)
        
    wardrobe_items = []
    
    if not PHOTOS_DIR.exists():
        return wardrobe_items
        
    for image_name in os.listdir(PHOTOS_DIR):
        if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
            
        img_path = PHOTOS_DIR / image_name
        if not silent:
            print(f"Scanning {image_name}...")
            
        img_b64 = get_base64_image(img_path)
        items = ask_llava(img_b64)
        
        seen_cats = set()
        has_full_body = any(i.get("category", "").lower() in ["dress", "swimsuit", "bikini", "gown", "kurta", "saree"] for i in items)
        
        for item in items:
            cat = item.get("category", "Unknown").title()
            col = item.get("color", "Unknown").title()
            
            if cat == "Unknown": continue
            
            cat_lower = cat.lower()
            
            # 1. Deduplicate
            if cat_lower in seen_cats:
                continue
                
            # 2. Filter out heavy layer hallucinations for beach wear
            if cat_lower in ["blazer", "jacket", "coat"]:
                continue
                
            # 3. Filter out shorts/pants if wearing a full body outfit (Dress/Swimsuit/Saree)
            if has_full_body and cat_lower in ["shorts", "pants", "jeans", "trousers"]:
                continue
                
            seen_cats.add(cat_lower)
            meta = enrich_metadata(cat_lower)
            
            wardrobe_items.append({
                "image": image_name,
                "category": cat,
                "color": col,
                "confidence": 0.99,
                "crop": image_name,
                "style": meta["style"],
                "occasion": meta["occasion"],
                "weather": meta["weather"],
                "fit": meta["fit"]
            })
            if not silent:
                print(f"  - Detected: {col} {cat}")

        # Save incrementally after every image to prevent data loss on crash
        with open(WARDROBE_FILE, "w", encoding="utf-8") as f:
            json.dump(wardrobe_items, f, indent=4)
        
    if not silent:
        print(f"Total Unique Items: {len(wardrobe_items)}")
        print("Saved to wardrobe.json")
        
    return wardrobe_items

if __name__ == "__main__":
    build_wardrobe()

