#!/usr/bin/env python3
"""
Version Consistency Checker for Xavier Framework
Ensures all version references are consistent across the entire codebase
Usage: python scripts/check_version.py
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class VersionChecker:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.canonical_version = None
        self.version_locations = defaultdict(list)
        self.inconsistencies = []

    def get_canonical_version(self) -> str:
        """Get the canonical version from VERSION file"""
        version_file = self.project_root / "VERSION"
        if not version_file.exists():
            raise FileNotFoundError("VERSION file not found - this is the source of truth")

        with open(version_file, 'r') as f:
            version = f.read().strip()

        # Validate format
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            raise ValueError(f"Invalid version format in VERSION file: {version}")

        self.canonical_version = version
        return version

    def scan_file(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Scan a file for version references"""
        version_refs = []

        # Define patterns to search for
        patterns = [
            r'\d+\.\d+\.\d+',  # Basic version pattern
            r'v\d+\.\d+\.\d+',  # Version with v prefix
        ]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        version_str = match.group()
                        # Normalize by removing 'v' prefix if present
                        normalized = version_str.lstrip('v')
                        # Only track semantic versions
                        if re.match(r'^\d+\.\d+\.\d+$', normalized):
                            version_refs.append((line_num, version_str, normalized))

        except (UnicodeDecodeError, PermissionError):
            pass

        return version_refs

    def scan_all_files(self):
        """Scan all relevant files in the project"""
        print("🔍 Scanning all files for version references...")

        # Files to check
        file_patterns = [
            '*.py', '*.md', '*.txt', '*.sh', '*.html', '*.json', '*.yaml', '*.yml'
        ]

        files_checked = 0
        for root, dirs, files in self.project_root.rglob('*'):
            # Skip certain directories
            if any(skip in str(root) for skip in ['.git', '__pycache__', 'trees', 'node_modules', '.venv']):
                continue

            for pattern in file_patterns:
                for file_path in Path(root).glob(pattern):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(self.project_root)

                        # Skip certain files
                        if any(skip in str(rel_path) for skip in ['CHANGELOG', 'LICENSE']):
                            continue

                        version_refs = self.scan_file(file_path)
                        if version_refs:
                            for line_num, original, normalized in version_refs:
                                self.version_locations[normalized].append({
                                    'file': str(rel_path),
                                    'line': line_num,
                                    'original': original
                                })
                            files_checked += 1

        print(f"✅ Checked {files_checked} files")

    def analyze_consistency(self):
        """Analyze version consistency across all files"""
        print(f"\n📊 Analyzing version consistency...")
        print(f"📌 Canonical version: {self.canonical_version}")

        # Count version occurrences
        version_counts = {
            version: len(locations)
            for version, locations in self.version_locations.items()
        }

        # Sort by occurrence count
        sorted_versions = sorted(version_counts.items(), key=lambda x: x[1], reverse=True)

        print(f"\n📈 Version distribution:")
        for version, count in sorted_versions[:10]:  # Show top 10
            if version == self.canonical_version:
                print(f"  ✅ {version}: {count} occurrences (CANONICAL)")
            else:
                print(f"  ❌ {version}: {count} occurrences (INCONSISTENT)")
                self.inconsistencies.append(version)

    def report_inconsistencies(self):
        """Report all version inconsistencies"""
        if not self.inconsistencies:
            print("\n✅ All version references are consistent!")
            return True

        print(f"\n❌ Found {len(self.inconsistencies)} inconsistent version(s)")
        print("\n📋 Files with incorrect versions:")

        for version in self.inconsistencies:
            if version != self.canonical_version:
                print(f"\n  Version {version} found in:")
                for location in self.version_locations[version][:20]:  # Limit to 20 per version
                    print(f"    - {location['file']}:{location['line']} ({location['original']})")

                if len(self.version_locations[version]) > 20:
                    print(f"    ... and {len(self.version_locations[version]) - 20} more")

        return False

    def get_critical_files(self) -> Dict[str, str]:
        """Check critical files that must have correct version"""
        critical_files = {
            'VERSION': None,
            'README.md': None,
            'xavier/src/commands/xavier_commands.py': None,
            'xavier/src/utils/greeting.sh': None,
            'docs/index.html': None,
            'install.sh': None,
            'update.sh': None
        }

        print("\n🎯 Checking critical files:")

        for file_path in critical_files.keys():
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"  ⚠️  {file_path}: NOT FOUND")
                continue

            # Find version in this file
            versions_in_file = set()
            for version, locations in self.version_locations.items():
                for loc in locations:
                    if loc['file'] == file_path:
                        versions_in_file.add(version)

            if self.canonical_version in versions_in_file:
                print(f"  ✅ {file_path}: {self.canonical_version}")
                critical_files[file_path] = self.canonical_version
            elif versions_in_file:
                wrong_version = list(versions_in_file)[0]
                print(f"  ❌ {file_path}: {wrong_version} (should be {self.canonical_version})")
                critical_files[file_path] = wrong_version
            else:
                print(f"  ⚠️  {file_path}: No version found")

        return critical_files

    def suggest_fix(self):
        """Suggest how to fix inconsistencies"""
        if self.inconsistencies:
            print("\n💡 To fix inconsistencies:")
            print("  1. Run: python scripts/bump_version.py patch")
            print("     (This will update all files to match VERSION file)")
            print("  2. Or manually update VERSION file to the desired version")
            print("  3. Then run bump_version.py to sync all files")


def main():
    print("🔍 Xavier Framework Version Consistency Checker")
    print("=" * 50)

    checker = VersionChecker()

    try:
        # Get canonical version
        canonical = checker.get_canonical_version()

        # Scan all files
        checker.scan_all_files()

        # Check critical files
        checker.get_critical_files()

        # Analyze consistency
        checker.analyze_consistency()

        # Report inconsistencies
        is_consistent = checker.report_inconsistencies()

        # Suggest fixes
        if not is_consistent:
            checker.suggest_fix()
            sys.exit(1)
        else:
            print("\n🎉 All versions are consistent!")
            print(f"   Current version: {canonical}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()