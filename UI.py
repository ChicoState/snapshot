import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
#from PIL import Image
from io import BytesIO 
from screenshot import take_screenshot



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

        #iImage preview label
        self.image_label = QLabel("Screenshot will appear here.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.setLayout(self.layout)

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
        else:
            self.image_label.setText("No image captured.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())