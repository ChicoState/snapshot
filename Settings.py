import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QPushButton, QLabel, QRadioButton, QCheckBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import ImageGrab
import io

class UI(QWidget):
    def __init__(self):
        super().__init__() #initalixing the parent class constructor 

        self.setWindowTitle("Screenshot Preview App") #window title 
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout() #shows the window layout

        # button to take screenshot
        self.capture_button = QPushButton("Take Screenshot")
        self.capture_button.clicked.connect(self.take_screenshot)
        self.layout.addWidget(self.capture_button)




        # Start of menu code
        # Button to access menu
        self.options_button = QPushButton("Options")

        self.options_button.clicked.connect(self.open_settings)
        self.layout.addWidget(self.options_button)
        # End of menu code





        # Image preview label
        self.image_label = QLabel("Screenshot will appear here.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.setLayout(self.layout)

    # Screenshot code
    def take_screenshot(self):
        # Take a screenshot using PIL
        screenshot = ImageGrab.grab()

        # Save to bytes and convert to QPixmap
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)

        qt_image = QImage()
        qt_image.loadFromData(buffer.read())
        pixmap = QPixmap.fromImage(qt_image)

        # Show in label
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
    # End Screenshot Code




    # Menu Code
    # This code was from an example, have to confirm it works as expected
    def open_settings(self):
        self.open_settings = Settings()
        self.open_settings.show()
    # Open settings window here
        
class Settings(QWidget):
    def __init__(self):
        super().__init__() #initalizing the parent class constructor 

        # Setup window

        # Window name, size, and layout
        self.setWindowTitle("Settings") 
        self.setGeometry(100, 100, 800, 600)
        self.main_layout = QVBoxLayout()

        # Notification settings group box
        self.notification_group_box = QGroupBox("Notification Settings:")
        self.notification_button1 = QRadioButton("Show notifications")
        self.notification_button2 = QRadioButton("Do not show notifications")

        # Set default to show notifications
        self.notification_button1.setChecked(True)

        # Set up notification group box layout
        self.notification_layout = QVBoxLayout()
        self.notification_layout.addWidget(self.notification_button1)
        self.notification_layout.addWidget(self.notification_button2)
        self.notification_group_box.setLayout(self.notification_layout)

        # Add notification setting group box to main settings window
        self.main_layout.addWidget(self.notification_group_box)

        # Open file settings group box
        self.open_file_group_box = QGroupBox("File Settings:")
        self.open_file_button1 = QRadioButton("Open file after Snapshot")
        self.open_file_button2 = QRadioButton("Do not open file after Snapshot")

        # Set default to open file after Snapshot
        self.open_file_button1.setChecked(True)

        # Set up open file group box layout
        self.open_file_layout = QVBoxLayout()
        self.open_file_layout.addWidget(self.open_file_button1)
        self.open_file_layout.addWidget(self.open_file_button2)
        self.open_file_group_box.setLayout(self.open_file_layout)

        # Add open file setting group box to main settings window
        self.main_layout.addWidget(self.open_file_group_box)

        # Text destination settings group box
        self.text_destination_group_box = QGroupBox("Text Destination Settings:")
        self.text_destination_button1 = QCheckBox("Save text to clipboard")
        self.text_destination_button2 = QCheckBox("Save text to new file")
        self.text_destination_button3 = QCheckBox("Save text to old file")

        # Set default to new file
        self.text_destination_button2.setCheckState(True)

        # Set up text destination group box layout
        self.text_destination_layout = QVBoxLayout()
        self.text_destination_layout.addWidget(self.text_destination_button1)
        self.text_destination_layout.addWidget(self.text_destination_button2)
        self.text_destination_layout.addWidget(self.text_destination_button3)
        self.text_destination_group_box.setLayout(self.text_destination_layout)

        # Add text destination settings group box to main settings window
        self.main_layout.addWidget(self.text_destination_group_box)

        # Button to save changed settings
        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.clicked.connect(self.apply_settings)

        # Add apply button to main layout
        self.main_layout.addWidget(self.apply_button)

        # Finalize layout
        self.setLayout(self.main_layout)

    # When you click apply settings button:
    def apply_settings(self):
        # Placeholder code to show what you've applied:
        # In future, options should be saved to reflect the choices made
        print("Settings applied:")

        # Notification settings
        if self.notification_button1.isChecked():
            print("Notification: Show")
        else:
            print("Notification: Do not show")

        # File settings
        if self.open_file_button1.isChecked():
            print("File Settings: Open file after Snapshot")
        else:
            print("File Settings: Do not open file after Snapshot")

        # Text destination settings
        if self.text_destination_button1.isChecked():
            print("Text Destination: Save to clipboard")
        if self.text_destination_button2.isChecked():
            print("Text Destination: Save to new file")
        if self.text_destination_button3.isChecked():
            print("Text Destination: Save to old file")

    # End menu code





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())