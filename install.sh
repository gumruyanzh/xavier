#!/bin/bash

# Xavier Framework Installation Script
# Enterprise-Grade SCRUM Development for Claude Code

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
PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.8"

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
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
mkdir -p .xavier/{data,agents,sprints,reports}

# Download Xavier core files
echo -e "${BLUE}Downloading Xavier Framework...${NC}"

# Create temporary directory for Xavier files
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone or download Xavier (replace with actual repository URL when published)
if command -v git &> /dev/null; then
    git clone https://github.com/xavier-framework/xavier.git 2>/dev/null || {
        echo -e "${YELLOW}Using local Xavier installation${NC}"
        cp -r /Users/Toto/Projects/xavier/xavier/* .
    }
else
    echo -e "${YELLOW}Git not found. Downloading as archive...${NC}"
    curl -L https://github.com/xavier-framework/xavier/archive/main.tar.gz | tar xz
    mv xavier-main/* .
fi

# Copy Xavier files to project
cd - > /dev/null
cp -r "$TEMP_DIR/src" .xavier/
cp -r "$TEMP_DIR/templates" .xavier/ 2>/dev/null || true
cp "$TEMP_DIR/xavier.config.json" .xavier/config.json

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

# Create Xavier command wrapper for Claude Code
echo -e "${BLUE}Creating Claude Code integration...${NC}"
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