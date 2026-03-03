# vibeVoice

Desktop-only voice-to-text tool based on `iic/SenseVoiceSmall`.

## Files

- `install-deps.bat`: create `.venv` and install dependencies
- `start.bat`: start the desktop app
- `start-hotkey.bat`: same as `start.bat`

## Usage

1. Run `install-deps.bat` once
2. Run `start.bat`
3. Focus any input box
4. Press `Ctrl+Shift+Space` to start recording
5. Press `Ctrl+Shift+Space` again to stop and type the result

## Notes

- Default language is Chinese (`zh`)
- Card-based desktop UI
- Live microphone level meter
- History list for recent recognition results
- Supports window "Always on top"
- Supports "Send window to background after stop"
- If you want to force reinstall dependencies:
  - `start.bat install`
  - `start-hotkey.bat install`
- If hotkey does not trigger inside elevated/admin apps, run this app as administrator too
