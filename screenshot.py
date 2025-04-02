import pyautogui
import tkinter as tk
import ocr
import os
import json
from PIL import Image, ImageTk
import pyperclip
from win11toast import toast

class SnippingTool:
    def __init__(self):
        self.screenshot = pyautogui.screenshot()
        
        self.root = tk.Tk()  # Initialize Tkinter window
        self.root.attributes("-fullscreen", True)  # Fullscreen mode

        self.canvas = tk.Canvas(self.root, cursor="cross")  # Cross cursor for selection
        self.tk_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.pack(fill=tk.BOTH, expand=True)
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
            self.extracted_text = ocr.extract_text(image_path)  # Call OCR function

            # Load configuration
            config = self.load_config()
            text_file = "extracted_text.txt"
            with open(text_file, "w", encoding="utf-8") as file:
                file.write(self.extracted_text)

            print(f"Extracted text saved to {text_file}")
            if config.get("output_mode", "to_clipboard") != "to_clipboard":
                # Open text file automatically
                if os.name == "nt":  # Windows
                    os.startfile(text_file)
                elif os.name == "posix":  # macOS/Linux
                    os.system(f"xdg-open {text_file}")  # Linux
                    os.system(f"open {text_file}")  # macOS
            else:  # clipboard
                pyperclip.copy(self.extracted_text)
                if os.name == "nt":  # Windows
                    self.show_clipboard_notification_windows()
                elif os.name == "posix":  # macOS/Linux
                    print("Text copied to clipboard. No notification available for macOS/Linux.")

        except Exception as e:
            print(f"Error processing OCR: {e}")

    # replace with whatever config function we end up with
    def load_config(self):
        """Loads configuration from config.json, or creates a default config."""
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            default_config = {"output_mode": "to_clipboard"}  # Default to clipboard
            with open("config.json", "w") as f:
                json.dump(default_config, f)
            return default_config

    def show_clipboard_notification_windows(self):
        """Shows a toast notification with an option to open the text editor."""
        def handle_click(event):
            action = event.get('arguments', 'http:')[5:] #ignore 'http:' prefix; workaround for win11toast

            if action == '1':
                text_file = "extracted_text.txt"
                os.startfile(text_file)
            elif action == '2':
                image_file = "screenshot.png"
                os.startfile(image_file)


        buttons = [
            {'activationType': 'protocol', 'arguments': 'http:1', 'content': 'Open Text Editor'},
            {'activationType': 'protocol', 'arguments': 'http:2', 'content': 'View Image'}
        ]

        toast('Text copied to clipboard', self.extracted_text, on_click=handle_click, buttons=buttons)

SnippingTool()
