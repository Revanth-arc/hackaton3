from __future__ import annotations

import logging
import os
import re
import time

import requests

from ai.validator import ExtractedEntitiesDTO, ExtractionError, parse_and_validate

logger = logging.getLogger(__name__)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
ALLOW_HEURISTIC_FALLBACK = os.getenv("ALLOW_HEURISTIC_FALLBACK", "true").lower() == "true"


def _extract_with_heuristics(raw_text: str) -> ExtractedEntitiesDTO:
    """Create a usable draft when the local LLM is unavailable on hosted deployments."""
    cleaned_text = " ".join(raw_text.split())
    vehicle_numbers = sorted(
        set(re.findall(r"\b[A-Z]{2}\s?\d{1,2}\s?[A-Z]{1,3}\s?\d{3,4}\b", raw_text.upper()))
    )
    dates = re.findall(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", raw_text)
    times = re.findall(r"\b\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?\b", raw_text)

    lowered = raw_text.lower()
    crime_type = "theft" if any(word in lowered for word in ("stolen", "theft", "robbed")) else None
    sections = ["BNS/IPC section review required"] if crime_type else []

    return ExtractedEntitiesDTO(
        date=dates[0] if dates else None,
        time=times[0] if times else None,
        crime_type=crime_type,
        vehicles=vehicle_numbers,
        sections=sections,
        summary=cleaned_text[:800] if cleaned_text else None,
    )


def _select_ollama_model() -> str:
    """Use the configured model when available, otherwise pick an installed local model."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = [model["name"] for model in response.json().get("models", [])]
    except requests.exceptions.RequestException as exc:
        raise ExtractionError(f"Ollama API Error: Is Ollama running? Details: {exc}") from exc

    if DEFAULT_OLLAMA_MODEL in models:
        return DEFAULT_OLLAMA_MODEL

    preferred_models = ["qwen2.5:3b", "qwen3.5:latest", "gemma3:4b"]
    for model in preferred_models:
        if model in models:
            logger.warning(
                "Configured Ollama model %s is not installed. Falling back to %s.",
                DEFAULT_OLLAMA_MODEL,
                model,
            )
            return model

    if models:
        logger.warning(
            "Configured Ollama model %s is not installed. Falling back to %s.",
            DEFAULT_OLLAMA_MODEL,
            models[0],
        )
        return models[0]

    raise ExtractionError(
        "Ollama is running, but no models are installed. "
        "Install one with `ollama pull qwen2.5:3b` or set OLLAMA_MODEL."
    )


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

    try:
        model = _select_ollama_model()
    except ExtractionError:
        if ALLOW_HEURISTIC_FALLBACK:
            logger.warning("Ollama is unavailable. Falling back to heuristic extraction.")
            return _extract_with_heuristics(raw_text)
        raise
    last_error: Exception | None = None

    for attempt in range(3):
        start_time = time.time()
        try:
            payload: dict[str, str | bool] = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            }
            response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
            response.raise_for_status()

            response_data = response.json()
            result_json = response_data.get("response") or response_data.get("thinking", "")
            dto = parse_and_validate(result_json)

            elapsed = time.time() - start_time
            logger.info(
                f"LLM Extraction completed on attempt {attempt+1} in {elapsed:.2f} seconds."
            )
            return dto

        except ExtractionError as e:
            last_error = e
            logger.warning(f"Attempt {attempt+1} failed validation: {e}. Retrying...")
            prompt += f"\n\nError in previous output: {e}. Please ensure output is STRICTLY valid JSON matching the schema."
        except requests.exceptions.RequestException as e:
            if ALLOW_HEURISTIC_FALLBACK:
                logger.warning("Ollama generation failed. Falling back to heuristic extraction.")
                return _extract_with_heuristics(raw_text)
            raise ExtractionError(
                f"Ollama API Error: Is Ollama running? Is the '{model}' model installed? Details: {e}"
            )
        except Exception as e:
            last_error = e
            logger.error(f"LLM API Error on attempt {attempt+1}: {e}")

    raise ExtractionError(
        f"Failed to extract valid FIR entities after 3 attempts. Last error: {last_error}"
    )
