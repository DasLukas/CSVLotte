#!/usr/bin/env python3
"""
Release script for CSVLotte.
Handles version bumping, tagging, and release preparation.
Cross-platform support for Windows, macOS, and Linux.
"""

import re
import sys
import os
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
    # Parse current version (handle beta/rc versions)
    base_version, pre_release = parse_version(version)
    major, minor, patch = map(int, base_version.split('.'))
    
    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    elif part == 'beta':
        if pre_release and pre_release[0] == 'beta':
            # Increment beta number
            return f"{base_version}-beta.{pre_release[1] + 1}"
        else:
            # First beta version
            return f"{major}.{minor}.{patch}-beta.1"
    elif part == 'rc':
        if pre_release and pre_release[0] == 'rc':
            # Increment rc number
            return f"{base_version}-rc.{pre_release[1] + 1}"
        else:
            # First rc version
            return f"{major}.{minor}.{patch}-rc.1"
    
    return f"{major}.{minor}.{patch}"

def parse_version(version):
    """Parse version string into base version and pre-release info."""
    import re
    
    # Match version pattern: 1.0.0-beta.1 or 1.0.0-rc.2
    match = re.match(r'^(\d+\.\d+\.\d+)(?:-(beta|rc)\.(\d+))?$', version)
    
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    
    base_version = match.group(1)
    pre_release_type = match.group(2)
    pre_release_number = match.group(3)
    
    if pre_release_type and pre_release_number:
        return base_version, (pre_release_type, int(pre_release_number))
    
    return base_version, None

def get_version_type(version):
    """Get the type of version (stable, beta, rc)."""
    _, pre_release = parse_version(version)
    if pre_release:
        return pre_release[0]
    return 'stable'

def format_version_for_display(version):
    """Format version for display purposes."""
    base_version, pre_release = parse_version(version)
    if pre_release:
        return f"{base_version} {pre_release[0]} {pre_release[1]}"
    return base_version

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

def get_github_repo_info():
    """Get GitHub repository information from git remote."""
    try:
        result = run_command(["git", "remote", "get-url", "origin"])
        if result and result.returncode == 0:
            url = result.stdout.strip()
            # Convert SSH URL to HTTPS if needed
            if url.startswith("git@github.com:"):
                url = url.replace("git@github.com:", "https://github.com/")
            if url.endswith(".git"):
                url = url[:-4]
            return url
    except:
        pass
    return "https://github.com/your-username/csvlotte"

def get_github_actions_url():
    """Get GitHub Actions URL for the repository."""
    repo_url = get_github_repo_info()
    return f"{repo_url}/actions"

def get_github_releases_url():
    """Get GitHub Releases URL for the repository."""
    repo_url = get_github_repo_info()
    return f"{repo_url}/releases"

def check_github_cli_available():
    """Check if GitHub CLI is available on the system."""
    try:
        result = run_command(["gh", "--version"])
        return result and result.returncode == 0
    except:
        return False

def check_release_status(version):
    """Check if a GitHub release was created successfully."""
    if not check_github_cli_available():
        return False
    
    try:
        result = run_command(["gh", "release", "view", f"v{version}"])
        if result and result.returncode == 0:
            stdout = result.stdout.lower()
            
            # Check if the release has executable assets
            has_assets = (
                "assets:" in stdout or 
                "asset" in stdout or
                "windows" in stdout or 
                ".exe" in stdout or 
                "win" in stdout or
                "linux" in stdout or 
                ".tar.gz" in stdout or 
                "ubuntu" in stdout or
                "macos" in stdout or 
                "mac" in stdout or 
                "darwin" in stdout or 
                ".dmg" in stdout or
                ".zip" in stdout
            )
            
            if has_assets:
                return True
            else:
                # Release exists but might not have assets yet
                # Let's count how many lines we have to see if there's meaningful content
                lines = result.stdout.strip().split('\n')
                if len(lines) > 5:  # If we have more than 5 lines, it's likely a real release
                    return True
                return False
        return False
    except Exception as e:
        return False

