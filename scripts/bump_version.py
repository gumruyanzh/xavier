#!/usr/bin/env python3
"""
Automated version bumping for Xavier Framework
Usage: python scripts/bump_version.py [major|minor|patch]
"""

import re
import sys
import os
from pathlib import Path
from typing import Tuple
from datetime import datetime


class VersionManager:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
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
        if not version_file.exists():
            raise FileNotFoundError("VERSION file not found")

        with open(version_file, 'r') as f:
            version_str = f.read().strip()

        match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
        if match:
            return tuple(map(int, match.groups()))
        raise ValueError(f"Invalid version format: {version_str}")

    def bump_version(self, bump_type: str) -> str:
        """Bump version based on type (major, minor, patch)"""
        major, minor, patch = self.get_current_version()
        old_version = f"{major}.{minor}.{patch}"

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

        new_version = f"{major}.{minor}.{patch}"
        print(f"Bumping from {old_version} to {new_version}")
        return new_version

    def _update_simple_version(self, file_path: Path, new_version: str):
        """Update simple VERSION file"""
        print(f"  Updating {file_path.name}")
        with open(file_path, 'w') as f:
            f.write(f"{new_version}\n")

    def _update_python_version(self, file_path: Path, new_version: str):
        """Update version in Python files"""
        print(f"  Updating {file_path.name}")
        with open(file_path, 'r') as f:
            content = f.read()

        # Count replacements
        count = 0

        # Update all version references
        patterns = [
            (r'"xavier_version": "\d+\.\d+\.\d+"', f'"xavier_version": "{new_version}"'),
            (r'"framework_version": "\d+\.\d+\.\d+"', f'"framework_version": "{new_version}"'),
            (r'current_version = "\d+\.\d+\.\d+"', f'current_version = "{new_version}"'),
            (r'greeting_script, "welcome", "\d+\.\d+\.\d+"', f'greeting_script, "welcome", "{new_version}"')
        ]

        for pattern, replacement in patterns:
            content, n = re.subn(pattern, replacement, content)
            count += n

        with open(file_path, 'w') as f:
            f.write(content)

        print(f"    Updated {count} version references")

    def _update_bash_version(self, file_path: Path, new_version: str):
        """Update version in bash scripts"""
        print(f"  Updating {file_path.name}")
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
        print(f"  Updating {file_path.name}")
        with open(file_path, 'r') as f:
            content = f.read()

        # Update header version
        content = re.sub(
            r'# Xavier Framework v\d+\.\d+\.\d+',
            f'# Xavier Framework v{new_version}',
            content
        )

        # Update latest version line
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
        print(f"  Updating {file_path.name}")
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if version already exists
        if f"## [{new_version}]" in content:
            print(f"    Version {new_version} already exists in CHANGELOG")
            return

        # Create new entry
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"""## [{new_version}] - {date_str}

### Added
-

### Changed
-

### Fixed
-

"""

        # Find insertion point (after the header, before the first version)
        lines = content.split('\n')
        insert_pos = None

        for i, line in enumerate(lines):
            if line.startswith('## ['):
                insert_pos = i
                break

        if insert_pos is not None:
            # Insert the new entry
            lines.insert(insert_pos, new_entry.rstrip())
            lines.insert(insert_pos + 1, "")  # Add blank line
        else:
            # No existing versions, add at the end
            lines.append("")
            lines.append(new_entry.rstrip())

        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))

        print(f"    Added entry for version {new_version}")

    def update_all_files(self, new_version: str):
        """Update version in all tracked files"""
        print("\nUpdating version in all files:")
        for file_path, updater in self.version_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                updater(full_path, new_version)
            else:
                print(f"  Warning: {file_path} not found")

        # Set environment variables for GitHub Actions (if running in CI)
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"new_version={new_version}\n")

        if 'GITHUB_ENV' in os.environ:
            with open(os.environ['GITHUB_ENV'], 'a') as f:
                f.write(f"NEW_VERSION={new_version}\n")

    def verify_updates(self, new_version: str) -> bool:
        """Verify that all files have been updated correctly"""
        print("\nVerifying updates:")
        all_good = True

        # Check VERSION file
        version_file = self.project_root / "VERSION"
        with open(version_file, 'r') as f:
            if f.read().strip() != new_version:
                print(f"  ❌ VERSION file not updated correctly")
                all_good = False
            else:
                print(f"  ✅ VERSION file")

        # Check Python file
        py_file = self.project_root / "xavier/src/commands/xavier_commands.py"
        if py_file.exists():
            with open(py_file, 'r') as f:
                content = f.read()
                if f'"{new_version}"' in content:
                    print(f"  ✅ Python files")
                else:
                    print(f"  ❌ Python files not updated correctly")
                    all_good = False

        # Check README
        readme = self.project_root / "README.md"
        if readme.exists():
            with open(readme, 'r') as f:
                content = f.read()
                if f"v{new_version}" in content:
                    print(f"  ✅ README.md")
                else:
                    print(f"  ❌ README.md not updated correctly")
                    all_good = False

        return all_good


def main():
    print("Xavier Framework Version Bumper")
    print("=" * 40)

    if len(sys.argv) != 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print("\nUsage: python scripts/bump_version.py [major|minor|patch]")
        print("\n  major: Increment major version (X.0.0) - Breaking changes")
        print("  minor: Increment minor version (x.X.0) - New features")
        print("  patch: Increment patch version (x.x.X) - Bug fixes")
        sys.exit(1)

    bump_type = sys.argv[1]
    manager = VersionManager()

    try:
        # Get current version
        current = manager.get_current_version()
        print(f"\nCurrent version: {'.'.join(map(str, current))}")

        # Calculate new version
        new_version = manager.bump_version(bump_type)

        # Update all files
        manager.update_all_files(new_version)

        # Verify updates
        if manager.verify_updates(new_version):
            print(f"\n✅ Successfully bumped version to {new_version}")
            print("\nNext steps:")
            print("  1. Review the changes: git diff")
            print("  2. Commit the changes: git add . && git commit -m 'chore: bump version to {}'".format(new_version))
            print("  3. Push to repository: git push")
            print("  4. Create a release tag: git tag v{} && git push --tags".format(new_version))
        else:
            print(f"\n❌ Some files were not updated correctly")
            print("Please check the files and run the script again")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()