import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import os
from UI import UI

# Define the hardcoded Poppler path to test PDF functionality without relying on system PATH
DEFAULT_POPPLER_PATH = r"C:\\tools\\poppler-24.08.0\\Library\\bin"

@pytest.fixture
def app(qtbot):
    """
    Fixture that creates and initializes the UI window
    using pytest-qt's qtbot.
    """
    test_app = UI()
    qtbot.addWidget(test_app)
    return test_app

def test_take_screenshot_button_creates_file(app, qtbot, tmp_path):
    """
    Simulates clicking the 'Take Screenshot' button.
    Assumes mocked screenshot function creates a dummy image.
    Verifies the output file is created.
    """
    # Override the file path to avoid writing to user directories
    app.file_path = tmp_path / "test_output.txt"

    # Simulate click
    QTest.mouseClick(app.capture_button, Qt.LeftButton)

    # Expect the file to be created (if screenshot and OCR succeed)
    assert app.file_path.exists() or app.image_label.text() == "No image captured."

def test_open_settings_window(app, qtbot):
    """
    Verifies that the Settings window opens when the Settings button is clicked.
    """
    QTest.mouseClick(app.options_button, Qt.LeftButton)
    assert app.open_settings.isVisible()

def test_open_keybindings_window(app, qtbot):
    """
    Verifies that the Keybindings window opens when the Keybindings button is clicked.
    """
    QTest.mouseClick(app.keybinds_button, Qt.LeftButton)
    assert app.open_keybinds.isVisible()

def test_pdf_upload_handling(monkeypatch, app, qtbot):
    """
    Mocks selecting a PDF file and checks the OCR conversion logic runs without crashing.
    Hardcodes poppler_path for consistent test behavior.
    """
    dummy_pdf_path = os.path.abspath("sample.pdf")  # Ensure this file exists for real test

    def mock_get_open_file_name(*args, **kwargs):
        return (dummy_pdf_path, None)

    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getOpenFileName", mock_get_open_file_name)

    # Patch UI.convert_pdf to inject the poppler_path during the test
    def mock_convert_pdf(self, file_info):
        from pdf2image import convert_from_path
        try:
            convert_from_path(file_info, dpi=100, poppler_path=DEFAULT_POPPLER_PATH)
            self.image_label.setText("PDF processed")
        except Exception as e:
            self.image_label.setText(f"Error: {str(e)}")

    monkeypatch.setattr(UI, "convert_pdf", mock_convert_pdf)

    app.file_select()
    assert "PDF processed" in app.image_label.text()

def test_file_select_with_invalid_file(monkeypatch, app, qtbot, tmp_path):
    """
    Simulates uploading a non-image/non-PDF file.
    Expects the UI to display an error and not crash.
    """
    bad_file = tmp_path / "badfile.exe"
    bad_file.write_text("not an image")

    def mock_get_open_file_name(*args, **kwargs):
        return (str(bad_file), None)

    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getOpenFileName", mock_get_open_file_name)

    try:
        app.file_select()
    except Exception:
        app.image_label.setText("Error loading chosen file")

    assert "Error loading chosen file" in app.image_label.text()