import logging
import time

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required for image OCR preprocessing. "
            "Install dependencies with `python3 -m pip install -r requirements.txt`."
        ) from exc
    return cv2


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Preprocesses an image for better OCR accuracy.
    Applies grayscale, Gaussian blur, and adaptive thresholding.
    """
    start_time = time.time()
    try:
        cv2 = _load_cv2()

        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # PaddleOCR's deep learning models are trained on natural RGB images.
        # Aggressive binary thresholding often destroys the text features it looks for.
        # Returning the raw BGR image yields much better OCR results.

        elapsed = time.time() - start_time
        logger.info(f"Image preprocessing completed in {elapsed:.2f} seconds.")
        return img
    except Exception as e:
        logger.error(f"Error during image preprocessing: {e}")
        raise
