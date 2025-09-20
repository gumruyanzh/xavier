#!/bin/bash

# Xavier Framework Command Fix Script
# Fixes missing estimate-story and set-story-points commands for v1.1.2
# This is for users who updated but didn't get the new commands

set -e
set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Xavier Framework Command Fix${NC}"
echo -e "${BLUE}==============================${NC}"
echo

# Check if Xavier is installed
if [ ! -d ".xavier" ] || [ ! -f ".xavier/config.json" ]; then
    echo -e "${RED}Error: Xavier Framework not found in this directory${NC}"
    echo "Please run this script from a directory with Xavier installed"
    exit 1
fi

# Check current version
CURRENT_VERSION=$(python3 -c "import json; config=json.load(open('.xavier/config.json')); print(config.get('xavier_version', '1.0.0'))" 2>/dev/null || echo "1.0.0")
echo -e "${BLUE}Current Xavier version: ${YELLOW}$CURRENT_VERSION${NC}"

if [ "$CURRENT_VERSION" != "1.1.2" ]; then
    echo -e "${YELLOW}This fix is for version 1.1.2. Please update Xavier first.${NC}"
    exit 1
fi

# Create .claude/commands directory if it doesn't exist
mkdir -p .claude/commands

echo -e "${BLUE}Installing missing commands...${NC}"

# Create estimate-story command
cat > .claude/commands/estimate-story.md << 'EOF'
---
title: Estimate Story
command: estimate-story
description: Use PM agent to automatically estimate story points for backlog stories
cwd: .
output_format: text
output_file: .xavier/last_estimation.json
---

# /estimate-story

Automatically estimates story points for backlog stories using the PM (Project Manager) agent.

## Usage

```
/estimate-story              # Estimate all unestimated stories
/estimate-story STORY-001    # Estimate specific story
/estimate-story --all        # Re-estimate all stories (including already estimated)
```

## How it works

The PM agent analyzes:
- Technical complexity (APIs, databases, algorithms)
- CRUD operations required
- UI/UX complexity
- Testing requirements
- Acceptance criteria count
- Integration points

Then maps the complexity to Fibonacci story points (1, 2, 3, 5, 8, 13, 21).

## Example

```
/estimate-story

📊 [PM] ProjectManager analyzing backlog...

Estimating STORY-001: User Authentication
  ⚙️ Analyzing complexity...
  ✅ Estimated: 8 points

Estimating STORY-002: Dashboard Creation
  ⚙️ Analyzing complexity...
  ✅ Estimated: 13 points

Summary:
- Estimated 2 stories
- Total points: 21
- Ready for sprint planning
```

## Notes

- PM agent provides consistent, objective estimates
- Estimates based on comprehensive complexity analysis
- Use /set-story-points to manually override if needed

Execute by running:
```
python3 .xavier/xavier_bridge.py estimate-story
```
EOF

echo "  ✅ Created /estimate-story command"

# Create set-story-points command
cat > .claude/commands/set-story-points.md << 'EOF'
---
title: Set Story Points
command: set-story-points
description: Manually set story points for a specific story
cwd: .
output_format: text
---

# /set-story-points

Manually set or update story points for a specific story.

## Usage

```
/set-story-points STORY-001 8    # Set STORY-001 to 8 points
/set-story-points STORY-002 13   # Set STORY-002 to 13 points
```

## Parameters

- **story_id** (required): The story identifier (e.g., STORY-001)
- **points** (required): Fibonacci story points (1, 2, 3, 5, 8, 13, 21)

## Example

```
/set-story-points STORY-001 8

✅ Story STORY-001 updated with 8 story points

Updated story:
- Title: User Authentication System
- Points: 8
- Status: Ready for sprint
```

## Notes

- Use this for manual adjustments after team discussion
- Overrides any previous estimation (manual or automatic)
- Points should follow Fibonacci sequence for consistency
- For automatic estimation, use /estimate-story instead

Execute by running:
```
python3 .xavier/xavier_bridge.py set-story-points '{"story_id": "STORY-001", "points": 8}'
```
EOF

echo "  ✅ Created /set-story-points command"

# Verify commands exist
if [ -f ".claude/commands/estimate-story.md" ] && [ -f ".claude/commands/set-story-points.md" ]; then
    echo
    echo -e "${GREEN}✅ Commands successfully installed!${NC}"
    echo
    echo "You can now use:"
    echo "  • /estimate-story - Automatic PM estimation"
    echo "  • /set-story-points - Manual point setting"
    echo
    echo -e "${BLUE}Restart Claude Code or reload commands to see them.${NC}"
else
    echo -e "${RED}❌ Error: Commands were not created properly${NC}"
    exit 1
fi