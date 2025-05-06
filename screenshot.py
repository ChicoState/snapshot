import pyautogui
import tkinter as tk
import ocr
import os
import json
import json
from PIL import Image, ImageTk
from pathlib import Path
import pytesseract
from io import BytesIO
import pyperclip
from PyQt5.QtCore import QSettings

if os.name == "nt": 
    from toast import show_clipboard_notification_windows, show_notification_windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Correct path
else :
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"



 
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
        self.extracted_text = ""
        self.extracted_text = ""

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
        self.cropped_image = self.screenshot.crop((left, top, right, bottom))  # PIL.image formate

    def get_cropped_image(self):
        """Return the cropped image."""
        return self.cropped_image


def take_screenshot():
    # Initialize SnippingTool and capture cropped image
    # wait for the key 

    snip_tool = SnippingTool()
    cropped_image = snip_tool.get_cropped_image()  #return the image in PIL.image formate
    
    if cropped_image:
        # Extract text using Tesseract OCR
        return cropped_image


def process_ocr(cropped_image=None, save_path="extracted_text.txt"):
    """
    Extracts text from the image or image path, saves to a text file, and opens it.
    :param cropped_image: The cropped PIL image to process (optional).
    :param image_path: The image path to process (optional).
    """
    try:

        if cropped_image:

            extracted_text = pytesseract.image_to_string(cropped_image)
            if extracted_text:  # Check if OCR extraction was successful
                
                # Check settings
                settings = QSettings("Software Engineering Class", "Snapshot")
                text_destination_json = settings.value("Text Destination: ", "[]") 
                text_destination = json.loads(text_destination_json)
                notification_settings = settings.value("Notification Settings: ", "Show Notifications")


                # Save the extracted text to a text file
                if "Save Text to New File" in text_destination:
                    with open(save_path, "w", encoding="utf-8") as file:
                        file.write(extracted_text)
                elif "Save Text to Old File" in text_destination:
                    with open(save_path, "a", encoding="utf-8") as file:
                        file.write(extracted_text + "\n")
                else:
                    print("err screenshot.py ln:119")    # this shouldnt be reached ever                    

                print(f"Extracted text saved to {save_path}")


                if "Save Text to Clipboard" in text_destination:
                    pyperclip.copy(extracted_text)  # Copy text to clipboard
                    print("Extracted text copied to clipboard.")
                
                if notification_settings == "Show Notifications" and os.name == "nt": # feature only available on windows
                    if "Save Text to Clipboard" not in text_destination: # option to copy to clipboard in notification
                        show_notification_windows(cropped_image, extracted_text)
                    else:
                        show_clipboard_notification_windows(cropped_image, extracted_text)


                # Open the text file automatically
                if os.name == "nt":  # Windows
                    os.startfile(save_path)
                elif os.name == "posix":  # macOS/Linux
                    os.system(f"xdg-open {save_path}")  # Linux
                    os.system(f"open {save_path}")  # macOS
            else:
                print("No text extracted from the image.")

        else:
            print("No valid image provided.")

    except Exception as e:
        print(f"Error processing OCR: {e}")

#clears content from cumulative ocr process
def clear_cumulative(save_path="extracted_text.txt"):
    open(save_path, "w").close()
