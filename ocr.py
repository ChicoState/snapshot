import pytesseract
from PIL import Image
import os

if os.name == "nt":  # Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif os.name == "posix": # Linux
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_text(image_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        return f"Error extracting text: {e}"
