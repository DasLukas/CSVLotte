# CSVLotte Deployment Guide

This guide explains how to build and deploy CSVLotte for release.

## Overview

The deployment process includes:
- **Local builds** with PyInstaller
- **Automated builds** with GitHub Actions
- **Installer creation** for Windows
- **Version management** and releases

## Prerequisites

- Python 3.11 or higher
- Git for version control
- (Optional) Inno Setup for Windows installer

## Local Build

### 1. Windows Build

```bash
# Simple build
build.bat

# Or manually
python build.py
```

### 2. Linux/macOS Build

```bash
# Simple build
chmod +x build.sh
./build.sh

# Or manually
python3 build.py
```

The result can be found in `dist/CSVLotte.exe` (Windows) or `dist/CSVLotte` (Linux/macOS).

## Release Process

### 1. Version increment

```bash
# Patch version (0.1.0 → 0.1.1)
python release.py patch

# Minor version (0.1.0 → 0.2.0)
python release.py minor

# Major version (0.1.0 → 1.0.0)
python release.py major

# Skip tests (if needed)
python release.py patch --skip-tests
```

The script:
- Installs test dependencies automatically if needed
- Runs tests (can be skipped with --skip-tests)
- Updates version numbers
- Prepares release for dev branch

### 2. Publishing

```bash
# Push changes
git push

# Push tag (triggers automatic build)
git push origin v0.1.1
```

## GitHub Actions

The automated pipeline (`.github/workflows/build.yml`):

1. **Run tests** - All tests must pass
2. **Create build** - PyInstaller creates executable
3. **Create release** - Automatically on Git tags
4. **Upload assets** - ZIP file with executable

## Files in the Deployment System

- `build.py` - Main build script
- `build.bat` - Windows build script
- `build.sh` - Linux/macOS build script
- `release.py` - Release management
- `installer.iss` - Inno Setup installer configuration
- `.github/workflows/build.yml` - GitHub Actions CI/CD

## Manual Steps

### Create Windows Installer

