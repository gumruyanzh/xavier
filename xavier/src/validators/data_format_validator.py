"""
Xavier Data Format Validator
Ensures all data in .xavier/data directory is stored strictly in JSON format
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


class DataFormatValidator:
    """Validates and enforces JSON-only data storage in Xavier Framework"""

    ALLOWED_EXTENSIONS = ['.json']
    DATA_DIRECTORY = '.xavier/data'

    # Required JSON files in data directory
    REQUIRED_JSON_FILES = [
        'stories.json',
        'tasks.json',
        'bugs.json',
        'sprints.json',
        'epics.json',
        'roadmaps.json',
        'backlog.json'
    ]

    def __init__(self, project_path: str = None):
        """Initialize the data format validator"""
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.data_path = self.project_path / self.DATA_DIRECTORY

    def validate_data_directory(self) -> Tuple[bool, List[str]]:
        """
        Validate that data directory contains only JSON files
        Returns: (is_valid, list_of_issues)
        """
        issues = []

        if not self.data_path.exists():
            return True, []  # No data directory yet is OK

        # Check for non-JSON files
        for file_path in self.data_path.glob('*'):
            if file_path.is_file():
                if file_path.suffix not in self.ALLOWED_EXTENSIONS:
                    issues.append(f"Non-JSON file found: {file_path.name}")

        # Check for markdown files specifically
        md_files = list(self.data_path.glob('*.md'))
        for md_file in md_files:
            issues.append(f"Markdown file found (should be JSON): {md_file.name}")

        return len(issues) == 0, issues

    def ensure_json_format(self, data: Any) -> str:
        """
        Ensure data is in JSON format, not markdown or other formats
        Returns JSON string
        """
        if isinstance(data, str):
            # Check if it looks like markdown
            if self._looks_like_markdown(data):
                raise ValueError("Data appears to be in Markdown format. Only JSON is allowed in data directory.")

        # Ensure it's valid JSON
        try:
            if isinstance(data, str):
                json.loads(data)
                return data
            else:
                return json.dumps(data, indent=2, default=str)
        except json.JSONDecodeError:
            raise ValueError("Data is not valid JSON format")

    def _looks_like_markdown(self, text: str) -> bool:
        """Check if text appears to be markdown format"""
        markdown_indicators = [
            '##',  # Headers
            '**',  # Bold
            '```',  # Code blocks
            '- [ ]',  # Task lists
            '- [x]',  # Completed tasks
            '* ',  # Bullet points (at line start)
            '1.',  # Numbered lists
            '![',  # Images
            '[](', # Links
        ]

        lines = text.split('\n')
        for line in lines:
            line_stripped = line.strip()
            for indicator in markdown_indicators:
                if indicator in line_stripped:
                    return True

        return False

    def convert_md_to_json(self, md_file_path: Path) -> Dict[str, Any]:
        """
        Convert a markdown file to JSON format
        This is for migration purposes only
        """
        if not md_file_path.exists():
            raise FileNotFoundError(f"File not found: {md_file_path}")

        with open(md_file_path, 'r') as f:
            content = f.read()

        # Parse markdown content and convert to structured JSON
        data = self._parse_markdown_to_dict(content)

        # Save as JSON
        json_path = md_file_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)

        # Remove the markdown file
        md_file_path.unlink()

        return data

    def _parse_markdown_to_dict(self, md_content: str) -> Dict[str, Any]:
        """Parse markdown content into a dictionary structure"""
        lines = md_content.strip().split('\n')
        data = {}
        current_section = None
        current_list = []

        for line in lines:
            line = line.strip()

            # Parse headers
            if line.startswith('## '):
                if current_section and current_list:
                    data[current_section] = current_list
                    current_list = []
                current_section = line[3:].strip()

            elif line.startswith('# '):
                data['title'] = line[2:].strip()

            # Parse key-value pairs
            elif ':' in line and not line.startswith('-'):
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()

            # Parse list items
            elif line.startswith('- ') or line.startswith('* '):
                item = line[2:].strip()
                if current_section:
                    current_list.append(item)

        # Add any remaining list
        if current_section and current_list:
            data[current_section] = current_list

        return data

    def validate_json_structure(self, file_path: Path, expected_schema: Dict = None) -> Tuple[bool, str]:
        """
        Validate JSON file structure
        Returns: (is_valid, error_message)
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Basic validation - ensure it's a dict or list
            if not isinstance(data, (dict, list)):
                return False, f"Root element must be object or array, got {type(data).__name__}"

            # Schema validation if provided
            if expected_schema:
                # Simple schema validation (can be extended)
                for required_key in expected_schema.get('required_keys', []):
                    if required_key not in data:
                        return False, f"Missing required key: {required_key}"

            return True, ""

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"

    def enforce_json_only_storage(self) -> Dict[str, Any]:
        """
        Enforce JSON-only storage in data directory
        Converts any non-JSON files and returns a report
        """
        report = {
            'validated': True,
            'issues_found': [],
            'files_converted': [],
            'files_removed': []
        }

        if not self.data_path.exists():
            self.data_path.mkdir(parents=True, exist_ok=True)

        # Initialize required JSON files if missing
        for json_file in self.REQUIRED_JSON_FILES:
            file_path = self.data_path / json_file
            if not file_path.exists():
                # Create empty JSON structure
                initial_data = [] if 'backlog' in json_file else {}
                with open(file_path, 'w') as f:
                    json.dump(initial_data, f, indent=2)
                report['files_converted'].append(f"Created {json_file}")

        # Check for non-JSON files
        for file_path in self.data_path.glob('*'):
            if file_path.is_file():
                if file_path.suffix == '.md':
                    # Convert markdown to JSON
                    try:
                        self.convert_md_to_json(file_path)
                        report['files_converted'].append(f"Converted {file_path.name} to JSON")
                    except Exception as e:
                        report['issues_found'].append(f"Could not convert {file_path.name}: {str(e)}")

                elif file_path.suffix not in self.ALLOWED_EXTENSIONS:
                    # Remove non-allowed files (after backing up)
                    backup_path = file_path.parent / f".backup_{file_path.name}"
                    file_path.rename(backup_path)
                    report['files_removed'].append(f"Moved {file_path.name} to {backup_path.name}")

        # Validate all JSON files
        for json_file in self.data_path.glob('*.json'):
            is_valid, error = self.validate_json_structure(json_file)
            if not is_valid:
                report['issues_found'].append(f"{json_file.name}: {error}")
                report['validated'] = False

        return report

    def wrap_data_save(self, data_type: str, data: Any) -> None:
        """
        Wrapper for saving data that ensures JSON format

        Args:
            data_type: Type of data (stories, tasks, etc.)
            data: The data to save
        """
        # Ensure data directory exists
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Validate it's JSON-serializable
        json_str = self.ensure_json_format(data)

        # Save to appropriate file
        file_path = self.data_path / f"{data_type}.json"

        # Parse back to ensure it's valid
        json_data = json.loads(json_str) if isinstance(json_str, str) else data

        # Write to file
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)


def validate_xavier_data_format(project_path: str = None) -> None:
    """
    Main validation function to ensure JSON-only data storage
    This should be called periodically or before operations
    """
    validator = DataFormatValidator(project_path)

    # Enforce JSON-only storage
    report = validator.enforce_json_only_storage()

    if report['issues_found']:
        print("⚠️ Data format issues found:")
        for issue in report['issues_found']:
            print(f"  - {issue}")

    if report['files_converted']:
        print("✅ Files converted to JSON:")
        for conversion in report['files_converted']:
            print(f"  - {conversion}")

    if report['files_removed']:
        print("🗑️ Non-JSON files backed up:")
        for removal in report['files_removed']:
            print(f"  - {removal}")

    if report['validated']:
        print("✅ All data files are in valid JSON format")
    else:
        print("❌ Some data files have validation errors")

    return report['validated']