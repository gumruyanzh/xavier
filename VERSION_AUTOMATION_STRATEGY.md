# Xavier Framework Version Automation Strategy

## Problem Statement
Currently, version updates require manual intervention to update multiple files across the codebase. This creates opportunities for inconsistency and requires reminder from users to update versions during releases.

## Proposed Solution: Automated Version Management

### 1. **Semantic Version Automation with Conventional Commits**

#### Implementation
```yaml
# .github/workflows/version-automation.yml
name: Automated Version Management

on:
  push:
    branches: [main]
  pull_request:
    types: [closed]
    branches: [main]

jobs:
  version-bump:
    if: github.event.pull_request.merged == true || github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Analyze Commits
        id: analyze
        run: |
          # Analyze commit messages to determine version bump type
          if git log -1 --pretty=%B | grep -q "^BREAKING CHANGE:\|^feat!:"; then
            echo "bump=major" >> $GITHUB_OUTPUT
          elif git log -1 --pretty=%B | grep -q "^feat:"; then
            echo "bump=minor" >> $GITHUB_OUTPUT
          elif git log -1 --pretty=%B | grep -q "^fix:"; then
            echo "bump=patch" >> $GITHUB_OUTPUT
          else
            echo "bump=none" >> $GITHUB_OUTPUT
          fi

      - name: Bump Version
        if: steps.analyze.outputs.bump != 'none'
        run: |
          python scripts/bump_version.py ${{ steps.analyze.outputs.bump }}

      - name: Create Release PR
        if: steps.analyze.outputs.bump != 'none'
        uses: peter-evans/create-pull-request@v5
        with:
          title: "chore: Release v${{ env.NEW_VERSION }}"
          body: "Automated version bump to ${{ env.NEW_VERSION }}"
          branch: release/v${{ env.NEW_VERSION }}
          commit-message: "chore: bump version to ${{ env.NEW_VERSION }}"
```

### 2. **Version Bump Script**

```python
# scripts/bump_version.py
#!/usr/bin/env python3
"""
Automated version bumping for Xavier Framework
"""

import re
import sys
import json
from pathlib import Path
from typing import Tuple

class VersionManager:
    def __init__(self, project_root: Path = Path.cwd()):
        self.project_root = project_root
        self.version_files = {
            "VERSION": self._update_simple_version,
            "xavier/src/commands/xavier_commands.py": self._update_python_version,
            "xavier/src/utils/greeting.sh": self._update_bash_version,
            "README.md": self._update_readme_version,
            "CHANGELOG.md": self._update_changelog,
        }

    def get_current_version(self) -> Tuple[int, int, int]:
        """Read current version from VERSION file"""
        version_file = self.project_root / "VERSION"
        with open(version_file, 'r') as f:
            version_str = f.read().strip()

        match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
        if match:
            return tuple(map(int, match.groups()))
        raise ValueError(f"Invalid version format: {version_str}")

    def bump_version(self, bump_type: str) -> str:
        """Bump version based on type (major, minor, patch)"""
        major, minor, patch = self.get_current_version()

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        return f"{major}.{minor}.{patch}"

    def _update_simple_version(self, file_path: Path, new_version: str):
        """Update simple VERSION file"""
        with open(file_path, 'w') as f:
            f.write(f"{new_version}\n")

    def _update_python_version(self, file_path: Path, new_version: str):
        """Update version in Python files"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Update all version references
        patterns = [
            (r'"xavier_version": "\d+\.\d+\.\d+"', f'"xavier_version": "{new_version}"'),
            (r'"framework_version": "\d+\.\d+\.\d+"', f'"framework_version": "{new_version}"'),
            (r'current_version = "\d+\.\d+\.\d+"', f'current_version = "{new_version}"'),
            (r'greeting_script, "welcome", "\d+\.\d+\.\d+"', f'greeting_script, "welcome", "{new_version}"')
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        with open(file_path, 'w') as f:
            f.write(content)

    def _update_bash_version(self, file_path: Path, new_version: str):
        """Update version in bash scripts"""
        with open(file_path, 'r') as f:
            content = f.read()

        content = re.sub(
            r'VERSION="\$\{2:-\d+\.\d+\.\d+\}"',
            f'VERSION="${{2:-{new_version}}}"',
            content
        )

        with open(file_path, 'w') as f:
            f.write(content)

    def _update_readme_version(self, file_path: Path, new_version: str):
        """Update version in README"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Update header version
        content = re.sub(
            r'# Xavier Framework v\d+\.\d+\.\d+',
            f'# Xavier Framework v{new_version}',
            content
        )

        # Update latest version line
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        content = re.sub(
            r'\*\*Latest Version:\*\* v\d+\.\d+\.\d+ \([^)]+\)',
            f'**Latest Version:** v{new_version} ({date_str})',
            content
        )

        with open(file_path, 'w') as f:
            f.write(content)

    def _update_changelog(self, file_path: Path, new_version: str):
        """Add new version entry to CHANGELOG"""
        from datetime import datetime

        with open(file_path, 'r') as f:
            content = f.read()

        # Create new entry
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"\n## [{new_version}] - {date_str}\n\n### Added\n- \n\n### Changed\n- \n\n### Fixed\n- \n"

        # Insert after header
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                insert_pos = i
                break

        lines.insert(insert_pos, new_entry)

        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))

    def update_all_files(self, new_version: str):
        """Update version in all tracked files"""
        for file_path, updater in self.version_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"Updating {file_path}")
                updater(full_path, new_version)
            else:
                print(f"Warning: {file_path} not found")

        # Set environment variable for GitHub Actions
        print(f"::set-output name=new_version::{new_version}")

        # Also export as environment variable
        with open(os.environ['GITHUB_ENV'], 'a') as f:
            f.write(f"NEW_VERSION={new_version}\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: bump_version.py [major|minor|patch]")
        sys.exit(1)

    bump_type = sys.argv[1]
    manager = VersionManager()

    # Get new version
    new_version = manager.bump_version(bump_type)
    print(f"Bumping version to {new_version}")

    # Update all files
    manager.update_all_files(new_version)

    print(f"Version bumped to {new_version}")

if __name__ == "__main__":
    main()
```

