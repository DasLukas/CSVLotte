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

### 1. Version increment and Release

The new unified `release.py` script handles both version bumping and the complete release process:

```bash
# Patch version (0.1.0 → 0.1.1)
python release.py patch

# Minor version (0.1.0 → 0.2.0)
python release.py minor

# Major version (0.1.0 → 1.0.0)
python release.py major

# Skip tests (if needed)
python release.py patch --skip-tests

# Complete release process only (after version bump)
python release.py --release
```

#### Unified Workflow Options:

**Option 1: Complete Release in One Step**
```bash
python release.py patch
# Script will ask: "Do you want to continue with the release process? (y/N)"
# Answer: y
# → Automatically handles: version bump, tests, push to dev, PR creation, merge to main, tag creation
```

**Option 2: Two-Step Process**
```bash
# Step 1: Version bump only
python release.py patch
# Answer: N (when asked about release process)

# Step 2: Complete release later
python release.py --release
```

The script will:
- Run tests automatically (can be skipped with --skip-tests)
- Update version numbers in pyproject.toml and installer.iss
- Create git commit on dev branch
- Optionally push to dev and handle the complete release process
- Create Pull Request from dev to main (or direct merge)
- Create and push the release tag
- Automatically sync dev branch with main after release

### 2. Release Methods

The script offers three release methods:

1. **Create PR for review** (recommended):
   - Uses GitHub CLI if available
   - Falls back to manual PR creation instructions
   - Allows for code review before release

2. **Direct merge** (for solo development):
   - Directly merges dev to main
   - Skips PR review process
   - Faster but no review step

3. **Manual handling**:
   - Exits and provides instructions
   - Allows for custom release process

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
- `release.py` - Unified release management (version bump + complete release process)
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

#### Issue: py release.py --release produces no output
**Solution**: This was a bug where the script was missing the `if __name__ == "__main__":` block. The issue has been fixed. If you encounter this, make sure you have the latest version of the script.

#### Issue: "No module named pytest"
**Solution**: The release script will automatically install pytest and test dependencies. If this fails, install manually:
```bash
pip install pytest pytest-cov pytest-mock
```

#### Issue: "GitHub CLI (gh) not found"
**Solution**: Install GitHub CLI or the script will guide you through manual PR creation:
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

#### Issue: Not on dev branch
**Solution**: The script will warn you if you're not on the dev branch and ask for confirmation.

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

## Unified Release Workflow

The new unified `release.py` script streamlines the entire release process:

### Single Command Release
```bash
python release.py patch
# Answer 'y' when asked about continuing with release process
# → Complete release from version bump to GitHub release
```

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

# Create release
python release.py patch  # This can now handle the complete process
```

### Automated Process

The unified script handles:
1. **Version bumping** in pyproject.toml and installer.iss
2. **Test execution** (with automatic dependency installation)
3. **Git commit** creation on dev branch
4. **Push to dev** branch
5. **PR creation** (via GitHub CLI or manual instructions)
6. **Merge to main** (after PR approval or direct merge)
7. **Tag creation** and push
8. **Branch synchronization** (dev synced with main)

### GitHub Actions Integration

After the tag is created, GitHub Actions automatically:
- Runs tests on all platforms
- Creates builds for Windows, Linux, and macOS
- Creates GitHub release with downloadable assets

### Release Methods

The unified `release.py` script offers flexible release methods:

#### Method 1: Complete Automated Release (Recommended)
```bash
# One command does everything
python release.py patch
# Answer 'y' to continue with release process
# → Version bump, tests, push, PR creation, merge, tag creation
```

#### Method 2: Two-Step Process
```bash
# Step 1: Version bump only
python release.py patch
# Answer 'N' when asked about release process

# Step 2: Complete release later
python release.py --release
```

#### Method 3: Manual Control
```bash
# Bump version and commit
python release.py patch
# Answer 'N' to release process

# Push manually
git push origin dev

# Create PR manually on GitHub
# After PR is merged, create tag manually:
git checkout main && git pull origin main
git tag v1.0.1 && git push origin v1.0.1
```

### GitHub CLI Integration

The script automatically detects GitHub CLI availability:
- **Available**: Automated PR creation
- **Not available**: Detailed manual instructions with platform-specific installation commands

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

The unified `release.py` script is designed to work identically across all platforms:

#### 1. Platform Detection
The script automatically detects:
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

#### 3. Unified Workflow
The same commands work across all platforms:
```bash
# Complete release process (all platforms)
python release.py patch
# Answer 'y' for complete release

# Release-only mode (all platforms)
python release.py --release
```

#### 4. Error Handling
Robust error handling for platform-specific issues:
- Missing dependencies are detected and installation instructions provided
- Shell command failures are properly handled
- File path differences are automatically resolved

#### 5. GitHub CLI Integration
The script checks for GitHub CLI availability and provides fallback options:
- **Available**: Automated PR creation
- **Not available**: Manual PR instructions with platform-specific installation commands

#### 6. Git Integration
Cross-platform Git operations:
- Branch detection and switching
- Commit creation and pushing
- Tag creation and management
- Remote repository operations
- Automatic branch synchronization

### Testing Your Platform

Before running your first release, test your platform setup:

```bash
# Test release script (without committing)
py release.py patch --skip-tests    # Windows
python3 release.py patch --skip-tests    # macOS/Linux

# Test release mode
py release.py --release    # Windows
python3 release.py --release    # macOS/Linux
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

The unified `release.py` script handles version increments and complete releases:

```bash
# Version increment with optional complete release
python release.py patch    # 1.0.0 → 1.0.1
python release.py minor    # 1.0.0 → 1.1.0  
python release.py major    # 1.0.0 → 2.0.0

# Skip tests if needed
python release.py patch --skip-tests

# Complete release process only (after version already bumped)
python release.py --release
```

The script will:
1. **Detect current version** from pyproject.toml
2. **Increment version** according to semantic versioning
3. **Run tests** (optional with --skip-tests)
4. **Update version files** (pyproject.toml, installer.iss)
5. **Create git commit** on dev branch
6. **Optionally continue** with complete release process
7. **Handle PR creation** and merge to main
8. **Create and push tags** automatically
9. **Sync dev branch** with main after release

### Semantic Versioning

- **patch**: Bug fixes and small changes (1.0.0 → 1.0.1)
- **minor**: New features, backwards compatible (1.0.0 → 1.1.0)
- **major**: Breaking changes (1.0.0 → 2.0.0)

### Files Updated

The script automatically updates:
- `pyproject.toml` - Project version
- `installer.iss` - Windows installer version (if exists)

### Safety Features

- **Duplicate detection**: Prevents creating existing versions/tags
- **Branch validation**: Warns if not on dev branch
- **Clean directory check**: Ensures no uncommitted changes
- **Test execution**: Runs tests before release (unless skipped)
- **Confirmation prompts**: Asks before major operations
```
