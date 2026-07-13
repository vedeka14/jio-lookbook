import json
import re
import easyocr
from ollama import chat

# ==================================================
# Project Configuration
# ==================================================

from config import *

# ==================================================
# Initialize EasyOCR
# ==================================================

print("=" * 60)
print("Loading EasyOCR...")
print("=" * 60)

reader = easyocr.Reader(
    ["en"],
    gpu=(DEVICE == "cuda")
)

# ==================================================
# Read Ticket
# ==================================================

print(f"\nReading ticket:\n{TICKET_IMAGE}\n")

results = reader.readtext(str(TICKET_IMAGE))

# ==================================================
# Extract OCR Text
# ==================================================

ocr_text = []

print("=" * 60)
print("Detected Text")
print("=" * 60)

for bbox, text, confidence in results:

    print(f"{text}   ({confidence:.2f})")

    ocr_text.append({
        "text": text,
        "confidence": round(confidence, 3)
    })

# ==================================================
# Combine OCR Text
# ==================================================

full_text = " ".join(item["text"] for item in ocr_text)

print("\n" + "=" * 60)
print("Full OCR Text")
print("=" * 60)
print(full_text)

# ==================================================
# Prompt for Ollama
# ==================================================

prompt = f"""
You are an AI information extraction system.

Extract the travel details from this airline ticket.

IMPORTANT RULES

- Return CITY names, NOT airport codes.
- Example:
    Origin: Mumbai
    Destination: North Goa

- Never return airport codes like:
  BOM
  GOX
  DEL
  BLR
  HYD
  MAA
  CCU

- Ignore passenger names.
- Ignore PNR.
- Ignore booking reference.
- Ignore barcode.
- Ignore payment status.

Return ONLY valid JSON.

Schema:

{{
    "origin": "",
    "destination": "",
    "travel_date": ""
}}

OCR TEXT:

{full_text}
"""

# ==================================================
# Ask Ollama
# ==================================================

print("\n" + "=" * 60)
print("Sending OCR text to Ollama...")
print("=" * 60)

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    options={
        "temperature": 0
    }
)

llm_output = response.message.content

print("\n" + "=" * 60)
print("LLM Response")
print("=" * 60)
print(llm_output)

# ==================================================
# Parse JSON
# ==================================================

trip_info = {
    "origin": None,
    "destination": None,
    "travel_date": None
}

try:

    cleaned = re.sub(
        r"<think>.*?</think>",
        "",
        llm_output,
        flags=re.DOTALL
    )

    json_match = re.search(
        r"\{.*\}",
        cleaned,
        re.DOTALL
    )

    if json_match:
        trip_info = json.loads(json_match.group())
    else:
        raise ValueError("No JSON found.")

except Exception as e:

    print("\nWarning:", e)
    print("Could not parse Ollama response.")

# ==================================================
# Backup Date Extraction
# ==================================================

if not trip_info.get("travel_date"):

    match = re.search(
        r"\b\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\b",
        full_text
    )

    if match:
        trip_info["travel_date"] = match.group()

# ==================================================
# Save JSON
# ==================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(OCR_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(
        trip_info,
        f,
        indent=4,
        ensure_ascii=False
    )

# ==================================================
# Display Results
# ==================================================

print("\n" + "=" * 60)
print("Trip Information")
print("=" * 60)

for key, value in trip_info.items():
    print(f"{key:15}: {value}")

print("\n" + "=" * 60)
print("OCR Complete")
print("=" * 60)
print(f"Results saved to:\n{OCR_OUTPUT}")