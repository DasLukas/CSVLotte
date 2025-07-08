# Git Branching Strategy for CSVLotte

This document describes the branching strategy and deployment process for CSVLotte using separate development and release branches.

## Branch Structure

### `main` Branch
- **Purpose**: Production-ready releases only
- **Content**: Stable, tested versions
- **Protection**: No direct commits, only merges from `dev`
- **Tags**: All version tags (v1.0.0, v1.1.0, etc.)

### `dev` Branch
- **Purpose**: Active development
- **Content**: Latest features, bug fixes, work in progress
- **Protection**: All development happens here
- **Testing**: Continuous integration runs on every commit

## Workflow

### 1. Development Process

```bash
# Start from dev branch
git checkout dev
git pull origin dev

# Create feature branch (optional, for larger features)
git checkout -b feature/your-feature-name

# Make your changes, commit
git add .
git commit -m "Add new feature"

# Push to dev branch
git checkout dev
git merge feature/your-feature-name  # or push feature branch and create PR
git push origin dev
```

### 2. Release Process

```bash
# 1. Ensure dev branch is ready for release
git checkout dev
git pull origin dev

# 2. Run tests to ensure everything works
pytest tests/

# 3. Use release script to bump version
python release.py patch  # or minor/major

# 4. Push the version changes to dev
git push origin dev

# 5. Create Pull Request from dev to main
# (This should be done via GitHub/GitLab UI)

# 6. After PR is merged, checkout main and tag
git checkout main
git pull origin main
git tag v1.0.1
git push origin v1.0.1
```

### 3. Automated Release Process

The ideal process using GitHub:

1. **Develop on `dev`** - All development happens here
2. **Create PR to `main`** - When ready for release
3. **Merge PR** - Triggers automated build and release
4. **Tag automatically** - GitHub Actions creates tag and release

## GitHub Actions Configuration

We need to update the GitHub Actions to work with this branching strategy:

### Development Pipeline (on `dev` branch)
- Run tests
- Build executable (for testing)
- No release creation

### Release Pipeline (on `main` branch)
- Run tests
- Build executable
- Create GitHub release
- Upload assets

## Branch Protection Rules

### For `main` branch:
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes to administrators only

### For `dev` branch:
- Require status checks to pass
- Allow force pushes (for development flexibility)

## Updated Release Script

The release script needs to be updated to work with this branching strategy.

## Hotfix Process

For urgent fixes to production:

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/urgent-fix

# 2. Make the fix
# ... make changes ...
git commit -m "Fix critical bug"

# 3. Merge to main
git checkout main
git merge hotfix/urgent-fix
git push origin main

# 4. Also merge back to dev
git checkout dev
git merge hotfix/urgent-fix
git push origin dev

# 5. Tag the hotfix release
git tag v1.0.2
git push origin v1.0.2
```

## Benefits

- **Clean main branch**: Only stable releases
- **Continuous development**: Work freely on dev branch
- **Clear history**: Easy to see what went into each release
- **Automated releases**: Tags on main trigger deployments
- **Rollback capability**: Easy to revert to previous stable version

## Migration Steps

1. Create and switch to dev branch
2. Update GitHub Actions workflows
3. Set up branch protection rules
4. Update release script
5. Document new process for team
