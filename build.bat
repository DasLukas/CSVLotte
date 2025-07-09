@echo off
REM Build script for CSVLotte on Windows

echo Building CSVLotte...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.11 or later.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install PyInstaller

REM Run build script
echo Running build script...
python embed_readme.py
python build.py

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo Build completed successfully!
echo Executable can be found in: dist\CSVLotte.exe
pause
