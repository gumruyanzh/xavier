#!/bin/bash

# Xavier Framework Update Script
# Updates existing Xavier installations to the latest version
# Version 1.1.12

set -e
set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD_CYAN='\033[1;36m'
BOLD_WHITE='\033[1;37m'
LIGHT_WHITE='\033[0;97m'
LIGHT_CYAN='\033[0;96m'
NC='\033[0m' # No Color

# Xavier ANSI Art Banner
echo
echo -e "${LIGHT_CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_CYAN}██╗  ██╗ █████╗ ██╗   ██╗██╗███████╗██████╗${NC}                        ${LIGHT_CYAN}║${NC}"
echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_CYAN}╚██╗██╔╝██╔══██╗██║   ██║██║██╔════╝██╔══██╗${NC}                       ${LIGHT_CYAN}║${NC}"
echo -e "${LIGHT_CYAN}║${NC}   ${BOLD_CYAN}╚███╔╝ ███████║╚██╗ ██╔╝██║█████╗  ██████╔╝${NC}                       ${LIGHT_CYAN}║${NC}"
echo -e "${LIGHT_CYAN}║${NC}   ${BOLD_CYAN}██╔██╗ ██╔══██║ ╚████╔╝ ██║██╔══╝  ██╔══██╗${NC}                       ${LIGHT_CYAN}║${NC}"
echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_CYAN}██╔╝ ██╗██║  ██║  ╚██╔╝  ██║███████╗██║  ██║${NC}                       ${LIGHT_CYAN}║${NC}"
echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_CYAN}╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚══════╝╚═╝  ╚═╝${NC}                       ${LIGHT_CYAN}║${NC}"
echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
echo -e "${LIGHT_CYAN}║${NC}              ${BOLD_WHITE}Framework Update Manager${NC}                               ${LIGHT_CYAN}║${NC}"
echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
echo -e "${LIGHT_CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo

# Check if Xavier is installed
if [ ! -d ".xavier" ] || [ ! -f ".xavier/config.json" ]; then
    echo -e "${RED}Error: Xavier Framework not found in this directory${NC}"
    echo "Please run this script from a directory with Xavier installed"
    exit 1
