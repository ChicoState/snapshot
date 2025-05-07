import subprocess
import sys
import os
import shutil
import tempfile
import requests


def get_real_python():
    if getattr(sys, 'frozen', False):
        # Use system-installed Python, not the PyInstaller executable
        for candidate in ['python', 'python3']:
            if shutil.which(candidate):
                return candidate
        raise RuntimeError("Could not find a valid Python interpreter.")
    return sys.executable

def install_tesseract_silently():
    # Tesseract installer URL (UB Mannheim version)
    url = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe?raw=true"

    # Temporary location to save the installer
    installer_path = os.path.join(tempfile.gettempdir(), "tesseract-installer.exe")

    # Download the installer
    print("Downloading Tesseract...")
    response = requests.get(url, stream=True)
    with open(installer_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Run silent install
    print("Installing Tesseract silently...")
    try:
        subprocess.run([installer_path, "/S"], check=True)
        print("✅ Tesseract installed successfully.")
    except subprocess.CalledProcessError as e:
        print("❌ Installation failed:", e)

def main():

    install_tesseract_silently()


    # Check if requirements.txt exists in the current directory
    req_file = "requirements.txt"
    if not os.path.isfile(req_file):
        print(f"❌ '{req_file}' not found in current directory.")
        return

    python_exec = get_real_python()

    with open(req_file, "r") as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not packages:
        print("✅ requirements.txt is empty or only has comments.")
        return

    for pkg in packages:
        print(f"\n📦 Installing: {pkg}")
        try:
            process = subprocess.Popen(
                [python_exec, "-m", "pip", "install", "--no-cache-dir", pkg],
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            process.communicate()

            if process.returncode != 0:
                print(f"❌ Failed to install {pkg} (exit code {process.returncode})")
                break
        except Exception as e:
            print(f"❌ Error while installing {pkg}: {e}")
            break

    else:
        print("\n✅ All packages installed successfully.")

if __name__ == "__main__":
    main()
