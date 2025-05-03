import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, QRadioButton, QCheckBox, QDialog, QFileDialog, QLineEdit
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSettings
from PIL import Image
from io import BytesIO 
from pdf2image import convert_from_path
import json
from screenshot import take_screenshot, process_ocr
import os


class UI(QWidget):
    def __init__(self):
        super().__init__() #initalixing the parent class constructor 

        self.setWindowTitle("Screenshot Preview App") #window title 
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout() #shows the window layout
        self.settings = QSettings("Software Engineering Class", "Snapshot")
        # button to take screenshot calles the self.screenshot_text function which takes the screenshot 
        self.capture_button = QPushButton("Take Screenshot")
        self.capture_button.clicked.connect(self.screenshot_text) #connects the screenshot tool to the botton on the screen 
        self.layout.addWidget(self.capture_button)
        
        self.default_filename = "extracted_text.txt"
        saved_path = self.settings.value("text_destination", "")
        if saved_path:
            self.file_path = saved_path
        else:
            self.file_path = os.path.join(os.path.expanduser("~"), "Documents", self.default_filename)

    
        # Upload file code:
        # Goal is to be able to click button to choose file to give to ocr
        self.file_select_button = QPushButton("Select File")
        self.file_select_button.clicked.connect(self.file_select)
        self.layout.addWidget(self.file_select_button)
        # End of upload file code 
        
        # Start of Settings code
        # Button to access settings connects to the self.open_settings when it is pressed

        self.options_button = QPushButton("Settings")
        self.options_button.clicked.connect(self.open_settings)
        self.layout.addWidget(self.options_button)
        # End of Settings code

        # Image preview label
        self.image_label = QLabel("Screenshot will appear here.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Set final layout
        self.setLayout(self.layout)

    # When Settings button is pressed:
    def open_settings(self):
        self.open_settings = Settings(self)
        self.open_settings.show()

    # Convert PIL Image to QPixmap
    def convert_to_QPixmap (self, pic_to_convert):
        buffer = BytesIO()
        pic_to_convert.save(buffer, format="PNG")
        buffer.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue(), "PNG")
        self.image_label.setPixmap(pixmap)

        # Calling the process ocr to take the image and save it
        # You can also pass a custom path to the process_ocr to save it in a custom location
        return process_ocr (pic_to_convert, save_path = self.file_path)


    # Function to convert pdf to image for OCR
    def convert_pdf (self, file_info):
        # We initialize extracted_text as an empty string here so it can be filled with concatenated pdf page text
        extracted_text = ""
        # Converting from pdf process; first parameter is file to be converted, second is the DPI value
        # NOTE: The larger the dpi, the more accurate the OCR is, but the window scales up larger as well
        # 100 is the minimum dpi value I've found to consistently have few errors but still fits on the screen
        pages = convert_from_path(file_info, dpi = 100)
        
        # For each page in the pdf file, extract text then concatenate to the extracted_text string to be held
        for i, page_image in enumerate(pages):
            page_text = self.convert_to_QPixmap (page_image)

            # Send current page_image to the OCR, then concatenate the results onto the previous results.
            # The "\n\n" indicates a page break with a double newline; can be removed if we want it to be seamless
            # page_text = process_ocr (page_image)
            # In the case page_text returns no text from OCR, "(page_text or "")" makes sure we're always trying to concatenate a string onto a string which prevents errors
            extracted_text += (page_text or "") + "\n\n"

