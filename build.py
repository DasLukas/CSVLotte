#!/usr/bin/env python3
"""
Build script for CSVLotte application.
Creates executable files for Windows, macOS, and Linux using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
import platform

# Configuration
APP_NAME = "CSVLotte"
MAIN_SCRIPT = "src/main.py"
DIST_DIR = "dist"
BUILD_DIR = "build"
SPEC_FILE = f"{APP_NAME.lower()}.spec"

def get_icon_path():
    """Get the appropriate icon path for the current platform."""
    system = platform.system()
    if system == "Windows":
        return "src/csvlotte/assets/logo.ico"
    elif system == "Darwin":  # macOS
        return "src/csvlotte/assets/logo.icns"
    else:  # Linux and others
        return "src/csvlotte/assets/logo.png"

def get_executable_name():
    """Get the executable name for the current platform."""
    system = platform.system()
    if system == "Windows":
        return f"{APP_NAME}.exe"
    else:
        return APP_NAME

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
    icon_path = get_icon_path()
    executable_name = get_executable_name()
    
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
    name='{executable_name}',
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
    icon='{icon_path}',
)
'''
    
    with open(SPEC_FILE, 'w') as f:
        f.write(spec_content)
    print(f"Created {SPEC_FILE} for {platform.system()}")

def build_executable():
    """Build the executable using PyInstaller."""
    print(f"Building executable for {platform.system()}...")
    
    # Ensure src directory is in Python path
    import sys
    src_path = os.path.abspath('src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Set PYTHONPATH environment variable
    env = os.environ.copy()
    current_pythonpath = env.get('PYTHONPATH', '')
    if current_pythonpath:
        env['PYTHONPATH'] = f"{src_path}{os.pathsep}{current_pythonpath}"
    else:
        env['PYTHONPATH'] = src_path
    
    # First, embed README.md content as Python string
    print("Embedding README.md content...")
    result = subprocess.run([sys.executable, "embed_readme.py"], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print("Warning: Could not embed README.md content")
        print(result.stderr)
    
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", SPEC_FILE]
    subprocess.check_call(cmd, env=env)
    print("Build completed successfully!")

def create_installer():
    """Create installer using platform-specific tools (if available)."""
    system = platform.system()
    
    if system == "Windows":
        # Create installer with Inno Setup
        inno_setup_path = shutil.which("iscc")
        if inno_setup_path:
            print("Creating installer with Inno Setup...")
            iss_file = "installer.iss"
            if os.path.exists(iss_file):
                subprocess.check_call([inno_setup_path, iss_file])
                print("Installer created successfully!")
        else:
            print("Inno Setup not found. Skipping installer creation.")
            print("You can manually create an installer or distribute the executable from the dist folder.")
    
    elif system == "Darwin":
        # macOS: Create .app bundle or .dmg
        print("macOS: Executable created. Consider creating a .app bundle or .dmg for distribution.")
        print("You can use tools like py2app or create-dmg for this.")
    
    elif system == "Linux":
        # Linux: Create .deb, .rpm, or AppImage
        print("Linux: Executable created. Consider creating a .deb, .rpm, or AppImage for distribution.")
        print("You can use tools like fpm, alien, or appimagetool for this.")
    
    else:
        print(f"Unknown platform: {system}. Executable created in {DIST_DIR}/")

def main():
    """Main build process."""
    system = platform.system()
    executable_name = get_executable_name()
    
    print(f"Building {APP_NAME} for {system}...")
    
    # Add src to Python path
    import sys
    src_path = os.path.abspath('src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Check if we're in the right directory
    if not os.path.exists(MAIN_SCRIPT):
        print(f"Error: {MAIN_SCRIPT} not found. Make sure you're in the project root directory.")
        sys.exit(1)
    
    # Check if icon file exists
    icon_path = get_icon_path()
    if not os.path.exists(icon_path):
        print(f"Warning: Icon file {icon_path} not found. Build will continue without icon.")
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    build_executable()
    
    # Create installer (platform-specific)
    create_installer()
    
    print("\nBuild process completed!")
    print(f"Executable can be found in: {DIST_DIR}/{executable_name}")
    
    # Show platform-specific instructions
    if system == "Windows":
        print("You can now run the executable directly or create an installer.")
    elif system == "Darwin":
        print("To run: ./dist/CSVLotte")
        print("Consider creating a .app bundle for better macOS integration.")
    elif system == "Linux":
        print("To run: ./dist/CSVLotte")
        print("You may need to set execute permissions: chmod +x dist/CSVLotte")
    
    print(f"\nFor cross-platform distribution, run this script on each target platform.")
    
    # Verify the build
    dist_path = os.path.join(DIST_DIR, executable_name)
    if os.path.exists(dist_path):
        print(f"✓ Build successful: {dist_path}")
        file_size = os.path.getsize(dist_path)
        print(f"✓ File size: {file_size / (1024*1024):.1f} MB")
    else:
        print("✗ Build failed: Executable not found")
        sys.exit(1)

if __name__ == "__main__":
    main()
