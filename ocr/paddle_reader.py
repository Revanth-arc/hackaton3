import logging
import time
import numpy as np

import os
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

logger = logging.getLogger(__name__)

def extract_text(enhanced_image: np.ndarray) -> str:
    """Extracts text from an enhanced image using PaddleOCR."""
    start_time = time.time()
    try:
        from paddleocr import PaddleOCR
        # Initialize PaddleOCR (offline, English) with MKLDNN disabled to bypass PIR bug
        ocr = PaddleOCR(use_angle_cls=True, lang='en', enable_mkldnn=False)
        
        result = ocr.ocr(enhanced_image)
        
        text_blocks = []
        if isinstance(result, list):
            for page in result:
                if isinstance(page, dict) and 'rec_texts' in page:
                    text_blocks.extend(page['rec_texts'])
                elif isinstance(page, list):
                    for line in page:
                        if isinstance(line, (list, tuple)) and len(line) == 2:
                            # Handle traditional format: [[coords], (text, score)]
                            if isinstance(line[1], (list, tuple)) and len(line[1]) >= 1:
                                text_blocks.append(line[1][0])
                                
        if not text_blocks:
            raise Exception(f"No text found. Raw output: {str(result)[:200]}...")
            
        raw_text = "\n".join(text_blocks)
        
        elapsed = time.time() - start_time
        logger.info(f"PaddleOCR text extraction completed in {elapsed:.2f} seconds.")
        return raw_text
    except Exception as e:
        logger.error(f"Error during OCR extraction: {e}")
        raise
