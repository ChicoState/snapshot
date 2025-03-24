import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
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

        #iImage preview label
        self.image_label = QLabel("Screenshot will appear here.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.setLayout(self.layout)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())