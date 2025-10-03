#!/usr/bin/env python3
"""
Test script to verify agent transformation from underscore to hyphen naming
"""

import os
import yaml
from pathlib import Path

def test_xavier_agents():
    """Test that all Xavier agents use hyphen naming"""
    xavier_agents_dir = Path('/Users/Toto/Projects/xavier/.xavier/agents')

    print("Testing Xavier agents...")
    print("-" * 50)

    issues = []

    for yaml_file in xavier_agents_dir.glob('*.yaml'):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        if 'name' in data:
            name = data['name']
            # Check for underscores in name
            if '_' in name:
                issues.append(f"  ❌ {yaml_file.name}: name '{name}' contains underscore")
            else:
                print(f"  ✅ {yaml_file.name}: {name}")

    return len(issues) == 0, issues

def test_claude_agents():
    """Test that all Claude agents exist with hyphen naming"""
    claude_agents_dir = Path('/Users/Toto/Projects/xavier/.claude/agents')

    print("\nTesting Claude agents...")
    print("-" * 50)

    expected_agents = [
        'python-engineer.md',
        'golang-engineer.md',
        'frontend-engineer.md',
        'java-engineer.md',
        'ruby-engineer.md',
        'rust-engineer.md',
        'swift-engineer.md',
        'kotlin-engineer.md',
        'elixir-engineer.md',
        'r-engineer.md',
        'test-runner.md',
        'project-manager.md',
        'context-manager.md',
    ]

    issues = []

    for agent_file in expected_agents:
        agent_path = claude_agents_dir / agent_file
        if agent_path.exists():
            # Verify the name in frontmatter
            with open(agent_path, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('name:'):
                        name = line.split(':', 1)[1].strip()
                        if '_' in name:
                            issues.append(f"  ❌ {agent_file}: name '{name}' contains underscore")
                        else:
                            print(f"  ✅ {agent_file}: {name}")
                        break
        else:
            issues.append(f"  ❌ {agent_file}: file not found")

    # Check for any underscore files
    for md_file in claude_agents_dir.glob('*_*.md'):
        issues.append(f"  ❌ {md_file.name}: filename contains underscore")

    return len(issues) == 0, issues

def test_codebase_references():
    """Test that codebase doesn't contain old underscore references"""
    print("\nTesting codebase references...")
    print("-" * 50)

    # Patterns to check for
    old_patterns = [
        'python_engineer',
        'golang_engineer',
        'frontend_engineer',
        'test_runner',
        'project_manager',
        'context_manager',
        'ruby_engineer',
        'java_engineer',
    ]

    files_to_check = [
        Path('/Users/Toto/Projects/xavier/xavier/src/commands/xavier_commands.py'),
        Path('/Users/Toto/Projects/xavier/xavier/src/agents/orchestrator.py'),
    ]

    issues = []

    for file_path in files_to_check:
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()

            for pattern in old_patterns:
                # Check for pattern in quotes (string references)
                if f'"{pattern}"' in content or f"'{pattern}'" in content:
                    issues.append(f"  ❌ {file_path.name}: contains '{pattern}'")
                    break
            else:
                print(f"  ✅ {file_path.name}: no underscore agent references")

    return len(issues) == 0, issues

def main():
    """Run all tests"""
    print("=" * 60)
    print("Agent Transformation Verification")
    print("=" * 60)

    all_passed = True

    # Test Xavier agents
    passed, issues = test_xavier_agents()
    if not passed:
        all_passed = False
        print("\nXavier agent issues:")
        for issue in issues:
            print(issue)

    # Test Claude agents
    passed, issues = test_claude_agents()
    if not passed:
        all_passed = False
        print("\nClaude agent issues:")
        for issue in issues:
            print(issue)

    # Test codebase
    passed, issues = test_codebase_references()
    if not passed:
        all_passed = False
        print("\nCodebase reference issues:")
        for issue in issues:
            print(issue)

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Agent transformation successful.")
    else:
        print("❌ Some tests failed. Please review the issues above.")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)