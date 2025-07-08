#!/usr/bin/env python3
"""
Automated release script for CSVLotte.
This script handles the complete release process from dev to main branch.
"""

import subprocess
import sys
import os
import re
from pathlib import Path

def get_current_branch():
    """Get the current Git branch."""
    result = subprocess.run(["git", "branch", "--show-current"], 
                          capture_output=True, text=True)
    return result.stdout.strip()

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

def get_latest_tag():
    """Get the latest Git tag."""
    result = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def ensure_clean_working_directory():
    """Ensure the working directory is clean."""
    result = subprocess.run(["git", "status", "--porcelain"], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        print("Error: Working directory is not clean. Please commit or stash changes.")
        return False
    return True

def create_pull_request():
    """Create a pull request from dev to main (requires GitHub CLI)."""
    print("Creating pull request from dev to main...")
    
    # Check if GitHub CLI is available
    result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("GitHub CLI (gh) not found. Please create PR manually:")
        print("https://github.com/your-username/csvlotte/compare/main...dev")
        return False
    
    # Create PR
    version = get_current_version()
    pr_title = f"Release v{version}"
    pr_body = f"""## Release v{version}

This PR contains the changes for version {version}.

### Changes
- Version bump to {version}
- See commit history for detailed changes

### Checklist
- [x] Tests pass
- [x] Version updated
- [x] Ready for release
"""
    
    result = subprocess.run([
        "gh", "pr", "create",
        "--title", pr_title,
        "--body", pr_body,
        "--base", "main",
        "--head", "dev"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Pull request created successfully")
        print(result.stdout)
        return True
    else:
        print("Error creating pull request:")
        print(result.stderr)
        return False

def merge_to_main():
    """Merge dev branch to main and create tag."""
    print("Switching to main branch...")
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull", "origin", "main"], check=True)
    
    print("Merging dev branch...")
    subprocess.run(["git", "merge", "dev"], check=True)
    
    print("Pushing to main...")
    subprocess.run(["git", "push", "origin", "main"], check=True)
    
    # Create and push tag
    version = get_current_version()
    tag = f"v{version}"
    
    print(f"Creating tag {tag}...")
    subprocess.run(["git", "tag", "-a", tag, "-m", f"Release v{version}"], check=True)
    subprocess.run(["git", "push", "origin", tag], check=True)
    
    print("✓ Release completed successfully!")
    print(f"✓ Tag {tag} created and pushed")
    
    return True

def main():
    """Main release process."""
    print("CSVLotte Automated Release to Main")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("Error: pyproject.toml not found. Are you in the project root?")
        sys.exit(1)
    
    # Ensure clean working directory
    if not ensure_clean_working_directory():
        sys.exit(1)
    
    # Check current branch
    current_branch = get_current_branch()
    print(f"Current branch: {current_branch}")
    
    if current_branch != "dev":
        print("Error: You must be on the 'dev' branch to create a release")
        sys.exit(1)
    
    # Get version info
    current_version = get_current_version()
    latest_tag = get_latest_tag()
    
    print(f"Current version: {current_version}")
    print(f"Latest tag: {latest_tag}")
    
    # Confirm release
    print(f"\nThis will create a release for version {current_version}")
    print("The process will:")
    print("1. Create a pull request from 'dev' to 'main'")
    print("2. Wait for you to merge the PR")
    print("3. Create and push the release tag")
    
    response = input("\nProceed with release? (y/N): ")
    if response.lower() != 'y':
        print("Release cancelled.")
        sys.exit(0)
    
    # Option 1: Create PR (manual merge)
    print("\nChoose release method:")
    print("1. Create PR for manual review and merge")
    print("2. Directly merge to main (skip PR)")
    
    choice = input("Choose option (1/2): ")
    
    if choice == "1":
        if create_pull_request():
            print("\n✓ Pull request created successfully!")
            print("Please review and merge the PR, then run this script again with option 2")
        else:
            print("Failed to create pull request. Please create it manually.")
    
    elif choice == "2":
        # Verify that dev changes are in main (either via merged PR or direct merge)
        response = input("Are you sure dev changes are merged into main? (y/N): ")
        if response.lower() != 'y':
            print("Please merge dev to main first.")
            sys.exit(1)
        
        if merge_to_main():
            print(f"\n🎉 Release v{current_version} completed successfully!")
            print("GitHub Actions will now build and publish the release.")
    
    else:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
