import pyautogui
import tkinter as tk
import ocr
import os
from PIL import Image, ImageTk
from pathlib import Path
import pytesseract
 
"""
the snipping tool takes the screenshot and is able to return it somewhere by calling the function get cropped image 

"""

class SnippingTool:
    def __init__(self):
        """Initializes the snipping tool, takes a screenshot, and sets up the Tkinter window."""
        self.screenshot = pyautogui.screenshot()  # Take the initial screenshot
        
        self.root = tk.Tk()  # Initialize Tkinter window , this is just used for the screenshot 
        self.root.attributes("-fullscreen", True)  # Fullscreen mode

        self.canvas = tk.Canvas(self.root, cursor="cross")  # Cross cursor for selection
        self.tk_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Selection variables
        self.start_x = None
        self.start_y = None
        self.rect = None

        # Mouse bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.root.mainloop()  # Keep window open until finished

    def on_press(self, event):
        """Start the selection rectangle."""
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="red", width=2
        )

    def on_drag(self, event):
        """Update the selection rectangle as the mouse moves."""
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        """Capture the cropped selection and close the Tkinter window."""
        end_x, end_y = event.x, event.y
        self.root.destroy()  # Close Tkinter window

        # Ensure correct cropping order
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)
        self.cropped_image = self.screenshot.crop((left, top, right, bottom))  # Crop image

    def get_cropped_image(self):
        """Return the cropped image."""
        return self.cropped_image


def take_screenshot():
    # Initialize SnippingTool and capture cropped image
    #wait for the key 
    snip_tool = SnippingTool()
    cropped_image = snip_tool.get_cropped_image()
    
    if cropped_image:
        # Extract text using Tesseract OCR
        return cropped_image


def extract_text_from_image(cropped_image):
    """
    Perform OCR on the given cropped image and return the extracted text. 
    :param cropped_image: The cropped PIL image to process.
    :return: Extracted text from the image.
    """
    try:
        # Perform OCR to extract text from the image
        extracted_text = ocr.extract_text_from_image(cropped_image)  # Assuming ocr.extract_text_from_image handles PIL.Image
       
        #extracted_text = pytesseract.image_to_string(cropped_image)
        
        # Return the extracted text
        return extracted_text
    except Exception as e:
        print(f"Error processing OCR: {e}")
        return None

#basically hearing for the key - and then calling the snipping 

