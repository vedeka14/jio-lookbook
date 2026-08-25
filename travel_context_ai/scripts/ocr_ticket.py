import json
import re
import sys
import warnings
import cv2
warnings.filterwarnings('ignore')

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import easyocr
from travel_context_ai.config import *

def ocr_ticket(silent=False):
    def _print(*args, **kwargs):
        if not silent:
            print(*args, **kwargs)

    _print("="*60)
    _print("Loading EasyOCR...")
    _print("="*60)

    reader = easyocr.Reader(["en"], gpu=(DEVICE=="cuda"), verbose=False)
    
    # Read manually to avoid any cv2 path issues inside easyocr when combined with yolo
    img = cv2.imread(str(TICKET_IMAGE))
    if img is None:
        raise FileNotFoundError(f"Could not read image: {TICKET_IMAGE}")
        
    results = reader.readtext(img)

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

    _print("\n" + "=" * 60)
    _print("OCR Summary")
    _print("=" * 60)
    _print(f"Origin      : {origin}")
    _print(f"Destination : {destination}")
    _print(f"Travel Date : {travel_date}")
    try:
        _print("\n✓ OCR Complete")
    except UnicodeEncodeError:
        _print("\n[OK] OCR Complete")
    _print(f"Saved to    : {OCR_OUTPUT.name}")

    return {
        "origin": origin,
        "destination": destination,
        "travel_date": travel_date,
        "ocr_text": ocr_text
    }

def main():
    ocr_ticket(silent=False)

if __name__ == "__main__":
    main()
