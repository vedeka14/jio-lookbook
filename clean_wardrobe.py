
import json
from pathlib import Path

WARDROBE_FILE = Path("fashion_ai/wardrobeinference/data/wardrobe.json")
with open(WARDROBE_FILE, "r", encoding="utf-8") as f:
    items = json.load(f)

# Group by image
from collections import defaultdict
by_image = defaultdict(list)
for item in items:
    by_image[item["image"]].append(item)

cleaned_items = []
hallucinated_cats = ["blazer", "jacket", "coat"] # user said these are hallucinated

for img, img_items in by_image.items():
    seen_cats = set()
    has_full_body = any(i["category"].lower() in ["dress", "swimsuit", "bikini", "gown"] for i in img_items)
    
    for item in img_items:
        cat = item["category"].lower()
        
        # 1. Deduplicate exact categories
        if cat in seen_cats:
            continue
            
        # 2. Drop heavy layers (Hallucinations in Goa context)
        if cat in hallucinated_cats:
            continue
            
        # 3. If it has a Dress/Swimsuit, it probably doesnt have Shorts/Pants
        if has_full_body and cat in ["shorts", "pants", "jeans", "trousers"]:
            continue
            
        seen_cats.add(cat)
        cleaned_items.append(item)

with open(WARDROBE_FILE, "w", encoding="utf-8") as f:
    json.dump(cleaned_items, f, indent=4)

print(f"Cleaned wardrobe! Reduced from {len(items)} to {len(cleaned_items)} items.")

