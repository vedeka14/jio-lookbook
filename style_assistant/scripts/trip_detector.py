import json
import logging
import ollama
import requests
import base64

import easyocr
import io

def extract_destination_from_ticket(image_bytes: bytes) -> str:
    """Uses EasyOCR to read text, then Mistral to extract destination."""
    logging.info("[TripDetector] Running EasyOCR on uploaded ticket...")
    try:
        reader = easyocr.Reader(["en"], verbose=False)
        result = reader.readtext(image_bytes)
        
        # Join all extracted text into one giant string
        raw_text = " ".join([text for _, text, _ in result])
        
        # Ask Mistral to pull the destination from the raw text
        prompt = (
            f"Here is raw text extracted from a flight ticket/boarding pass: {raw_text}\n\n"
            "Look carefully for the 'To', 'Arrival', or 'Destination' city. DO NOT output the departure or 'From' city. "
            "What is the final arrival destination city? Output ONLY the name of the destination city (e.g. 'Goa', 'Paris', 'Tokyo'), nothing else. If you cannot find one, output 'Unknown'."
        )
        
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        content = response["message"]["content"].strip().replace("'", "").replace('"', "").replace("\n", " ").strip()
        
        if content.lower() == "unknown" or len(content) > 30:
            return ""
        return content
        
    except Exception as e:
        logging.error(f"[TripDetector] EasyOCR/Mistral pipeline failed: {e}")
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
