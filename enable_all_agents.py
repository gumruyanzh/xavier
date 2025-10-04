#!/usr/bin/env python3
"""
Enable ALL Xavier Agents for Claude Code Delegation
This script ensures all custom agents work with Claude's automatic delegation system
"""

import os
import yaml
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Complete agent configuration with explicit delegation triggers
AGENT_CONFIGS = {
    "python-engineer": {
        "name": "python-engineer",
        "description": "Use for: Python code, Django, Flask, FastAPI, APIs, backend services, pytest, unittest. Automatically handles all Python development tasks.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["python", "django", "flask", "fastapi", "pytest", "py", "api", "backend"]
    },
    "frontend-engineer": {
        "name": "frontend-engineer",
        "description": "Use for: React, TypeScript, JavaScript, Vue, Angular, HTML, CSS, frontend, UI/UX, web components. Handles all frontend development.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["react", "typescript", "javascript", "frontend", "ui", "vue", "angular", "css", "html"]
    },
    "golang-engineer": {
        "name": "golang-engineer",
        "description": "Use for: Go, Golang, Gin, microservices, concurrent programming, goroutines. Expert in Go development.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["go", "golang", "gin", "microservice", "goroutine"]
    },
    "devops-engineer": {
        "name": "devops-engineer",
        "description": "Use for: Docker, Kubernetes, CI/CD, Jenkins, GitHub Actions, Terraform, Ansible, infrastructure, deployment, containers.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["docker", "kubernetes", "k8s", "cicd", "jenkins", "terraform", "ansible", "deployment", "container"]
    },
    "test-runner": {
        "name": "test-runner",
        "description": "Use for: Running tests, test coverage, unit tests, integration tests, e2e tests, test automation, TDD.",
        "tools": "Read, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["test", "testing", "coverage", "tdd", "unit test", "integration test", "e2e"]
    },
    "java-engineer": {
        "name": "java-engineer",
        "description": "Use for: Java, Spring, SpringBoot, Maven, Gradle, JUnit, enterprise applications.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["java", "spring", "springboot", "maven", "gradle", "junit"]
    },
    "ruby-engineer": {
        "name": "ruby-engineer",
        "description": "Use for: Ruby, Rails, RSpec, Bundler, web applications with Ruby on Rails.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["ruby", "rails", "rspec", "bundler", "gem"]
    },
    "rust-engineer": {
        "name": "rust-engineer",
        "description": "Use for: Rust, Cargo, systems programming, memory-safe code, Actix, Tokio.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["rust", "cargo", "actix", "tokio", "memory safe"]
    },
    "swift-engineer": {
        "name": "swift-engineer",
        "description": "Use for: Swift, iOS, SwiftUI, UIKit, Xcode, iPhone, iPad, macOS app development.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["swift", "ios", "swiftui", "xcode", "iphone", "ipad", "macos"]
    },
    "kotlin-engineer": {
        "name": "kotlin-engineer",
        "description": "Use for: Kotlin, Android, Jetpack Compose, mobile app development for Android.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["kotlin", "android", "jetpack", "compose", "mobile"]
    },
    "elixir-engineer": {
        "name": "elixir-engineer",
        "description": "Use for: Elixir, Phoenix, Ecto, OTP, concurrent and fault-tolerant systems.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["elixir", "phoenix", "ecto", "otp", "erlang"]
    },
    "r-engineer": {
        "name": "r-engineer",
        "description": "Use for: R programming, statistical analysis, data science, ggplot2, tidyverse, Shiny.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["r", "statistics", "ggplot", "tidyverse", "shiny", "data analysis"]
    },
    "haskell-engineer": {
        "name": "haskell-engineer",
        "description": "Use for: Haskell, functional programming, pure functions, monads, type theory.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["haskell", "functional", "monad", "pure function"]
    },
    "project-manager": {
        "name": "project-manager",
        "description": "Use for: Sprint planning, task management, story creation, backlog management, SCRUM, agile.",
        "tools": "Read, Write, Edit, Bash",
        "model": "opus",
        "trigger_words": ["sprint", "story", "task", "backlog", "scrum", "agile", "planning"]
    },
    "context-manager": {
        "name": "context-manager",
        "description": "Use for: Codebase analysis, architecture understanding, documentation review, code exploration.",
        "tools": "Read, Grep, Glob",
        "model": "sonnet",
        "trigger_words": ["analyze", "understand", "explore", "architecture", "codebase", "context"]
    },
    "orchestrator": {
        "name": "orchestrator",
        "description": "Internal use: Coordinates multiple agents, delegates tasks, manages workflow.",
        "tools": "Read, Write, Edit, Bash, Grep, Glob",
        "model": "opus",
        "trigger_words": ["orchestrate", "coordinate", "delegate", "workflow"]
    }
}


def update_agent_file(agent_name: str, config: dict) -> bool:
    """Update a single agent file with enhanced configuration"""
    claude_agents_dir = Path(".claude/agents")
    agent_file = claude_agents_dir / f"{agent_name}.md"

    if not agent_file.exists():
        logger.warning(f"Agent file not found: {agent_file}")
        return False

    # Read existing content
    with open(agent_file, 'r') as f:
        content = f.read()

    # Parse existing content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            body = parts[2]
        else:
            body = content
    else:
        body = content

    # Create enhanced YAML frontmatter
    yaml_content = {
        'name': config['name'],
        'description': config['description'],
        'tools': config['tools']
    }

    if 'model' in config:
        yaml_content['model'] = config['model']

    # Get enhanced body based on agent type
    enhanced_body = get_enhanced_agent_prompt(agent_name, config)

    # Construct new content
    new_content = "---\n"
    new_content += yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)
    new_content += "---\n\n"
    new_content += enhanced_body

    # Write updated content
    with open(agent_file, 'w') as f:
        f.write(new_content)

    logger.info(f"✅ Updated {agent_name}")
    return True


