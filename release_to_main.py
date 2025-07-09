#!/usr/bin/env python3
"""
Automated release script for CSVLotte.
This script handles the complete release process from dev to main branch.
Cross-platform support for Windows, macOS, and Linux.
"""

import subprocess
import sys
import os
import re
import platform
from pathlib import Path

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

def check_github_cli_available():
    """Check if GitHub CLI is available on the system."""
    try:
        result = run_command(["gh", "--version"])
        return result and result.returncode == 0
    except:
        return False

def get_current_branch():
    """Get the current Git branch."""
    result = run_command(["git", "branch", "--show-current"])
    if result and result.returncode == 0:
        return result.stdout.strip()
    return None

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
    result = run_command(["git", "describe", "--tags", "--abbrev=0"])
    if result and result.returncode == 0:
        return result.stdout.strip()
    return None

def ensure_clean_working_directory():
    """Ensure the working directory is clean."""
    result = run_command(["git", "status", "--porcelain"])
    if result and result.returncode == 0 and result.stdout.strip():
        print("Error: Working directory is not clean. Please commit or stash changes.")
        return False
    return True

def create_pull_request():
    """Create a pull request from dev to main (requires GitHub CLI)."""
    print("Creating pull request from dev to main...")
    
    # Check if GitHub CLI is available
    if not check_github_cli_available():
        print("GitHub CLI (gh) not found.")
        return show_manual_pr_instructions()
    
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
    
    try:
        result = run_command([
            "gh", "pr", "create",
            "--title", pr_title,
            "--body", pr_body,
            "--base", "main",
            "--head", "dev"
        ])
        
        if result and result.returncode == 0:
            print("✓ Pull request created successfully")
            print(result.stdout)
            return True
        else:
            print("Error creating pull request:")
            if result:
                print(result.stderr)
            return show_manual_pr_instructions()
    except Exception as e:
        print(f"Error creating pull request: {e}")
        return show_manual_pr_instructions()

def show_manual_pr_instructions():
    """Show instructions for creating a PR manually."""
    print("\n" + "="*50)
    print("MANUAL PULL REQUEST INSTRUCTIONS")
    print("="*50)
    print("GitHub CLI not available. Please create PR manually:")
    print("\n1. Go to your GitHub repository")
    print("2. Click 'Compare & pull request' or go to:")
    print("   https://github.com/your-username/csvlotte/compare/main...dev")
    print("3. Create pull request from 'dev' to 'main'")
    print("4. Use this title: Release v" + get_current_version())
    print("5. Add release notes in the description")
    print("6. Review and merge the PR")
    print("7. Then run this script again with option 2 to create the tag")
    print("\nAlternatively, install GitHub CLI:")
    
    system = platform.system()
    if system == "Windows":
        print("- Windows: winget install GitHub.cli")
        print("- Or with Chocolatey: choco install gh")
        print("- Or with Scoop: scoop install gh")
    elif system == "Darwin":
        print("- macOS: brew install gh")
    else:
        print("- Linux: Check your package manager or visit https://cli.github.com/")
    
    print("- Or download from: https://cli.github.com/")
    print("="*50)
    
    response = input("\nHave you created the PR manually? (y/N): ")
    return response.lower() == 'y'

def merge_to_main():
    """Merge dev branch to main and create tag."""
    print("Switching to main branch...")
    result = run_command(["git", "checkout", "main"])
    if not result or result.returncode != 0:
        print(f"Error switching to main branch: {result.stderr if result else 'Unknown error'}")
        return False
    
    print("Pulling latest changes from main...")
    result = run_command(["git", "pull", "origin", "main"])
    if not result or result.returncode != 0:
        print(f"Error pulling from main: {result.stderr if result else 'Unknown error'}")
        return False
    
    print("Merging dev branch...")
    result = run_command(["git", "merge", "dev"])
    if not result or result.returncode != 0:
        print(f"Error merging dev: {result.stderr if result else 'Unknown error'}")
        return False
    
    print("Pushing to main...")
    result = run_command(["git", "push", "origin", "main"])
    if not result or result.returncode != 0:
        print(f"Error pushing to main: {result.stderr if result else 'Unknown error'}")
        return False
    
    # Create and push tag
    version = get_current_version()
    tag = f"v{version}"
    
    print(f"Creating tag {tag}...")
    result = run_command(["git", "tag", "-a", tag, "-m", f"Release v{version}"])
    if not result or result.returncode != 0:
        print(f"Error creating tag: {result.stderr if result else 'Unknown error'}")
        return False
    
    print(f"Pushing tag {tag}...")
    result = run_command(["git", "push", "origin", tag])
    if not result or result.returncode != 0:
        print(f"Error pushing tag: {result.stderr if result else 'Unknown error'}")
        return False
    
    print("✓ Release completed successfully!")
    print(f"✓ Tag {tag} created and pushed")
    
    return True

def main():
    """Main release process."""
    print("CSVLotte Automated Release to Main")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)
    
    # Check prerequisites
    if not check_git_available():
        print("Error: Git is not available on this system.")
        print("Please install Git and try again.")
        
        system = platform.system()
        if system == "Windows":
            print("Windows: Download from https://git-scm.com/download/win")
        elif system == "Darwin":
            print("macOS: Install with 'brew install git' or from https://git-scm.com/download/mac")
        else:
            print("Linux: Install with your package manager (e.g., 'sudo apt install git')")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("Error: pyproject.toml not found. Are you in the project root?")
        sys.exit(1)
    
    # Ensure clean working directory
    if not ensure_clean_working_directory():
        sys.exit(1)
    
    # Check current branch
    current_branch = get_current_branch()
    if not current_branch:
        print("Error: Could not determine current Git branch.")
        sys.exit(1)
    
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
    print("1. Create PR for manual review and merge (requires GitHub CLI or manual process)")
    print("2. Directly merge to main (skip PR - only if you're sure)")
    print("3. Exit and handle manually")
    
    choice = input("Choose option (1/2/3): ")
    
    if choice == "1":
        if create_pull_request():
            print("\n✓ Pull request created or ready for manual creation!")
            print("Next steps:")
            print("1. Review and merge the PR on GitHub")
            print(f"2. Run: {get_platform_command_prefix()} release_to_main.py")
            print("3. Choose option 2 to create the tag")
        else:
            print("\nPR creation failed. Please handle manually or try again.")
    
    elif choice == "2":
        # Verify that dev changes are in main (either via merged PR or direct merge)
        print("\n⚠️  WARNING: This will directly merge dev to main without PR review!")
        response = input("Are you sure you want to proceed? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(1)
        
        if merge_to_main():
            print(f"\n🎉 Release v{current_version} completed successfully!")
            print("GitHub Actions will now build and publish the release.")
    
    elif choice == "3":
        print("\nExiting. You can:")
        print("1. Create PR manually on GitHub")
        
        system = platform.system()
        if system == "Windows":
            print("2. Install GitHub CLI: winget install GitHub.cli")
        elif system == "Darwin":
            print("2. Install GitHub CLI: brew install gh")
        else:
            print("2. Install GitHub CLI: Check your package manager")
        
        print(f"3. Run this script again: {get_platform_command_prefix()} release_to_main.py")
        sys.exit(0)
    
    else:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
