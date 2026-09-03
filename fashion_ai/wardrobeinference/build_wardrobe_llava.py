
import os
import json
import base64
import requests
from pathlib import Path
from fashion_ai.wardrobeinference.config import PHOTOS_DIR, WARDROBE_FILE

def get_base64_image(image_path):
    from io import BytesIO
    from PIL import Image
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
        img = Image.open(BytesIO(img_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((512, 512))
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

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

from groq import Groq
import streamlit as st

def get_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY")
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def ask_llava(img_b64):
    client = get_groq_client()
    if not client: return []
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "You are a strict fashion AI. Analyze the image and output ONLY a raw JSON array containing a list of clothing items worn. You MUST be able to recognize standard Western wear (e.g. Jeans, Blazer, Skirt, T-Shirt, Shrug) AND Indian/Indo-Western ethnic wear (e.g. Kurta, Saree, Sharara, Jodhpuri Set, Fishtail Lehenga). For each item, give the 'category' and the 'color'. Do not use markdown. Example: [{\"category\": \"Sharara\", \"color\": \"Pink\"}]"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ],
            temperature=0.0
        )
        import re
        raw_content = response.choices[0].message.content
        content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
        content = content.replace("```json", "").replace("```", "").strip()
        idx = content.find("[")
        edx = content.rfind("]")
        if idx != -1 and edx != -1:
            return json.loads(content[idx:edx+1])
        return []
    except Exception as e:
        print("Groq Vision Error:", e)
        return []

def build_wardrobe(silent=False):
    if not silent:
        print("="*60)
        print("Building Wardrobe using LLaVA (Vision LLM)")
        print("="*60)
        
    wardrobe_items = []
    if WARDROBE_FILE.exists():
        try:
            with open(WARDROBE_FILE, "r", encoding="utf-8-sig") as f:
                loaded_items = json.load(f)
                # Auto-clean any bogus items that were saved previously
                wardrobe_items = [i for i in loaded_items if "not applicable" not in i.get("category", "").lower() and "none" not in i.get("category", "").lower()]
            if not silent:
                print(f"Loaded {len(wardrobe_items)} existing items from database. New scans will be appended.")
        except Exception as e:
            print(f"Could not load existing wardrobe: {e}")
    
    if not PHOTOS_DIR.exists():
        return wardrobe_items
        
    existing_images = {item.get("image") for item in wardrobe_items if item.get("image")}
    
    for image_name in os.listdir(PHOTOS_DIR):
        if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
            
        if image_name in existing_images:
            if not silent:
                print(f"Skipping {image_name} (already in database)...")
            continue
            
        img_path = PHOTOS_DIR / image_name
        if not silent:
            print(f"Scanning {image_name}...")
            
        img_b64 = get_base64_image(img_path)
        raw_items = ask_llava(img_b64)
        
        # Guard against hallucinated non-dictionary items (e.g. if the AI returned a list of strings)
        items = [i for i in raw_items if isinstance(i, dict)] if isinstance(raw_items, list) else []
        
        seen_cats = set()
        has_full_body = any(i.get("category", "").lower() in ["dress", "swimsuit", "bikini", "gown", "kurta", "saree"] for i in items)
        
        for item in items:
            cat = item.get("category", "Unknown").title()
            col = item.get("color", "Unknown").title()
            
            if cat == "Unknown": continue
            
            cat_lower = cat.lower()
            if "not applicable" in cat_lower or "none" in cat_lower:
                continue
            
            # 1. Deduplicate
            if cat_lower in seen_cats:
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


if __name__ == '__main__':
    build_wardrobe(silent=False)
