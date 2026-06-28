import logging
import time
import requests
from ai.validator import parse_and_validate, ExtractedEntitiesDTO, ExtractionError

logger = logging.getLogger(__name__)

def extract_fir_entities(raw_text: str) -> ExtractedEntitiesDTO:
    """Extracts FIR entities from raw text using local Ollama LLM."""
    if not raw_text or len(raw_text.strip()) == 0:
        raise ExtractionError("Garbage In, Graceful Out: No text was extracted by OCR.")

    prompt = f"""
    Extract the following details from the complaint text below. Return ONLY a JSON object.
    Required keys: victim (string), accused (string), date (string), time (string), location (string), crime_type (string), vehicles (list of strings), weapons (list of strings), stolen_items (list of strings), sections (list of strings), summary (string).
    For lists (vehicles, weapons, stolen_items, sections), output an array of strings. Do not output objects/dictionaries.
    If a list is empty, return an empty array [].
    
    Complaint Text:
    {raw_text}
    """
    
    url = "http://127.0.0.1:11434/api/generate"
    model = "llama3" # Default to lightweight model for CPU
    
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
            last_error = e
            logger.warning(f"Attempt {attempt+1} failed validation: {e}. Retrying...")
            prompt += f"\n\nError in previous output: {e}. Please ensure output is STRICTLY valid JSON matching the schema."
        except requests.exceptions.RequestException as e:
            raise ExtractionError(f"Ollama API Error: Is Ollama running? Is the '{model}' model installed? Details: {e}")
        except Exception as e:
            last_error = e
            logger.error(f"LLM API Error on attempt {attempt+1}: {e}")
            
    raise ExtractionError(f"Failed to extract valid FIR entities after 3 attempts. Last error: {last_error}")
