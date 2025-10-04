# Automatic Agent Assignment

## Overview

Xavier Framework now includes **intelligent automatic agent assignment** during task creation. When you create a task, Xavier analyzes the title, description, and technical details to automatically:

1. **Detect the required technology/skill**
2. **Assign the most appropriate agent**
3. **Create the agent if it doesn't exist**
4. **Provide confidence scores for assignments**

## How It Works

### 1. Technology Detection

The `TaskAgentMatcher` analyzes task content for technology keywords:

```python
# Example task
{
    "title": "Build React dashboard",
    "description": "Create interactive UI",
    "technical_details": "Use TypeScript with Material-UI"
}

# Detected: React, TypeScript
# Assigned: frontend-engineer (100% confidence)
```

### 2. Agent Mapping

Technologies are mapped to specialized agents:

| Technology | Agent | Keywords |
|------------|-------|----------|
| Python, Django, Flask | `python-engineer` | python, py, django, flask, fastapi |
| JavaScript, React, Vue | `frontend-engineer` | javascript, typescript, react, vue, angular |
| Go, Gin | `golang-engineer` | go, golang, gin, gorilla |
| Java, Spring | `java-engineer` | java, spring, springboot, maven |
| Ruby, Rails | `ruby-engineer` | ruby, rails, rspec |
| Rust | `rust-engineer` | rust, cargo, actix |
| Swift, iOS | `swift-engineer` | swift, ios, swiftui, xcode |
| Kotlin, Android | `kotlin-engineer` | kotlin, android |
| Testing | `test-runner` | test, testing, unittest, coverage |
| Docker, K8s | `devops-engineer` | docker, kubernetes, terraform |
| Database | `database-engineer` | sql, postgres, mysql, mongodb |

### 3. Confidence Scoring

Assignments include confidence scores:
- **100%**: Exact technology match in title
- **50-99%**: Technology found in description/details
- **30-49%**: Task type inference (test, deploy, etc.)
- **<30%**: Default assignment

## Usage

### Automatic Assignment (Default)

```python
# Creating a task automatically assigns an agent
xavier.create_task({
    "story_id": "US-001",
    "title": "Implement Python API",
    "description": "Create REST endpoints",
    "technical_details": "Use FastAPI"
})

# Result:
{
    "task_id": "T-001",
    "assigned_to": "python-engineer",  # Automatically assigned!
    "agent_assignment": {
        "agent": "python-engineer",
        "reason": "Detected 'python' technology in task",
        "confidence": 1.0,
        "created_new": false
    }
}
```

### Manual Override

```python
# Manually specify an agent
xavier.create_task({
    "story_id": "US-001",
    "title": "Review code",
    "assigned_to": "senior-engineer"  # Manual assignment
})

# Or disable auto-assignment
xavier.create_task({
    "story_id": "US-001",
    "title": "Generic task",
    "auto_assign": False  # Skip auto-assignment
})
```

## Dynamic Agent Creation

If a required agent doesn't exist, Xavier creates it automatically:

```python
# Task requiring a new technology
{
    "title": "Implement Elixir service",
    "technical_details": "Use Phoenix framework"
}

# Xavier automatically:
1. Detects "elixir" technology
2. Checks for elixir-engineer agent
3. Creates agent if missing:
   - Generates .xavier/agents/elixir_engineer.yaml
   - Creates .claude/agents/elixir-engineer.md
   - Configures with appropriate skills
4. Assigns the new agent to task
```

## Examples

### Example 1: Multi-Technology Task

```python
task = {
    "title": "Full-stack feature",
    "description": "Backend in Python, frontend in React",
    "technical_details": "Django REST + React with Redux"
}

# Analysis:
# - Detected: python, django, react
# - Primary: python (appears first)
# - Assigned: python-engineer (100% confidence)
```

### Example 2: Test Task

```python
task = {
    "title": "Write unit tests",
    "description": "Add test coverage",
    "technical_details": "Use pytest with mocking"
}

# Analysis:
# - Detected: test, pytest
# - Assigned: test-runner (100% confidence)
```

### Example 3: DevOps Task

