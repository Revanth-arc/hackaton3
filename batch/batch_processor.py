import hashlib
import logging
import time
import uuid

from ai.extractor import ExtractionError, extract_fir_entities
from batch.duplicate_detector import check_duplicate

from database.repository import get_complaint_by_hash
from database.sqlite import save_fir_draft
from ingestion.file_detector import detect_file_type
from ingestion.pdf_handler import process_pdf
from ocr.image_preprocessing import preprocess_image
from ocr.paddle_reader import extract_text

logger = logging.getLogger(__name__)


def process_batch(uploaded_files, process_callback=None, pdf_progress_callback=None, on_duplicates: str = "reuse_cached"):
    """Sequentially processes uploaded files.

    on_duplicates:
      - "reuse_cached" (default): if the DB already has a record for the file hash, skip OCR/LLM and return cached.
      - "reprocess_anyway": force re-running OCR/LLM even if hash exists.

    NOTE: AI extraction logic is preserved via `process_single_file`.
    """
    results = []

    for idx, uploaded_file in enumerate(uploaded_files):
        filename = uploaded_file.name
        file_bytes = uploaded_file.read()

        if process_callback:
            process_callback(idx=idx, total=len(uploaded_files), filename=filename)

        # Duplicate handling policy
        if on_duplicates == "reuse_cached":
            result = process_single_file(file_bytes, filename, pdf_progress_callback)
        else:
            # Reprocess: temporarily bypass cache by computing hash and checking.
            # We call existing `process_single_file`, but it always caches when a duplicate exists.
            # To avoid modifying AI extraction logic deeply, we implement a minimal workaround:
            # delete existing record for the same hash, if any.
            dup = check_duplicate(file_bytes)
            if dup.is_duplicate and dup.existing_data:
                # We do not have a delete-by-hash API; fall back to calling process_single_file after removing cached record.
                # This function will not be used unless on_duplicates == reprocess_anyway.
                from database.repository import delete_complaint

                delete_complaint(dup.existing_data["id"])
            result = process_single_file(file_bytes, filename, pdf_progress_callback)

        results.append(result)

    return results


def process_single_file(file_bytes: bytes, filename: str, pdf_progress_callback=None):
    """Processes a single file and returns the result dictionary."""
    start_time = time.time()

    file_type = detect_file_type(file_bytes)
    is_pdf = "pdf" in file_type.lower()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # Check duplicate
    existing = get_complaint_by_hash(file_hash)
    if existing:
        return {
            "status": "cached",
            "filename": filename,
            "data": existing,
            "hash": file_hash,
            "time": time.time() - start_time,
        }

    complaint_id = str(uuid.uuid4())
    metadata = {
        "filename": filename,
        "file_type": file_type,
        "page_count": 1,
        "file_hash": file_hash,
        "processing_method": "OCR",
        "ocr_required": True,
    }

    raw_text = ""

    # Ingestion & OCR
    try:
        ocr_start = time.time()
        if is_pdf:
            pdf_result = process_pdf(file_bytes, pdf_progress_callback)
            raw_text = pdf_result["text"]
            metadata["page_count"] = pdf_result["page_count"]
            metadata["processing_method"] = pdf_result["processing_method"]
            metadata["ocr_required"] = pdf_result["ocr_required"]
        else:
            enhanced_img = preprocess_image(file_bytes)
            raw_text = extract_text(enhanced_img)
        ocr_duration = time.time() - ocr_start
    except Exception as e:
        logger.error(f"OCR failed for {filename}: {e}")
        return {
            "status": "error",
            "filename": filename,
            "error": f"OCR failed: {str(e)}",
            "step": "OCR",
        }

    # AI Extraction
    try:
        llm_start = time.time()
        dto = extract_fir_entities(raw_text)
        llm_duration = time.time() - llm_start
    except ExtractionError as e:
        logger.error(f"Extraction failed for {filename}: {e}")
        return {"status": "error", "filename": filename, "error": str(e), "step": "AI Extraction"}
    except Exception as e:
        logger.error(f"Unknown extraction error for {filename}: {e}")
        return {"status": "error", "filename": filename, "error": str(e), "step": "AI Extraction"}

    # Save to DB
    try:
        db_start = time.time()
        fir_id = save_fir_draft(dto, complaint_id, metadata)
        db_duration = time.time() - db_start
    except Exception as e:
        logger.error(f"Database save failed for {filename}: {e}")
        return {"status": "error", "filename": filename, "error": str(e), "step": "Database"}

    return {
        "status": "success",
        "filename": filename,
        "fir_id": fir_id,
        "complaint_id": complaint_id,
        "raw_text": raw_text,
        "json": dto.model_dump(),
        "metadata": metadata,
        "metrics": {
            "ocr_time": ocr_duration,
            "llm_time": llm_duration,
            "db_time": db_duration,
            "total_time": time.time() - start_time,
        },
    }
