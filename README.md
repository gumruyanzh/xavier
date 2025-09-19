# Xavier Framework
## Enterprise-Grade SCRUM Development Framework for Claude Code

Xavier is a comprehensive enterprise development framework that brings strict SCRUM methodology, test-first development, and Clean Code principles to Claude Code. It ensures 100% test coverage, sequential task execution, and enterprise-grade code quality.

## Key Features

### 🎯 Strict Sequential Execution
- Tasks are executed one at a time, in order
- No task begins until the previous one is 100% complete and tested
- Dependencies are strictly enforced

### 🧪 Test-First Development (TDD)
- Tests must be written before implementation
- 100% test coverage required for task completion
- Automatic test validation and coverage reporting

### 🏗️ Clean Code & SOLID Principles
- Enforces Clean Code standards
- SOLID principles validation
- Inversion of Control (IoC) patterns
- Cyclomatic complexity monitoring
- Code duplication detection

### 👥 Specialized Sub-Agents
- **Project Manager**: Sprint planning, story estimation, task assignment
- **Context Manager**: Codebase analysis, pattern detection, knowledge management
- **Python Engineer**: Python-only development with strict boundaries
- **Golang Engineer**: Go-only development with strict boundaries
- **Frontend Engineer**: TypeScript/React/Vue/Angular development
- **DevOps Engineer**: CI/CD, deployment, infrastructure
- **UI/UX Designer**: Design systems, user experience

### 📊 SCRUM Management
- User stories with acceptance criteria
- Tasks with test criteria
- Bug tracking with severity levels
- Sprint planning and execution
- Velocity tracking and burndown charts
- Roadmap management with milestones

## Installation

### Quick Setup

Run this command in your project directory:

```bash
curl -sSL https://raw.githubusercontent.com/xavier-framework/xavier/main/setup.sh | bash
```

Or manually:

```bash
# Clone Xavier
git clone https://github.com/xavier-framework/xavier.git
cd xavier

# Run setup
python setup.py install
```

### Initialize in Existing Project

```bash
# In your project root
xavier init
```

### Initialize New Project

```bash
# Create new project with Xavier
xavier create-project myproject
cd myproject
```

## Commands

### Story Management

#### Create User Story
```bash
/create-story
```
Arguments:
- `title`: Story title
- `as_a`: User role (e.g., "developer", "user")
- `i_want`: Feature description
- `so_that`: Business value
- `acceptance_criteria`: List of criteria
- `priority`: Critical/High/Medium/Low

Example:
```json
{
  "title": "User Authentication",
  "as_a": "user",
  "i_want": "to log in with email and password",
  "so_that": "I can access my personal dashboard",
  "acceptance_criteria": [
    "Email validation",
    "Password strength requirements",
    "Remember me option",
    "Password reset capability"
  ],
  "priority": "High"
}
```

#### Create Task
```bash
/create-task
```
Arguments:
- `story_id`: Parent story ID
- `title`: Task title
- `description`: Task description
- `technical_details`: Implementation details
- `estimated_hours`: Hour estimate
- `test_criteria`: Test requirements
- `dependencies`: List of dependency task IDs

#### Create Bug
```bash
/create-bug
```
Arguments:
- `title`: Bug title
- `description`: Bug description
- `steps_to_reproduce`: Reproduction steps
- `expected_behavior`: What should happen
- `actual_behavior`: What actually happens
- `severity`: Critical/High/Medium/Low

### Sprint Management

#### Create Sprint
```bash
/create-sprint
```
Arguments:
- `name`: Sprint name
- `goal`: Sprint goal
- `duration_days`: Sprint length (default: 14)
- `auto_plan`: Auto-select items by priority (default: true)

#### Start Sprint
```bash
/start-sprint
```
Arguments:
- `sprint_id`: Sprint to start (optional, uses latest)
- `strict_mode`: Enable strict sequential execution (default: true)

This command will:
1. Activate the sprint
2. Assign tasks to appropriate agents
3. Begin sequential task execution
4. Enforce test-first development
5. Validate Clean Code compliance

#### End Sprint
```bash
/end-sprint
```
Arguments:
- `retrospective_notes`: Sprint retrospective

### Project Commands

#### Learn Existing Project
```bash
/learn-project
```
Analyzes your existing codebase and:
- Detects technology stack
- Identifies patterns and conventions
- Generates appropriate agents
- Creates initial backlog

#### Create Roadmap
```bash
/create-roadmap
```
Arguments:
- `name`: Roadmap name
- `vision`: Product vision
- `milestones`: List of milestone definitions

### Reporting

#### Generate Reports
```bash
/generate-report
```
Report types:
- `backlog`: Backlog overview
- `sprint`: Sprint progress
- `velocity`: Team velocity trends
- `burndown`: Sprint burndown chart
- `agents`: Agent capabilities

#### Show Backlog
```bash
/show-backlog
```
Shows prioritized backlog with story points.

#### List Items
```bash
/list-stories    # List all user stories
/list-tasks      # List all tasks
/list-bugs       # List all bugs
```

### Help
```bash
/xavier-help     # Show all commands
```

## Workflow Example

