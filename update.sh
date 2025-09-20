#!/bin/bash
set -o pipefail

# Xavier Framework Update Script
# Updates existing Xavier installations to the latest version
# Version 1.0.2

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
echo "║                  XAVIER FRAMEWORK UPDATER                 ║"
echo "║            Updating to the Latest Version                 ║"
echo "╔══════════════════════════════════════════════════════════╗"
echo -e "${NC}"

# Check if Xavier is installed
if [ ! -d ".xavier" ] || [ ! -f ".xavier/config.json" ]; then
    echo -e "${RED}Error: Xavier Framework not found in this directory${NC}"
    echo "Please run this script from a directory with Xavier installed"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('.xavier/config.json'))['xavier_version'])" 2>/dev/null || echo "1.0.0")
echo -e "${BLUE}Current Xavier version: ${YELLOW}$CURRENT_VERSION${NC}"

# Fetch latest version from GitHub
echo -e "${BLUE}Checking for updates...${NC}"
LATEST_VERSION=$(curl -s https://raw.githubusercontent.com/gumruyanzh/xavier/main/VERSION || echo "1.0.2")

# Compare versions
if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo -e "${GREEN}✅ Xavier is already up to date (version $LATEST_VERSION)${NC}"
    exit 0
fi

echo -e "${GREEN}📦 New version available: ${YELLOW}$LATEST_VERSION${NC}"
echo

# Show what's new
echo -e "${BLUE}What's new in version $LATEST_VERSION:${NC}"
echo "• Intelligent /create-project command with AI-powered analysis"
echo "• Strict command boundaries (no auto-implementation)"
echo "• Enhanced project templates and tech stack detection"
echo "• Improved command documentation and examples"
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

# Update framework files
echo -e "${BLUE}Updating Xavier Framework files...${NC}"

# Update source code
if [ -d "$TEMP_DIR/xavier/xavier/src" ]; then
    echo "• Updating framework source code..."
    rm -rf .xavier/src
    cp -r "$TEMP_DIR/xavier/xavier/src" .xavier/
elif [ -d "$TEMP_DIR/xavier/src" ]; then
    echo "• Updating framework source code..."
    rm -rf .xavier/src
    cp -r "$TEMP_DIR/xavier/src" .xavier/
fi

# Update Claude commands
if [ -d ".claude/commands" ]; then
    echo "• Updating Claude Code commands..."

    # Create new commands that don't exist
    for cmd in create-project xavier-update; do
        if [ ! -f ".claude/commands/$cmd.md" ]; then
            echo "  - Adding new command: $cmd"
        fi
    done

    # Update all command files from the new installation script
    temp_install_dir=$(mktemp -d)
    cd "$temp_install_dir"
    bash "$TEMP_DIR/xavier/install.sh" > /dev/null 2>&1 || true
    cd - > /dev/null

    if [ -d "$temp_install_dir/.claude/commands" ]; then
        cp -r "$temp_install_dir/.claude/commands/"* .claude/commands/ 2>/dev/null || true
    fi
    rm -rf "$temp_install_dir"
fi

# Update instructions
if [ -f ".claude/instructions.md" ]; then
    echo "• Updating Claude Code instructions..."
    # Extract the instructions from install.sh and update
    sed -n '/^cat > .claude\/instructions.md << '\''EOF'\''/,/^EOF$/p' "$TEMP_DIR/xavier/install.sh" | sed '1d;$d' > .claude/instructions.md
fi

# Update agents
if [ -d ".claude/agents" ]; then
    echo "• Updating agent definitions..."
    # Extract agent files from install.sh
    temp_install_dir=$(mktemp -d)
    cd "$temp_install_dir"
    bash "$TEMP_DIR/xavier/install.sh" > /dev/null 2>&1 || true
    cd - > /dev/null

    if [ -d "$temp_install_dir/.claude/agents" ]; then
        cp -r "$temp_install_dir/.claude/agents/"* .claude/agents/ 2>/dev/null || true
    fi
    rm -rf "$temp_install_dir"
fi

# Update version in config
echo "• Updating version information..."
python3 << EOF
import json
config_path = '.xavier/config.json'
with open(config_path, 'r') as f:
    config = json.load(f)
config['xavier_version'] = '$LATEST_VERSION'
# Add any new config options from latest version
if 'auto_update_check' not in config.get('settings', {}):
    config['settings']['auto_update_check'] = True
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
EOF

# Update xavier_bridge.py if it exists
if [ -f ".xavier/xavier_bridge.py" ]; then
    echo "• Updating xavier_bridge.py..."
    if [ -f "$TEMP_DIR/xavier/install.sh" ]; then
        # Extract xavier_bridge.py from install.sh
        sed -n '/^cat > .xavier\/xavier_bridge.py << '\''EOF'\''/,/^EOF$/p' "$TEMP_DIR/xavier/install.sh" | sed '1d;$d' > .xavier/xavier_bridge.py
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
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          ✅ XAVIER FRAMEWORK UPDATED SUCCESSFULLY!        ║"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo -e "${NC}"
    echo
    echo -e "${GREEN}Updated from version $CURRENT_VERSION to $LATEST_VERSION${NC}"
    echo
    echo "Your data has been preserved and backed up at:"
    echo "  $BACKUP_DIR"
    echo
    echo "What's next:"
    echo "• Use /xavier-help to see all available commands"
    echo "• Try /create-project for intelligent project setup"
    echo "• Your existing stories, tasks, and sprints are intact"
    echo
    echo -e "${BLUE}Thank you for using Xavier Framework!${NC}"
else
    echo -e "${RED}❌ Update verification failed${NC}"
    echo "Please check the installation manually or restore from backup:"
    echo "  cp -r $BACKUP_DIR/* .xavier/"
    exit 1
fi