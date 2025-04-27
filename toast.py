import os
from win11toast import toast
from PIL import Image
import pyperclip
from PyQt5.QtCore import QSettings
import json
import sys
import tempfile
import time

def get_settings():
    """Get the current application settings"""
    settings = QSettings("Software Engineering Class", "Snapshot")
    return {
        'notifications': settings.value("Notification Settings: ", "Show Notifications"),
        'text_dest': json.loads(settings.value("Text Destination: ", "[]")),
        'output_dir': settings.value("output_dir", os.path.join(os.path.expanduser("~"), "Documents", "Snapshot")),
        'file_handling': settings.value("file_handling", "overwrite")
    }

def show_clipboard_notification_windows(cropped_image, extracted_text):
    """Shows a toast notification with an option to open the text editor."""
    try:
        settings = get_settings()
        
        def handle_click(event):
            try:
                action = event.get('arguments', 'http:')[5:] #ignore 'http:' prefix; workaround for win11toast

                if action == '1':
                    # Get the current output file path
                    output_file = os.path.join(settings['output_dir'], "extracted_text.txt")
                    if os.path.exists(output_file):
                        os.startfile(output_file)
                elif action == '2':
                    # Save image to temp file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        image_path = temp_file.name
                        cropped_image.save(image_path)
                        os.startfile(image_path)
            except Exception as e:
                print(f"Error handling notification click: {e}")

        buttons = [
            {'activationType': 'protocol', 'arguments': 'http:1', 'content': 'Open Text Editor'},
            {'activationType': 'protocol', 'arguments': 'http:2', 'content': 'View Image'}
        ]

        # Truncate text if too long
        if len(extracted_text) > 100:
            extracted_text = extracted_text[:100] + "..."
            
        # Show toast with longer duration and explicit dismissal
        toast('Text copied to clipboard', 
              extracted_text, 
              on_click=handle_click, 
              buttons=buttons,
              duration='long',
              audio={'silent': 'true'},
              scenario='reminder')  # Use reminder scenario to prevent auto-dismissal
        
    except Exception as e:
        print(f"Error showing clipboard notification: {e}")

def show_notification_windows(cropped_image, extracted_text):
    """Shows a toast notification with an option to open the text editor."""
    try:
        settings = get_settings()
        
        def handle_click(event):
            try:
                action = event.get('arguments', 'http:')[5:] #ignore 'http:' prefix; workaround for win11toast

                if action == '1':
                    # Get the current output file path
                    output_file = os.path.join(settings['output_dir'], "extracted_text.txt")
                    if os.path.exists(output_file):
                        os.startfile(output_file)
                elif action == '2':
                    # Save image to temp file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        image_path = temp_file.name
                        cropped_image.save(image_path)
                        os.startfile(image_path)
                elif action == '3':
                    pyperclip.copy(extracted_text)
                    print("Text copied to clipboard.")
            except Exception as e:
                print(f"Error handling notification click: {e}")

        buttons = [
            {'activationType': 'protocol', 'arguments': 'http:1', 'content': 'Open Text Editor'},
            {'activationType': 'protocol', 'arguments': 'http:2', 'content': 'View Image'},
            {'activationType': 'protocol', 'arguments': 'http:3', 'content': 'Copy to Clipboard'}
        ]

        # Truncate text if too long
        if len(extracted_text) > 100:
            extracted_text = extracted_text[:100] + "..."
            
        # Show toast with longer duration and explicit dismissal
        toast('Text extracted successfully', 
              extracted_text, 
              on_click=handle_click, 
              buttons=buttons,
              duration='long',
              audio={'silent': 'true'},
              scenario='reminder')  # Use reminder scenario to prevent auto-dismissal
        
    except Exception as e:
        print(f"Error showing notification: {e}")