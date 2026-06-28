import os

import cv2
import numpy as np

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
from paddleocr import PaddleOCR  # noqa: E402

print("Creating dummy image with text...")
img = np.zeros((200, 400, 3), dtype=np.uint8)
cv2.putText(img, "FIR TEST 123", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

print("Initializing PaddleOCR...")
ocr = PaddleOCR(use_angle_cls=True, lang="en", enable_mkldnn=False)

print("Running OCR...")
result = ocr.ocr(img)

print("Raw OCR Result:", result)


def extract_strings(data):
    texts = []
    if isinstance(data, (list, tuple)):
        if len(data) == 2 and isinstance(data[0], str):
            texts.append(data[0])
        else:
            for item in data:
                texts.extend(extract_strings(item))
    return texts


print("Extracted strings:", extract_strings(result))
