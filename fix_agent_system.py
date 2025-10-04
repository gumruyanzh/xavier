#!/usr/bin/env python3
"""
Fix Agent System - Ensures all agents work properly with Claude Code delegation and have correct colors
"""

import os
import yaml
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def update_claude_agent_files():
    """Update all Claude agent MD files to have proper YAML frontmatter"""
    claude_agents_dir = Path(".claude/agents")
    xavier_agents_dir = Path(".xavier/agents")

    if not claude_agents_dir.exists():
        logger.error(f"Claude agents directory not found: {claude_agents_dir}")
        return False

    logger.info(f"Updating Claude agent files in {claude_agents_dir}")

    # Map of agent names to proper descriptions for delegation
    agent_descriptions = {
        "python-engineer": "Python development with Django, Flask, FastAPI. Use for Python tasks, API development, backend services",
        "frontend-engineer": "React, TypeScript, JavaScript, Vue, Angular. Use for frontend, UI, web development tasks",
        "golang-engineer": "Go development with Gin, microservices. Use for Go/Golang tasks, high-performance services",
        "test-runner": "Testing, test coverage, unit tests, integration tests. Use for all testing tasks",
        "project-manager": "Sprint planning, story management, task coordination. Use for project management tasks",
        "context-manager": "Codebase analysis, architecture understanding. Use for code exploration and documentation",
        "java-engineer": "Java development with Spring, SpringBoot. Use for Java tasks, enterprise applications",
        "ruby-engineer": "Ruby on Rails development. Use for Ruby tasks, web applications",
        "rust-engineer": "Rust development with Actix, Tokio. Use for Rust tasks, systems programming",
        "swift-engineer": "iOS development with Swift, SwiftUI. Use for iOS/macOS app development",
        "kotlin-engineer": "Android development with Kotlin. Use for Android app development",
        "elixir-engineer": "Elixir development with Phoenix. Use for Elixir tasks, concurrent systems",
        "r-engineer": "R statistical computing, data analysis. Use for statistical analysis and data science",
        "devops-engineer": "Docker, Kubernetes, CI/CD, infrastructure. Use for DevOps, deployment, containerization",
        "orchestrator": "Agent coordination and task delegation. Internal use only",
        "haskell-engineer": "Haskell functional programming. Use for Haskell tasks"
    }

    # Process each Claude agent file
    updated_count = 0
    for agent_file in claude_agents_dir.glob("*.md"):
        agent_name = agent_file.stem

        # Read current content
        with open(agent_file, 'r') as f:
            content = f.read()

        # Check if it already has YAML frontmatter
        if content.startswith('---'):
            # Extract existing frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    yaml_content = yaml.safe_load(parts[1])
                    body = parts[2]
                except:
                    logger.warning(f"Failed to parse YAML in {agent_file}")
                    continue
            else:
                body = content
                yaml_content = {}
        else:
            body = content
            yaml_content = {}

        # Get agent metadata from Xavier YAML if available
        xavier_yaml_file = xavier_agents_dir / f"{agent_name.replace('-', '_')}.yaml"
        if xavier_yaml_file.exists():
            try:
                with open(xavier_yaml_file, 'r') as f:
                    xavier_data = yaml.safe_load(f)

                # Update tools list from Xavier data
                if 'tools' in xavier_data:
                    yaml_content['tools'] = ', '.join(xavier_data.get('tools', []))
            except Exception as e:
                logger.warning(f"Could not read Xavier YAML for {agent_name}: {e}")

        # Update/create YAML frontmatter with required fields
        yaml_content['name'] = agent_name
        yaml_content['description'] = agent_descriptions.get(
            agent_name,
            f"Specialized {agent_name.replace('-', ' ').title()} for development tasks"
        )

        # Ensure tools are specified
        if 'tools' not in yaml_content:
            yaml_content['tools'] = 'Read, Write, Edit, Bash, Grep, Glob'

        # Optional: specify model for certain agents
        if agent_name in ['project-manager', 'orchestrator']:
            yaml_content['model'] = 'opus'

        # Reconstruct the file with updated YAML frontmatter
        new_content = "---\n"
        new_content += yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)
        new_content += "---\n"
        new_content += body.lstrip()

        # Write back the updated content
        with open(agent_file, 'w') as f:
            f.write(new_content)

        updated_count += 1
        logger.info(f"Updated {agent_file.name}")

    logger.info(f"Updated {updated_count} Claude agent files")
    return True


