#!/usr/bin/env python3
"""
Release script for CSVLotte.
Handles version bumping, tagging, and release preparation.
Cross-platform support for Windows, macOS, and Linux.
"""

import os
import re
import sys
import subprocess
import platform
from pathlib import Path

def get_python_executable():
    """Get the correct Python executable for the current platform."""
    return sys.executable

def run_command(cmd, **kwargs):
    """Run command with proper error handling across platforms."""
    try:
        if isinstance(cmd, str):
            # Use shell=True on Windows for string commands
            shell = platform.system() == "Windows"
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, **kwargs)
        else:
            # List commands work the same on all platforms
            result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
        return result
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def get_platform_command_prefix():
    """Get the proper command prefix for the current platform."""
    if platform.system() == "Windows":
        return "py"
    else:
        return "python3"

def check_git_available():
    """Check if Git is available on the system."""
    try:
        result = run_command(["git", "--version"])
        return result and result.returncode == 0
    except:
        return False

def get_current_version():
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    
    return match.group(1)

def update_version(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    # Update version
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    
    with open(pyproject_path, 'w') as f:
        f.write(content)
    
    print(f"Updated version to {new_version} in pyproject.toml")

def update_installer_version(new_version):
    """Update version in installer.iss."""
    installer_path = Path("installer.iss")
    
    if installer_path.exists():
        with open(installer_path, 'r') as f:
            content = f.read()
        
        # Update version
        content = re.sub(r'AppVersion=[^\r\n]+', f'AppVersion={new_version}', content)
        
        with open(installer_path, 'w') as f:
            f.write(content)
        
        print(f"Updated version to {new_version} in installer.iss")

def increment_version(version, part='patch'):
    """Increment version number."""
    major, minor, patch = map(int, version.split('.'))
    
    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def install_test_dependencies():
    """Install test dependencies if not available."""
    try:
        import pytest
        return True
    except ImportError:
        print("pytest not found. Installing test dependencies...")
        try:
            python_exe = get_python_executable()
            result = run_command([python_exe, "-m", "pip", "install", "pytest", "pytest-cov", "pytest-mock"])
            if result and result.returncode == 0:
                print("✓ Test dependencies installed successfully")
                return True
            else:
                print(f"Failed to install test dependencies: {result.stderr if result else 'Unknown error'}")
                return False
        except Exception as e:
            print(f"Failed to install test dependencies: {e}")
            return False

def run_tests():
    """Run tests before release."""
    print("Checking test environment...")
    
    # Install test dependencies if needed
    if not install_test_dependencies():
        return False
    
    print("Running tests...")
    try:
        python_exe = get_python_executable()
        result = run_command([python_exe, "-m", "pytest", "tests/", "-v"], timeout=300)
        
        if not result or result.returncode != 0:
            print("Tests failed!")
            if result:
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            return False
        
        print("All tests passed!")
        if result.stdout:
            print("Test output:", result.stdout)
        return True
        
    except subprocess.TimeoutExpired:
        print("Tests timed out after 5 minutes!")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def create_git_tag(version):
    """Create git tag for the release."""
    if not check_git_available():
        print("Error: Git is not available on this system.")
        print("Please install Git and try again.")
        return False
    
    tag = f"v{version}"
    
    # Ensure we're on dev branch
    result = run_command(["git", "branch", "--show-current"])
    if not result or result.returncode != 0:
        print("Error: Could not determine current Git branch.")
        return False
    
    current_branch = result.stdout.strip()
    if current_branch != "dev":
        print(f"Warning: You're on branch '{current_branch}', should be on 'dev'")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Check if tag already exists
    result = run_command(["git", "tag", "-l", tag])
    if result and result.stdout.strip():
        print(f"Tag {tag} already exists!")
        return False
    
    # Commit version changes
    print("Adding changes to Git...")
    result = run_command(["git", "add", "."])
    if not result or result.returncode != 0:
        print(f"Error adding files to Git: {result.stderr if result else 'Unknown error'}")
        return False
    
    print(f"Committing version bump...")
    result = run_command(["git", "commit", "-m", f"Bump version to {version}"])
    if not result or result.returncode != 0:
        print(f"Error committing changes: {result.stderr if result else 'Unknown error'}")
        return False
    
    print(f"Version {version} committed to dev branch")
    return True

def main():
    """Main release process."""
    print(f"CSVLotte Release Script")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)
    
    if len(sys.argv) not in [2, 3]:
        print("Usage:")
        print(f"  {get_platform_command_prefix()} release.py <major|minor|patch> [--skip-tests]")
        print("")
        print("Examples:")
        print(f"  {get_platform_command_prefix()} release.py patch")
        print(f"  {get_platform_command_prefix()} release.py minor --skip-tests")
        sys.exit(1)
    
    # Check prerequisites
    if not check_git_available():
        print("Error: Git is not available on this system.")
        print("Please install Git and try again.")
        if platform.system() == "Windows":
            print("Windows: Download from https://git-scm.com/download/win")
        elif platform.system() == "Darwin":
            print("macOS: Install with 'brew install git' or from https://git-scm.com/download/mac")
        else:
            print("Linux: Install with your package manager (e.g., 'sudo apt install git')")
        sys.exit(1)
    
    part = sys.argv[1]
    if part not in ['major', 'minor', 'patch']:
        print("Invalid version part. Use: major, minor, or patch")
        sys.exit(1)
    
    skip_tests = len(sys.argv) == 3 and sys.argv[2] == '--skip-tests'
    
    # Get current version
    try:
        current_version = get_current_version()
        print(f"Current version: {current_version}")
    except Exception as e:
        print(f"Error reading current version: {e}")
        sys.exit(1)
    
    # Calculate new version
    new_version = increment_version(current_version, part)
    print(f"New version: {new_version}")
    
    # Confirm
    response = input(f"Release version {new_version}? (y/N): ")
    if response.lower() != 'y':
        print("Release cancelled.")
        sys.exit(0)
    
    # Run tests (unless skipped)
    if not skip_tests:
        if not run_tests():
            print("Release cancelled due to test failures.")
            print(f"You can skip tests with: {get_platform_command_prefix()} release.py {part} --skip-tests")
            sys.exit(1)
    else:
        print("⚠️  Tests skipped as requested")
    
    # Update version files
    try:
        update_version(new_version)
        update_installer_version(new_version)
    except Exception as e:
        print(f"Error updating version files: {e}")
        sys.exit(1)
    
    # Create git tag
    if not create_git_tag(new_version):
        print("Failed to create git commit.")
        sys.exit(1)
    
    print(f"\nVersion {new_version} prepared successfully!")
    print("\nNext steps for release:")
    print("1. Push changes to dev: git push origin dev")
    print("2. Create Pull Request from 'dev' to 'main' branch")
    print("3. After PR is merged, checkout main and create tag:")
    print(f"   git checkout main && git pull origin main")
    print(f"   git tag v{new_version} && git push origin v{new_version}")
    print("4. GitHub Actions will automatically build and create the release")
    print("\nAlternatively, use the automated release script:")
    print(f"{get_platform_command_prefix()} release_to_main.py")

if __name__ == "__main__":
    main()
