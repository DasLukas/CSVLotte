#!/usr/bin/env python3
"""
Build script for CSVLotte application.
Creates executable files for Windows using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
APP_NAME = "CSVLotte"
MAIN_SCRIPT = "src/main.py"
ICON_PATH = "src/csvlotte/assets/logo.ico"
DIST_DIR = "dist"
BUILD_DIR = "build"
SPEC_FILE = f"{APP_NAME.lower()}.spec"

def clean_build_dirs():
    """Remove existing build and dist directories."""
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(dir_path):
            print(f"Removing {dir_path}...")
            shutil.rmtree(dir_path)

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])

def create_spec_file():
    """Create PyInstaller spec file."""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/csvlotte/assets', 'csvlotte/assets'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'pandas',
        'tkhtmlview',
        'markdown',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{ICON_PATH}',
)
'''
    
    with open(SPEC_FILE, 'w') as f:
        f.write(spec_content)
    print(f"Created {SPEC_FILE}")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    # First, embed README.md content as Python string
    print("Embedding README.md content...")
    result = subprocess.run([sys.executable, "embed_readme.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Warning: Could not embed README.md content")
        print(result.stderr)
    
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", SPEC_FILE]
    subprocess.check_call(cmd)
    print("Build completed successfully!")

def create_installer():
    """Create installer using Inno Setup (if available)."""
    inno_setup_path = shutil.which("iscc")
    if inno_setup_path:
        print("Creating installer with Inno Setup...")
        # We'll create the Inno Setup script next
        iss_file = "installer.iss"
        if os.path.exists(iss_file):
            subprocess.check_call([inno_setup_path, iss_file])
            print("Installer created successfully!")
    else:
        print("Inno Setup not found. Skipping installer creation.")
        print("You can manually create an installer or distribute the executable from the dist folder.")

def main():
    """Main build process."""
    print(f"Building {APP_NAME}...")
    
    # Check if we're in the right directory
    if not os.path.exists(MAIN_SCRIPT):
        print(f"Error: {MAIN_SCRIPT} not found. Make sure you're in the project root directory.")
        sys.exit(1)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    build_executable()
    
    # Create installer
    create_installer()
    
    print("\nBuild process completed!")
    print(f"Executable can be found in: {DIST_DIR}/{APP_NAME}.exe")

if __name__ == "__main__":
    main()
