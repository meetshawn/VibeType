@echo off
setlocal
chcp 65001 >nul
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"

echo [1/3] Checking Python...
python --version >nul 2>nul
if errorlevel 1 (
  echo Python not found. Please install Python 3.10+ and try again.
  goto :err
)

if not exist "%PYTHON_EXE%" (
  echo [2/3] Creating virtual environment...
  python -m venv "%VENV_DIR%"
  if errorlevel 1 goto :err
) else (
  echo [2/3] Virtual environment already exists.
)

echo [3/3] Installing dependencies...
"%PIP_EXE%" install -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 goto :err

echo.
echo Install completed successfully.
pause
exit /b 0

:err
echo.
echo Install failed. Check the error messages above.
pause
exit /b 1