def check_workflow_status(version):
    """Check if the GitHub Actions workflow is still running for this version."""
    if not check_github_cli_available():
        return None
    
    try:
        tag = f"v{version}"
        
        # First, check for any currently running workflows
        result = run_command(["gh", "run", "list", "--status", "in_progress", "--limit", "5", "--json", "status,conclusion,event,createdAt,headBranch,displayTitle"])
        if result and result.returncode == 0:
            import json
            try:
                running_runs = json.loads(result.stdout)
                if running_runs:
                    # We have running workflows, check if any are recent enough to be ours
                    for run in running_runs:
                        if run.get('status') in ['in_progress', 'queued']:
                            return 'running'
            except json.JSONDecodeError:
                pass
        
        # Check for queued workflows
        result = run_command(["gh", "run", "list", "--status", "queued", "--limit", "5", "--json", "status,conclusion,event,createdAt,headBranch,displayTitle"])
        if result and result.returncode == 0:
            try:
                queued_runs = json.loads(result.stdout)
                if queued_runs:
                    for run in queued_runs:
                        if run.get('status') == 'queued':
                            return 'running'
            except json.JSONDecodeError:
                pass
        
        # Check recent workflow runs (last 10) to see if any completed recently
        result = run_command(["gh", "run", "list", "--limit", "10", "--json", "status,conclusion,event,createdAt,headBranch,displayTitle,updatedAt"])
        if result and result.returncode == 0:
            try:
                runs = json.loads(result.stdout)
                
                # Look for recently completed workflows
                import datetime
                now = datetime.datetime.now(datetime.timezone.utc)
                
                for run in runs:
                    # Check if this run was updated recently (within last 10 minutes)
                    updated_at = run.get('updatedAt')
                    if updated_at:
                        try:
                            # Parse ISO datetime
                            updated_time = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                            time_diff = now - updated_time
                            
                            # If updated within last 10 minutes, it could be our workflow
                            if time_diff.total_seconds() < 600:  # 10 minutes
                                status = run.get('status')
                                conclusion = run.get('conclusion')
                                
                                if status in ['in_progress', 'queued']:
                                    return 'running'
                                elif status == 'completed':
                                    if conclusion == 'success':
                                        return 'success'
                                    elif conclusion in ['failure', 'cancelled']:
                                        return 'failed'
                        except:
                            # If we can't parse the date, skip this run
                            continue
                
                # If we have any completed workflows but none recent, check the most recent one
                if runs:
                    most_recent = runs[0]
                    status = most_recent.get('status')
                    conclusion = most_recent.get('conclusion')
                    
                    if status in ['in_progress', 'queued']:
                        return 'running'
                    elif status == 'completed' and conclusion == 'success':
                        # Only return success if it's very recent
                        updated_at = most_recent.get('updatedAt')
                        if updated_at:
                            try:
                                updated_time = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                                time_diff = now - updated_time
                                if time_diff.total_seconds() < 1800:  # 30 minutes
                                    return 'success'
                            except:
                                pass
                
                return 'unknown'
            except json.JSONDecodeError:
                return None
        
        return 'unknown'
    except Exception as e:
        print(f"Error checking workflow status: {e}")
        return None

