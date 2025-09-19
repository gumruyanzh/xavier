#!/bin/bash

# Xavier Framework Installation Script
# Enterprise-Grade SCRUM Development for Claude Code
# Version 1.0.1 - macOS compatible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Xavier banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  XAVIER FRAMEWORK                         ║"
echo "║     Enterprise SCRUM Development for Claude Code          ║"
echo "╔══════════════════════════════════════════════════════════╗"
echo -e "${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | sed 's/Python //' | cut -d. -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo -e "${GREEN}Python $PYTHON_VERSION detected${NC}"
else
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Detect installation mode
if [ "$1" == "new" ]; then
    MODE="new"
    echo -e "${GREEN}Creating new Xavier project...${NC}"
elif [ "$1" == "existing" ]; then
    MODE="existing"
    echo -e "${GREEN}Installing Xavier in existing project...${NC}"
else
    # Auto-detect
    if [ -z "$(ls -A)" ] || [ ! -f "package.json" ] && [ ! -f "requirements.txt" ] && [ ! -f "go.mod" ]; then
        MODE="new"
        echo -e "${YELLOW}Detected: Empty or new directory${NC}"
        echo -e "${GREEN}Creating new Xavier project...${NC}"
    else
        MODE="existing"
        echo -e "${YELLOW}Detected: Existing project${NC}"
        echo -e "${GREEN}Installing Xavier in existing project...${NC}"
    fi
fi

# Create Xavier directory
echo -e "${BLUE}Setting up Xavier directories...${NC}"
mkdir -p .xavier/{data,sprints,reports}

# Create Claude Code integration directory
echo -e "${BLUE}Setting up Claude Code integration...${NC}"
mkdir -p .claude/agents

# Download Xavier core files
echo -e "${BLUE}Downloading Xavier Framework...${NC}"

