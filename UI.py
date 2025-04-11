import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, QRadioButton, QCheckBox, QDialog, QFileDialog, QLineEdit
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSettings
#from PIL import Image
from io import BytesIO 
import json
from screenshot import take_screenshot, process_ocr


class UI(QWidget):
    def __init__(self):
        super().__init__() #initalixing the parent class constructor 

        self.setWindowTitle("Screenshot Preview App") #window title 
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout() #shows the window layout

        # button to take screenshot
        self.capture_button = QPushButton("Take Screenshot")

        self.capture_button.clicked.connect(self.sreenshot_text) #connects the screenshot tool to the botton on the screen 
        self.layout.addWidget(self.capture_button)

        # Start of Settings code
        # Button to access settings
        self.options_button = QPushButton("Settings")

        self.options_button.clicked.connect(self.open_settings)
        self.layout.addWidget(self.options_button)
        # End of Settings code

        # Image preview label

        self.image_label = QLabel("Screenshot will appear here.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.setLayout(self.layout)

    # When Settings button is pressed:
    def open_settings(self):
        self.open_settings = Settings()
        self.open_settings.show()
        
# Settings Window:        
class Settings(QWidget):
    def __init__(self):
        super().__init__() #initalizing the parent class constructor 

        # Window name, size, and layout. Also indicates this is a settings window, which means changes should persist
        self.setWindowTitle("Settings") 
        self.settings = QSettings("Software Engineering Class", "Snapshot")
        self.setGeometry(100, 100, 800, 600)
        self.main_layout = QVBoxLayout()

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
        self.text_destination_group_box = QGroupBox("Text Destination Settings:")
        self.text_destination_button1 = QCheckBox("Save text to clipboard")
        self.text_destination_button2 = QCheckBox("Save text to new file")
        self.text_destination_button3 = QCheckBox("Save text to old file")

        # Set up text destination group box layout
        self.text_destination_layout = QVBoxLayout()
        self.text_destination_layout.addWidget(self.text_destination_button1)
        self.text_destination_layout.addWidget(self.text_destination_button2)
        self.text_destination_layout.addWidget(self.text_destination_button3)
        self.text_destination_group_box.setLayout(self.text_destination_layout)

        # Add text destination settings group box to main settings window
        self.main_layout.addWidget(self.text_destination_group_box)

        # File Name Group Box
        self.file_path_group_box = QGroupBox("File Name Settings: ")
        self.file_browse_button = QPushButton("Browse")

        # Format file name group box layout
        self.file_path_layout = QHBoxLayout()
        self.file_path_layout.addWidget(QLabel("Text Destination File Name: "))
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_layout.addWidget(self.file_path_input)
        self.file_path_layout.addWidget(self.file_browse_button)
        self.file_path_group_box.setLayout(self.file_path_layout)

        # Add file name group box to main settings window
        self.main_layout.addWidget(self.file_path_group_box)
        
        # When Browse button is clicked, go to choose_file function
        self.file_browse_button.clicked.connect(self.choose_destination_file)

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
        self.file_name, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "", "Text File"
        )
        if self.file_name:
            self.file_path_input.setText(self.file_name)

    def sreenshot_text(self):
         # Call the function to take a screenshot
        cropped_image = take_screenshot()

        if cropped_image:
            # Convert PIL Image to QPixmap
            buffer = BytesIO()
            cropped_image.save(buffer, format="PNG")
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue(), "PNG")
            self.image_label.setPixmap(pixmap)

            #calling the process ocr to take the screen and save it
            # you can also pass a custom path to the process_ocr to save it in a custom location  
            process_ocr(cropped_image= cropped_image) #converts to texts and saves
        else:
            self.image_label.setText("No image captured.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())