```python
task = {
    "title": "Setup CI/CD pipeline",
    "description": "Configure GitHub Actions",
    "technical_details": "Docker containers with Kubernetes"
}

# Analysis:
# - Detected: docker, kubernetes
# - Assigned: devops-engineer (100% confidence)
# - Note: Creates devops-engineer if doesn't exist
```

## Workload Balancing

When multiple agents could handle a task, Xavier considers current workload:

```python
# If both python-engineer and backend-engineer match:
workload = {
    "python-engineer": 5 tasks,
    "backend-engineer": 2 tasks
}
# Assigns to backend-engineer (lower workload)
```

## CLI Integration

### Using Slash Commands

```bash
# Auto-assignment happens automatically
/create-task STORY-001 "Build React component"
# Output: Task created and assigned to frontend-engineer

/create-task STORY-001 "Write Go microservice"
# Output: Task created and assigned to golang-engineer

/create-task STORY-001 "Deploy to Kubernetes"
# Output: Task created, devops-engineer created, and assigned
```

## Configuration

### Customizing Agent Mappings

Edit `xavier/src/agents/task_agent_matcher.py`:

```python
TECH_AGENT_MAP = {
    'your_tech': 'your-agent',
    'custom_framework': 'specialist-engineer',
    # Add your mappings
}
```

### Adding Task Type Detection

```python
TASK_TYPE_KEYWORDS = {
    'security': ['audit', 'vulnerability', 'security'],
    'performance': ['optimize', 'performance', 'speed'],
    # Add task types
}
```

## Benefits

1. **Zero Configuration**: Works out of the box
2. **Intelligent Assignment**: Based on actual task content
3. **Dynamic Adaptation**: Creates agents as needed
4. **Time Saving**: No manual agent assignment
5. **Consistent**: Same technology always gets same agent
6. **Transparent**: Shows reasoning and confidence

## Monitoring

View agent assignments:

```bash
# Check task assignments
cat .xavier/data/tasks.json | jq '.[] | {id, title, assigned_to}'

# See agent workload
cat .xavier/data/tasks.json | jq '[.[] | .assigned_to] | group_by(.) | map({agent: .[0], count: length})'
```

## Troubleshooting

### Agent Not Created
**Problem**: "Failed to create specialized agent"
**Solution**: Ensure agent name follows pattern, check logs

### Wrong Agent Assigned
**Problem**: Task assigned to wrong specialist
**Solution**: Add more specific keywords to technical_details

### Low Confidence Score
**Problem**: Assignment confidence < 50%
**Solution**: Include technology names explicitly in title

### Manual Override Needed
**Problem**: Need specific agent regardless of content
**Solution**: Use `assigned_to` parameter explicitly

## API Reference

### TaskAgentMatcher Class

```python
class TaskAgentMatcher:
    def analyze_task(task_data: Dict) -> Tuple[agent_name, reason, confidence]
    def check_agent_exists(agent_name: str) -> bool
    def create_agent_if_needed(agent_name: str, context: Dict) -> bool
    def assign_agent_to_task(task_data: Dict) -> Dict
    def get_agent_workload() -> Dict[str, int]
    def balance_assignment(candidates: List[str]) -> str
```

### Enhanced create_task

```python
xavier.create_task({
    "story_id": str,          # Required
    "title": str,             # Required
    "description": str,       # Required
    "technical_details": str, # Used for agent detection
    "assigned_to": str,       # Optional, manual override
    "auto_assign": bool,      # Optional, default True
    ...
})
```

## Best Practices

1. **Be Specific**: Include technology names in task titles
2. **Use Technical Details**: Add frameworks, languages, tools
3. **Trust the System**: Let auto-assignment work first
4. **Override When Needed**: Use manual assignment for special cases
5. **Review Assignments**: Check confidence scores
6. **Monitor Workload**: Ensure balanced distribution

## Summary

Automatic agent assignment makes Xavier Framework more intelligent and efficient:
- **Analyzes** task content for technology requirements
- **Assigns** the most appropriate specialist automatically
- **Creates** new agents dynamically when needed
- **Balances** workload across available agents
- **Provides** transparency with confidence scores

This feature eliminates manual agent assignment while ensuring tasks always go to the right specialist!