def wait_for_release(version, max_wait=300):
    """Wait for GitHub release to be created (up to 5 minutes)."""
    if not check_github_cli_available():
        print("⏭️  GitHub CLI not available. Cannot check release status automatically.")
        return False
    
    print(f"🕐 Waiting for GitHub release v{version} to be created...")
    print("This may take a few minutes while GitHub Actions builds the executables...")
    
    import time
    waited = 0
    last_workflow_status = None
    workflow_completed = False
    consecutive_success_checks = 0
    consecutive_unknown_checks = 0
    
    while waited < max_wait:
        # Check workflow status
        workflow_status = check_workflow_status(version)
        
        if workflow_status != last_workflow_status:
            if workflow_status == 'running':
                print(f"🔄 GitHub Actions workflow is running...")
                consecutive_unknown_checks = 0
            elif workflow_status == 'success':
                print(f"✅ GitHub Actions workflow completed successfully!")
                workflow_completed = True
                consecutive_unknown_checks = 0
            elif workflow_status == 'failed':
                print(f"❌ GitHub Actions workflow failed!")
                print(f"Check the workflow at: {get_github_actions_url()}")
                return False
            elif workflow_status == 'unknown':
                consecutive_unknown_checks += 1
                if consecutive_unknown_checks == 1:
                    print(f"❓ Workflow status unknown, checking for release...")
            last_workflow_status = workflow_status
        
        # Check if release is ready
        release_ready = check_release_status(version)
        if release_ready:
            print(f"✅ Release v{version} created successfully with executables!")
            
            # Show release info
            result = run_command(["gh", "release", "view", f"v{version}"])
            if result and result.returncode == 0:
                print("\n📦 Release Information:")
                print(result.stdout)
            
            return True
        
        # Count consecutive workflow success checks
        if workflow_status == 'success':
            consecutive_success_checks += 1
        else:
            consecutive_success_checks = 0
        
        # If we have unknown status for too long, provide more detailed info
        if consecutive_unknown_checks >= 3:
            print(f"⚠️  Workflow status has been unknown for a while.")
            print(f"🔍 Checking current workflow runs...")
            
            # Show current workflow status
            result = run_command(["gh", "run", "list", "--limit", "3"])
            if result and result.returncode == 0:
                print("Recent workflow runs:")
                print(result.stdout)
            
            consecutive_unknown_checks = 0  # Reset counter
        
        # If workflow has been successful for multiple checks but no release
        if consecutive_success_checks >= 2 and workflow_completed:
            print(f"⚠️  Workflow shows as completed but no release detected.")
            print(f"🔍 Checking if release exists but wasn't detected...")
            
            # Check if release exists at all (even without assets)
            result = run_command(["gh", "release", "view", f"v{version}", "--json", "tagName,name,publishedAt"])
            if result and result.returncode == 0:
                print(f"✅ Release v{version} found but may not have assets yet!")
                print(f"⏳ Waiting for assets to be uploaded...")
            else:
                print(f"❌ No release found. The workflow may have failed or not created a release.")
                print(f"🔗 Check manually at: {get_github_releases_url()}")
                
                # Show recent releases for comparison
                result = run_command(["gh", "release", "list", "--limit", "3"])
                if result and result.returncode == 0:
                    print("Recent releases:")
                    print(result.stdout)
                
                return False
        
        # Show progress
        if waited > 0 and waited % 60 == 0:
            if workflow_status == 'running':
                print(f"⏳ Workflow still running... ({waited}s / {max_wait}s)")
            elif workflow_status == 'success':
                print(f"⏳ Workflow completed, waiting for release... ({waited}s / {max_wait}s)")
            else:
                print(f"⏳ Still waiting... ({waited}s / {max_wait}s)")
        
        time.sleep(20)  # Check every 20 seconds instead of 30
        waited += 20
    
    print(f"⏰ Timeout waiting for release after {max_wait} seconds.")
    
    # Final comprehensive check
    print(f"🔍 Performing final comprehensive check...")
    
    # Check workflow status one more time
    workflow_status = check_workflow_status(version)
    print(f"Final workflow status: {workflow_status}")
    
    # Check if release exists
    release_ready = check_release_status(version)
    if release_ready:
        print(f"✅ Release v{version} was found on final check!")
        return True
    
    # Show what we can find
    print(f"Diagnostic information:")
    
    # Show recent workflows
    result = run_command(["gh", "run", "list", "--limit", "5"])
    if result and result.returncode == 0:
        print("Recent workflow runs:")
        print(result.stdout)
    
    # Show recent releases
    result = run_command(["gh", "release", "list", "--limit", "3"])
    if result and result.returncode == 0:
        print("Recent releases:")
        print(result.stdout)
    
    print(f"Please check manually:")
    print(f"• Workflows: {get_github_actions_url()}")
    print(f"• Releases: {get_github_releases_url()}")
    
    return False

def get_current_branch():
    """Get the current Git branch."""
    result = run_command(["git", "branch", "--show-current"])
    if result and result.returncode == 0:
        return result.stdout.strip()
    return None

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

def create_pull_request(version):
    """Create a pull request from dev to main (requires GitHub CLI)."""
    print("Creating pull request from dev to main...")
    
    # Check if GitHub CLI is available
    if not check_github_cli_available():
        print("GitHub CLI (gh) not found.")
        return show_manual_pr_instructions(version)
    
    # Create PR
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
            return show_manual_pr_instructions(version)
    except Exception as e:
        print(f"Error creating pull request: {e}")
        return show_manual_pr_instructions(version)