def get_enhanced_agent_prompt(agent_name: str, config: dict) -> str:
    """Generate an enhanced system prompt for the agent"""
    trigger_words = config.get('trigger_words', [])

    prompt = f"""# {agent_name.replace('-', ' ').title()}

You are a specialized {agent_name.replace('-', ' ')} for the Xavier Framework.

## Activation Triggers
This agent is automatically activated when tasks involve:
{', '.join(trigger_words)}

## Core Responsibilities
{config['description']}

## Expertise Areas
"""

    # Add specific expertise based on agent type
    if agent_name == "python-engineer":
        prompt += """
- Python 3.x development with best practices
- API development (REST, GraphQL)
- Django, Flask, FastAPI frameworks
- Testing with pytest, unittest
- Package management with pip, poetry
- Async programming with asyncio
- Database integration (SQLAlchemy, Django ORM)
"""
    elif agent_name == "frontend-engineer":
        prompt += """
- React, Vue, Angular frameworks
- TypeScript and modern JavaScript
- State management (Redux, MobX, Vuex)
- CSS, SCSS, styled-components
- Webpack, Vite, build tools
- Testing with Jest, React Testing Library
- Responsive design and accessibility
"""
    elif agent_name == "devops-engineer":
        prompt += """
- Docker containerization
- Kubernetes orchestration
- CI/CD pipelines (Jenkins, GitHub Actions, GitLab CI)
- Infrastructure as Code (Terraform, Ansible)
- Cloud platforms (AWS, GCP, Azure)
- Monitoring and logging
- Security best practices
"""
    elif agent_name == "test-runner":
        prompt += """
- Test-Driven Development (TDD)
- Unit, integration, and e2e testing
- Test coverage analysis
- Performance testing
- Security testing
- Test automation frameworks
- Continuous testing in CI/CD
"""

    prompt += """
## Working Principles
1. Follow Test-Driven Development (TDD)
2. Maintain 100% test coverage where possible
3. Write clean, maintainable code
4. Follow language-specific best practices
5. Document code thoroughly

## Communication Style
When activated, I will:
1. Clearly identify myself and my role
2. Explain my approach before starting
3. Provide updates on progress
4. Highlight any issues or blockers
5. Confirm completion with summary

Remember: I am automatically invoked when Claude detects tasks matching my expertise area.
"""

    return prompt


def create_delegation_helper():
    """Create a helper script for testing delegation"""
    helper_content = '''#!/usr/bin/env python3
"""
Xavier Agent Delegation Helper
Tests that all agents are properly configured for automatic delegation
"""

def test_agent_delegation(task_description: str):
    """
    Test which agent would handle a given task

    Instead of using Task tool, describe the task and let Claude
    automatically delegate to the appropriate agent.
    """
    print(f"Task: {task_description}")
    print("Claude should automatically delegate to the appropriate agent.")
    print("The agent will be chosen based on the task description.")

# Example usage:
# Instead of: Task(subagent_type="devops-engineer", ...)
# Use: "I need help setting up Docker containers for the application"
# Claude will automatically use the devops-engineer

tasks = {
    "python-engineer": "Create a REST API endpoint using FastAPI",
    "frontend-engineer": "Build a React component with TypeScript",
    "devops-engineer": "Set up Docker containers and Kubernetes deployment",
    "test-runner": "Run the test suite and check coverage",
    "golang-engineer": "Create a Go microservice with Gin",
    "java-engineer": "Implement a Spring Boot application",
    "ruby-engineer": "Create a Rails controller",
    "rust-engineer": "Write a memory-safe Rust function",
    "swift-engineer": "Build an iOS app with SwiftUI",
    "kotlin-engineer": "Create an Android app with Jetpack Compose",
}

print("Example delegation triggers:")
print("-" * 60)
for agent, task in tasks.items():
    print(f"{agent:20} → {task}")
'''

    with open("test_delegation.py", "w") as f:
        f.write(helper_content)

    logger.info("Created test_delegation.py helper")


def main():
    """Main function to enable all agents"""
    print("="*70)
    print("Enabling ALL Xavier Agents for Claude Code")
    print("="*70)

    # Update all agent files
    success_count = 0
    for agent_name, config in AGENT_CONFIGS.items():
        if update_agent_file(agent_name, config):
            success_count += 1

    print(f"\n✅ Updated {success_count}/{len(AGENT_CONFIGS)} agents")

    # Create helper script
    create_delegation_helper()

    print("\n" + "="*70)
    print("🎯 All Agents Now Enabled!")
    print("="*70)

    print("\n📝 How to use agents WITHOUT Task tool:")
    print("-" * 70)
    print("Instead of using Task tool with subagent_type, simply describe")
    print("what you need and Claude will automatically delegate:")
    print()
    print("Examples:")
    print('  ❌ OLD: Task(subagent_type="devops-engineer", ...)')
    print('  ✅ NEW: "Set up Docker containers for the application"')
    print()
    print('  ❌ OLD: Task(subagent_type="ruby-engineer", ...)')
    print('  ✅ NEW: "Create a Rails controller for user management"')
    print()
    print("Claude will automatically detect the task type and delegate")
    print("to the appropriate specialized agent.")
    print("="*70)


if __name__ == "__main__":
    main()