
import json
import warnings
warnings.filterwarnings('ignore')
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

print("\nExtracted Ticket Text Preview:")
print("-" * 60)
print(ocr_text[:300] + "..." if len(ocr_text) > 300 else ocr_text)
print("-" * 60)
print("Saved:", OCR_OUTPUT)

