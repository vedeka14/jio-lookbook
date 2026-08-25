import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
import warnings
warnings.filterwarnings("ignore")
import re
from ollama import chat
from travel_context_ai.config import *

def understand_trip(silent=False):
    def _print(*args, **kwargs):
        if not silent:
            print(*args, **kwargs)

    with open(OCR_OUTPUT,"r",encoding="utf-8") as f:
        ocr=json.load(f)

    prompt=f'''
    You are an intelligent travel context extraction assistant.

    Return ONLY valid JSON.

    Schema:
    {{
     "origin":"",
     "destination":"",
     "travel_date":"",
     "trip":"",
     "weather":"",
     "packing_style":"",
     "activities":[],
     "recommendation_tags":[],
     "reasoning":""
    }}

    Return city names (not airport codes). Infer trip type (must be one of: "Beach", "Mountain", "City"), weather and packing style.

    OCR TEXT:
    {ocr["ocr_text"]}
    '''

    response=chat(
        model="qwen3:8b",
        messages=[{"role":"user","content":prompt}],
        options={"temperature":0}
    )

    raw=response.message.content
    raw=re.sub(r"<think>.*?</think>","",raw,flags=re.DOTALL)
    match=re.search(r"\{.*\}",raw,re.DOTALL)
    if not match:
        raise ValueError("No JSON found.")
    context=json.loads(match.group())

    outfile=OUTPUT_DIR/"travel_context.json"
    with open(outfile,"w",encoding="utf-8") as f:
        json.dump(context,f,indent=4,ensure_ascii=False)

    _print("\n" + "=" * 60)
    _print("Trip Summary")
    _print("=" * 60)

    _print(f"\nDestination   : {context.get('destination', 'N/A')}")
    _print(f"Trip Type     : {context.get('trip', 'N/A')}")
    _print(f"Weather       : {context.get('weather', 'N/A')}")

    _print("\nPacking Style")
    packing = context.get('packing_style', [])
    if isinstance(packing, str):
        items = [item.strip(" .") for item in re.split(r',|\band\b', packing) if item.strip(" .")]
        for item in items:
            try:
                _print(f"• {item.capitalize()}")
            except UnicodeEncodeError:
                _print(f"- {item.capitalize()}")
    elif isinstance(packing, list):
        for item in packing:
            try:
                _print(f"• {str(item).capitalize()}")
            except UnicodeEncodeError:
                _print(f"- {str(item).capitalize()}")

    _print("\nActivities")
    activities = context.get('activities', [])
    if isinstance(activities, list):
        for act in activities[:4]:
            try:
                _print(f"• {act}")
            except UnicodeEncodeError:
                _print(f"- {act}")
    elif isinstance(activities, str):
        items = [item.strip(" .") for item in re.split(r',|\band\b', activities) if item.strip(" .")]
        for item in items[:4]:
            try:
                _print(f"• {item.capitalize()}")
            except UnicodeEncodeError:
                _print(f"- {item.capitalize()}")

    try:
        _print("\n✓ Trip Context Generated")
    except UnicodeEncodeError:
        _print("\n[OK] Trip Context Generated")

    return context

def main():
    understand_trip(silent=False)

if __name__ == "__main__":
    main()
