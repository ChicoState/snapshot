import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QPushButton, QLabel, QRadioButton, QCheckBox, QDialog, QFileDialog, 
                           QLineEdit, QMessageBox, QMainWindow, QStatusBar, QToolBar, QAction)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QSettings, QSize
from io import BytesIO 
import json
from screenshot import take_screenshot, process_ocr, get_settings
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot OCR Tool")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Create main content
        self.create_main_content()
        
        # Load settings
        self.settings = QSettings("Software Engineering Class", "Snapshot")
        
        # Track if we're minimized for screenshot
        self.is_minimized_for_screenshot = False
        self.screenshot_in_progress = False
        
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Screenshot action
        screenshot_action = QAction("Take Screenshot", self)
        screenshot_action.setStatusTip("Take a new screenshot")
        screenshot_action.triggered.connect(self.take_screenshot)
        toolbar.addAction(screenshot_action)
        
        # Open Screenshot Utility action
        utility_action = QAction("Open Screenshot Utility", self)
        utility_action.setStatusTip("Open the screenshot utility directly")
        utility_action.triggered.connect(self.open_screenshot_utility)
        toolbar.addAction(utility_action)
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
    def create_main_content(self):
        # Image preview area
        self.image_label = QLabel("Screenshot will appear here")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
            }
        """)
        self.layout.addWidget(self.image_label)
        
        # Buttons area
        button_layout = QHBoxLayout()
        
        self.capture_button = QPushButton("Take Screenshot")
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.capture_button.clicked.connect(self.take_screenshot)
        button_layout.addWidget(self.capture_button)
        
        self.settings_button = QPushButton("Settings")
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)
        
        self.layout.addLayout(button_layout)
        
    def take_screenshot(self):
        try:
            if self.screenshot_in_progress:
                return
                
            self.screenshot_in_progress = True
            
            # Minimize the window
            self.showMinimized()
            self.is_minimized_for_screenshot = True
            
            # Take the screenshot
            cropped_image = take_screenshot()
            
            # Restore the window
            self.showNormal()
            self.is_minimized_for_screenshot = False
            
            if cropped_image:
                # Convert PIL Image to QPixmap
                buffer = BytesIO()
                cropped_image.save(buffer, format="PNG")
                buffer.seek(0)

                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue(), "PNG")
                
                # Scale the image to fit the label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                
                # Process OCR with current settings
                settings = get_settings()
                if settings.get('auto_process', True):
                    process_ocr(cropped_image=cropped_image)
                    self.statusBar().showMessage("Screenshot processed successfully", 3000)
                else:
                    self.statusBar().showMessage("Screenshot captured", 3000)
            else:
                self.statusBar().showMessage("Screenshot cancelled", 3000)
        except Exception as e:
            # Make sure window is restored if there's an error
            if self.is_minimized_for_screenshot:
                self.showNormal()
                self.is_minimized_for_screenshot = False
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            self.screenshot_in_progress = False
            
    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def open_screenshot_utility(self):
        """Open the screenshot utility directly"""
        try:
            # Import here to avoid circular imports
            from screenshot import take_screenshot, process_ocr
            settings = get_settings()
            
            # Take screenshot
            cropped_image = take_screenshot()
            
            # Process if auto-process is enabled
            if cropped_image and settings.get('auto_process', True):
                process_ocr(cropped_image)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open screenshot utility: {str(e)}")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 600, 400)
        self.settings = QSettings("Software Engineering Class", "Snapshot")
        
        self.layout = QVBoxLayout()
        
        # Auto-process settings
        auto_process_group = QGroupBox("Processing Settings")
        auto_process_layout = QVBoxLayout()
        
        self.auto_process_checkbox = QCheckBox("Automatically process screenshots")
        self.auto_process_checkbox.setChecked(self.settings.value("auto_process", True, type=bool))
        auto_process_layout.addWidget(self.auto_process_checkbox)
        
        self.show_ui_checkbox = QCheckBox("Show UI after taking screenshot")
        self.show_ui_checkbox.setChecked(self.settings.value("show_ui", True, type=bool))
        auto_process_layout.addWidget(self.show_ui_checkbox)
        
        auto_process_group.setLayout(auto_process_layout)
        self.layout.addWidget(auto_process_group)
        
        # File handling settings
        file_handling_group = QGroupBox("File Handling Settings")
        file_handling_layout = QVBoxLayout()
        
        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("Output Directory:")
        self.dir_input = QLineEdit()
        self.dir_input.setReadOnly(True)
        self.dir_input.setText(self.settings.value("output_dir", os.path.join(os.path.expanduser("~"), "Documents", "Snapshot")))
        self.dir_browse_button = QPushButton("Browse")
        self.dir_browse_button.clicked.connect(self.choose_output_directory)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_browse_button)
        file_handling_layout.addLayout(dir_layout)
        
        # File handling options
        self.file_handling_group = QGroupBox("File Handling")
        file_options_layout = QVBoxLayout()
        
        self.overwrite_radio = QRadioButton("Overwrite existing file")
        self.new_file_radio = QRadioButton("Create new file for each screenshot")
        
        file_handling = self.settings.value("file_handling", "overwrite")
        self.overwrite_radio.setChecked(file_handling == "overwrite")
        self.new_file_radio.setChecked(file_handling == "new")
        
        file_options_layout.addWidget(self.overwrite_radio)
        file_options_layout.addWidget(self.new_file_radio)
        self.file_handling_group.setLayout(file_options_layout)
        file_handling_layout.addWidget(self.file_handling_group)
        
        file_handling_group.setLayout(file_handling_layout)
        self.layout.addWidget(file_handling_group)
        
        # Notification settings
        notification_group = QGroupBox("Notification Settings")
        notification_layout = QVBoxLayout()
        
        self.notification_button1 = QRadioButton("Show Notifications")
        self.notification_button2 = QRadioButton("Don't Show Notifications")
        
        notification_settings = self.settings.value("Notification Settings: ", "Show Notifications")
        self.notification_button1.setChecked(notification_settings == "Show Notifications")
        self.notification_button2.setChecked(notification_settings == "Don't Show Notifications")
        
        notification_layout.addWidget(self.notification_button1)
        notification_layout.addWidget(self.notification_button2)
        notification_group.setLayout(notification_layout)
        self.layout.addWidget(notification_group)
        
        # Text destination settings
        text_dest_group = QGroupBox("Text Destination Settings")
        text_dest_layout = QVBoxLayout()
        
        self.text_destination_button1 = QCheckBox("Save text to clipboard")
        self.text_destination_button2 = QCheckBox("Save text to file")
        
        text_destination = json.loads(self.settings.value("Text Destination: ", "[]"))
        self.text_destination_button1.setChecked("Save Text to Clipboard" in text_destination)
        self.text_destination_button2.setChecked("Save Text to New File" in text_destination)
        
        text_dest_layout.addWidget(self.text_destination_button1)
        text_dest_layout.addWidget(self.text_destination_button2)
        text_dest_group.setLayout(text_dest_layout)
        self.layout.addWidget(text_dest_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)
        
        self.setLayout(self.layout)
        
    def choose_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", 
            self.dir_input.text(),
            QFileDialog.ShowDirsOnly
        )
        if dir_path:
            self.dir_input.setText(dir_path)
            
    def apply_settings(self):
        # Auto-process settings
        self.settings.setValue("auto_process", self.auto_process_checkbox.isChecked())
        self.settings.setValue("show_ui", self.show_ui_checkbox.isChecked())
        
        # File handling settings
        output_dir = self.dir_input.text()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.settings.setValue("output_dir", output_dir)
        
        file_handling = "overwrite" if self.overwrite_radio.isChecked() else "new"
        self.settings.setValue("file_handling", file_handling)
        
        # Notification settings
        if self.notification_button1.isChecked():
            self.settings.setValue("Notification Settings: ", "Show Notifications")
        else:
            self.settings.setValue("Notification Settings: ", "Don't Show Notifications")
            
        # Text destination settings
        text_destination = []
        if self.text_destination_button1.isChecked():
            text_destination.append("Save Text to Clipboard")
        if self.text_destination_button2.isChecked():
            text_destination.append("Save Text to New File")
            
        self.settings.setValue("Text Destination: ", json.dumps(text_destination))
        
        self.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

