#!/usr/bin/env python3
"""
Xavier Framework Setup Script
Automatic installation and configuration for enterprise SCRUM development
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, Optional


class XavierSetup:
    """Setup and configuration manager for Xavier Framework"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).absolute()
        self.xavier_path = self.project_path / ".xavier"
        self.config_path = self.xavier_path / "config.json"
        self.is_new_project = not self.project_path.exists() or not any(self.project_path.iterdir())

    def setup(self, mode: str = "auto"):
        """Main setup process"""
        print("\n" + "="*60)
        print("    XAVIER FRAMEWORK SETUP")
        print("    Enterprise-Grade SCRUM Development for Claude Code")
        print("="*60 + "\n")

        if mode == "new":
            self.setup_new_project()
        elif mode == "existing":
            self.setup_existing_project()
        else:
            # Auto-detect
            if self.is_new_project:
                self.setup_new_project()
            else:
                self.setup_existing_project()

    def setup_new_project(self):
        """Setup Xavier for a new project"""
        print("📦 Setting up new Xavier project...")

        # Get project details
        project_name = input("Project name: ").strip()
        project_description = input("Project description: ").strip()

        print("\nSelect primary technology stack:")
        print("1. Python (Django/FastAPI)")
        print("2. TypeScript (React/Vue/Angular)")
        print("3. Go (Gin/Fiber)")
        print("4. Full-Stack (Python + TypeScript)")
        print("5. Custom")

        tech_choice = input("Choice (1-5): ").strip()

        tech_stack = self._get_tech_stack(tech_choice)

        # Create project structure
        self._create_project_structure(project_name)

        # Create Xavier configuration
        config = self._create_config(project_name, project_description, tech_stack)

        # Save configuration
        self._save_config(config)

        # Install dependencies
        self._install_dependencies(tech_stack)

        # Create initial files
        self._create_initial_files(project_name, tech_stack)

        # Initialize git
        self._init_git()

        print(f"\n✅ Xavier project '{project_name}' created successfully!")
        self._print_next_steps()

    def setup_existing_project(self):
        """Setup Xavier for an existing project"""
        print("🔍 Analyzing existing project...")

        # Detect tech stack
        tech_stack = self._detect_tech_stack()

        print(f"\nDetected technologies:")
        for category, items in tech_stack.items():
            if items:
                print(f"  {category}: {', '.join(items)}")

        # Ask for confirmation
        confirm = input("\nProceed with this configuration? (y/n): ").lower()
        if confirm != 'y':
            print("Setup cancelled.")
            return

        # Create Xavier directories
        self._create_xavier_directories()

        # Create configuration
        project_name = self.project_path.name
        config = self._create_config(
            project_name,
            f"Xavier-enabled {project_name} project",
            tech_stack
        )

        # Save configuration
        self._save_config(config)

        # Create Claude Code integration
        self._create_claude_integration()

        print(f"\n✅ Xavier Framework installed in {self.project_path}")
        self._print_next_steps()

    def _create_project_structure(self, project_name: str):
        """Create standard project structure"""
        directories = [
            "src",
            "tests",
            "docs",
            "scripts",
            ".xavier",
            ".xavier/data",
            ".xavier/agents",
            ".xavier/sprints",
            ".xavier/reports"
        ]

        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)

        print(f"  ✓ Created project structure")

    def _create_xavier_directories(self):
        """Create Xavier-specific directories"""
        directories = [
            ".xavier",
            ".xavier/data",
            ".xavier/agents",
            ".xavier/sprints",
            ".xavier/reports"
        ]

        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)

        print(f"  ✓ Created Xavier directories")

    def _get_tech_stack(self, choice: str) -> Dict[str, list]:
        """Get tech stack based on user choice"""
        stacks = {
            "1": {
                "languages": ["python"],
                "frameworks": ["fastapi", "django"],
                "test_frameworks": ["pytest"],
                "build_tools": ["pip", "poetry"]
            },
            "2": {
                "languages": ["typescript", "javascript"],
                "frameworks": ["react", "vue"],
                "test_frameworks": ["jest", "cypress"],
                "build_tools": ["npm", "yarn"]
            },
            "3": {
                "languages": ["go"],
                "frameworks": ["gin", "fiber"],
                "test_frameworks": ["go test"],
                "build_tools": ["go"]
            },
            "4": {
                "languages": ["python", "typescript"],
                "frameworks": ["fastapi", "react"],
                "test_frameworks": ["pytest", "jest"],
                "build_tools": ["pip", "npm"]
            },
            "5": self._get_custom_stack()
        }

        return stacks.get(choice, stacks["1"])

    def _get_custom_stack(self) -> Dict[str, list]:
        """Get custom tech stack from user"""
        print("\nEnter custom tech stack:")
        languages = input("Languages (comma-separated): ").split(",")
        frameworks = input("Frameworks (comma-separated): ").split(",")
        test_frameworks = input("Test frameworks (comma-separated): ").split(",")

        return {
            "languages": [l.strip() for l in languages],
            "frameworks": [f.strip() for f in frameworks],
            "test_frameworks": [t.strip() for t in test_frameworks],
            "build_tools": []
        }

    def _detect_tech_stack(self) -> Dict[str, list]:
        """Detect tech stack from existing project"""
        tech_stack = {
            "languages": [],
            "frameworks": [],
            "test_frameworks": [],
            "build_tools": [],
            "databases": []
        }

        # Check for package.json (Node.js)
        if (self.project_path / "package.json").exists():
            tech_stack["languages"].append("javascript")
            tech_stack["build_tools"].append("npm")

            with open(self.project_path / "package.json") as f:
                package = json.load(f)
                deps = package.get("dependencies", {})

                if "typescript" in deps or "typescript" in package.get("devDependencies", {}):
                    tech_stack["languages"].append("typescript")
                if "react" in deps:
                    tech_stack["frameworks"].append("react")
                if "vue" in deps:
                    tech_stack["frameworks"].append("vue")
                if "jest" in package.get("devDependencies", {}):
                    tech_stack["test_frameworks"].append("jest")

        # Check for requirements.txt or pyproject.toml (Python)
        if (self.project_path / "requirements.txt").exists() or \
           (self.project_path / "pyproject.toml").exists():
            tech_stack["languages"].append("python")
            tech_stack["build_tools"].append("pip")

            if (self.project_path / "requirements.txt").exists():
                with open(self.project_path / "requirements.txt") as f:
                    reqs = f.read().lower()
                    if "django" in reqs:
                        tech_stack["frameworks"].append("django")
                    if "fastapi" in reqs:
                        tech_stack["frameworks"].append("fastapi")
                    if "pytest" in reqs:
                        tech_stack["test_frameworks"].append("pytest")

        # Check for go.mod (Go)
        if (self.project_path / "go.mod").exists():
            tech_stack["languages"].append("go")
            tech_stack["build_tools"].append("go")
            tech_stack["test_frameworks"].append("go test")

        # Check for docker-compose.yml (Databases)
        if (self.project_path / "docker-compose.yml").exists():
            with open(self.project_path / "docker-compose.yml") as f:
                compose = f.read().lower()
                if "postgres" in compose:
                    tech_stack["databases"].append("postgresql")
                if "mysql" in compose:
                    tech_stack["databases"].append("mysql")
                if "mongo" in compose:
                    tech_stack["databases"].append("mongodb")

        return tech_stack

    def _create_config(self, project_name: str, description: str,
                      tech_stack: Dict[str, list]) -> Dict[str, Any]:
        """Create Xavier configuration"""
        config = {
            "name": project_name,
            "description": description,
            "version": "1.0.0",
            "xavier_version": "1.2.2",
            "settings": {
                "strict_mode": True,
                "test_first": True,
                "clean_code_enforcement": True,
                "ioc_patterns": True,
                "sequential_execution": True,
                "test_coverage_required": 100,
                "sprint_velocity": 20,
                "default_sprint_duration": 14
            },
            "tech_stack": tech_stack,
            "agents": self._configure_agents(tech_stack)
        }

        return config

    def _configure_agents(self, tech_stack: Dict[str, list]) -> Dict[str, Dict]:
        """Configure agents based on tech stack"""
        agents = {
            "project_manager": {"enabled": True},
            "context_manager": {"enabled": True},
            "devops": {"enabled": True}
        }

        # Enable language-specific agents
        for lang in tech_stack.get("languages", []):
            if lang.lower() == "python":
                agents["python_engineer"] = {
                    "enabled": True,
                    "frameworks": tech_stack.get("frameworks", [])
                }
            elif lang.lower() == "go":
                agents["golang_engineer"] = {
                    "enabled": True,
                    "frameworks": tech_stack.get("frameworks", [])
                }
            elif lang.lower() in ["typescript", "javascript"]:
                agents["frontend_engineer"] = {
                    "enabled": True,
                    "frameworks": tech_stack.get("frameworks", [])
                }

        return agents

    def _save_config(self, config: Dict[str, Any]):
        """Save Xavier configuration"""
        self.xavier_path.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"  ✓ Created Xavier configuration")

    def _install_dependencies(self, tech_stack: Dict[str, list]):
        """Install required dependencies"""
        print("\n📦 Installing dependencies...")

        # Python dependencies
        if "python" in tech_stack.get("languages", []):
            requirements = [
                "pytest>=7.0.0",
                "pytest-cov>=4.0.0",
                "black>=22.0.0",
                "flake8>=5.0.0",
                "mypy>=0.990"
            ]

            # Add framework-specific deps
            if "django" in tech_stack.get("frameworks", []):
                requirements.append("django>=4.0.0")
            if "fastapi" in tech_stack.get("frameworks", []):
                requirements.extend(["fastapi>=0.80.0", "uvicorn>=0.18.0"])

            # Write requirements
            with open(self.project_path / "requirements.txt", 'w') as f:
                f.write("\n".join(requirements))

            # Install
            try:
                subprocess.run(["pip", "install", "-r", "requirements.txt"],
                             cwd=self.project_path, check=True)
                print("  ✓ Installed Python dependencies")
            except:
                print("  ⚠ Please install Python dependencies manually")

        # Node.js dependencies
        if "typescript" in tech_stack.get("languages", []) or \
           "javascript" in tech_stack.get("languages", []):
            package = {
                "name": self.project_path.name,
                "version": "1.0.0",
                "scripts": {
                    "test": "jest --coverage",
                    "lint": "eslint .",
                    "build": "tsc"
                },
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "jest": "^29.0.0",
                    "@types/jest": "^29.0.0",
                    "eslint": "^8.0.0",
                    "@typescript-eslint/parser": "^5.0.0",
                    "@typescript-eslint/eslint-plugin": "^5.0.0"
                }
            }

            # Add framework-specific deps
            if "react" in tech_stack.get("frameworks", []):
                package["dependencies"] = {"react": "^18.0.0", "react-dom": "^18.0.0"}
            if "vue" in tech_stack.get("frameworks", []):
                package["dependencies"] = {"vue": "^3.0.0"}

            # Write package.json
            with open(self.project_path / "package.json", 'w') as f:
                json.dump(package, f, indent=2)

            # Install
            try:
                subprocess.run(["npm", "install"], cwd=self.project_path, check=True)
                print("  ✓ Installed Node.js dependencies")
            except:
                print("  ⚠ Please install Node.js dependencies manually")

    def _create_initial_files(self, project_name: str, tech_stack: Dict[str, list]):
        """Create initial project files"""
        # Create README
        readme_content = f"""# {project_name}

Xavier-enabled enterprise project with strict SCRUM methodology and 100% test coverage.

## Setup

Xavier Framework is already configured for this project.

## Commands

Use Xavier commands in Claude Code:
- `/create-story` - Create user story
- `/create-task` - Create task
- `/create-sprint` - Create sprint
- `/start-sprint` - Start sprint execution
- `/xavier-help` - Show all commands

## Tech Stack

{json.dumps(tech_stack, indent=2)}

## Development

This project follows:
- Test-First Development (TDD)
- Clean Code principles
- SOLID design patterns
- 100% test coverage requirement
"""

        with open(self.project_path / "README.md", 'w') as f:
            f.write(readme_content)

        # Create .gitignore
        gitignore_content = """# Xavier
.xavier/data/
.xavier/reports/
*.pyc
__pycache__/
node_modules/
dist/
build/
*.log
.coverage
coverage/
.pytest_cache/
"""

        with open(self.project_path / ".gitignore", 'w') as f:
            f.write(gitignore_content)

        print("  ✓ Created initial project files")

    def _create_claude_integration(self):
        """Create Claude Code integration files in .claude directory"""
        claude_path = self.project_path / ".claude"
        claude_path.mkdir(exist_ok=True)
        (claude_path / "agents").mkdir(exist_ok=True)

        # Create main Claude instructions
        instructions_content = """# Xavier Framework Integration

This project uses Xavier Framework for enterprise-grade SCRUM development with Claude Code.

## Framework Rules

Xavier enforces the following strict rules:
1. **Test-First Development (TDD)**: Tests must be written before implementation
2. **100% Test Coverage Required**: No task is complete without full coverage
3. **Sequential Task Execution**: One task at a time, no parallel work
4. **Clean Code Standards**: Functions ≤20 lines, classes ≤200 lines
5. **SOLID Principles**: All code must follow SOLID design patterns
6. **Agent Language Boundaries**: Each agent works only in their assigned language

## Available Commands

### Story Management
- `/create-story` - Create user story with acceptance criteria
- `/create-task` - Create task under a story
- `/create-bug` - Report a bug

### Sprint Management
- `/create-sprint` - Plan a new sprint
- `/start-sprint` - Begin sprint execution
- `/end-sprint` - Complete current sprint

### Reporting
- `/show-backlog` - View prioritized backlog
- `/show-sprint` - Current sprint status
- `/generate-report` - Generate various reports

### Project
- `/learn-project` - Analyze existing codebase
- `/tech-stack-analyze` - Detect technologies
- `/xavier-help` - Show all commands

## Workflow

1. Create stories with `/create-story`
2. Break into tasks with `/create-task`
3. Plan sprint with `/create-sprint`
4. Execute with `/start-sprint` (agents work sequentially)
5. Complete with `/end-sprint`

## Active Agents

Check `.xavier/config.json` for enabled agents. Each agent has strict boundaries:
- Python Engineer: Python only
- Golang Engineer: Go only
- Frontend Engineer: TypeScript/JavaScript only

## Important Notes

- Xavier commands are executed through the framework in `.xavier/`
- All data is stored in `.xavier/data/`
- Sprint information in `.xavier/sprints/`
- Reports generated in `.xavier/reports/`
"""

        with open(claude_path / "instructions.md", 'w') as f:
            f.write(instructions_content)

        # Create command documentation
        commands_content = """# Xavier Commands Reference

All commands use JSON arguments. Examples provided for each command.

## /create-story
Create a user story following SCRUM methodology.

```json
{
  "title": "User Authentication",
  "as_a": "user",
  "i_want": "to log in securely",
  "so_that": "I can access my account",
  "acceptance_criteria": [
    "Email validation",
    "Password strength check",
    "Remember me option"
  ],
  "priority": "High"
}
```

## /create-task
Create a task under an existing story.

```json
{
  "story_id": "US-ABC123",
  "title": "Implement email validation",
  "description": "Add email format validation",
  "technical_details": "Use regex pattern matching",
  "estimated_hours": 4,
  "test_criteria": [
    "Valid emails pass",
    "Invalid emails rejected"
  ],
  "dependencies": []
}
```

## /create-bug
Report a bug with reproduction steps.

```json
{
  "title": "Login fails with special characters",
  "description": "Users cannot log in if password contains @",
  "steps_to_reproduce": [
    "Go to login page",
    "Enter email",
    "Enter password with @",
    "Click login"
  ],
  "expected_behavior": "User logs in successfully",
  "actual_behavior": "Error: Invalid credentials",
  "severity": "High",
  "priority": "High"
}
```

## /create-sprint
Create and plan a sprint.

```json
{
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "duration_days": 14,
  "auto_plan": true
}
```

## /start-sprint
Begin sprint execution with agents.

```json
{
  "sprint_id": "SP-123",
  "strict_mode": true
}
```
"""

        with open(claude_path / "xavier_commands.md", 'w') as f:
            f.write(commands_content)

        # Create agent definitions
        self._create_agent_definitions(claude_path / "agents")

        print("  ✓ Created Claude Code integration in .claude/")

    def _create_agent_definitions(self, agents_path):
        """Create agent definition files for Claude Code"""
        agents = {
            "project_manager.md": """# Project Manager Agent

## Role
Responsible for sprint planning, story point estimation, and task assignment.

## Capabilities
- Estimate story points using Fibonacci scale (1,2,3,5,8,13,21)
- Plan sprints based on velocity and priority
- Assign tasks to appropriate agents
- Track sprint progress

## Restrictions
- Cannot write code
- Cannot modify implementations
- Cannot deploy

## Commands
- Handles `/create-sprint`, `/estimate-story`, `/assign-task`
""",
            "python_engineer.md": """# Python Engineer Agent

## Role
Python backend development with strict language boundaries.

## Capabilities
- Python development ONLY
- Frameworks: Django, FastAPI, Flask
- Testing: pytest with 100% coverage
- Clean Code enforcement

## Restrictions
- CANNOT write JavaScript, TypeScript, Go, or any other language
- CANNOT modify frontend code
- Must write tests before implementation (TDD)
- Must achieve 100% test coverage

## Workflow
1. Write comprehensive tests first
2. Run tests (must fail)
3. Write minimal code to pass
4. Refactor with tests passing
5. Verify 100% coverage
""",
            "golang_engineer.md": """# Golang Engineer Agent

## Role
Go backend development with strict language boundaries.

## Capabilities
- Go development ONLY
- Frameworks: Gin, Fiber, Echo
- Testing: go test with full coverage
- Clean Code enforcement

## Restrictions
- CANNOT write Python, JavaScript, TypeScript, or any other language
- CANNOT modify non-Go code
- Must write tests before implementation (TDD)
- Must achieve 100% test coverage

## Workflow
1. Write comprehensive tests first
2. Run tests (must fail)
3. Write minimal code to pass
4. Refactor with tests passing
5. Verify 100% coverage
""",
            "frontend_engineer.md": """# Frontend Engineer Agent

## Role
Frontend development with TypeScript and modern frameworks.

## Capabilities
- TypeScript/JavaScript ONLY
- Frameworks: React, Vue, Angular
- Testing: Jest, Cypress with full coverage
- Component-based architecture

## Restrictions
- CANNOT write backend code (Python, Go, etc.)
- CANNOT modify API implementations
- Must use TypeScript for type safety
- Must write tests before implementation
- Must achieve 100% test coverage

## Workflow
1. Write component tests first
2. Run tests (must fail)
3. Implement component
4. Refactor with tests passing
5. Verify 100% coverage
""",
            "context_manager.md": """# Context Manager Agent

## Role
Maintains codebase understanding and finds existing implementations.

## Capabilities
- Analyze any language/framework
- Find similar implementations
- Detect patterns and conventions
- Check for code duplication

## Restrictions
- Cannot write new code
- Cannot modify existing code
- Read-only operations only

## Purpose
Ensures no duplicate code is created and existing patterns are followed.
""",
            "devops_engineer.md": """# DevOps Engineer Agent

## Role
CI/CD, deployment, and infrastructure management.

## Capabilities
- Docker and containerization
- CI/CD pipeline configuration
- Infrastructure as Code
- Monitoring and logging setup

## Restrictions
- Cannot modify application logic
- Cannot change business requirements
- Must maintain security best practices

## Workflow
1. Ensure tests pass before deployment
2. Validate 100% coverage
3. Deploy only tested code
""",
            "ui_ux_designer.md": """# UI/UX Designer Agent

## Role
Design systems, user experience, and interface design.

## Capabilities
- Component design specifications
- Accessibility requirements
- User flow documentation
- Design system maintenance

## Restrictions
- Cannot write implementation code
- Provides specifications only
- Must follow accessibility standards

## Output
Design specifications for engineers to implement with TDD.
"""
        }

        for filename, content in agents.items():
            with open(agents_path / filename, 'w') as f:
                f.write(content)

    def _init_git(self):
        """Initialize git repository"""
        try:
            subprocess.run(["git", "init"], cwd=self.project_path, check=True)
            subprocess.run(["git", "add", "."], cwd=self.project_path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit with Xavier Framework"],
                cwd=self.project_path,
                check=True
            )
            print("  ✓ Initialized git repository")
        except:
            print("  ⚠ Please initialize git manually")

    def _print_next_steps(self):
        """Print next steps for user"""
        print("\n" + "="*60)
        print("  NEXT STEPS")
        print("="*60)
        print("\n1. Open this project in Claude Code")
        print("2. Run `/xavier-help` to see available commands")
        print("3. Run `/create-story` to create your first user story")
        print("4. Run `/create-sprint` to plan your first sprint")
        print("5. Run `/start-sprint` to begin development")
        print("\nXavier enforces:")
        print("  • Test-first development (TDD)")
        print("  • 100% test coverage")
        print("  • Clean Code principles")
        print("  • Sequential task execution")
        print("  • Strict SCRUM methodology")
        print("\nEnjoy enterprise-grade development with Xavier! 🚀\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Xavier Framework Setup - Enterprise SCRUM Development for Claude Code"
    )

    parser.add_argument(
        "command",
        choices=["init", "new", "existing"],
        help="Setup command: init (auto-detect), new (new project), existing (existing project)"
    )

    parser.add_argument(
        "--path",
        default=".",
        help="Project path (default: current directory)"
    )

    args = parser.parse_args()

    setup = XavierSetup(args.path)

    if args.command == "init":
        setup.setup("auto")
    elif args.command == "new":
        setup.setup("new")
    elif args.command == "existing":
        setup.setup("existing")


if __name__ == "__main__":
    main()