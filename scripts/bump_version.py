#!/usr/bin/env python3
"""
Automated version bumping for Xavier Framework
Updates version in ALL files across the entire codebase
Usage: python scripts/bump_version.py [major|minor|patch]
"""

import re
import sys
import os
from pathlib import Path
from typing import Tuple, List, Dict
from datetime import datetime


class VersionManager:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        # Track all files that need version updates
        self.version_files = {
            # Core files
            "VERSION": self._update_simple_version,
            "xavier/src/commands/xavier_commands.py": self._update_python_version,
            "xavier/src/utils/greeting.sh": self._update_bash_version,
            "README.md": self._update_readme_version,
            "CHANGELOG.md": self._update_changelog,

            # Documentation website
            "docs/index.html": self._update_website_index,
            "docs/documentation.html": self._update_website_docs,
            "docs/quick-start.html": self._update_website_quickstart,
            "docs/changelog.html": self._update_website_changelog,

            # Installation scripts
            "install.sh": self._update_install_script,
            "update.sh": self._update_update_script,
            "setup.py": self._update_setup_py,
        }

        # Track all version patterns to search for
        self.version_patterns = []

    def get_current_version(self) -> Tuple[int, int, int]:
        """Read current version from VERSION file"""
        version_file = self.project_root / "VERSION"
        if not version_file.exists():
            raise FileNotFoundError("VERSION file not found")

        with open(version_file, 'r') as f:
            version_str = f.read().strip()

        match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
        if match:
            current = tuple(map(int, match.groups()))
            # Store patterns for the current version to find all occurrences
            self.version_patterns = self._generate_version_patterns(*current)
            return current
        raise ValueError(f"Invalid version format: {version_str}")

    def _generate_version_patterns(self, major: int, minor: int, patch: int) -> List[str]:
        """Generate all possible version string patterns"""
        version = f"{major}.{minor}.{patch}"
        patterns = [
            version,                              # 1.2.2
            f"v{version}",                       # v1.2.2
            f"Version {version}",                # Version 1.2.2
            f"version {version}",                # version 1.2.2
            f"Xavier Framework v{version}",      # Xavier Framework v1.2.2
            f'"xavier_version": "{version}"',    # JSON format
            f'"framework_version": "{version}"', # JSON format
        ]
        return patterns

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
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        count = 0
        patterns = [
            (r'"xavier_version": "\d+\.\d+\.\d+"', f'"xavier_version": "{new_version}"'),
            (r'"framework_version": "\d+\.\d+\.\d+"', f'"framework_version": "{new_version}"'),
            (r'current_version = "\d+\.\d+\.\d+"', f'current_version = "{new_version}"'),
            (r'greeting_script, "welcome", "\d+\.\d+\.\d+"', f'greeting_script, "welcome", "{new_version}"')
        ]

        for pattern, replacement in patterns:
            content, n = re.subn(pattern, replacement, content)
            count += n

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"    Updated {count} version references")

    def _update_bash_version(self, file_path: Path, new_version: str):
        """Update version in bash scripts"""
        print(f"  Updating {file_path.name}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(
            r'VERSION="\$\{2:-\d+\.\d+\.\d+\}"',
            f'VERSION="${{2:-{new_version}}}"',
            content
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_readme_version(self, file_path: Path, new_version: str):
        """Update version in README"""
        print(f"  Updating {file_path.name}")
        with open(file_path, 'r', encoding='utf-8') as f:
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

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_changelog(self, file_path: Path, new_version: str):
        """Add new version entry to CHANGELOG if not exists"""
        print(f"  Updating {file_path.name}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Only add if version doesn't exist
        if f"## [{new_version}]" not in content:
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_entry = f"""## [{new_version}] - {date_str}

### Added
-

### Changed
-

### Fixed
-

"""
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('## ['):
                    lines.insert(i, new_entry.rstrip())
                    lines.insert(i + 1, "")
                    break

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f"    Added entry for version {new_version}")

    def _update_website_index(self, file_path: Path, new_version: str):
        """Update version in website index.html"""
        print(f"  Updating {file_path.name}")
        if not file_path.exists():
            print(f"    Skipping (file not found)")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        count = 0
        # Update version badge
        content, n = re.subn(
            r'>v\d+\.\d+\.\d+<',
            f'>v{new_version}<',
            content
        )
        count += n

        # Update "What's New" section
        content, n = re.subn(
            r'What\'s New in v\d+\.\d+\.\d+',
            f"What's New in v{new_version}",
            content
        )
        count += n

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"    Updated {count} version references")

    def _update_website_docs(self, file_path: Path, new_version: str):
        """Update version in documentation.html"""
        print(f"  Updating {file_path.name}")
        if not file_path.exists():
            print(f"    Skipping (file not found)")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update version references
        content = re.sub(
            r'<strong>📚 Version:</strong> \d+\.\d+\.\d+',
            f'<strong>📚 Version:</strong> {new_version}',
            content
        )

        # Update any version mentions in text
        content = re.sub(
            r'Version \d+\.\d+\.\d+',
            f'Version {new_version}',
            content
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_website_quickstart(self, file_path: Path, new_version: str):
        """Update version in quick-start.html"""
        print(f"  Updating {file_path.name}")
        if not file_path.exists():
            print(f"    Skipping (file not found)")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update any version references
        content = re.sub(r'v\d+\.\d+\.\d+', f'v{new_version}', content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_website_changelog(self, file_path: Path, new_version: str):
        """Update version in changelog.html"""
        print(f"  Updating {file_path.name}")
        if not file_path.exists():
            print(f"    Skipping (file not found)")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add new version section if not exists
        if f"[{new_version}]" not in content:
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_section = f"""
                <div class="changelog-entry">
                    <h3>[{new_version}] - {date_str}</h3>
                    <h4>Added</h4>
                    <ul><li>-</li></ul>
                    <h4>Changed</h4>
                    <ul><li>-</li></ul>
                    <h4>Fixed</h4>
                    <ul><li>-</li></ul>
                </div>"""

            # Insert after changelog header
            content = re.sub(
                r'(<div class="section-content">)',
                f'\\1{new_section}',
                content,
                count=1
            )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_install_script(self, file_path: Path, new_version: str):
        """Update version in install.sh"""
        print(f"  Updating {file_path.name}")
        if not file_path.exists():
            print(f"    Skipping (file not found)")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        count = 0
        # Update version comments
        content, n = re.subn(
            r'# Version \d+\.\d+\.\d+',
            f'# Version {new_version}',
            content
        )
        count += n

        # Update displayed version
        content, n = re.subn(
            r'Version \d+\.\d+\.\d+',
            f'Version {new_version}',
            content
        )
        count += n

        # Update version echo
        content, n = re.subn(
            r'echo "\d+\.\d+\.\d+" > VERSION',
            f'echo "{new_version}" > VERSION',
            content
        )
        count += n

        # Update JSON version
        content, n = re.subn(
            r'"xavier_version": "\d+\.\d+\.\d+"',
            f'"xavier_version": "{new_version}"',
            content
        )
        count += n

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"    Updated {count} version references")

    def _update_update_script(self, file_path: Path, new_version: str):
        """Update version in update.sh"""
        print(f"  Updating {file_path.name}")
        if not file_path.exists():
            print(f"    Skipping (file not found)")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update version comment
        content = re.sub(
            r'# Version \d+\.\d+\.\d+',
            f'# Version {new_version}',
            content
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_setup_py(self, file_path: Path, new_version: str):
        """Update version in setup.py if it exists"""
        print(f"  Updating {file_path.name}")
        if not file_path.exists():
            print(f"    Skipping (file not found)")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update version in setup()
        content = re.sub(
            r'version\s*=\s*["\']?\d+\.\d+\.\d+["\']?',
            f'version="{new_version}"',
            content
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def find_all_version_occurrences(self) -> Dict[str, List[str]]:
        """Find all files containing version strings"""
        print("\n🔍 Scanning for version occurrences...")
        occurrences = {}

        # Get current version patterns
        major, minor, patch = self.get_current_version()
        patterns = [
            f"{major}.{minor}.{patch}",
            f"v{major}.{minor}.{patch}",
            f"Version {major}.{minor}.{patch}",
        ]

        # Search in all text files
        for root, dirs, files in os.walk(self.project_root):
            # Skip .git and other hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                # Only check text files
                if file.endswith(('.py', '.md', '.txt', '.sh', '.html', '.json', '.yaml', '.yml', '.js', '.css')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for pattern in patterns:
                                if pattern in content:
                                    rel_path = file_path.relative_to(self.project_root)
                                    if str(rel_path) not in occurrences:
                                        occurrences[str(rel_path)] = []
                                    occurrences[str(rel_path)].append(pattern)
                    except (UnicodeDecodeError, PermissionError):
                        continue

        return occurrences

    def update_all_files(self, new_version: str):
        """Update version in all tracked files"""
        print("\n📝 Updating version in all files:")
        for file_path, updater in self.version_files.items():
            full_path = self.project_root / file_path
            try:
                updater(full_path, new_version)
            except Exception as e:
                print(f"  ❌ Error updating {file_path}: {e}")

        # Set environment variables for GitHub Actions (if running in CI)
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"new_version={new_version}\n")

        if 'GITHUB_ENV' in os.environ:
            with open(os.environ['GITHUB_ENV'], 'a') as f:
                f.write(f"NEW_VERSION={new_version}\n")

    def verify_updates(self, new_version: str) -> bool:
        """Verify that all files have been updated correctly"""
        print("\n✅ Verifying updates:")
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
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if f'"{new_version}"' in content:
                    print(f"  ✅ Python files")
                else:
                    print(f"  ❌ Python files not updated correctly")
                    all_good = False

        # Check README
        readme = self.project_root / "README.md"
        if readme.exists():
            with open(readme, 'r', encoding='utf-8') as f:
                content = f.read()
                if f"v{new_version}" in content:
                    print(f"  ✅ README.md")
                else:
                    print(f"  ❌ README.md not updated correctly")
                    all_good = False

        # Check website
        index_html = self.project_root / "docs/index.html"
        if index_html.exists():
            with open(index_html, 'r', encoding='utf-8') as f:
                content = f.read()
                if f"v{new_version}" in content:
                    print(f"  ✅ Website documentation")
                else:
                    print(f"  ❌ Website not updated correctly")
                    all_good = False

        return all_good

    def check_missed_occurrences(self, new_version: str) -> List[str]:
        """Check for any version occurrences that might have been missed"""
        print("\n🔎 Checking for missed version occurrences...")

        # Get old version
        old_major, old_minor, old_patch = self.get_current_version()
        old_version = f"{old_major}.{old_minor}.{old_patch}"

        missed = []

        # Search for old version patterns
        old_patterns = [
            old_version,
            f"v{old_version}",
            f"Version {old_version}",
        ]

        for root, dirs, files in os.walk(self.project_root):
            # Skip .git and other directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'trees']

            for file in files:
                if file.endswith(('.py', '.md', '.txt', '.sh', '.html', '.json', '.yaml', '.yml')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for pattern in old_patterns:
                                if pattern in content and new_version not in content:
                                    rel_path = str(file_path.relative_to(self.project_root))
                                    if rel_path not in missed:
                                        missed.append(rel_path)
                    except (UnicodeDecodeError, PermissionError):
                        continue

        return missed


def main():
    print("🚀 Xavier Framework Comprehensive Version Bumper")
    print("=" * 50)

    if len(sys.argv) not in [2, 3]:
        print("\nUsage: python scripts/bump_version.py [major|minor|patch] [--check]")
        print("\n  major: Increment major version (X.0.0) - Breaking changes")
        print("  minor: Increment minor version (x.X.0) - New features")
        print("  patch: Increment patch version (x.x.X) - Bug fixes")
        print("  --check: Check for all version occurrences without updating")
        sys.exit(1)

    # Check mode
    if "--check" in sys.argv:
        manager = VersionManager()
        occurrences = manager.find_all_version_occurrences()
        print(f"\nFound version in {len(occurrences)} files:")
        for file, patterns in occurrences.items():
            print(f"  📄 {file}: {', '.join(set(patterns))}")
        sys.exit(0)

    bump_type = sys.argv[1]
    manager = VersionManager()

    try:
        # Get current version
        current = manager.get_current_version()
        print(f"\n📌 Current version: {'.'.join(map(str, current))}")

        # Show current occurrences
        occurrences = manager.find_all_version_occurrences()
        print(f"\n📊 Version found in {len(occurrences)} files")

        # Calculate new version
        new_version = manager.bump_version(bump_type)

        # Update all files
        manager.update_all_files(new_version)

        # Check for missed occurrences
        missed = manager.check_missed_occurrences(new_version)
        if missed:
            print(f"\n⚠️  Warning: Old version still found in:")
            for file in missed:
                print(f"  - {file}")

        # Verify updates
        if manager.verify_updates(new_version):
            print(f"\n✅ Successfully bumped version to {new_version}")
            print("\n📋 Next steps:")
            print("  1. Review the changes: git diff")
            print("  2. Commit: git add . && git commit -m 'chore: bump version to {}'".format(new_version))
            print("  3. Push: git push")
            print("  4. Tag release: git tag v{} && git push --tags".format(new_version))
        else:
            print(f"\n❌ Some files were not updated correctly")
            print("Please check the files and run the script again")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()