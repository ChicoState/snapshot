# snapshot

## 📦 How to Use the `snapshot.exe` Tool

### 🔧 Requirements
- Windows 10 or 11
- **Must be run as Administrator** (required for AutoHotkey automation and screen control)

### 🚀 Running the Executable

1. Download or copy `snapshot.exe` to any folder on your system.
2. Right-click on `snapshot.exe` and select **"Run as administrator"**.
3. The application will launch and begin handling UI automation tasks as configured.

> ⚠️ **Important:** The tool uses AutoHotkey behind the scenes. The `AutoHotkey.exe` binary is embedded automatically in the executable when built, so **you do not need to install AutoHotkey manually**.

---

### 💡 Notes

- If the application does not launch or fails silently, ensure:
  - It’s run with admin rights.
  - No antivirus is blocking AutoHotkey automation.
- You can check logs or run from a Command Prompt with:
  ```cmd
  snapshot.exe
