import logging
import time
import numpy as np

logger = logging.getLogger(__name__)

def extract_text(enhanced_image: np.ndarray) -> str:
    """Extracts text from an enhanced image using PaddleOCR."""
    start_time = time.time()
    try:
        from paddleocr import PaddleOCR
        # Initialize PaddleOCR (offline, English)
        ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)
        
        result = ocr.ocr(enhanced_image, cls=True)
        
        text_blocks = []
        if result and result[0]:
            for line in result[0]:
                text_blocks.append(line[1][0])
                
        raw_text = "\n".join(text_blocks)
        
        elapsed = time.time() - start_time
        logger.info(f"PaddleOCR text extraction completed in {elapsed:.2f} seconds.")
        return raw_text
    except Exception as e:
        logger.error(f"Error during OCR extraction: {e}")
        raise
