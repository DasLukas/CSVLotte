#!/bin/bash
# Build script for CSVLotte on Linux/macOS

echo "Building CSVLotte..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.11 or later."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install PyInstaller

# Run build script
echo "Running build script..."
python3 embed_readme.py
python3 build.py

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo "Build completed successfully!"
echo "Executable can be found in: dist/CSVLotte"
