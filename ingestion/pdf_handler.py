import logging
import time

import cv2
import fitz  # PyMuPDF
import numpy as np

from ocr.image_preprocessing import preprocess_image
from ocr.paddle_reader import extract_text

logger = logging.getLogger(__name__)


def process_pdf(file_bytes: bytes, progress_callback=None) -> dict:
    """
    Processes a PDF file, extracting text natively if available,
    otherwise falling back to OCR on a per-page basis.
    """
    start_time = time.time()

    # Load PDF from bytes
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_count = doc.page_count

    extracted_text_blocks = []
    ocr_used = False

    for i, page in enumerate(doc):
        if progress_callback:
            progress_callback(i + 1, page_count, "reading")

        # Try extracting text natively
        text = page.get_text("text").strip()

        # Threshold to determine if it's a scanned page vs text PDF
        if len(text) > 50:
            extracted_text_blocks.append(text)
        else:
            if progress_callback:
                progress_callback(i + 1, page_count, "ocr")

            ocr_used = True
            # Render page to image for OCR
            pix = page.get_pixmap(dpi=200)  # Good balance of quality and speed

            # Convert fitz pixmap to numpy array for opencv/paddle
            # pix.samples contains the raw image data
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

            # Convert RGB/RGBA to BGR for OpenCV
            if pix.n == 4:
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)

            # Use existing pipeline
            # Wait, preprocess_image expects bytes. We can either pass bytes or modify it.
            # Let's just convert img_bgr to bytes
            is_success, buffer = cv2.imencode(".png", img_bgr)
            if is_success:
                img_bytes = buffer.tobytes()
                enhanced_img = preprocess_image(img_bytes)
                try:
                    page_ocr_text = extract_text(enhanced_img)
                    extracted_text_blocks.append(page_ocr_text)
                except Exception as e:
                    logger.error(f"OCR failed on page {i+1}: {e}")
                    extracted_text_blocks.append(f"[OCR Failed for Page {i+1}]")
            else:
                logger.error(f"Failed to encode page {i+1} to image.")

    doc.close()

    final_text = "\n\n".join(extracted_text_blocks)

    method = "Native PDF + OCR fallback" if ocr_used else "Native PDF Extraction"

    return {
        "text": final_text,
        "page_count": page_count,
        "processing_method": method,
        "ocr_required": ocr_used,
        "time_taken": time.time() - start_time,
    }
