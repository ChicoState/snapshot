import tkinter as tk
from PIL import Image, ImageTk
import pytesseract
import mss
import pyperclip
import os
import json
import datetime
from PyQt5.QtCore import QSettings  # For settings management
from toast import show_clipboard_notification_windows, show_notification_windows
import sys

# Make sure Tesseract path is correct
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class MonitorSelector:
    def __init__(self):
        self.selected_monitor_index = None
        self.root = tk.Tk()
        self.root.title("Select a Monitor")
        self.root.attributes("-topmost", True)  # Keep window on top
        
        # Get all monitors
        with mss.mss() as sct:
            self.monitors = sct.monitors[1:]  # Skip index 0 (all monitors)
            
            # Create a frame for monitor previews
            self.frame = tk.Frame(self.root)
            self.frame.pack(padx=10, pady=10)
            
            # Add monitor previews
            for idx, monitor in enumerate(self.monitors):
                # Take a small preview of each monitor
                shot = sct.grab(monitor)
                pil_img = Image.frombytes("RGB", shot.size, shot.rgb)
                
                # Resize preview to fit in window
                preview_size = (300, int(300 * shot.height / shot.width))
                pil_img = pil_img.resize(preview_size)
                photo = ImageTk.PhotoImage(pil_img)
                
                # Create monitor preview button
                btn = tk.Button(
                    self.frame,
                    image=photo,
                    command=lambda i=idx: self.select_monitor(i),
                    cursor="hand2"
                )
                btn.image = photo  # Keep reference
                btn.grid(row=0, column=idx, padx=5, pady=5)
                
                # Add monitor label
                label = tk.Label(
                    self.frame,
                    text=f"Monitor {idx + 1}\n{monitor['width']}x{monitor['height']}",
                    font=("Arial", 10)
                )
                label.grid(row=1, column=idx, padx=5, pady=5)
            
            # Add cancel button
            cancel_btn = tk.Button(
                self.root,
                text="Cancel",
                command=self.cancel,
                font=("Arial", 12),
                width=20
            )
            cancel_btn.pack(pady=10)
            
            # Bind ESC key to cancel
            self.root.bind("<Escape>", lambda e: self.cancel())
            
            self.root.mainloop()
    
    def select_monitor(self, index):
        """Select a monitor and close the window"""
        self.selected_monitor_index = index + 1  # MSS is 1-indexed
        self.root.destroy()
    
    def cancel(self):
        """Cancel monitor selection"""
        self.selected_monitor_index = None
        self.root.destroy()


def get_monitor_screenshot(monitor_index=1):
    """Take a screenshot of a specific monitor"""
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_index]
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.rgb)


class SnippingTool:
    def __init__(self, screenshot):
        self.screenshot = screenshot
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)  # Keep window on top

        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.tk_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = self.start_y = self.rect = None
        self.cropped_image = None

        # Bind ESC key to cancel
        self.root.bind("<Escape>", self.cancel_screenshot)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.root.mainloop()

    def cancel_screenshot(self, event=None):
        """Cancel the screenshot and close the window"""
        self.cropped_image = None
        self.root.destroy()

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="red", width=2
        )

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.start_x is None or self.start_y is None:
            self.cancel_screenshot()
            return

        end_x, end_y = event.x, event.y
        left, top = min(self.start_x, end_x), min(self.start_y, end_y)
        right, bottom = max(self.start_x, end_x), max(self.start_y, end_y)
        self.cropped_image = self.screenshot.crop((left, top, right, bottom))
        self.root.destroy()

    def get_cropped_image(self):
        return getattr(self, "cropped_image", None)


def get_settings():
    """Get the current application settings"""
    settings = QSettings("Software Engineering Class", "Snapshot")
    return {
        'notifications': settings.value("Notification Settings: ", "Show Notifications"),
        'text_dest': json.loads(settings.value("Text Destination: ", "[]")),
        'output_dir': settings.value("output_dir", os.path.join(os.path.expanduser("~"), "Documents", "Snapshot")),
        'file_handling': settings.value("file_handling", "overwrite"),
        'auto_process': settings.value("auto_process", True, type=bool),
        'show_ui': settings.value("show_ui", True, type=bool)
    }


def get_output_file_path():
    """Get the appropriate output file path based on settings"""
    settings = get_settings()
    output_dir = settings['output_dir']
    
    # Ensure directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if settings['file_handling'] == "overwrite":
        return os.path.join(output_dir, "extracted_text.txt")
    else:
        # Create new file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(output_dir, f"extracted_text_{timestamp}.txt")


def take_screenshot():
    """Take a screenshot and return the cropped image"""
    try:
        with mss.mss() as sct:
            monitors = sct.monitors[1:]  # Skip index 0 (all monitors)
            
            if len(monitors) == 1:
                # If only one monitor, use it directly
                selected_index = 1
            else:
                # Show monitor selector
                selector = MonitorSelector()
                selected_index = selector.selected_monitor_index
                
                if not selected_index:
                    print("No monitor selected.")
                    return None
            
            # Take screenshot of selected monitor
            screenshot = get_monitor_screenshot(selected_index)
            snip_tool = SnippingTool(screenshot)
            cropped_image = snip_tool.get_cropped_image()
            
            if cropped_image:
                settings = get_settings()
                if settings['auto_process']:
                    process_ocr(cropped_image)
            
            return cropped_image
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None


def process_ocr(cropped_image=None, save_path=None):
    """Process OCR on the given image"""
    try:
        if not cropped_image:
            print("No valid image provided.")
            return

        settings = get_settings()
        save_path = save_path or get_output_file_path()
        
        text = pytesseract.image_to_string(cropped_image)
        if not text:
            print("No text extracted from the image.")
            return

        # Save text based on settings
        if "Save Text to New File" in settings['text_dest']:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Extracted text saved to {save_path}")

        if "Save Text to Clipboard" in settings['text_dest']:
            pyperclip.copy(text)
            print("Extracted text copied to clipboard.")

        # Show notifications based on settings
        if settings['notifications'] == "Show Notifications" and os.name == "nt":
            if "Save Text to Clipboard" in settings['text_dest']:
                show_clipboard_notification_windows(cropped_image, text)
            else:
                show_notification_windows(cropped_image, text)

        # Open file based on settings
        if os.path.exists(save_path):
            if os.name == "nt":
                os.startfile(save_path)
            else:
                os.system(f"xdg-open {save_path}")
                
    except Exception as e:
        print(f"Error processing OCR: {e}")


if __name__ == "__main__":
    print("Launching screenshot tool...")
    settings = get_settings()
    
    # Check if we should show UI
    if settings['show_ui']:
        from UI import main
        main()
    else:
        # Just take screenshot and process
        img = take_screenshot()
        if img and settings['auto_process']:
            process_ocr(img)
        sys.exit(0)