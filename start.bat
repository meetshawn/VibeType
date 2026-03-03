@echo off
setlocal
chcp 65001 >nul
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"
set "NEED_INSTALL=0"

if /I "%~1"=="install" set "NEED_INSTALL=1"

if not exist "%PYTHON_EXE%" (
  echo [1/3] Creating virtual environment...
  python -m venv "%VENV_DIR%"
  if errorlevel 1 goto :err
  set "NEED_INSTALL=1"
)

if "%NEED_INSTALL%"=="1" (
  echo [2/3] Installing dependencies...
  "%PIP_EXE%" install -r "%SCRIPT_DIR%requirements.txt"
  if errorlevel 1 goto :err
) else (
  echo [2/3] Skip dependency install. ^(run: start.bat install^)
)

echo [3/3] Starting desktop hotkey app...
"%PYTHON_EXE%" "%SCRIPT_DIR%desktop_hotkey.py"
goto :eof

:err
echo Failed. Please check errors above.
pause
exit /b 1
