#!/usr/bin/env python3
"""
Transform Xavier agents to Claude Code compatible format
Converts underscore naming to hyphen naming and generates Claude agent files
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List

# Agent transformation mappings
AGENT_TRANSFORMATIONS = {
    'python_engineer': 'python-engineer',
    'golang_engineer': 'golang-engineer',
    'frontend_engineer': 'frontend-engineer',
    'java_engineer': 'java-engineer',
    'ruby_engineer': 'ruby-engineer',
    'rust_engineer': 'rust-engineer',
    'swift_engineer': 'swift-engineer',
    'kotlin_engineer': 'kotlin-engineer',
    'elixir_engineer': 'elixir-engineer',
    'r_engineer': 'r-engineer',
    'test_runner': 'test-runner',
    'project_manager': 'project-manager',
    'context_manager': 'context-manager',
}

# Agent descriptions for Claude
AGENT_DESCRIPTIONS = {
    'python-engineer': 'Specialized Python developer following TDD, Clean Code principles, and Xavier Framework standards',
    'golang-engineer': 'Expert Go developer focusing on microservices, performance, and concurrent programming',
    'frontend-engineer': 'Frontend specialist with expertise in React, TypeScript, and modern web technologies',
    'java-engineer': 'Enterprise Java developer specializing in Spring Boot, microservices, and clean architecture',
    'ruby-engineer': 'Ruby/Rails expert focused on convention over configuration and test-driven development',
    'rust-engineer': 'Systems programmer specializing in memory-safe, concurrent Rust development',
    'swift-engineer': 'iOS/macOS developer expert in Swift, SwiftUI, and Apple platform development',
    'kotlin-engineer': 'Modern JVM developer specializing in Kotlin for Android and backend development',
    'elixir-engineer': 'Functional programming expert specializing in Elixir, Phoenix, and fault-tolerant systems',
    'r-engineer': 'Data science specialist focusing on statistical computing and data visualization with R',
    'test-runner': 'Testing specialist ensuring 100% code coverage and quality assurance',
    'project-manager': 'Sprint planning, story estimation, and project coordination specialist',
    'context-manager': 'Codebase analysis and architectural context provider',
}

def load_xavier_agent(yaml_path: Path) -> Dict[str, Any]:
    """Load a Xavier agent YAML file"""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def generate_claude_agent_content(agent_data: Dict[str, Any], agent_name: str) -> str:
    """Generate Claude Code agent MD content from Xavier agent data"""

    # Get description or use default
    description = AGENT_DESCRIPTIONS.get(agent_name, f"Specialized {agent_name.replace('-', ' ').title()} for Xavier Framework")

    # Get tools list
    tools = agent_data.get('tools', ['Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob'])
    tools_str = ', '.join(tools)

    # Get emoji and display name
    emoji = agent_data.get('emoji', '🤖')
    display_name = agent_data.get('display_name', agent_name.replace('-', ' ').title())

    # Get capabilities
    capabilities = agent_data.get('capabilities', [])

    # Get languages and frameworks
    languages = agent_data.get('languages', [])
    frameworks = agent_data.get('frameworks', [])

    # Generate content
    content = f"""---
name: {agent_name}
description: {description}
tools: {tools_str}
model: sonnet
---

# {display_name} Agent {emoji}

You are the **{display_name}** for Xavier Framework, specializing in development with strict adherence to TDD and Clean Code principles.

## Role & Responsibilities
"""

    # Add capabilities as responsibilities
    if capabilities:
        for cap in capabilities:
            content += f"- {cap.replace('_', ' ').title()}\n"
    else:
        content += f"- {display_name} development and implementation\n"
        content += f"- Test-first development (TDD) enforcement\n"
        content += f"- Clean Code implementation and refactoring\n"

    content += """
## Core Capabilities
"""

    # Add language-specific capabilities
    if languages:
        content += f"- **Languages**: {', '.join(languages)}\n"
    if frameworks:
        content += f"- **Frameworks**: {', '.join(frameworks)}\n"

    content += """- **TDD Implementation**: Write tests before code, ensure 100% coverage
- **Clean Code**: SOLID principles, DRY, KISS, proper naming conventions
- **Best Practices**: Language-specific idioms and patterns
- **Performance**: Optimization and scalability considerations

## Development Standards

### Test-First Approach
1. **Always write tests first** - No implementation without tests
2. **Red-Green-Refactor cycle** - Fail, pass, improve
3. **100% test coverage** - Every line must be tested
4. **Test types**: Unit, integration, functional, performance