### 1. Initialize Project
```bash
xavier init
/learn-project
```

### 2. Create Stories
```bash
/create-story {
  "title": "User Registration",
  "as_a": "new user",
  "i_want": "to create an account",
  "so_that": "I can use the application",
  "acceptance_criteria": [
    "Email verification",
    "Strong password enforcement",
    "Profile creation"
  ],
  "priority": "High"
}
```

### 3. Break Down into Tasks
```bash
/create-task {
  "story_id": "US-ABC123",
  "title": "Implement email validation",
  "description": "Add email validation service",
  "technical_details": "Use regex and MX record checking",
  "estimated_hours": 4,
  "test_criteria": [
    "Valid emails accepted",
    "Invalid emails rejected",
    "MX record verification works"
  ]
}
```

### 4. Plan Sprint
```bash
/create-sprint {
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "auto_plan": true
}
```

### 5. Execute Sprint
```bash
/start-sprint
```

Xavier will:
- Assign tasks to appropriate agents
- Enforce test-first development
- Execute tasks sequentially
- Validate 100% test coverage
- Check Clean Code compliance
- Update progress in real-time

### 6. Complete Sprint
```bash
/end-sprint {
  "retrospective_notes": "Completed authentication module with 100% coverage"
}
```

## Configuration

### xavier.config.json
```json
{
  "settings": {
    "strict_mode": true,
    "test_first": true,
    "clean_code_enforcement": true,
    "ioc_patterns": true,
    "sequential_execution": true,
    "test_coverage_required": 100,
    "sprint_velocity": 20,
    "default_sprint_duration": 14
  },
  "agents": {
    "project_manager": {
      "enabled": true
    },
    "python_engineer": {
      "enabled": true,
      "tech_stack": ["django", "fastapi", "pytest"]
    }
  }
}
```

## Best Practices

### Test-First Development
1. Write tests before implementation
2. Ensure tests fail initially
3. Write minimal code to pass tests
4. Refactor while keeping tests green
5. Achieve 100% coverage

### Clean Code Standards
- Functions: Max 20 lines
- Classes: Max 200 lines
- Methods per class: Max 10
- Function parameters: Max 3
- Cyclomatic complexity: Max 10
- Line length: Max 120 characters

### SOLID Principles
- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

### Agent Boundaries
- Python Engineer writes ONLY Python
- Go Engineer writes ONLY Go
- Frontend Engineer writes ONLY TypeScript/JavaScript
- No agent crosses language boundaries

## Architecture

```
Xavier Framework
├── Core Engine (Strict Execution Control)
├── SCRUM Manager (Sprint & Backlog Management)
├── Agent Orchestrator (Task Delegation)
├── Sub-Agents
│   ├── Project Manager
│   ├── Context Manager
│   ├── Python Engineer
│   ├── Golang Engineer
│   ├── Frontend Engineer
│   └── [Dynamic Agents]
├── Validators
│   ├── Test-First Enforcer
│   ├── Clean Code Analyzer
│   ├── SOLID Validator
│   └── IoC Validator
└── Command System
```

## Tech Stack Detection

Xavier automatically detects and adapts to:
- **Languages**: Python, Go, TypeScript, JavaScript, Java, Ruby, C#
- **Frameworks**: Django, FastAPI, Flask, React, Vue, Angular, Spring
- **Build Tools**: npm, pip, go, maven, gradle, bundler
- **Test Frameworks**: pytest, jest, go test, junit, rspec
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins

## Dynamic Agent Generation

When Xavier detects a technology not covered by default agents, it automatically generates specialized agents:

```python
# Detected Ruby on Rails
Xavier generates -> RubyEngineerAgent

# Detected Java Spring
Xavier generates -> JavaEngineerAgent

# Detected Rust
Xavier generates -> RustEngineerAgent
```

## Integration with Claude Code

Xavier seamlessly integrates with Claude Code through custom commands. All Xavier commands are available directly in your Claude Code chat:

```
User: /create-story
Claude Code + Xavier: [Creates story with PM agent estimation]

User: /start-sprint
Claude Code + Xavier: [Orchestrates agents to execute sprint]
```

## Troubleshooting

### Tests Not Running
- Ensure test frameworks are installed
- Check test file naming conventions
- Verify test paths in configuration

### Agent Not Found
- Run `/tech-stack-analyze` to detect stack
- Use `/create-agent` to add custom agents
- Check agent is enabled in config

### Sprint Won't Start
- Ensure sprint has items assigned
- Check no other sprint is active
- Verify all dependencies are resolved

## Contributing

Xavier is open-source and welcomes contributions:

1. Fork the repository
2. Create a feature branch
3. Write tests first (100% coverage required)
4. Implement feature following Clean Code
5. Ensure all validators pass
6. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

- Documentation: https://xavier-framework.dev
- Issues: https://github.com/xavier-framework/xavier/issues
- Discord: https://discord.gg/xavier-dev

## Credits

Created for enterprise teams using Claude Code who demand:
- 100% test coverage
- Clean, maintainable code
- Strict SCRUM methodology
- Professional development standards

---

**Xavier Framework** - Enterprise Development, Properly Executed