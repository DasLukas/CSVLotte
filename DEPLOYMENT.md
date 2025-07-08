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
```

The script:
- Runs tests
- Updates version numbers
- Creates Git tag
- Prepares release

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