fi

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is required but not found${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Get current version from multiple sources (priority order)
CURRENT_VERSION="1.0.0"  # Default fallback

# 1. Try VERSION file first (most reliable)
if [ -f "VERSION" ]; then
    CURRENT_VERSION=$(cat VERSION 2>/dev/null | tr -d '\n' || echo "1.0.0")
# 2. Try .xavier/config.json as secondary
elif [ -f ".xavier/config.json" ]; then
    CURRENT_VERSION=$(python3 -c "import json; config=json.load(open('.xavier/config.json')); print(config.get('xavier_version', '1.0.0'))" 2>/dev/null || echo "1.0.0")
fi
echo -e "${BLUE}Current Xavier version: ${YELLOW}$CURRENT_VERSION${NC}"

# Fetch latest version from GitHub
echo -e "${BLUE}Checking for updates...${NC}"
LATEST_VERSION=$(curl -s https://raw.githubusercontent.com/gumruyanzh/xavier/main/VERSION || echo "$CURRENT_VERSION")

# Compare versions (with downgrade protection)
if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo -e "${GREEN}✅ Xavier is already up to date (version $LATEST_VERSION)${NC}"
    exit 0
fi

# Check if this would be a downgrade
CURRENT_MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
CURRENT_MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
CURRENT_PATCH=$(echo $CURRENT_VERSION | cut -d. -f3)

LATEST_MAJOR=$(echo $LATEST_VERSION | cut -d. -f1)
LATEST_MINOR=$(echo $LATEST_VERSION | cut -d. -f2)
LATEST_PATCH=$(echo $LATEST_VERSION | cut -d. -f3)

# Simple version comparison (major.minor.patch)
if [ "$LATEST_MAJOR" -lt "$CURRENT_MAJOR" ] || \
   [ "$LATEST_MAJOR" -eq "$CURRENT_MAJOR" -a "$LATEST_MINOR" -lt "$CURRENT_MINOR" ] || \
   [ "$LATEST_MAJOR" -eq "$CURRENT_MAJOR" -a "$LATEST_MINOR" -eq "$CURRENT_MINOR" -a "$LATEST_PATCH" -lt "$CURRENT_PATCH" ]; then
    echo -e "${RED}❌ Cannot downgrade from version $CURRENT_VERSION to $LATEST_VERSION${NC}"
    echo -e "${YELLOW}Your version is newer than the remote version.${NC}"
    echo "This usually means:"
    echo "  • You're using a development version"
    echo "  • The remote repository has an older version"
    echo "  • There's a caching issue"
    echo
    echo -e "${GREEN}No action needed - you're already on a newer version!${NC}"
    exit 0
fi

echo -e "${GREEN}📦 New version available: ${YELLOW}$LATEST_VERSION${NC}"
echo

# Show what's new
echo -e "${BLUE}What's new in version $LATEST_VERSION:${NC}"
echo "• Epic Management: /create-epic, /add-to-epic, /list-epics commands"
echo "• Enhanced Roadmaps: Auto-generation and /add-to-roadmap command"
echo "• JSON-only storage clarification in .xavier/data/"
echo "• Native Claude Code sub-agent integration"
echo "• Bug fixes and performance improvements"
echo

# Ask for confirmation
if [ -t 0 ]; then
    # Interactive mode - ask for confirmation
    read -p "Do you want to update Xavier to version $LATEST_VERSION? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Update cancelled${NC}"
        exit 0
    fi
else
    # Non-interactive mode (piped) - show instructions
    echo
    echo -e "${GREEN}To proceed with the update, run this command directly:${NC}"
    echo
    echo "  cd $(pwd) && \\"
    echo "  curl -sSL https://raw.githubusercontent.com/gumruyanzh/xavier/main/update.sh -o xavier-update.sh && \\"
    echo "  bash xavier-update.sh && rm xavier-update.sh"
    echo
    echo -e "${YELLOW}Or download and run the script manually for interactive mode.${NC}"
    exit 0
fi

# Create backup directory with timestamp
BACKUP_DIR=".xavier/backups/backup_$(date +%Y-%m-%d_%H-%M-%S)"
echo -e "${BLUE}Creating backup at $BACKUP_DIR...${NC}"
mkdir -p "$BACKUP_DIR"

# Backup user data
echo -e "${BLUE}Backing up user data...${NC}"
if [ -d ".xavier/data" ]; then cp -r .xavier/data "$BACKUP_DIR/"; fi
if [ -d ".xavier/stories" ]; then cp -r .xavier/stories "$BACKUP_DIR/"; fi
if [ -d ".xavier/tasks" ]; then cp -r .xavier/tasks "$BACKUP_DIR/"; fi
if [ -d ".xavier/bugs" ]; then cp -r .xavier/bugs "$BACKUP_DIR/"; fi
if [ -d ".xavier/sprints" ]; then cp -r .xavier/sprints "$BACKUP_DIR/"; fi
if [ -f ".xavier/config.json" ]; then cp .xavier/config.json "$BACKUP_DIR/"; fi

echo -e "${GREEN}✅ Backup created successfully${NC}"

# Download latest Xavier
echo -e "${BLUE}Downloading Xavier Framework v$LATEST_VERSION...${NC}"
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone or download Xavier
if command -v git &> /dev/null; then
    git clone https://github.com/gumruyanzh/xavier.git --quiet 2>/dev/null || {
        echo -e "${YELLOW}Failed to clone. Downloading as archive...${NC}"
        curl -L https://github.com/gumruyanzh/xavier/archive/main.tar.gz | tar xz
        mv xavier-main/* .
    }
else
    curl -L https://github.com/gumruyanzh/xavier/archive/main.tar.gz | tar xz
    mv xavier-main/* .
fi

# Return to original directory
cd - > /dev/null

# Find install.sh in either location (git clone vs archive)
INSTALL_SCRIPT=""
if [ -f "$TEMP_DIR/xavier/install.sh" ]; then
    INSTALL_SCRIPT="$TEMP_DIR/xavier/install.sh"
elif [ -f "$TEMP_DIR/install.sh" ]; then
    INSTALL_SCRIPT="$TEMP_DIR/install.sh"
fi

# Update framework files
echo -e "${BLUE}Updating Xavier Framework files...${NC}"

# Update source code
if [ -d "$TEMP_DIR/xavier/src" ]; then
    echo "• Updating framework source code..."
    rm -rf .xavier/src
    cp -r "$TEMP_DIR/xavier/src" .xavier/
else
    echo -e "${YELLOW}Warning: Source code directory not found in update package${NC}"
fi

# Copy new Claude Code agent definitions from repository
echo "• Updating Claude Code agent definitions..."
mkdir -p .claude/agents

# Handle both git clone and archive download structures
if [ -d "$TEMP_DIR/xavier/.claude/agents" ]; then
    cp -r "$TEMP_DIR/xavier/.claude/agents/"*.md .claude/agents/ 2>/dev/null || true
    echo "  - Updated native Claude Code sub-agents"
elif [ -d "$TEMP_DIR/xavier-main/.claude/agents" ]; then
    cp -r "$TEMP_DIR/xavier-main/.claude/agents/"*.md .claude/agents/ 2>/dev/null || true
    echo "  - Updated native Claude Code sub-agents"
else
    echo "  - Warning: Could not find agent files in repository"
fi

# Update Claude commands
if [ -d ".claude/commands" ]; then
    echo "• Updating Claude Code commands..."

    # Create new commands that don't exist
    for cmd in create-project xavier-update estimate-story set-story-points; do
        if [ ! -f ".claude/commands/$cmd.md" ]; then
            echo "  - Adding new command: $cmd"
        fi
    done

    # Extract command files directly from install.sh without running it
    # This avoids any Python execution errors
    mkdir -p /tmp/xavier_commands_extract

    # Extract each command file from install.sh
    commands=(
        "create-story" "create-task" "create-bug" "create-sprint"
        "start-sprint" "show-backlog" "xavier-help" "xavier-update"
        "create-project" "estimate-story" "set-story-points"
    )

    if [ -n "$INSTALL_SCRIPT" ]; then
        for cmd in "${commands[@]}"; do
            # Extract the command content from install.sh
            sed -n "/^cat > .claude\/commands\/$cmd.md << 'EOF'$/,/^EOF$/p" "$INSTALL_SCRIPT" | sed '1d;$d' > "/tmp/xavier_commands_extract/$cmd.md" 2>/dev/null || true
            if [ -s "/tmp/xavier_commands_extract/$cmd.md" ]; then
                cp "/tmp/xavier_commands_extract/$cmd.md" ".claude/commands/$cmd.md" 2>/dev/null || true
                echo "  - Updated command: $cmd"
            fi
        done
    else
        echo -e "${YELLOW}Warning: Could not find install.sh to extract commands${NC}"
    fi

    rm -rf /tmp/xavier_commands_extract
fi

# Update instructions
if [ -f ".claude/instructions.md" ]; then
    echo "• Updating Claude Code instructions..."
    # Extract the instructions from install.sh and update
    if [ -n "$INSTALL_SCRIPT" ]; then
        sed -n '/^cat > .claude\/instructions.md << '\''EOF'\''/,/^EOF$/p' "$INSTALL_SCRIPT" | sed '1d;$d' > .claude/instructions.md
    fi
fi

# Note: Agent files are now updated directly from repository above

# Update version in config
echo "• Updating version information..."
cat > /tmp/update_config.py << EOPYTH
import json
import sys

config_path = '.xavier/config.json'

# Read existing config
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"Warning: Could not read config.json: {e}", file=sys.stderr)
    config = {}

# Update version
config['xavier_version'] = '$LATEST_VERSION'

# Ensure settings exists before adding to it
if 'settings' not in config:
    config['settings'] = {}

# Add any new config options from latest version
if 'auto_update_check' not in config.get('settings', {}):
    if 'settings' not in config:
        config['settings'] = {}
    config['settings']['auto_update_check'] = True

# Write updated config
try:
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Successfully updated config to version $LATEST_VERSION")
except Exception as e:
    print(f"Error writing config: {e}", file=sys.stderr)
    sys.exit(1)
EOPYTH

python3 /tmp/update_config.py || {
    echo -e "${RED}Failed to update version information${NC}"
    echo "Attempting to continue with update..."
}
rm -f /tmp/update_config.py

# Update xavier_bridge.py if it exists
if [ -f ".xavier/xavier_bridge.py" ]; then
    echo "• Updating xavier_bridge.py..."
    if [ -n "$INSTALL_SCRIPT" ]; then
        # Extract xavier_bridge.py from install.sh
        sed -n '/^cat > .xavier\/xavier_bridge.py << '\''EOF'\''/,/^EOF$/p' "$INSTALL_SCRIPT" | sed '1d;$d' > .xavier/xavier_bridge.py
        chmod +x .xavier/xavier_bridge.py
    fi
fi

# Clean up
rm -rf "$TEMP_DIR"

# Show migration notes if needed
if [ "$CURRENT_VERSION" = "1.0.0" ] || [ "$CURRENT_VERSION" = "1.0.1" ]; then
    echo
    echo -e "${YELLOW}Migration Notes:${NC}"
    echo "• New /create-project command available for intelligent project initialization"
    echo "• Commands now have strict boundaries - implementation only starts with /start-sprint"
    echo "• Use /xavier-update to check for future updates"
    echo
fi

# Verify update
echo -e "${BLUE}Verifying update...${NC}"
NEW_VERSION=$(python3 -c "import json; print(json.load(open('.xavier/config.json'))['xavier_version'])" 2>/dev/null)

if [ "$NEW_VERSION" = "$LATEST_VERSION" ]; then
    # Create VERSION file for future updates
    echo -e "${BLUE}Creating VERSION file...${NC}"
    echo "$LATEST_VERSION" > VERSION

    echo
    echo -e "${LIGHT_CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}        ${BOLD_GREEN}✅ XAVIER FRAMEWORK UPDATED SUCCESSFULLY!${NC}                    ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
    echo -e "${LIGHT_CYAN}╠═══════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_WHITE}Update Summary:${NC}                                                    ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    Previous version: ${YELLOW}v$CURRENT_VERSION${NC}                                              ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    Current version:  ${GREEN}v$LATEST_VERSION${NC}                                              ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}                                                                       ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_WHITE}What's New:${NC}                                                        ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    ${GREEN}◆${NC} Intelligent project creation with AI analysis                  ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    ${GREEN}◆${NC} Automatic update system with backup                           ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    ${GREEN}◆${NC} Strict command boundaries (no auto-implementation)            ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    ${GREEN}◆${NC} Enhanced ANSI art and visual feedback                        ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}                                                                       ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_WHITE}Your Data:${NC}                                                         ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    ${GREEN}✓${NC} All stories, tasks, and sprints preserved                     ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    ${GREEN}✓${NC} Backup created at:                                            ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}      ${LIGHT_WHITE}$BACKUP_DIR${NC}     ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}                                                                       ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_WHITE}Next Steps:${NC}                                                        ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    • Try ${CYAN}/create-project${NC} for AI-powered project setup              ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    • Run ${CYAN}/xavier-help${NC} to see all commands                          ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}    • Check changelog at ${LIGHT_CYAN}gumruyan.com/xavier/changelog${NC}              ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
    echo -e "${LIGHT_CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${GREEN}Thank you for using Xavier Framework! 🚀${NC}"
else
    echo -e "${RED}❌ Update verification failed${NC}"
    echo "Please check the installation manually or restore from backup:"
    echo "  cp -r $BACKUP_DIR/* .xavier/"
    exit 1
fi