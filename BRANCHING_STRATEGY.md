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

## Setting up Branch Protection on GitHub

### Step-by-Step Guide

#### 1. Access Repository Settings
1. Go to your GitHub repository
2. Click on **Settings** tab (must be repository owner/admin)
3. In the left sidebar, click **Branches**

#### 2. Add Branch Protection Rule for `main`

1. Click **Add rule** button
2. In **Branch name pattern**, enter: `main`
3. Configure the following settings:

**Required Settings:**
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: `1` (or more for team projects)
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from code owners (if you have CODEOWNERS file)
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Select status checks: `test` (from your GitHub Actions)
- ✅ **Require conversation resolution before merging**
- ✅ **Restrict pushes that create files larger than 100MB**

**Admin Settings:**
- ✅ **Restrict pushes to matching branches**
  - Only allow administrators to push
- ✅ **Allow force pushes** → **OFF**
- ✅ **Allow deletions** → **OFF**

4. Click **Create** to save the rule

#### 3. Add Branch Protection Rule for `dev`

1. Click **Add rule** button again
2. In **Branch name pattern**, enter: `dev`
3. Configure these settings:

**Required Settings:**
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Select status checks: `test` (from your GitHub Actions)
- ✅ **Require conversation resolution before merging**

**Flexible Settings for Development:**
- ❌ **Require a pull request before merging** (optional, for solo development)
- ✅ **Allow force pushes** → **ON** (for development flexibility)
- ❌ **Restrict pushes to matching branches** (allow direct pushes)

4. Click **Create** to save the rule

#### 4. Set Default Branch (Optional)

If you want `dev` to be the default branch for new PRs:
1. Go to **Settings** → **General**
2. In **Default branch** section, click the switch button
3. Select `dev` as the default branch
4. Click **Update**

#### 5. Create CODEOWNERS File (Optional)

For automatic review requests, create `.github/CODEOWNERS`:

```
# Global owners
* @your-username

# Python files
*.py @your-username

# Documentation
*.md @your-username

# Build and deployment
build.py @your-username
release*.py @your-username
.github/ @your-username
```

#### 6. Verify Protection Rules

1. Go to **Settings** → **Branches**
2. You should see both protection rules listed
3. Test by trying to push directly to `main` - it should be blocked

### Common Issues and Solutions

#### Issue: Can't push to main
**Solution**: This is expected! Use the proper workflow:
```bash
git checkout dev
git push origin dev
# Then create PR from dev to main
```

#### Issue: Status checks not appearing
**Solution**: 
1. Make sure GitHub Actions have run at least once
2. Check that workflow names match in protection rules
3. Verify workflows are enabled in **Actions** tab

#### Issue: No "Settings" tab visible
**Solution**: You need admin/owner permissions on the repository

### Testing Your Setup

After setting up protection:

1. **Test dev branch** - Should allow direct pushes
2. **Test main branch** - Should block direct pushes
3. **Test PR process** - Create PR from dev to main
4. **Test status checks** - Verify CI runs before merge

### Visual Confirmation

Once set up, you'll see:
- 🛡️ Shield icon next to protected branches
- Yellow merge button until status checks pass
- "Branch protection rule" messages when rules are enforced

### Quick Setup Commands

After GitHub setup, sync locally:
```bash
# Create dev branch if not exists
git checkout -b dev
git push origin dev

# Set dev as default locally
git remote set-head origin dev
```

This protection setup ensures code quality and prevents accidental direct pushes to your main branch while keeping development flexible on the dev branch.

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

1. **Create and switch to dev branch**
   ```bash
   git checkout -b dev
   git push origin dev
   ```

2. **Update GitHub Actions workflows**
   - Already completed with new workflow files
   - Ensure they're pushed to repository

3. **Set up branch protection rules**
   - Follow the detailed guide above
   - Configure main branch with strict protection
   - Configure dev branch with flexible protection

4. **Update release script**
   - Already completed with updated release.py
   - New release_to_main.py for automated releases

5. **Document new process for team**
   - Share this BRANCHING_STRATEGY.md with team
   - Update project README with new workflow
   - Train team on new release process

6. **Test the complete workflow**
   ```bash
   # Test development workflow
   git checkout dev
   echo "test" > test.txt
   git add . && git commit -m "Test commit"
   git push origin dev
   
   # Test release workflow
   python release.py patch
   python release_to_main.py
   ```
