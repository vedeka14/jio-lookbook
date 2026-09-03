import json
import logging
import os
import streamlit as st
from groq import Groq

import base64

def get_groq_client():
    api_key = None
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass
        
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")
        
    if not api_key:
        return None
    return Groq(api_key=api_key)

def extract_destination_from_ticket(image_bytes: bytes) -> str:
    """Uses Groq Vision (Qwen) to read text and extract destination natively."""
    logging.info("[TripDetector] Running Groq Vision on uploaded ticket...")
    try:
        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((512, 512))
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=85)
        compressed_bytes = buf.getvalue()
        
        img_b64 = base64.b64encode(compressed_bytes).decode('utf-8')
        client = get_groq_client()
        if not client:
            return ""

        prompt = (
            "Look carefully at this flight ticket/boarding pass. Look for the 'To', 'Arrival', or 'Destination' city. DO NOT output the departure or 'From' city. "
            "What is the final arrival destination city? Output ONLY the name of the destination city (e.g. 'Goa', 'Paris', 'Tokyo'), nothing else. If you cannot find one, output 'Unknown'."
        )
        
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ],
            temperature=0.0
        )
        
        import re
        raw_content = response.choices[0].message.content
        # Qwen might output reasoning tags
        clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
        
        content = clean_content.replace("'", "").replace('"', "").replace("\n", " ").strip()
        
        if content.lower() == "unknown" or len(content) > 30:
            return ""
        return content
        
    except Exception as e:
        logging.error(f"[TripDetector] Groq Vision pipeline failed: {e}")
        return ""

def detect_trip_context(destination: str, model="mistral") -> dict:
    """
    Uses the LLM to classify a travel destination into a predefined
    Destination Type and Weather category.
    """
    logging.info(f"[TripDetector] Auto-detecting context for: {destination}")
    
    system_prompt = (
        "You are an AI travel assistant. Your job is to classify a given destination "
        "into one of the predefined 'destination_type' and 'weather' categories.\n\n"
        "Valid destination_types: [Beach, Snow Mountains, Hills, City, Countryside, Desert, Cruise, Forest]\n"
        "Valid weathers: [Hot, Warm, Pleasant, Rainy, Cold, Snow]\n\n"
        "OUTPUT FORMAT: You MUST output ONLY a valid JSON object. Do not include markdown blocks or any conversational text.\n"
        "{\n"
        "  \"destination_type\": \"Chosen Type\",\n"
        "  \"weather\": \"Chosen Weather\"\n"
        "}"
    )
    
    try:
        client = get_groq_client()
        if not client:
            return {"destination_type": "City", "weather": "Pleasant"}
            
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Destination: {destination}"}
            ],
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            text = response_text[start_idx:end_idx+1]
            data = json.loads(text)
            
            # Fallbacks just in case the LLM hallucinates categories
            valid_types = ["Beach", "Snow Mountains", "Hills", "City", "Countryside", "Desert", "Cruise", "Forest"]
            valid_weathers = ["Hot", "Warm", "Pleasant", "Rainy", "Cold", "Snow"]
            
            if data.get("destination_type") not in valid_types:
                data["destination_type"] = "City"
            if data.get("weather") not in valid_weathers:
                data["weather"] = "Pleasant"
                
            return data
            
        logging.error("[TripDetector] No valid JSON found in response.")
        return {"destination_type": "City", "weather": "Pleasant"}
        
    except Exception as e:
        logging.error(f"[TripDetector] Error during auto-detection: {e}")
        return {"destination_type": "City", "weather": "Pleasant"}
