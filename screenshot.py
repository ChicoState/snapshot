import pyautogui
import tkinter as tk
import ocr
import os
from PIL import Image, ImageTk

#test

class SnippingTool:
    def __init__(self):
        self.screenshot = pyautogui.screenshot()
        
        self.root = tk.Tk()  # Initialize Tkinter window
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
        """Start selection rectangle."""
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="red", width=2
        )

    def on_drag(self, event):
        """Update selection rectangle."""
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        """Capture the cropped selection, save it, and run OCR."""
        end_x, end_y = event.x, event.y
        self.root.destroy()  # Close Tkinter window

        # Ensure correct cropping order
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)

        cropped_image = self.screenshot.crop((left, top, right, bottom))  # Crop image
        image_path = "screenshot.png"
        cropped_image.save(image_path)  # Save image
        print(f"Saved image as '{image_path}'")

        # **Now calling OCR processing**
        self.process_ocr(image_path)

    def process_ocr(self, image_path):
        """Extracts text from the image, saves to a text file, and opens it."""
        try:
            extracted_text = ocr.extract_text(image_path)  # Call OCR function

            text_file = "extracted_text.txt"
            with open(text_file, "w", encoding="utf-8") as file:
                file.write(extracted_text)

            print(f"Extracted text saved to {text_file}")

            # Open text file automatically
            if os.name == "nt":  # Windows
                os.startfile(text_file)
            elif os.name == "posix":  # macOS/Linux
                os.system(f"xdg-open {text_file}")  # Linux
                os.system(f"open {text_file}")  # macOS
        except Exception as e:
            print(f"Error processing OCR: {e}")

SnippingTool()  # Run snipping tool