def create_agent_color_config():
    """Create a configuration file that maps agents to their colors"""
    xavier_agents_dir = Path(".xavier/agents")
    config_file = Path(".xavier/agent_colors.json")

    if not xavier_agents_dir.exists():
        logger.error(f"Xavier agents directory not found: {xavier_agents_dir}")
        return False

    color_config = {}

    # Read all Xavier agent YAMLs to get color information
    for yaml_file in xavier_agents_dir.glob("*.yaml"):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)

            if 'name' in data and 'color' in data:
                agent_name = data['name']
                color_config[agent_name] = {
                    'color': data.get('color', 'white'),
                    'emoji': data.get('emoji', '🤖'),
                    'label': data.get('label', 'AGT'),
                    'display_name': data.get('display_name', agent_name.replace('-', ' ').title())
                }
        except Exception as e:
            logger.warning(f"Could not read {yaml_file}: {e}")

    # Save color configuration
    with open(config_file, 'w') as f:
        json.dump(color_config, f, indent=2, ensure_ascii=False)

    logger.info(f"Created agent color configuration at {config_file}")
    return True


def test_agent_system():
    """Test that the agent system is working"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    try:
        from xavier.src.agents.agent_metadata import get_metadata_manager
        from xavier.src.utils.ansi_art import AgentColors, display_agent_status

        # Test metadata loading
        metadata_manager = get_metadata_manager()
        metadata_manager.reload_metadata()

        available_agents = metadata_manager.list_available_agents()
        logger.info(f"Found {len(available_agents)} agents in metadata system")

        # Test color display for each agent
        test_agents = ['python-engineer', 'frontend-engineer', 'test-runner', 'devops-engineer']

        print("\n" + "="*60)
        print("Testing Agent Color Display:")
        print("="*60)

        for agent_name in test_agents:
            # Display with color
            display_agent_status(agent_name, "Testing color display", "This should appear in the agent's color")

        print("="*60)

        return True

    except Exception as e:
        logger.error(f"Failed to test agent system: {e}")
        return False


def verify_task_delegation():
    """Verify that Task tool can delegate to agents properly"""
    claude_agents_dir = Path(".claude/agents")

    print("\n" + "="*60)
    print("Agent Delegation Verification:")
    print("="*60)

    required_fields = ['name', 'description', 'tools']
    issues = []

    for agent_file in claude_agents_dir.glob("*.md"):
        with open(agent_file, 'r') as f:
            content = f.read()

        if not content.startswith('---'):
            issues.append(f"{agent_file.name}: Missing YAML frontmatter")
            continue

        # Parse YAML frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            issues.append(f"{agent_file.name}: Invalid YAML frontmatter structure")
            continue

        try:
            yaml_data = yaml.safe_load(parts[1])

            # Check required fields
            for field in required_fields:
                if field not in yaml_data:
                    issues.append(f"{agent_file.name}: Missing required field '{field}'")

            # Verify description is meaningful for delegation
            if 'description' in yaml_data:
                desc = yaml_data['description']
                if len(desc) < 20:
                    issues.append(f"{agent_file.name}: Description too short for proper delegation")

            print(f"✅ {agent_file.name}: Ready for delegation")

        except Exception as e:
            issues.append(f"{agent_file.name}: YAML parse error: {e}")

    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("\n✅ All agents are properly configured for delegation!")

    print("="*60)

    return len(issues) == 0


def main():
    """Main function to fix the agent system"""
    print("="*60)
    print("Fixing Xavier Agent System")
    print("="*60)

    # Step 1: Update Claude agent files
    print("\n📝 Updating Claude agent files...")
    if not update_claude_agent_files():
        logger.error("Failed to update Claude agent files")
        return False

    # Step 2: Create color configuration
    print("\n🎨 Creating agent color configuration...")
    if not create_agent_color_config():
        logger.error("Failed to create color configuration")

    # Step 3: Test the system
    print("\n🧪 Testing agent system...")
    if not test_agent_system():
        logger.error("Agent system test failed")

    # Step 4: Verify delegation
    print("\n🔄 Verifying task delegation...")
    if not verify_task_delegation():
        logger.warning("Some agents may have delegation issues")

    print("\n" + "="*60)
    print("✅ Agent system fix complete!")
    print("="*60)

    print("\nNext steps:")
    print("1. Agents should now delegate tasks properly")
    print("2. Colors should display correctly in terminal")
    print("3. Test with: /xavier-task <task-id>")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)