### 3. **Commit Message Convention**

To enable automatic version bumping, we'll adopt conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types that trigger version bumps:**
- `feat:` - New feature (minor bump)
- `fix:` - Bug fix (patch bump)
- `feat!:` or `BREAKING CHANGE:` - Breaking change (major bump)
- `docs:` - Documentation only (no bump)
- `style:` - Code style changes (no bump)
- `refactor:` - Code refactoring (no bump)
- `test:` - Test changes (no bump)
- `chore:` - Build/tooling changes (no bump)

### 4. **Pre-commit Hook for Version Consistency**

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check if VERSION file matches version in code
VERSION=$(cat VERSION)

# Check Python files
if ! grep -q "\"$VERSION\"" xavier/src/commands/xavier_commands.py; then
    echo "Error: Version mismatch in xavier_commands.py"
    echo "Run: python scripts/bump_version.py patch"
    exit 1
fi

# Check bash files
if ! grep -q "$VERSION" xavier/src/utils/greeting.sh; then
    echo "Error: Version mismatch in greeting.sh"
    echo "Run: python scripts/bump_version.py patch"
    exit 1
fi
```

### 5. **GitHub Release Automation**

```yaml
# .github/workflows/release.yml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Extract Release Notes
        id: extract_notes
        run: |
          # Extract latest version notes from CHANGELOG
          python scripts/extract_release_notes.py > release_notes.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: release_notes.md
          generate_release_notes: true
          files: |
            xavier-v${{ github.ref_name }}.tar.gz
            CHANGELOG.md
```

### 6. **Version Check in Xavier Commands**

Add automatic version checking to Xavier:

```python
# xavier/src/commands/version_check.py
def check_for_updates():
    """Check if a newer version is available"""
    import requests

    current = get_current_version()
    try:
        response = requests.get(
            "https://api.github.com/repos/gumruyanzh/xavier/releases/latest"
        )
        latest = response.json()['tag_name'].lstrip('v')

        if compare_versions(latest, current) > 0:
            return {
                "update_available": True,
                "current": current,
                "latest": latest,
                "download_url": response.json()['html_url']
            }
    except:
        pass

    return {"update_available": False, "current": current}
```

## Implementation Steps

1. **Phase 1: Manual Script** (Immediate)
   - Create `scripts/bump_version.py`
   - Test with manual execution
   - Document in contributing guide

2. **Phase 2: CI/CD Integration** (Next Sprint)
   - Set up GitHub Actions workflow
   - Configure branch protection rules
   - Test automated PR creation

3. **Phase 3: Full Automation** (Future)
   - Implement semantic-release
   - Auto-generate release notes
   - Create automated deployment pipeline

## Benefits

1. **Consistency**: Version is always synchronized across all files
2. **Automation**: No manual intervention needed for version bumps
3. **Semantic Versioning**: Clear understanding of change impact
4. **Release Notes**: Automatic generation from commit messages
5. **Traceability**: Every version bump is tracked in git history

## Alternative: Using semantic-release

For a more robust solution, consider using `semantic-release`:

```yaml
# .releaserc.yml
branches:
  - main
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - "@semantic-release/changelog"
  - - "@semantic-release/exec"
    - prepareCmd: "python scripts/bump_version.py ${nextRelease.version}"
  - "@semantic-release/github"
  - "@semantic-release/git"
```

## Conclusion

This automation strategy will eliminate the need for manual version updates and ensure consistency across the Xavier Framework. The phased approach allows for gradual implementation while maintaining stability.