1. Install [Inno Setup](https://www.jrsoftware.org/isinfo.php)
2. Run build: `python build.py`
3. The installer will be created automatically if Inno Setup is available

### Manual GitHub Release

1. Go to GitHub → Releases
2. Click "Create a new release"
3. Select tag and upload `dist/CSVLotte-Windows.zip`

## Tips

- **Always test** before release: `pytest tests/`
- **Check the executable** after build
- **Document changes** in release notes
- **Use semantic versioning** (Major.Minor.Patch)

## Troubleshooting

### PyInstaller Issues

```bash
# Clean build
python build.py
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
```

### Build Errors

- Check if all paths are correct
- Ensure asset files exist
- Verify Python version (3.11+)

### Common Release Issues

#### Issue: "No module named pytest"
**Solution**: The release script will automatically install pytest and test dependencies. If this fails, install manually:
```bash
pip install pytest pytest-cov pytest-mock
```

#### Issue: "GitHub CLI (gh) not found"
**Solution**: Install GitHub CLI or create PR manually:
```bash
# Install GitHub CLI
winget install GitHub.cli

# Or create PR manually at:
# https://github.com/your-username/csvlotte/compare/main...dev
```

#### Issue: Test failures blocking release
**Solution**: Fix the tests or skip them temporarily:
```bash
python release.py patch --skip-tests
```

#### Issue: Version already exists
**Solution**: The script will detect existing versions and prevent duplicates.

#### Issue: Git not clean
**Solution**: Commit or stash your changes before running the release script.

#### Issue: FileNotFoundError in release_to_main.py
**Solution**: This usually means GitHub CLI is not installed. The script will guide you through manual PR creation.

## README.md Integration

The build system ensures that README.md is available after build:

1. **File integration**: README.md is embedded directly into the executable
2. **Embedded fallback**: If file is not found, content is embedded as Python string
3. **Automatic process**: The script `embed_readme.py` is automatically executed during build

### How it works

- `embed_readme.py` converts README.md to a Python file
- PyInstaller copies README.md into the executable
- The application searches for README.md in various paths
- If not found, embedded content is used as fallback

## Next Steps

1. **Test the build process** completely once
2. **Create your first release** with `python release.py patch`
3. **Adjust GitHub URLs** in `installer.iss`
4. **Extend CI/CD** for additional platforms (Linux, macOS)

Your deployment system is now ready for the first release! 🚀

## Branch-based Deployment

For projects using separate development and release branches:

### Branch Structure
- **`dev` branch**: Active development, all new features and bug fixes
- **`main` branch**: Production-ready releases only, protected

### Development Workflow

```bash
# Work on dev branch
git checkout dev
git pull origin dev

# Make changes, commit, push
git add .
git commit -m "Add new feature"
git push origin dev
```

### Release Workflow

```bash
# 1. Prepare release on dev branch
git checkout dev
python release.py patch  # bump version

# 2. Push version bump to dev
git push origin dev

# 3. Create and merge PR to main
# Use GitHub UI or:
python release_to_main.py

# 4. Tag is created automatically after merge
# GitHub Actions builds and releases
```

### Automated Pipelines

- **Dev branch**: Runs tests, creates test build
- **Main branch**: Runs tests, creates release build, publishes to GitHub

### Files for Branch-based Deployment
- `release_to_main.py` - Automated release script
- `.github/workflows/dev.yml` - Development pipeline
- `.github/workflows/build.yml` - Release pipeline (updated)
- `BRANCHING_STRATEGY.md` - Detailed branching documentation

### Alternative Release Methods

#### Method 1: With GitHub CLI (Recommended)
```bash
# Install GitHub CLI first
winget install GitHub.cli

# Then use automated release
python release.py patch
python release_to_main.py
```

#### Method 2: Manual PR Creation
```bash
# 1. Bump version
python release.py patch

# 2. Push to dev
git push origin dev

# 3. Create PR manually on GitHub
# Go to: https://github.com/your-username/csvlotte/compare/main...dev

# 4. After PR is merged, create tag
git checkout main && git pull origin main
git tag v1.0.1 && git push origin v1.0.1
```

#### Method 3: Direct Merge (Not Recommended)
```bash
# Only for solo development without PR review
python release.py patch
python release_to_main.py
# Choose option 2 for direct merge
```

## Cross-Platform Compatibility

CSVLotte's deployment system is designed to work across Windows, macOS, and Linux. The release scripts automatically detect the platform and use the appropriate commands.

### Platform Testing

Before using the release scripts, run the platform compatibility test:

```bash
# Windows
py test_platform_compatibility.py

# macOS/Linux
python3 test_platform_compatibility.py
```

This script will:
- Check if Git is installed and working
- Verify Python executable detection
- Test GitHub CLI availability
- Validate required dependencies
- Provide platform-specific installation instructions

### Platform-Specific Commands

The release scripts automatically use the correct commands for each platform:

| Platform | Python Command | Package Manager | Shell |
|----------|----------------|----------------|--------|
| Windows  | `py`           | `pip`          | PowerShell/CMD |
| macOS    | `python3`      | `pip3`         | zsh/bash |
| Linux    | `python3`      | `pip3`         | bash |

### Installation Instructions

#### Windows
```powershell
# Install Python (if not already installed)
winget install Python.Python.3.11

# Install Git
winget install Git.Git

# Install GitHub CLI (optional but recommended)
winget install GitHub.cli

# Install project dependencies
py -m pip install -r requirements.txt
```

#### macOS
```bash
# Install Python (using Homebrew)
brew install python@3.11

# Install Git (usually pre-installed)
brew install git

# Install GitHub CLI (optional but recommended)
brew install gh

# Install project dependencies
python3 -m pip install -r requirements.txt
```

#### Linux (Ubuntu/Debian)
```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip git

# Install GitHub CLI (optional but recommended)
# Follow instructions at https://cli.github.com/

# Install project dependencies
python3 -m pip install -r requirements.txt
```

### Build Commands by Platform

The build scripts automatically handle platform differences:

```bash
# Windows
build.bat
# or
py build.py

# macOS/Linux
chmod +x build.sh
./build.sh
# or
python3 build.py
```

### Common Issues and Solutions

#### Issue: Command not found
Different platforms use different Python commands:
- Windows: `py`, `python`, or `python3`
- macOS/Linux: `python3` or `python`

The scripts automatically detect the correct command.

#### Issue: Permission denied (Unix/Linux)
Make shell scripts executable:
```bash
chmod +x build.sh
chmod +x release.py
```

#### Issue: PyInstaller not found
Install PyInstaller in your environment:
```bash
# Windows
py -m pip install pyinstaller

# macOS/Linux
python3 -m pip install pyinstaller
```

#### Issue: Git not in PATH
Ensure Git is installed and in your system PATH:
- Windows: Install from git-scm.com or use winget
- macOS: Install Xcode Command Line Tools or use Homebrew
- Linux: Install via package manager

### Environment Variables

The scripts respect these environment variables:
- `PYTHONPATH`: Python module search path
- `PATH`: System executable search path
- `VIRTUAL_ENV`: Virtual environment detection

### Shell Compatibility

The scripts work with:
- **Windows**: PowerShell, Command Prompt
- **macOS**: zsh (default), bash
- **Linux**: bash, sh

## Cross-Platform Release Process

The release scripts (`release.py` and `release_to_main.py`) are designed to work identically across all platforms:

#### 1. Platform Detection
The scripts automatically detect:
- Operating system (Windows, macOS, Linux)
- Python executable location
- Shell type and capabilities
- Available tools (Git, GitHub CLI)

#### 2. Command Adaptation
Commands are automatically adapted for each platform:
```python
# Windows example
py release.py patch

# macOS/Linux example  
python3 release.py patch
```

#### 3. Error Handling
Robust error handling for platform-specific issues:
- Missing dependencies are detected and installation instructions provided
- Shell command failures are properly handled
- File path differences are automatically resolved

#### 4. GitHub CLI Integration
The scripts check for GitHub CLI availability and provide fallback options:
- **Available**: Automated PR creation
- **Not available**: Manual PR instructions with platform-specific installation commands

#### 5. Git Integration
Cross-platform Git operations:
- Branch detection and switching
- Commit creation and pushing
- Tag creation and management
- Remote repository operations

### Testing Your Platform

Before running your first release, test your platform setup:

```bash
# Run platform compatibility test
py test_platform_compatibility.py    # Windows
python3 test_platform_compatibility.py    # macOS/Linux

# Test release script (without committing)
py release.py patch --skip-tests    # Windows
python3 release.py patch --skip-tests    # macOS/Linux
```

### Platform-Specific Notes

#### Windows
- Uses `py` launcher for Python execution
- PowerShell and CMD both supported
- Windows Defender might scan executables (normal behavior)
- Path separators automatically handled

#### macOS
- Uses `python3` command
- Homebrew-installed tools preferred
- Code signing may be required for distribution
- Gatekeeper warnings for unsigned executables

#### Linux
- Uses `python3` command
- Package manager dependencies may vary
- Different distributions have different package names
- AppImage or Flatpak distribution possible

## Version increment
```
