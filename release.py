#!/usr/bin/env python3
"""
Release script for CSVLotte.
Handles version bumping, tagging, and release preparation.
"""

import os
import re
import sys
import subprocess
from pathlib import Path

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

def run_tests():
    """Run tests before release."""
    print("Running tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Tests failed!")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("All tests passed!")
    return True

def create_git_tag(version):
    """Create git tag for the release."""
    tag = f"v{version}"
    
    # Ensure we're on dev branch
    current_branch = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True).stdout.strip()
    if current_branch != "dev":
        print(f"Warning: You're on branch '{current_branch}', should be on 'dev'")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Check if tag already exists
    result = subprocess.run(["git", "tag", "-l", tag], capture_output=True, text=True)
    if result.stdout.strip():
        print(f"Tag {tag} already exists!")
        return False
    
    # Commit version changes
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Bump version to {version}"], check=True)
    
    print(f"Version {version} committed to dev branch")
    return True

def main():
    """Main release process."""
    if len(sys.argv) != 2:
        print("Usage: python release.py <major|minor|patch>")
        sys.exit(1)
    
    part = sys.argv[1]
    if part not in ['major', 'minor', 'patch']:
        print("Invalid version part. Use: major, minor, or patch")
        sys.exit(1)
    
    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Calculate new version
    new_version = increment_version(current_version, part)
    print(f"New version: {new_version}")
    
    # Confirm
    response = input(f"Release version {new_version}? (y/N): ")
    if response.lower() != 'y':
        print("Release cancelled.")
        sys.exit(0)
    
    # Run tests
    if not run_tests():
        print("Release cancelled due to test failures.")
        sys.exit(1)
    
    # Update version files
    update_version(new_version)
    update_installer_version(new_version)
    
    # Create git tag
    if not create_git_tag(new_version):
        print("Failed to create git tag.")
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
    print("python release_to_main.py")

if __name__ == "__main__":
    main()
