import os
import numpy as np
import cv2
import pytesseract

# To work with the Tesseract engine first we need to configure pytesseract with the Tesseract Engine install path.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def countWord(image_path):
    image_path = np.fromfile(image_path, dtype=np.uint8)

    # Load the image 
    original = cv2.imdecode(image_path, cv2.IMREAD_COLOR)   

    # Preprocessing
    gray = cv2.cvtColor(original.copy(), cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thres = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Perform OCR
    text = pytesseract.image_to_string(thres)
  
    # Count words
    word_count = len(text.split())

    # return image_path;
    return word_count;
