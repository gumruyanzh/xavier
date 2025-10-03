# Xavier Framework Slash Commands for Claude Code

## Overview
Xavier Framework slash commands are now integrated with Claude Code, allowing you to use SCRUM management, agent orchestration, and development workflow features directly within Claude Code.

## Available Commands

### Project Management

#### `/xavier-init` - Initialize Xavier Framework
```bash
/xavier-init name="My Project" type=web stack=python
```
- **name** (required): Project name
- **type**: Project type (web/api/mobile/cli) - default: web
- **stack**: Tech stack - default: python

#### `/xavier-status` - Show project status
```bash
/xavier-status verbose=true
```
- **verbose**: Show detailed metrics - default: false

### Story Management

#### `/create-story` - Create a user story
```bash
/create-story title="User login" as_a="user" i_want="to log in" so_that="I can access features" points=5
```
- **title** (required): Story title
- **as_a** (required): As a...
- **i_want** (required): I want...
- **so_that** (required): So that...
- **points**: Story points (0 for auto-estimate) - default: 0

#### `/estimate` - Estimate story points
```bash
/estimate story_ids="STORY-001,STORY-002"
```
- **story_ids**: Comma-separated story IDs (empty for all)

#### `/create-epic` - Create an epic
```bash
/create-epic title="Authentication System" description="Complete auth implementation" stories="STORY-001,STORY-002"
```
- **title** (required): Epic title
- **description** (required): Epic description
- **stories**: Comma-separated story IDs to include

### Sprint Management

#### `/sprint` - Manage sprints
```bash
/sprint action=create name="Sprint 1" duration=14
/sprint action=start
/sprint action=end
/sprint action=status
```
- **action** (required): Action to perform (create/start/end/status)
- **name**: Sprint name (for create)
- **duration**: Sprint duration in days - default: 14

#### `/velocity` - Show velocity metrics
```bash
/velocity sprints=3
```
- **sprints**: Number of past sprints to analyze - default: 3

#### `/backlog` - Manage backlog
```bash
/backlog action=view filter=unestimated
/backlog action=prioritize
/backlog action=groom
```
- **action**: Action (view/prioritize/groom) - default: view
- **filter**: Filter (unestimated/ready/blocked)

### Agent Management

#### `/create-agent` - Create a custom agent
```bash
/create-agent name="api-specialist" skills="FastAPI,PostgreSQL,Redis" tools="Read,Write,Edit,Bash" color=green emoji=⚡
```
- **name** (required): Agent name
- **skills** (required): Comma-separated skills
- **tools**: Available tools - default: Read,Write,Edit,Bash
- **color**: Agent color - default: blue
- **emoji**: Agent emoji - default: 🤖

#### `/assign-agent` - Assign agent to task
```bash
/assign-agent task_id="TASK-001" auto=true
```
- **task_id** (required): Task ID
- **auto**: Auto-select best agent - default: true

#### `/start-task` - Start working on a task
```bash
/start-task task_id="TASK-001" agent="python-engineer"
```
- **task_id** (required): Task ID
- **agent**: Specific agent to use (optional)

### Development Workflow

#### `/xavier-test` - Run test-first enforcement
```bash
/xavier-test coverage=true path="src/api"
```
- **coverage**: Check coverage - default: true
- **path**: Specific path to test

#### `/bug` - Report a bug
```bash
/bug title="Login fails" description="User cannot log in with valid credentials" priority=high component=auth
```
- **title** (required): Bug title
- **description** (required): Bug description
- **priority**: Priority (low/medium/high/critical) - default: medium
- **component**: Affected component

#### `/roadmap` - Manage roadmap
```bash
/roadmap action=view
/roadmap action=add milestone="MVP Release" date="2024-03-01"
```
- **action**: Action (view/add/update) - default: view
- **milestone**: Milestone name (for add)
- **date**: Target date (YYYY-MM-DD)

## Usage Examples

### Quick Start
```bash
# Initialize Xavier in your project
/xavier-init name="My App" type=web stack=python

# Create your first story
/create-story title="User Registration" as_a="new user" i_want="to create an account" so_that="I can use the app"

# Auto-estimate the story
/estimate

# Create and start a sprint
/sprint action=create name="Sprint 1"
/sprint action=start

# Start working on a task
/start-task task_id="TASK-001"
```

### Working with Agents
```bash
# Create a specialized agent
/create-agent name="frontend-specialist" skills="React,TypeScript,TailwindCSS"

# Assign agent to a task
/assign-agent task_id="TASK-002" auto=false

# Start task with specific agent
/start-task task_id="TASK-002" agent="frontend-specialist"
```

### Sprint Management
```bash
# Check current sprint status
/sprint action=status

# View team velocity
/velocity sprints=5

# View and groom backlog
/backlog action=view filter=unestimated
/backlog action=groom
```

## Command Line Usage

You can also use these commands directly from the terminal:

```bash
# List all available commands
python xavier_slash_command.py --list

# Get help for a specific command
python xavier_slash_command.py --help-command /create-story

# Execute a command
python xavier_slash_command.py "/create-story title='New Feature' as_a='user' i_want='functionality' so_that='benefit'"
```

## Integration with Claude Code

When using Claude Code, you can invoke these commands using the SlashCommand tool:

1. Simply type the command as you would in a terminal
2. Claude Code will execute it using the Xavier framework
3. Results will be displayed in the Claude Code interface

Example in Claude Code:
```
User: /create-story title="Add dark mode" as_a="user" i_want="to use dark mode" so_that="I can reduce eye strain"

Claude Code: [Executes the command and shows results]
```

## Notes

- All commands are prefixed with `/` for consistency with slash command conventions
- Arguments can be provided as `key=value` pairs
- String values with spaces should be quoted
- Commands maintain state in `.xavier/` directory structure
- All data is persisted as JSON for easy inspection and modification