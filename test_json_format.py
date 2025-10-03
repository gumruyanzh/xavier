#!/usr/bin/env python3
"""
Test script to verify JSON-only data format enforcement
"""

import os
import sys
import json
from pathlib import Path

# Add xavier to path
sys.path.insert(0, str(Path(__file__).parent))

from xavier.src.validators.data_format_validator import DataFormatValidator, validate_xavier_data_format
from xavier.src.utils.json_output_formatter import JSONOutputFormatter


def test_validator():
    """Test the data format validator"""
    print("Testing Data Format Validator...")
    print("-" * 50)

    # Initialize validator
    validator = DataFormatValidator()

    # Test 1: Check if markdown is detected
    md_text = """## User Story
    **As a** user
    **I want** to test
    **So that** I can verify

    ### Acceptance Criteria
    - [ ] Test 1
    - [ ] Test 2
    """

    try:
        validator.ensure_json_format(md_text)
        print("❌ Failed: Markdown should have been detected")
    except ValueError as e:
        print(f"✅ Passed: Markdown detected - {e}")

    # Test 2: Check if valid JSON passes
    json_data = {"title": "Test Story", "status": "backlog"}
    try:
        result = validator.ensure_json_format(json_data)
        print("✅ Passed: Valid JSON accepted")
    except Exception as e:
        print(f"❌ Failed: Valid JSON rejected - {e}")

    # Test 3: Validate data directory
    is_valid, issues = validator.validate_data_directory()
    if is_valid:
        print(f"✅ Data directory validation passed")
    else:
        print(f"⚠️ Data directory issues: {issues}")


def test_json_formatter():
    """Test the JSON output formatter"""
    print("\nTesting JSON Output Formatter...")
    print("-" * 50)

    # Test story formatting
    story_data = {
        "story_id": "US-001",
        "title": "Test Story",
        "as_a": "developer",
        "i_want": "to test JSON format",
        "so_that": "data is consistent",
        "story_points": 5
    }

    story_json = JSONOutputFormatter.format_story_output(story_data)
    try:
        parsed = json.loads(story_json)
        print(f"✅ Story JSON format valid: {parsed['type']} - {parsed['id']}")
    except:
        print("❌ Failed: Story JSON format invalid")

    # Test task formatting
    task_data = {
        "task_id": "TASK-001",
        "story_id": "US-001",
        "title": "Implement feature",
        "estimated_hours": 8
    }

    task_json = JSONOutputFormatter.format_task_output(task_data)
    try:
        parsed = json.loads(task_json)
        print(f"✅ Task JSON format valid: {parsed['type']} - {parsed['id']}")
    except:
        print("❌ Failed: Task JSON format invalid")

    # Test markdown detection
    md_content = "## This is markdown"
    is_markdown = JSONOutputFormatter._looks_like_markdown(md_content)
    if is_markdown:
        print("✅ Markdown detection working")
    else:
        print("❌ Failed: Markdown not detected")


def test_data_directory_enforcement():
    """Test that data directory only contains JSON files"""
    print("\nTesting Data Directory Enforcement...")
    print("-" * 50)

    data_path = Path(".xavier/data")

    if not data_path.exists():
        print("⚠️ No .xavier/data directory found")
        return

    # Check all files in data directory
    non_json_files = []
    json_files = []

    for file in data_path.iterdir():
        if file.is_file():
            if file.suffix == '.json':
                json_files.append(file.name)
                # Verify it's valid JSON
                try:
                    with open(file, 'r') as f:
                        json.load(f)
                except:
                    print(f"❌ Invalid JSON: {file.name}")
            else:
                non_json_files.append(file.name)

    if non_json_files:
        print(f"❌ Non-JSON files found: {non_json_files}")
    else:
        print(f"✅ Only JSON files in data directory: {len(json_files)} files")

    # List JSON files
    if json_files:
        print(f"   JSON files: {', '.join(json_files)}")


def test_full_validation():
    """Run full validation"""
    print("\nRunning Full Validation...")
    print("-" * 50)

    is_valid = validate_xavier_data_format()

    if is_valid:
        print("\n✅ All validation checks passed!")
    else:
        print("\n❌ Some validation checks failed")

    return is_valid


if __name__ == "__main__":
    print("=" * 60)
    print("Xavier Framework JSON Format Validation Test")
    print("=" * 60)

    test_validator()
    test_json_formatter()
    test_data_directory_enforcement()
    test_full_validation()

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)