# CURRENT PROJECT: HAVE TO CHANGE SETTINGS TO CONCATENATE FILE FOR HERE, MAY MEAN I NEED TO PUSH WHAT I'VE GOT TO GIT AND GET TYLER'S NEW BRANCH

        # Return the fully concatenated text
        return extracted_text


    # Function to transfer chosen image to OCR for text extraction
    def file_select(self):
        # Call the function to choose a library file
        # getOpenFileName takes the arguments of:
        # self - The parent function
        # "Select File" - The caption to be shown
        # "/Documents" - The starting directory
        # "Images (*.png *.jpg *.pdf)" - The filter, only show these types of files
        # This function returns a tuple with 2 values, have to separate out the file name with , _ holding the part of the tuple we don't need
        file_info, _ = QFileDialog.getOpenFileName(self, "Select File", "/Documents", "Images (*.png *.jpg *.bmp *.pdf)")

        # If successful:
        if file_info:
            # If file is pdf, we've got to change it to a simpler image format
            # Check if file is a pdf:
            if file_info.lower().endswith('.pdf'):
                # If file is a pdf, call convert_pdf function
                selected_file = self.convert_pdf(file_info)
                
            else:
                # If not a pdf, do the standard work instead
                selected_file = Image.open (file_info)
                self.convert_to_QPixmap (selected_file)
                # selected_file = self.convert_to_QPixmap (selected_file)
                # calling the process ocr to take the screen and save it
                # you can also pass a custom path to the process_ocr to save it in a custom location  
                # process_ocr(selected_file) #converts to texts and saves
                
            os.startfile(self.file_path) 
        else:
            self.image_label.setText("Error loading chosen file")

    def screenshot_text(self):
         # Call the function to take a screenshot
        cropped_image = take_screenshot()

        if cropped_image:
            if not self.file_path:
                file_name, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Select File Destination", self.default_filename, 
                    "Text Files (*.txt)")
                if file_name:
                    self.file_path = file_name
                    self.settings.setValue("text_destination", self.file_path)
                else:
                    # If user cancels, don't proceed
                    self.image_label.setText("No save location selected.")
                    return
                  
            # Convert PIL Image to QPixmap      
            self.convert_to_QPixmap (cropped_image)
            os.startfile(self.file_path)

        else:
            self.image_label.setText("No image captured.")
            
     
