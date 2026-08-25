import json
import logging
import ollama
import requests
import base64

def extract_destination_from_ticket(image_bytes: bytes) -> str:
    """Uses LLaVA vision model to extract the destination city/location from an image."""
    logging.info("[TripDetector] Running LLaVA OCR on uploaded ticket...")
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    
    payload = {
        "model": "llava",
        "messages": [
            {
                "role": "user",
                "content": "Analyze this travel ticket/boarding pass. What is the final destination city or location? Output ONLY the name of the destination city, nothing else. If you cannot find one, output 'Unknown'.",
                "images": [img_b64]
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        content = response.json().get("message", {}).get("content", "").strip()
        # Clean up any potential markdown or extra punctuation
        content = content.replace("'", "").replace('"', "").replace("\n", " ").strip()
        if content.lower() == "unknown" or len(content) > 30:
            return ""
        return content
    except Exception as e:
        logging.error(f"[TripDetector] LLaVA OCR failed: {e}")
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
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Destination: {destination}"}
            ]
        )
        
        response_text = response['message']['content']
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