### Clean Code Principles
- **SOLID principles**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **DRY (Don't Repeat Yourself)**: Extract common functionality
- **KISS (Keep It Simple, Stupid)**: Prefer simple, readable solutions
- **Meaningful names**: Variables, functions, classes should be self-documenting

### Code Quality Rules
- **Function length**: Maximum 20 lines
- **Class length**: Maximum 200 lines
- **Cyclomatic complexity**: Maximum 10
- **No magic numbers**: Use named constants
- **Single purpose**: Each function does one thing well

## Task Execution Protocol

When assigned a task:

1. **Understand Requirements**
   - Analyze the task requirements
   - Identify acceptance criteria
   - Clarify any ambiguities

2. **Write Tests First**
   - Create comprehensive test suite
   - Include edge cases
   - Ensure tests fail initially

3. **Implement Solution**
   - Write minimal code to pass tests
   - Follow language best practices
   - Maintain clean, readable code

4. **Refactor**
   - Improve code structure
   - Remove duplication
   - Enhance readability

5. **Validate**
   - Run all tests
   - Check coverage (must be 100%)
   - Verify acceptance criteria

## Communication Style

When taking over a task:
```
"""

    content += f"🎯 {display_name} taking over task: [TASK-ID]\n"
    content += f"{emoji} Analyzing requirements...\n"
    content += f"{emoji} Writing tests first...\n"
    content += f"{emoji} Implementing solution...\n"
    content += f"✅ Task completed with 100% test coverage\n"

    content += """```

## File Patterns
"""

    # Add allowed file patterns
    file_patterns = agent_data.get('allowed_file_patterns', [])
    if file_patterns:
        content += "Work only with these file types:\n"
        for pattern in file_patterns:
            content += f"- `{pattern}`\n"

    content += """
## Important Notes

- **Never skip tests** - TDD is mandatory
- **Never accept < 100% coverage** - Every line must be tested
- **Never violate Clean Code principles** - Maintain high standards
- **Never work outside your language scope** - Stay within expertise
- **Always communicate clearly** - Use the specified format

Remember: You are a specialized agent with deep expertise in your domain. Maintain the highest standards of code quality and testing discipline.
"""

    return content

def transform_agents():
    """Transform all Xavier agents to Claude Code format"""
    xavier_agents_dir = Path('/Users/Toto/Projects/xavier/.xavier/agents')
    claude_agents_dir = Path('/Users/Toto/Projects/xavier/.claude/agents')

    # Create Claude agents directory if it doesn't exist
    claude_agents_dir.mkdir(parents=True, exist_ok=True)

    transformed = []

    # Process each Xavier agent
    for yaml_file in xavier_agents_dir.glob('*.yaml'):
        # Get base name with underscores
        base_name = yaml_file.stem

        # Load agent data
        agent_data = load_xavier_agent(yaml_file)

        # Get hyphen name from data or transform
        hyphen_name = agent_data.get('name', base_name.replace('_', '-'))

        # Generate Claude agent content
        claude_content = generate_claude_agent_content(agent_data, hyphen_name)

        # Write Claude agent file
        claude_file = claude_agents_dir / f"{hyphen_name}.md"
        with open(claude_file, 'w') as f:
            f.write(claude_content)

        transformed.append({
            'original': base_name,
            'transformed': hyphen_name,
            'yaml_file': str(yaml_file),
            'claude_file': str(claude_file)
        })

        print(f"✅ Transformed {base_name} -> {hyphen_name}")

    return transformed

def update_xavier_agent_names():
    """Update Xavier agent YAML files to use hyphen naming"""
    xavier_agents_dir = Path('/Users/Toto/Projects/xavier/.xavier/agents')

    for yaml_file in xavier_agents_dir.glob('*.yaml'):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        # Update name field to use hyphens
        if 'name' in data:
            old_name = data['name']
            new_name = old_name.replace('_', '-')
            if old_name != new_name:
                data['name'] = new_name

                # Save updated YAML
                with open(yaml_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

                print(f"  Updated {yaml_file.name}: {old_name} -> {new_name}")

def update_codebase_references():
    """Update agent references in Python code to use hyphen naming"""
    replacements = []

    # Define paths to check
    paths_to_check = [
        Path('/Users/Toto/Projects/xavier/xavier/src'),
        Path('/Users/Toto/Projects/xavier/xavier_slash_command.py'),
    ]

    # Define replacement patterns
    patterns = {
        'python_engineer': 'python-engineer',
        'golang_engineer': 'golang-engineer',
        'frontend_engineer': 'frontend-engineer',
        'java_engineer': 'java-engineer',
        'ruby_engineer': 'ruby-engineer',
        'rust_engineer': 'rust-engineer',
        'test_runner': 'test-runner',
        'project_manager': 'project-manager',
        'context_manager': 'context-manager',
    }

    for path in paths_to_check:
        if path.is_file():
            files = [path]
        else:
            files = list(path.rglob('*.py'))

        for py_file in files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()

                original_content = content

                # Replace agent names in strings
                for old_name, new_name in patterns.items():
                    # Replace in quotes
                    content = content.replace(f'"{old_name}"', f'"{new_name}"')
                    content = content.replace(f"'{old_name}'", f"'{new_name}'")
                    # Replace in agent assignments
                    content = content.replace(f'agent_name = "{old_name}"', f'agent_name = "{new_name}"')
                    content = content.replace(f"agent_name = '{old_name}'", f"agent_name = '{new_name}'")

                if content != original_content:
                    with open(py_file, 'w') as f:
                        f.write(content)
                    replacements.append(str(py_file))
                    print(f"  Updated references in {py_file.name}")

            except Exception as e:
                print(f"  Error updating {py_file}: {e}")

    return replacements

def main():
    """Main transformation process"""
    print("=" * 60)
    print("Xavier to Claude Agent Transformation")
    print("=" * 60)

    print("\n1. Updating Xavier agent names to use hyphens...")
    update_xavier_agent_names()

    print("\n2. Transforming agents to Claude Code format...")
    transformed = transform_agents()

    print("\n3. Updating codebase references...")
    updated_files = update_codebase_references()

    print("\n" + "=" * 60)
    print("Transformation Complete!")
    print("=" * 60)

    print(f"\n✅ Transformed {len(transformed)} agents")
    print(f"✅ Updated {len(updated_files)} code files")

    print("\n📁 Claude agents created in: .claude/agents/")
    for item in transformed:
        print(f"   - {item['transformed']}.md")

    print("\n🎯 All agents now use hyphen naming convention!")
    print("   Example: python_engineer -> python-engineer")

if __name__ == "__main__":
    main()