# Create temporary directory for Xavier files
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone or download Xavier
if command -v git &> /dev/null; then
    git clone https://github.com/gumruyanzh/xavier.git 2>/dev/null || {
        echo -e "${YELLOW}Failed to clone. Downloading as archive...${NC}"
        curl -L https://github.com/gumruyanzh/xavier/archive/main.tar.gz | tar xz
        mv xavier-main/* .
    }
else
    echo -e "${YELLOW}Git not found. Downloading as archive...${NC}"
    curl -L https://github.com/gumruyanzh/xavier/archive/main.tar.gz | tar xz
    mv xavier-main/* .
fi

# Copy Xavier files to project
cd - > /dev/null

# Handle both cloned and extracted archive structures
if [ -d "$TEMP_DIR/xavier/xavier/src" ]; then
    # Cloned structure: xavier/xavier/src
    cp -r "$TEMP_DIR/xavier/xavier/src" .xavier/
    cp "$TEMP_DIR/xavier/xavier/xavier.config.json" .xavier/config.json 2>/dev/null || true
elif [ -d "$TEMP_DIR/xavier/src" ]; then
    # Archive structure: xavier/src
    cp -r "$TEMP_DIR/xavier/src" .xavier/
    cp "$TEMP_DIR/xavier/xavier.config.json" .xavier/config.json 2>/dev/null || true
else
    echo -e "${YELLOW}Warning: Xavier source files not found in expected location${NC}"
    # Try to find src directory
    find "$TEMP_DIR" -name "src" -type d | head -1 | xargs -I {} cp -r {} .xavier/
    find "$TEMP_DIR" -name "xavier.config.json" -type f | head -1 | xargs -I {} cp {} .xavier/config.json
fi

# Clean up
rm -rf "$TEMP_DIR"

# Run Python setup
echo -e "${BLUE}Running Xavier setup...${NC}"
cat > .xavier/setup_temp.py << 'EOF'
import os
import sys
import json
from pathlib import Path

# Add Xavier to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Xavier setup
from src.core.xavier_engine import XavierEngine
from src.commands.xavier_commands import XavierCommands

# Initialize Xavier
print("Initializing Xavier Framework...")

# Create default configuration
config = {
    "name": Path.cwd().name,
    "version": "1.0.0",
    "xavier_version": "1.0.0",
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
    "agents": {
        "project_manager": {"enabled": True},
        "context_manager": {"enabled": True},
        "python_engineer": {"enabled": True},
        "golang_engineer": {"enabled": True},
        "frontend_engineer": {"enabled": True},
        "devops": {"enabled": True}
    }
}

# Save configuration
with open(".xavier/config.json", "w") as f:
    json.dump(config, f, indent=2)

print("✅ Xavier Framework installed successfully!")
EOF

python3 .xavier/setup_temp.py
rm .xavier/setup_temp.py

# Create Claude Code integration files
echo -e "${BLUE}Creating Claude Code integration...${NC}"

# Create commands directory
mkdir -p .claude/commands

# Create main Claude instructions
cat > .claude/instructions.md << 'EOF'
# Xavier Framework Integration

This project uses Xavier Framework for enterprise-grade SCRUM development with Claude Code.

## Custom Commands

Xavier provides the following commands:

- `/create-story` - Create a user story with acceptance criteria
- `/create-task` - Create a task under a story
- `/create-bug` - Report a bug with reproduction steps
- `/create-sprint` - Plan a new sprint
- `/start-sprint` - Begin sprint execution
- `/show-backlog` - View prioritized backlog
- `/xavier-help` - Show all available commands

Type any command to get started. Commands are implemented through the Xavier Framework in `.xavier/`.

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
EOF

# Create Xavier command documentation
cat > .claude/xavier_commands.md << 'EOF'
# Xavier Commands Reference

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

## Test-First Enforcement

Xavier enforces that tests are written BEFORE implementation. The workflow is:
1. Agent writes comprehensive tests
2. Tests must fail initially (Red)
3. Agent implements minimal code to pass (Green)
4. Agent refactors while keeping tests passing
5. 100% coverage verified before task completion
EOF

# Create agent definitions based on detected tech stack
echo -e "${BLUE}Creating agent definitions...${NC}"

# Project Manager Agent
cat > .claude/agents/project_manager.md << 'EOF'
# Project Manager Agent

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
EOF

# Python Engineer Agent
cat > .claude/agents/python_engineer.md << 'EOF'
# Python Engineer Agent

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
EOF

# Golang Engineer Agent
cat > .claude/agents/golang_engineer.md << 'EOF'
# Golang Engineer Agent

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
EOF

# Frontend Engineer Agent
cat > .claude/agents/frontend_engineer.md << 'EOF'
# Frontend Engineer Agent

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
EOF

# Create individual command definition files
echo -e "${BLUE}Creating command definitions...${NC}"

# create-story command
cat > .claude/commands/create-story.md << 'EOF'
# create-story

Create a user story following SCRUM methodology with acceptance criteria.

## Usage

Type `/create-story` to create a new user story.

## Parameters

- **title**: Story title (required)
- **as_a**: User role (required)
- **i_want**: Feature description (required)
- **so_that**: Business value (required)
- **acceptance_criteria**: List of acceptance criteria (required)
- **priority**: Priority level - Critical/High/Medium/Low (optional, default: Medium)
- **epic_id**: Parent epic ID (optional)

## Example

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

## Implementation

This command uses the Xavier Framework to create a user story with automatic story point estimation by the Project Manager agent.
EOF

# create-task command
cat > .claude/commands/create-task.md << 'EOF'
# create-task

Create a task under an existing user story.

## Usage

Type `/create-task` to create a new task.

## Parameters

- **story_id**: Parent story ID (required)
- **title**: Task title (required)
- **description**: Task description (required)
- **technical_details**: Implementation details (required)
- **estimated_hours**: Hour estimate (optional, default: 4)
- **test_criteria**: List of test requirements (required)
- **priority**: Priority level - Critical/High/Medium/Low (optional, default: Medium)
- **dependencies**: List of dependency task IDs (optional)

## Implementation

Tasks are automatically assigned to the appropriate agent based on tech stack. Test-first development is enforced.
EOF

# create-bug command
cat > .claude/commands/create-bug.md << 'EOF'
# create-bug

Report a bug with detailed reproduction steps.

## Usage

Type `/create-bug` to report a bug.

## Parameters

- **title**: Bug title (required)
- **description**: Bug description (required)
- **steps_to_reproduce**: List of reproduction steps (required)
- **expected_behavior**: What should happen (required)
- **actual_behavior**: What actually happens (required)
- **severity**: Severity level - Critical/High/Medium/Low (required)
- **priority**: Priority level - Critical/High/Medium/Low (optional, default: High)

## Implementation

Bugs are automatically prioritized and assigned story points based on severity.
EOF

# create-sprint command
cat > .claude/commands/create-sprint.md << 'EOF'
# create-sprint

Plan a new sprint with automatic work item selection.

## Usage

Type `/create-sprint` to create a new sprint.

## Parameters

- **name**: Sprint name (required)
- **goal**: Sprint goal (required)
- **duration_days**: Sprint length in days (optional, default: 14)
- **auto_plan**: Automatically select items by priority (optional, default: true)

## Implementation

Xavier automatically calculates velocity, selects items, and prepares the sprint.
EOF

# start-sprint command
cat > .claude/commands/start-sprint.md << 'EOF'
# start-sprint

Begin sprint execution with strict sequential task processing.

## Usage

Type `/start-sprint` to begin sprint execution.

## Parameters

- **sprint_id**: Sprint ID to start (optional, uses latest planned sprint if not provided)
- **strict_mode**: Enable strict sequential execution (optional, default: true)

## Implementation

Xavier enforces sequential execution, test-first development, and 100% coverage.
EOF

# show-backlog command
cat > .claude/commands/show-backlog.md << 'EOF'
# show-backlog

Display prioritized product backlog.

## Usage

Type `/show-backlog` to view the backlog.

## Output

Shows total stories, tasks, bugs, story points, and top priority items.
EOF

# xavier-help command
cat > .claude/commands/xavier-help.md << 'EOF'
# xavier-help

Show all available Xavier commands and their usage.

## Usage

Type `/xavier-help` to see all commands.

## Output

Displays all available Xavier commands with descriptions and examples.
EOF

# Context Manager Agent
cat > .claude/agents/context_manager.md << 'EOF'
# Context Manager Agent

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
EOF

# Create Xavier bridge for Claude commands
cat > .xavier/xavier_bridge.py << 'EOF'
#!/usr/bin/env python3
"""Xavier Bridge - Command handler for Claude Code integration"""

import sys
import json
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.commands.xavier_commands import XavierCommands
except ImportError:
    print("Error: Xavier Framework not properly installed")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: xavier_bridge.py <command> [arguments]")
        sys.exit(1)

    command = sys.argv[1]
    args = {}

    if len(sys.argv) > 2:
        try:
            args = json.loads(' '.join(sys.argv[2:]))
        except:
            pass

    # Map commands
    command_map = {
        'create-story': '/create-story',
        'create-task': '/create-task',
        'create-bug': '/create-bug',
        'create-sprint': '/create-sprint',
        'start-sprint': '/start-sprint',
        'show-backlog': '/show-backlog',
        'xavier-help': '/xavier-help'
    }

    xavier_command = command_map.get(command.replace('/', ''), f"/{command}")

    try:
        xavier = XavierCommands(os.getcwd())
        result = xavier.execute(xavier_command, args)

        if result.get('success'):
            if 'result' in result:
                print(json.dumps(result['result'], indent=2))
            else:
                print("✅ Command executed successfully")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
EOF

chmod +x .xavier/xavier_bridge.py

# Create Xavier command wrapper
echo -e "${BLUE}Creating Xavier CLI wrapper...${NC}"
cat > xavier << 'EOF'
#!/usr/bin/env python3
"""Xavier Framework CLI for Claude Code"""

import sys
import json
from pathlib import Path

# Add Xavier to path
sys.path.insert(0, str(Path(__file__).parent / ".xavier"))

from src.commands.xavier_commands import XavierCommands

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: xavier <command> [args]")
        print("Run 'xavier help' for available commands")
        sys.exit(1)

    command = sys.argv[1]
    args = {}

    if len(sys.argv) > 2:
        # Parse JSON arguments if provided
        try:
            args = json.loads(sys.argv[2])
        except:
            args = {"input": " ".join(sys.argv[2:])}

    # Initialize Xavier commands
    xavier = XavierCommands()

    # Map command shortcuts
    command_map = {
        "help": "/xavier-help",
        "story": "/create-story",
        "task": "/create-task",
        "bug": "/create-bug",
        "sprint": "/create-sprint",
        "start": "/start-sprint",
        "backlog": "/show-backlog"
    }

    # Get full command
    full_command = command_map.get(command, f"/{command}")

    # Execute command
    result = xavier.execute(full_command, args)

    # Print result
    print(json.dumps(result, indent=2))
EOF

chmod +x xavier

# Create documentation
echo -e "${BLUE}Creating documentation...${NC}"
cat > XAVIER.md << 'EOF'
# Xavier Framework

This project is configured with Xavier Framework for enterprise SCRUM development.

## Quick Start

### Create a user story
```bash
./xavier story '{"title": "User Login", "as_a": "user", "i_want": "to log in", "so_that": "I can access my account", "acceptance_criteria": ["Email validation", "Password check"], "priority": "High"}'
```

### Create a sprint
```bash
./xavier sprint '{"name": "Sprint 1", "goal": "Complete authentication"}'
```

### Start sprint
```bash
./xavier start
```

## Claude Code Commands

All commands are available as slash commands in Claude Code:
- `/create-story`
- `/create-task`
- `/create-bug`
- `/create-sprint`
- `/start-sprint`
- `/show-backlog`
- `/xavier-help`

## Configuration

Edit `.xavier/config.json` to customize settings.

## Requirements

- Test-first development (100% coverage required)
- Clean Code principles enforced
- SOLID design patterns
- Sequential task execution
- Strict SCRUM methodology

## Support

Visit https://xavier-framework.dev for documentation.
EOF

# Final setup based on mode
if [ "$MODE" == "new" ]; then
    # Initialize git
    if ! [ -d .git ]; then
        git init
        git add .
        git commit -m "Initial commit with Xavier Framework"
    fi
fi

# Success message
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           XAVIER FRAMEWORK INSTALLED!                     ║"
echo "╔══════════════════════════════════════════════════════════╗"
echo -e "${NC}"
echo ""
echo "Next steps:"
echo "1. Open this project in Claude Code"
echo "2. Use Xavier commands:"
echo "   - /create-story    (Create user story)"
echo "   - /create-sprint   (Create sprint)"
echo "   - /start-sprint    (Begin development)"
echo "   - /xavier-help     (Show all commands)"
echo ""
echo "Or use the CLI:"
echo "   ./xavier help"
echo ""
echo -e "${BLUE}Xavier enforces:${NC}"
echo "  ✓ Test-first development (TDD)"
echo "  ✓ 100% test coverage"
echo "  ✓ Clean Code principles"
echo "  ✓ SOLID design patterns"
echo "  ✓ Sequential execution"
echo ""
echo -e "${GREEN}Happy coding with Xavier! 🚀${NC}"