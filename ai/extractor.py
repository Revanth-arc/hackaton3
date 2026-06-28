import logging
import time
import requests
from ai.validator import parse_and_validate, ExtractedEntitiesDTO, ExtractionError

logger = logging.getLogger(__name__)

def extract_fir_entities(raw_text: str) -> ExtractedEntitiesDTO:
    """Extracts FIR entities from raw text using local Ollama LLM."""
    if not raw_text or len(raw_text.split()) < 10:
        raise ExtractionError("Garbage In, Graceful Out: Extracted text is too short or unreadable.")

    prompt = f"""
    Extract the following details from the complaint text below. Return ONLY a JSON object.
    Required keys: victim, accused, date, time, location, crime_type, vehicles (list), weapons (list), stolen_items (list), sections (list), summary.
    If a list is empty, return an empty array [].
    
    Complaint Text:
    {raw_text}
    """
    
    url = "http://127.0.0.1:11434/api/generate"
    model = "qwen2.5:3b" # Default to lightweight model for CPU
    
    for attempt in range(3):
        start_time = time.time()
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result_json = response.json().get('response', '')
            dto = parse_and_validate(result_json)
            
            elapsed = time.time() - start_time
            logger.info(f"LLM Extraction completed on attempt {attempt+1} in {elapsed:.2f} seconds.")
            return dto
            
        except ExtractionError as e:
            logger.warning(f"Attempt {attempt+1} failed validation: {e}. Retrying...")
            prompt += f"\\n\\nError in previous output: {e}. Please ensure output is STRICTLY valid JSON matching the schema."
        except Exception as e:
            logger.error(f"LLM API Error on attempt {attempt+1}: {e}")
            
    raise ExtractionError("Failed to extract valid FIR entities after 3 attempts.")
