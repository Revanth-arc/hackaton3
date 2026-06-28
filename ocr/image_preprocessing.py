import cv2
import numpy as np
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Preprocesses an image for better OCR accuracy.
    Applies grayscale, Gaussian blur, and adaptive thresholding.
    """
    start_time = time.time()
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Blur
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive Thresholding
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        elapsed = time.time() - start_time
        logger.info(f"Image preprocessing completed in {elapsed:.2f} seconds.")
        return thresh
    except Exception as e:
        logger.error(f"Error during image preprocessing: {e}")
        raise
