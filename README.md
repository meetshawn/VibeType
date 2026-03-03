# VibeType

English | [简体中文](README.zh-CN.md)

Desktop-only voice-to-text tool based on `iic/SenseVoiceSmall`.

## Files

- `install-deps.bat`: create `.venv` and install dependencies on Windows
- `install-deps.sh`: create `.venv` and install dependencies on Linux/macOS
- `start.bat`: start the desktop app on Windows
- `start.sh`: start the desktop app on Linux/macOS
- `start-hotkey.bat`: same as `start.bat`
- `start-hotkey.sh`: same as `start.sh`

## Usage

### Windows

1. Run `install-deps.bat` once
2. Run `start.bat`
3. Focus any input box
4. Press `Ctrl+Shift+Space` to start recording
5. Press `Ctrl+Shift+Space` again to stop and type the result

### Linux/macOS

1. Run `chmod +x install-deps.sh start.sh start-hotkey.sh`
2. Run `./install-deps.sh` once
3. Run `./start.sh`
4. Focus any input box
5. Press `Ctrl+Shift+Space` to start recording
6. Press `Ctrl+Shift+Space` again to stop and type the result

## Notes

- Default language is Chinese (`zh`)
- Card-based desktop UI
- Live microphone level meter
- History list for recent recognition results
- Supports window "Always on top"
- Supports "Send window to background after stop"
- Force reinstall dependencies:
  - Windows: `start.bat install`
  - Linux/macOS: `./start.sh install`
- If hotkey does not trigger inside elevated/admin apps on Windows, run this app as administrator too
