
import json
import re
import sys
import warnings
warnings.filterwarnings('ignore')

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import easyocr
from travel_context_ai.config import *

print("="*60)
print("Loading EasyOCR...")
print("="*60)

reader = easyocr.Reader(["en"], gpu=(DEVICE=="cuda"), verbose=False)

results = reader.readtext(str(TICKET_IMAGE))

detections=[]
for _, text, conf in results:
    detections.append({"text": text, "confidence": round(conf,3)})

ocr_text = " ".join(d["text"] for d in detections)

ocr_data={
    "ocr_text": ocr_text,
    "detections": detections
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(OCR_OUTPUT,"w",encoding="utf-8") as f:
    json.dump(ocr_data,f,indent=4,ensure_ascii=False)

# Quick heuristic extraction for clean summary display
origin = "Unknown"
destination = "Unknown"
travel_date = "Unknown"

date_matches = re.findall(r'\b\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\b', ocr_text)
if date_matches:
    travel_date = date_matches[-1]

cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Goa", "Pune", "Jaipur", "Kochi", "Ahmedabad"]
found_cities = [c for c in cities if re.search(r'\b' + re.escape(c) + r'\b', ocr_text, re.IGNORECASE)]
if len(found_cities) >= 2:
    origin = found_cities[0]
    destination = found_cities[1]
elif len(found_cities) == 1:
    destination = found_cities[0]

print("\n" + "=" * 60)
print("OCR Summary")
print("=" * 60)
print(f"Origin      : {origin}")
print(f"Destination : {destination}")
print(f"Travel Date : {travel_date}")
try:
    print("\n✓ OCR Complete")
except UnicodeEncodeError:
    print("\n[OK] OCR Complete")
print(f"Saved to    : {OCR_OUTPUT.name}")

