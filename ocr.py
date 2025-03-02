import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        return f"Error extracting text: {e}"