# Settings Window:        
class Settings(QWidget):
    def __init__(self, UI_window):
        super().__init__() #initalizing the parent class constructor 

        # Window name, size, and layout. Also indicates this is a settings window, which means changes should persist
        self.setWindowTitle("Settings") #window title
        self.settings = QSettings("Software Engineering Class", "Snapshot")
        self.setGeometry(100, 100, 800, 600)
        self.main_layout = QVBoxLayout() #this is just the layout of the windown
        self.UI_window = UI_window
        # Notification settings group box
        self.notification_group_box = QGroupBox("Notification Settings: ")
        self.notification_button1 = QRadioButton("Show Notifications")
        self.notification_button2 = QRadioButton("Don't Show Notifications")

        # Set up notification group box layout
        self.notification_layout = QVBoxLayout()
        self.notification_layout.addWidget(self.notification_button1)
        self.notification_layout.addWidget(self.notification_button2)
        self.notification_group_box.setLayout(self.notification_layout)

        # Add notification setting group box to main settings window
        self.main_layout.addWidget(self.notification_group_box)

        # Open file settings group box
        self.open_file_group_box = QGroupBox("File Settings: ")
        self.open_file_button1 = QRadioButton("Open Destination File")
        self.open_file_button2 = QRadioButton("Don't Open Destination File")

        # Set up open file group box layout
        self.open_file_layout = QVBoxLayout()
        self.open_file_layout.addWidget(self.open_file_button1)
        self.open_file_layout.addWidget(self.open_file_button2)
        self.open_file_group_box.setLayout(self.open_file_layout)

        # Add open file setting group box to main settings window
        self.main_layout.addWidget(self.open_file_group_box)

        # Note: Should try and see if there is a setting that makes sure at least one box must be checked at all times to prevent user error
        # Text destination settings group box
        self.text_destination_group_box = QGroupBox("Text Destination Settings:") #this outlines the line around the below options 
        self.text_destination_button1 = QCheckBox("Save text to clipboard")
        self.text_destination_button2 = QCheckBox("Save text to new file")
        self.text_destination_button3 = QCheckBox("Save text to old file")
        
        ##this is the layout for the manaul and automatic file destination - 
        # Set up text destination group box layout
        self.text_destination_layout = QVBoxLayout()
        self.text_destination_layout.addWidget(self.text_destination_button1)
        self.text_destination_layout.addWidget(self.text_destination_button2)
        self.text_destination_layout.addWidget(self.text_destination_button3)
        self.text_destination_group_box.setLayout(self.text_destination_layout)

        # Add text destination settings group box to main settings window
        self.main_layout.addWidget(self.text_destination_group_box)

        # File Name Group Box
        self.file_path_group_box = QGroupBox("File Name Settings: ") #this is the outline around the destination file_name field 
        self.file_browse_button = QPushButton("Browse")

        # Format file name group box layout
        self.file_path_layout = QHBoxLayout() #creates a horizental line layout widgets will be arranged side by side and the layour is stored in the filepath layput
        self.file_path_layout.addWidget(QLabel("Text Destination File Name: ")) #adding a text widget to the layout 
        self.file_path_input = QLineEdit() #creates a single line tet input fiels to take in the destination input 
        self.file_path_input.setReadOnly(True) #it is set to read only for not but displays it contents from file_browse_button at the end of load settings function
        self.file_path_layout.addWidget(self.file_path_input) #adds the input layout field into the to horizental layout
        self.file_path_layout.addWidget(self.file_browse_button) #adds the browse button filed to the layout
        self.file_path_group_box.setLayout(self.file_path_layout) #sets the entire compoents as a group layout

        # Add file name group box to main settings window
        self.main_layout.addWidget(self.file_path_group_box)
        
        # When Browse button is clicked, go to choose_file function
        self.file_browse_button.clicked.connect(self.choose_destination_file) #

        # Button to save changed settings
        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.clicked.connect(self.apply_settings)

        # Add apply button to main layout
        self.main_layout.addWidget(self.apply_button)

        # Finalize layout
        self.setLayout(self.main_layout)

        # Load previously saved settings
        self.load_settings()

    # Process of loading previously saved settings:
    def load_settings(self):
        # Settings are stored in a JSON file
        
        # Notification Settings
        # Default to show notifications
        notification_settings = self.settings.value("Notification Settings: ", "Show Notifications")
        if notification_settings == "Show Notifications":
            self.notification_button1.setChecked(True)
        else:
            self.notification_button2.setChecked(True)

        # Open File Settings
        # Default to open file after Snapshot
        open_file_settings = self.settings.value("File Settings: ", "Open Destination File")
        if open_file_settings == "Open Destination File":
            self.open_file_button1.setChecked(True)
        else:
            self.open_file_button2.setChecked(True)


        # Text Destination Settings, stored in JSON
        # Default to new file
        text_destination_json_settings = self.settings.value("Text Destination: ", json.dumps(["Save Text to New File"]))
        try:
            text_destination = json.loads(text_destination_json_settings)
        except json.JSONDecodeError:
            text_destination = []

        self.text_destination_button1.setChecked("Save Text to Clipboard" in text_destination)
        self.text_destination_button2.setChecked("Save Text to New File" in text_destination)
        self.text_destination_button3.setChecked("Save Text to Old File" in text_destination)

        # Text Destination File Name (Default is currently empty)
        self.file_path = self.settings.value("text_destination", "")
        #self.file_path = self.settings.value("text_destination", self.file_name)
        self.file_path_input.setText(self.file_path)

    # When you click apply settings button:
    def apply_settings(self):
        # Apply new settings
        # Notification Setting:
        if self.notification_button1.isChecked():
            notification_setting = "Show Notifications" 
        else:
            notification_setting = "Don't Show Notifications"

        self.settings.setValue("Notification Settings: ", notification_setting)

        # Open File Setting:
        if self.open_file_button1.isChecked():
            file_setting = "Open Destination File"     
        else:
            file_setting = "Don't Open Destination File"

        self.settings.setValue("File Settings: ", file_setting)

        # Text Destination Setting:
        text_destination = []

        if self.text_destination_button1.isChecked():
            text_destination.append("Save Text to Clipboard")
        if self.text_destination_button2.isChecked():
            text_destination.append("Save Text to New File")
        if self.text_destination_button3.isChecked():
            text_destination.append("Save Text to Old File")

        self.settings.setValue("Text Destination: ", json.dumps(text_destination))

        # Placeholder code to show what you've applied:
        print("Settings applied: ")

        # Notification settings
        if self.notification_button1.isChecked():
            print("Notification: Show")
        else:
            print("Notification: Don't show")

        # File settings
        if self.open_file_button1.isChecked():
            print("File Settings: Open file after Snapshot")
        else:
            print("File Settings: Don't open file after Snapshot")

        # Text destination settings
        if self.text_destination_button1.isChecked():
            print("Text Destination: Save to clipboard")
        if self.text_destination_button2.isChecked():
            print("Text Destination: Save to new file")
        if self.text_destination_button3.isChecked():
            print("Text Destination: Save to old file")

        # Text Destination file name
        self.settings.setValue("text_destination", self.file_path_input.text())

    def choose_destination_file(self):
        default_path = os.path.join(os.path.expanduser("~"), "Documents", self.UI_window.default_filename)

        self.file_name, _ = QFileDialog.getSaveFileName(  #opens a standard save file dialog 
            self, 
            "Select File Destination path", 
            default_path,
            "Text File"  #header of dialog the default location is emput second arg " ",
                                                                    #Text file is the fill filter return a tuple the path and the fill_filter 
        )
        if self.file_name:
            self.file_path_input.setText(self.file_name) #this basically just displays the image to the text field 
            self.settings.setValue("text_destination", self.file_name)
            self.UI_window.file_path = self.file_name # should update the UI file path 
        print(self.file_name)  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())