def show_manual_pr_instructions(version):
    """Show instructions for creating a PR manually."""
    print("\n" + "="*50)
    print("MANUAL PULL REQUEST INSTRUCTIONS")
    print("="*50)
    print("GitHub CLI not available. Please create PR manually:")
    print("\n1. Go to your GitHub repository")
    print("2. Click 'Compare & pull request' or go to:")
    print(f"   {get_github_repo_info()}/compare/main...dev")
    print("3. Create pull request from 'dev' to 'main'")
    print(f"4. Use this title: Release v{version}")
    print("5. Add release notes in the description")
    print("6. Review and merge the PR")
    print("7. Then run this script again with --release option")
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

def merge_to_main_and_tag(version):
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
    
    # Check if GitHub Actions workflow was triggered
    print(f"\n🔄 GitHub Actions should now be running...")
    print("Check the workflow status at:")
    print(f"{get_github_actions_url()}")
    print("\nThe workflow will:")
    print("1. Run tests on all platforms")
    print("2. Build executables for Windows, Linux, and macOS")
    print("3. Create a GitHub Release with download links")
    print("4. Upload the following files:")
    print("   - CSVLotte-Windows.zip (Windows executable)")
    print("   - CSVLotte-Linux.tar.gz (Linux executable)")
    print("   - CSVLotte-macOS.zip (macOS executable)")
    
    # Wait a moment and check if we can detect the workflow
    if check_github_cli_available():
        print(f"\n🔍 Checking GitHub Actions status...")
        result = run_command(["gh", "run", "list", "--limit", "1"])
        if result and result.returncode == 0:
            print("Latest workflow runs:")
            print(result.stdout)
        else:
            print("Could not fetch workflow status. Check manually on GitHub.")
    else:
        print(f"\n💡 Install GitHub CLI to check workflow status automatically:")
        system = platform.system()
        if system == "Windows":
            print("   winget install GitHub.cli")
        elif system == "Darwin":
            print("   brew install gh")
        else:
            print("   Check your package manager or visit https://cli.github.com/")
    
    print(f"\n📦 Release will be available at:")
    print(f"{get_github_releases_url()}")
    print(f"Once the workflow completes, users can download:")
    print(f"- Release {tag} with executables for all platforms")
    print(f"- No installation required - just download and run!")
    
    # Sync dev with main
    print("\nSyncing dev branch with main...")
    result = run_command(["git", "checkout", "dev"])
    if not result or result.returncode != 0:
        print(f"Warning: Could not switch back to dev: {result.stderr if result else 'Unknown error'}")
    else:
        result = run_command(["git", "merge", "main"])
        if not result or result.returncode != 0:
            print(f"Warning: Could not sync dev with main: {result.stderr if result else 'Unknown error'}")
        else:
            result = run_command(["git", "push", "origin", "dev"])
            if not result or result.returncode != 0:
                print(f"Warning: Could not push dev: {result.stderr if result else 'Unknown error'}")
            else:
                print("✓ Dev branch synced with main")
    
    return True

def create_git_commit(version):
    """Create git commit for the version bump."""
    if not check_git_available():
        print("Error: Git is not available on this system.")
        print("Please install Git and try again.")
        return False
    
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

