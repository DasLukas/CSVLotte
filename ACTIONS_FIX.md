# GitHub Actions Fix - Deprecated Actions Update

## Problem
GitHub Actions build was failing due to deprecated action versions:
- `actions/upload-artifact@v3` - deprecated since April 2024
- `actions/setup-python@v4` - outdated
- `actions/create-release@v1` - deprecated
- `actions/upload-release-asset@v1` - deprecated
- `codecov/codecov-action@v3` - outdated

## Solution
Updated all GitHub Actions to latest versions:

### Updated Actions
- `actions/upload-artifact@v3` → `actions/upload-artifact@v4`
- `actions/setup-python@v4` → `actions/setup-python@v5`
- `codecov/codecov-action@v3` → `codecov/codecov-action@v4`
- `actions/create-release@v1` + `actions/upload-release-asset@v1` → `softprops/action-gh-release@v1`

### Files Updated
- `.github/workflows/dev.yml` - Development pipeline
- `.github/workflows/build.yml` - Release pipeline

### Key Changes

#### 1. Artifact Upload
```yaml
# Old
- uses: actions/upload-artifact@v3

# New
- uses: actions/upload-artifact@v4
```

#### 2. Release Creation
```yaml
# Old - Two separate actions
- uses: actions/create-release@v1
- uses: actions/upload-release-asset@v1

# New - Single action
- uses: softprops/action-gh-release@v1
  with:
    files: |
      dist/CSVLotte-Windows.zip
```

#### 3. Python Setup
```yaml
# Old
- uses: actions/setup-python@v4

# New
- uses: actions/setup-python@v5
```

## Benefits
- ✅ Fixed deprecated action warnings
- ✅ Improved performance with newer actions
- ✅ Better error handling
- ✅ Simplified release creation process
- ✅ Future-proof for GitHub Actions updates

## Testing
After these updates, the build should run without deprecation warnings and complete successfully.

## Next Steps
1. Push these changes to your repository
2. Test the dev pipeline by pushing to dev branch
3. Test the release pipeline by creating a release
4. Monitor GitHub Actions for any remaining issues
