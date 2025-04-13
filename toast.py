import os
from win11toast import toast
from PIL import Image, ImageTk
import pyperclip

def show_clipboard_notification_windows(cropped_image, extracted_text):
        """Shows a toast notification with an option to open the text editor."""
        def handle_click(event):
            action = event.get('arguments', 'http:')[5:] #ignore 'http:' prefix; workaround for win11toast

            if action == '1':
                text_file = "extracted_text.txt"
                os.startfile(text_file)
            elif action == '2':
                image_file = "screenshot.png"
                cropped_image.save(image_file)
                os.startfile(image_file)


        buttons = [
            {'activationType': 'protocol', 'arguments': 'http:1', 'content': 'Open Text Editor'},
            {'activationType': 'protocol', 'arguments': 'http:2', 'content': 'View Image'}
        ]

        toast('Text copied to clipboard', extracted_text, on_click=handle_click, buttons=buttons)

def show_notification_windows(cropped_image, extracted_text):
        """Shows a toast notification with an option to open the text editor."""
        def handle_click(event):
            action = event.get('arguments', 'http:')[5:] #ignore 'http:' prefix; workaround for win11toast

            if action == '1':
                text_file = "extracted_text.txt"
                os.startfile(text_file)
            elif action == '2':
                image_file = "screenshot.png"
                cropped_image.save(image_file)
                os.startfile(image_file)
            elif action == '3':
                pyperclip.copy(extracted_text)
                print("Text copied to clipboard.")


        buttons = [
            {'activationType': 'protocol', 'arguments': 'http:1', 'content': 'Open Text Editor'},
            {'activationType': 'protocol', 'arguments': 'http:2', 'content': 'View Image'},
            {'activationType': 'protocol', 'arguments': 'http:3', 'content': 'Copy to Clipboard'}
        ]

        toast('Text copied to clipboard', extracted_text, on_click=handle_click, buttons=buttons)