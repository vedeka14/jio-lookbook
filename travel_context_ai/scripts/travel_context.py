
import json
import re
from ollama import chat
from travel_context_ai.config import *

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

Return city names (not airport codes). Infer trip type, weather and packing style.

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

print(json.dumps(context,indent=4))
print("Saved:",outfile)