def handle_release_process(version):
    """Handle the complete release process."""
    print(f"\n🚀 Starting release process for version {version}")
    print("The process will:")
    print("1. Create a pull request from 'dev' to 'main' (or direct merge)")
    print("2. Merge to main branch")
    print("3. Create and push the release tag")
    print("4. Sync dev branch with main")
    
    response = input("\nProceed with release? (y/N): ")
    if response.lower() != 'y':
        print("Release cancelled.")
        return False
    
    # Choose release method
    print("\nChoose release method:")
    print("1. Create PR for manual review and merge (requires GitHub CLI or manual process)")
    print("2. Directly merge to main (skip PR - only if you're sure)")
    print("3. Exit and handle manually")
    
    choice = input("Choose option (1/2/3): ")
    
    if choice == "1":
        if create_pull_request(version):
            print("\n✓ Pull request created or ready for manual creation!")
            print("Next steps:")
            print("1. Review and merge the PR on GitHub")
            print(f"2. Run: {get_platform_command_prefix()} release.py --release")
            print("3. This will create the tag and complete the release")
            return True
        else:
            print("\nPR creation failed. Please handle manually or try again.")
            return False
    
    elif choice == "2":
        # Direct merge
        print("\n⚠️  WARNING: This will directly merge dev to main without PR review!")
        response = input("Are you sure you want to proceed? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return False
        
        if merge_to_main_and_tag(version):
            print(f"\n🎉 Release v{version} completed successfully!")
            print("GitHub Actions will now build and publish the release.")
            
            # Ask if user wants to wait for the release
            if check_github_cli_available():
                response = input(f"\nDo you want to wait for the GitHub release to be created? (y/N): ")
                if response.lower() == 'y':
                    wait_for_release(version)
                else:
                    print(f"You can check the release status manually at:")
                    print(f"{get_github_releases_url()}")
            
            return True
        else:
            print("Release failed.")
            return False
    
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
        
        print(f"3. Run this script again: {get_platform_command_prefix()} release.py --release")
        return False
    
    else:
        print("Invalid choice. Please run the script again.")
        return False

def show_help():
    """Show help information for the release script."""
    print(f"CSVLotte Release Script - Version Management Tool")
    print(f"=" * 50)
    print()
    print("USAGE:")
    print(f"  {get_platform_command_prefix()} release.py <version_type> [options]")
    print(f"  {get_platform_command_prefix()} release.py --release")
    print(f"  {get_platform_command_prefix()} release.py --help")
    print()
    print("VERSION TYPES:")
    print("  patch     Bug fixes and small changes (1.0.0 → 1.0.1)")
    print("  minor     New features, backwards compatible (1.0.0 → 1.1.0)")
    print("  major     Breaking changes (1.0.0 → 2.0.0)")
    print("  beta      Beta release (1.0.0 → 1.0.1-beta.1)")
    print("  rc        Release candidate (1.0.0 → 1.0.1-rc.1)")
    print()
    print("OPTIONS:")
    print("  --skip-tests    Skip running tests before release")
    print("  --release       Complete the release process (merge to main and create tag)")
    print("  --help          Show this help message")
    print()
    print("EXAMPLES:")
    print(f"  {get_platform_command_prefix()} release.py patch")
    print(f"  {get_platform_command_prefix()} release.py minor --skip-tests")
    print(f"  {get_platform_command_prefix()} release.py beta")
    print(f"  {get_platform_command_prefix()} release.py rc")
    print(f"  {get_platform_command_prefix()} release.py --release")
    print()
    print("WORKFLOW:")
    print("  1. Version Bump Mode:")
    print("     - Updates version in pyproject.toml and installer.iss")
    print("     - Runs tests (unless --skip-tests)")
    print("     - Commits changes to dev branch")
    print("     - Optionally continues with release process")
    print()
    print("  2. Release Mode (--release):")
    print("     - Merges dev to main")
    print("     - Creates and pushes git tag")
    print("     - Triggers GitHub Actions for builds")
    print("     - Creates GitHub release with executables")
    print()
    print("PRE-RELEASE VERSIONS:")
    print("  • Beta versions: For testing new features")
    print("  • RC versions: Release candidates, should be stable")
    print("  • Pre-releases are tagged directly on dev branch")
    print("  • Marked as pre-release on GitHub")
    print("  • Automatic numbering: beta.1, beta.2, rc.1, rc.2, etc.")
    print("  • NOT merged to main branch")
    print()
    print("STABLE RELEASES:")
    print("  • patch, minor, major versions")
    print("  • Always merged to main branch first")
    print("  • Tagged on main branch")
    print("  • Marked as full release on GitHub")
    print("  • Follow proper GitFlow process")
    print()
    print("REQUIREMENTS:")
    print("  • Git installed and configured")
    print("  • Working directory must be clean")
    print("  • Should be on 'dev' branch for version bumping")
    print("  • Python 3.11+ with required dependencies")
    print()
    print("GITHUB INTEGRATION:")
    print("  • GitHub CLI (gh) for automatic PR creation (optional)")
    print("  • GitHub Actions for automated builds")
    print("  • Releases created with Windows, Linux, and macOS executables")
    print()
    print("FILES UPDATED:")
    print("  • pyproject.toml - Main project version")
    print("  • installer.iss - Windows installer version (if exists)")
    print()
    print("For more information, see DEPLOYMENT.md")

def main():
    """Main release process."""
    print(f"CSVLotte Release Script")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)
    
    # Check for help
    if len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        sys.exit(0)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {get_platform_command_prefix()} release.py <major|minor|patch|beta|rc> [--skip-tests]")
        print(f"  {get_platform_command_prefix()} release.py --release")
        print(f"  {get_platform_command_prefix()} release.py --help")
        print("")
        print("Examples:")
        print(f"  {get_platform_command_prefix()} release.py patch")
        print(f"  {get_platform_command_prefix()} release.py minor --skip-tests")
        print(f"  {get_platform_command_prefix()} release.py beta")
        print(f"  {get_platform_command_prefix()} release.py rc")
        print(f"  {get_platform_command_prefix()} release.py --release")
        print("")
        print("Version types:")
        print("  patch: Bug fixes (1.0.0 → 1.0.1)")
        print("  minor: New features (1.0.0 → 1.1.0)")
        print("  major: Breaking changes (1.0.0 → 2.0.0)")
        print("  beta:  Beta release (1.0.0 → 1.0.1-beta.1)")
        print("  rc:    Release candidate (1.0.0 → 1.0.1-rc.1)")
        print("")
        print("Options:")
        print("  --release: Complete the release process (merge to main and create tag)")
        print("  --skip-tests: Skip running tests")
        print("  --help: Show detailed help")
        sys.exit(1)
    
    # Check for release mode
    if sys.argv[1] == "--release":
        # Release mode - merge to main and create tag
        if not check_git_available():
            print("Error: Git is not available on this system.")
            print("Please install Git and try again.")
            sys.exit(1)
        
        if not ensure_clean_working_directory():
            sys.exit(1)
        
        current_version = get_current_version()
        latest_tag = get_latest_tag()
        
        print(f"Current version: {current_version}")
        print(f"Latest tag: {latest_tag}")
        
        if merge_to_main_and_tag(current_version):
            print(f"\n🎉 Release v{current_version} completed successfully!")
            print("GitHub Actions will now build and publish the release.")
            
            # Ask if user wants to wait for the release
            if check_github_cli_available():
                response = input(f"\nDo you want to wait for the GitHub release to be created? (y/N): ")
                if response.lower() == 'y':
                    wait_for_release(current_version)
                else:
                    print(f"You can check the release status manually at:")
                    print(f"{get_github_releases_url()}")
            
        else:
            print("Release failed.")
            sys.exit(1)
        
        return
    
    # Version bump mode
    if len(sys.argv) not in [2, 3]:
        print("Invalid arguments. See usage above.")
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
        print("Warning: You should be on the 'dev' branch for version bumping")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(1)
    
    part = sys.argv[1]
    if part not in ['major', 'minor', 'patch', 'beta', 'rc']:
        print("Invalid version part. Use: major, minor, patch, beta, or rc")
        sys.exit(1)
    
    skip_tests = len(sys.argv) == 3 and sys.argv[2] == '--skip-tests'
    
    # Get current version
    try:
        current_version = get_current_version()
        version_type = get_version_type(current_version)
        print(f"Current version: {format_version_for_display(current_version)} ({version_type})")
    except Exception as e:
        print(f"Error reading current version: {e}")
        sys.exit(1)
    
    # Calculate new version
    new_version = increment_version(current_version, part)
    new_version_type = get_version_type(new_version)
    print(f"New version: {format_version_for_display(new_version)} ({new_version_type})")
    
    # Special handling for pre-release versions
    if part in ['beta', 'rc']:
        print(f"\n📋 Pre-release version details:")
        print(f"   Type: {new_version_type.upper()}")
        print(f"   Full version: {new_version}")
        
        if new_version_type == 'beta':
            print(f"   💡 This is a beta version - expect bugs and changes")
        elif new_version_type == 'rc':
            print(f"   🎯 This is a release candidate - should be stable")
        
        print(f"   📦 Tag will be: v{new_version}")
        print(f"   🌿 Branch: Pre-releases are created from dev branch")
        print(f"   🏷️  GitHub: Will be marked as pre-release")
        
    else:
        print(f"\n📋 Stable release version details:")
        print(f"   Type: {new_version_type.upper()}")
        print(f"   Full version: {new_version}")
        print(f"   📦 Tag will be: v{new_version}")
        print(f"   🌿 Branch: Stable releases are created from main branch")
        print(f"   🏷️  GitHub: Will be marked as full release")
        print(f"   ⚠️  Process: Will merge dev → main before creating tag")
    
    # Check if tag already exists
    result = run_command(["git", "tag", "-l", f"v{new_version}"])
    if result and result.stdout.strip():
        print(f"Tag v{new_version} already exists!")
        sys.exit(1)
    
    # Confirm
    response = input(f"Bump version to {new_version}? (y/N): ")
    if response.lower() != 'y':
        print("Version bump cancelled.")
        sys.exit(0)
    
    # Run tests (unless skipped)
    if not skip_tests:
        if not run_tests():
            print("Version bump cancelled due to test failures.")
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
    
    # Create git commit
    if not create_git_commit(new_version):
        print("Failed to create git commit.")
        sys.exit(1)
    
    print(f"\n✓ Version {new_version} prepared successfully!")
    print("Changes committed to dev branch.")
    
    # Ask if user wants to continue with release
    response = input(f"\nDo you want to continue with the release process? (y/N): ")
    if response.lower() == 'y':
        print("Pushing changes to dev...")
        result = run_command(["git", "push", "origin", "dev"])
        if not result or result.returncode != 0:
            print(f"Error pushing to dev: {result.stderr if result else 'Unknown error'}")
            print("Please push manually and then continue with release.")
            sys.exit(1)
        
        # Handle pre-release versions differently (beta/rc from dev branch)
        if part in ['beta', 'rc']:
            print(f"\n🚀 Creating pre-release {new_version}...")
            print(f"Pre-releases are created directly from dev branch")
            
            # Ensure latest changes are pushed to dev before creating tag
            print("Ensuring dev branch is up to date...")
            result = run_command(["git", "push", "origin", "dev"])
            if not result or result.returncode != 0:
                print(f"Error pushing to dev: {result.stderr if result else 'Unknown error'}")
                print("Please push manually before continuing.")
                sys.exit(1)
            
            # For pre-releases, we create the tag directly on dev branch
            # without merging to main
            tag = f"v{new_version}"
            
            print(f"Creating tag {tag} on dev branch...")
            result = run_command(["git", "tag", "-a", tag, "-m", f"Pre-release v{new_version}"])
            if not result or result.returncode != 0:
                print(f"Error creating tag: {result.stderr if result else 'Unknown error'}")
                sys.exit(1)
            
            print(f"Pushing tag {tag}...")
            result = run_command(["git", "push", "origin", tag])
            if not result or result.returncode != 0:
                print(f"Error pushing tag: {result.stderr if result else 'Unknown error'}")
                sys.exit(1)
            
            print(f"✅ Pre-release {new_version} created successfully!")
            print(f"📦 GitHub Actions will create a pre-release with executables")
            print(f"🔗 Check the release at: {get_github_releases_url()}")
            
            # Check if GitHub CLI is available for release status
            if check_github_cli_available():
                response = input(f"\nDo you want to wait for the GitHub pre-release to be created? (y/N): ")
                if response.lower() == 'y':
                    wait_for_release(new_version)
                else:
                    print(f"You can check the release status manually at:")
                    print(f"{get_github_releases_url()}")
        else:
            # Regular release process for stable versions (patch, minor, major)
            print(f"\n🚀 Stable release {new_version} - will be created from main branch")
            print("This will:")
            print("1. Create a PR from dev to main (or merge directly)")
            print("2. Create the release tag on main branch")
            print("3. Trigger GitHub Actions from main branch")
            
            if handle_release_process(new_version):
                print("\n🎉 Release process completed or initiated successfully!")
            else:
                print("\nRelease process stopped. You can continue later with:")
                print(f"{get_platform_command_prefix()} release.py --release")
    else:
        print("\nNext steps:")
        print("1. Push changes to dev: git push origin dev")
        if part in ['beta', 'rc']:
            print("2. For pre-releases, create tag directly on dev:")
            print(f"   git tag -a v{new_version} -m 'Pre-release v{new_version}'")
            print(f"   git push origin v{new_version}")
        else:
            print("2. Continue with stable release (merges to main first):")
            print(f"   {get_platform_command_prefix()} release.py --release")
            print("   This will handle the merge to main and tag creation")

if __name__ == "__main__":
    main()
