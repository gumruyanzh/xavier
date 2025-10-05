# Xavier Git Worktree Workflow

## Overview

Xavier Framework now implements an advanced Git worktree-based workflow that enables multiple agents to work simultaneously on different tasks without conflicts. Each agent works in an isolated branch and directory, automatically creating pull requests upon task completion.

## 🌳 Architecture

```
xavier/
├── .xavier/                      # Xavier configuration
├── trees/                        # Git worktrees directory (gitignored)
│   ├── python-engineer-TASK-001/ # Agent-specific worktree
│   ├── frontend-engineer-TASK-002/
│   ├── test-runner-TASK-006/
│   └── .worktree_metadata.json   # Worktree tracking metadata
└── src/                          # Main repository (stays on main branch)
```

## 🚀 How It Works

### 1. Sprint Initialization

When a sprint starts (`/xavier-sprint start`), Xavier:
1. Creates the `trees/` directory if it doesn't exist
2. Initializes a worktree for each agent-task combination
3. Creates branches following the pattern: `agent-name/task-id`
4. Updates sprint metadata with worktree information

```bash
# Start a sprint (automatically creates worktrees)
/xavier-sprint start

# Output:
Sprint 'Sprint 1 - Feature Development' started
- Tasks: 8
- Agents initialized: ['python-engineer', 'test-runner']
- Worktrees created: 8
```

### 2. Agent Task Execution

When an agent starts a task:
1. **Automatic Worktree Creation**: A dedicated worktree is created
2. **Branch Creation**: Feature branch `agent-name/task-id` is created from main
3. **Isolated Work**: Agent switches to worktree directory for all operations
4. **No Conflicts**: Main repository stays on main branch

```python
# Agent automatically creates worktree when starting task
agent.start_task(task)  # Creates worktree at trees/agent-name-task-id
```

### 3. Task Completion & PR Creation

When an agent completes a task:
1. **Automatic Commit**: Changes are committed in the worktree
2. **Branch Push**: Feature branch is pushed to origin
3. **PR Creation**: Pull request is automatically created (if `gh` CLI is available)
4. **Cleanup Ready**: Worktree can be safely removed after PR merge

```python
# Agent completes task and creates PR
agent.complete_task(success=True, summary="Implemented feature X")
# Automatically:
# - Commits changes
# - Pushes branch
# - Creates PR with task details
```

### 4. Sprint Completion

When a sprint ends (`/xavier-sprint end`):
1. **Change Detection**: Checks all worktrees for uncommitted changes
2. **Safe Cleanup**: Removes worktrees without uncommitted changes
3. **Warning**: Reports worktrees with pending changes
4. **Archive**: Stores worktree metadata for historical reference

```bash
# End sprint (with automatic cleanup)
/xavier-sprint end

# Output:
Sprint 'Sprint 1' ended
- Worktrees cleaned: 6
- Worktrees with changes: 2 (requires manual review)
```

## 📁 File Structure

### Worktree Metadata (`.worktree_metadata.json`)

```json
{
  "TASK-001": {
    "agent": "python-engineer",
    "branch": "python-engineer/TASK-001",
    "path": "trees/python-engineer-TASK-001",
    "created_at": "2024-10-03T10:00:00",
    "status": "active"
  }
}
```

### Sprint Data with Worktree Info

```json
{
  "name": "Sprint 1",
  "status": "active",
  "worktrees": [
    {
      "agent": "python-engineer",
      "task": "TASK-001",
      "worktree": "trees/python-engineer-TASK-001"
    }
  ]
}
```

## 🎯 Benefits

1. **Parallel Development**: Multiple agents work simultaneously without conflicts
2. **Clean Main Branch**: Main branch remains stable and uncluttered
3. **Automatic PR Creation**: Reduces manual overhead for developers
4. **Task Isolation**: Each task has its own working directory
5. **Easy Rollback**: Can abandon changes by removing worktree
6. **Sprint Tracking**: Clear visibility of who's working on what

## 🛠️ Commands

### Managing Worktrees

```python
from xavier.src.git_worktree import GitWorktreeManager

# Initialize manager
manager = GitWorktreeManager()

# Create worktree for a task
success, message = manager.create_worktree(
    branch_name="feature/auth",
    agent_name="python-engineer",
    task_id="TASK-001"
)

# List active worktrees
worktrees = manager.list_worktrees()

# Check worktree status
status = manager.get_worktree_status("TASK-001")

# Remove worktree
success, message = manager.remove_worktree("TASK-001", force=False)

# Create PR for completed task
success, pr_url = manager.create_pr_for_worktree(
    task_id="TASK-001",
    pr_title="[TASK-001] Add authentication",
    pr_body="Implements user authentication..."
)
```

### Sprint Commands with Worktree Support

```bash
# Start sprint (creates worktrees)
/xavier-sprint create name="Sprint 2"
/xavier-sprint start

# Check status (includes worktree info)
/xavier-status verbose=true

# End sprint (cleanup worktrees)
/xavier-sprint end
```

## 📊 Status Monitoring

The `/xavier-status` command now shows worktree information:

```json
{
  "worktrees": {
    "total_worktrees": 3,
    "active_worktrees": [
      {
        "task_id": "TASK-001",
        "agent": "python-engineer",
        "branch": "python-engineer/TASK-001",
        "has_changes": true,
        "commits_ahead": 2,
        "commits_behind": 0
      }
    ],
    "worktrees_with_changes": 1,
    "worktrees_ahead": 2,
    "worktrees_behind": 0
  }
}
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Worktree Already Exists
**Error**: "Worktree already exists at path"
**Solution**: Remove the existing worktree first
```bash
git worktree remove trees/agent-name-task-id
```

#### 2. Uncommitted Changes During Cleanup
**Error**: "Worktree has uncommitted changes"
**Solution**: Either commit changes or force removal
```python
# Option 1: Commit changes
cd trees/agent-name-task-id
git add .
git commit -m "Save work"

# Option 2: Force removal (loses changes)
manager.remove_worktree("TASK-ID", force=True)
```

#### 3. Branch Already Exists
**Error**: "Branch agent/task already exists"
**Solution**: Delete the branch and retry
```bash
git branch -D agent-name/task-id
```

#### 4. Cannot Create PR
**Error**: "gh command not found"
**Solution**: Install GitHub CLI
```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# After installation, authenticate
gh auth login
```

#### 5. Worktree Metadata Corrupted
**Solution**: Rebuild metadata from git
```python
manager.cleanup_worktrees()  # Removes orphaned entries
# Then recreate needed worktrees
```

## 🏃 Manual Worktree Operations

If you need to manually manage worktrees:

```bash
# List all worktrees
git worktree list

# Create worktree manually
git worktree add -b agent-name/task-id trees/agent-name-task-id main

# Remove worktree
git worktree remove trees/agent-name-task-id

# Prune stale worktree entries
git worktree prune
```

## 🔄 Integration with CI/CD

The worktree workflow integrates seamlessly with CI/CD:

1. **PR Triggers**: Each PR from agent branches triggers CI
2. **Isolated Testing**: Tests run in the feature branch
3. **Main Protection**: Main branch stays stable
4. **Auto-merge**: Can configure auto-merge when tests pass

## 📈 Best Practices

1. **One Task Per Worktree**: Don't reuse worktrees for multiple tasks
2. **Regular Cleanup**: Run cleanup at sprint end to avoid accumulation
3. **Commit Frequently**: Agents should commit progress regularly
4. **PR Reviews**: Review agent PRs before merging to main
5. **Branch Naming**: Follow the `agent-name/task-id` convention
6. **Metadata Backup**: Periodically backup `.worktree_metadata.json`

## 🚦 Workflow States

### Task Lifecycle
1. **Assigned**: Task assigned to agent
2. **Worktree Created**: Agent creates worktree
3. **In Progress**: Agent works in isolated branch
4. **Completed**: Agent finishes, creates PR
5. **PR Review**: Human reviews PR
6. **Merged**: PR merged to main
7. **Cleaned**: Worktree removed

### Sprint States with Worktrees
1. **Planned**: Sprint created, no worktrees
2. **Active**: Sprint started, worktrees created
3. **Ending**: Checking worktrees for cleanup
4. **Completed**: Sprint ended, worktrees cleaned

## 🔐 Security Considerations

1. **Branch Protection**: Protect main branch from direct pushes
2. **PR Requirements**: Require PR reviews before merge
3. **Access Control**: Limit worktree creation to authorized agents
4. **Sensitive Data**: Don't commit secrets in worktrees
5. **Cleanup**: Remove worktrees with sensitive data after use

## 📚 API Reference

### GitWorktreeManager Class

```python
class GitWorktreeManager:
    def __init__(self, repo_path: str = ".", worktree_dir: str = "trees")
    def initialize_worktree_directory() -> bool
    def create_worktree(branch_name: str, agent_name: str, task_id: str) -> Tuple[bool, str]
    def list_worktrees() -> List[Dict[str, str]]
    def remove_worktree(task_id: str, force: bool = False) -> Tuple[bool, str]
    def get_worktree_status(task_id: str) -> Optional[Dict[str, any]]
    def cleanup_worktrees(remove_completed: bool = False) -> List[str]
    def create_pr_for_worktree(task_id: str, pr_title: str = None, pr_body: str = None) -> Tuple[bool, str]
```

### Agent Integration

```python
class BaseAgent:
    def start_task(task: AgentTask) -> bool  # Creates worktree
    def complete_task(success: bool, summary: str, create_pr: bool = True) -> None  # Creates PR
```

## 🎓 Examples

### Example 1: Complete Sprint Workflow

```python
# 1. Create sprint with tasks
sprint = create_sprint("Feature Sprint", tasks=["TASK-001", "TASK-002"])

# 2. Start sprint (creates worktrees)
start_sprint(sprint.id)
# Creates: trees/python-engineer-TASK-001, trees/frontend-engineer-TASK-002

# 3. Agents work in parallel
python_agent.execute_task(task_001)  # Works in trees/python-engineer-TASK-001
frontend_agent.execute_task(task_002)  # Works in trees/frontend-engineer-TASK-002

# 4. Agents complete tasks (creates PRs)
python_agent.complete_task(True, "API implemented")
frontend_agent.complete_task(True, "UI completed")

# 5. End sprint (cleanup)
end_sprint(sprint.id)
# Cleans up worktrees after PR merge
```

### Example 2: Manual Worktree Management

```python
from xavier.src.git_worktree import GitWorktreeManager

manager = GitWorktreeManager()

# Check all worktrees
for wt in manager.list_worktrees():
    status = manager.get_worktree_status(wt['task_id'])
    print(f"Task {wt['task_id']}: {status['has_uncommitted_changes']}")

# Clean up completed tasks
cleaned = manager.cleanup_worktrees(remove_completed=True)
print(f"Cleaned {len(cleaned)} worktrees")
```

## 🔍 Troubleshooting

### Verifying Worktree Functionality

Run the verification script to check if worktrees are working:

```bash
python3 verify_worktree.py
```

**Expected output:**
- ✓ Shows worktree directory location (`trees/`)
- ✓ Lists all active worktrees with task IDs, agents, branches, and paths
- ✓ Confirms worktree functionality is working

### Common Issues

#### "Worktrees not being created"

**Symptoms:** No worktrees appear when tasks start

**Diagnosis:**
```bash
# Check if worktree directory exists
ls -la trees/

# List all worktrees
python3 -c "from xavier.src.git_worktree import GitWorktreeManager; print(GitWorktreeManager().list_worktrees())"
```

**Solutions:**
1. Worktrees are created automatically when agents start tasks
2. Check that `task.working_dir` is `None` when starting a task
3. Ensure the git repository is initialized
4. Verify `trees/` is in `.gitignore`

#### "Can't see worktree activity"

**Symptoms:** Unsure if worktrees are working

**Solution:** Worktrees ARE working if:
- The `trees/` directory exists
- Running `verify_worktree.py` shows active worktrees
- Agents start tasks successfully
- Each task has its own branch visible in `git branch --all`

**Check branches:**
```bash
git branch --all | grep "python-engineer\|frontend-engineer\|test-runner"
```

#### "Too many worktrees"

**Symptoms:** Many old worktrees from completed tasks

**Solution:** Clean up completed worktrees:
```python
from xavier.src.git_worktree import GitWorktreeManager

manager = GitWorktreeManager()
cleaned = manager.cleanup_worktrees()
print(f"Cleaned {len(cleaned)} worktrees")
```

Or manually remove specific worktrees:
```bash
# Using Python
python3 -c "from xavier.src.git_worktree import GitWorktreeManager; GitWorktreeManager().remove_worktree('TASK-001', force=True)"

# Or using git command
git worktree remove trees/agent-name-TASK-001
```

### How to Verify Worktrees Are Working

1. **Run verification script:**
   ```bash
   python3 verify_worktree.py
   ```

2. **Check directory structure:**
   ```bash
   ls -la trees/
   # Should show: agent-name-TASK-ID directories
   ```

3. **List git worktrees:**
   ```bash
   git worktree list
   ```

4. **Check branches:**
   ```bash
   git branch --all
   # Should show: agent-name/TASK-ID branches
   ```

5. **Monitor during task execution:**
   - Start a task with an agent
   - Watch for "Created worktree" in console output
   - Verify `trees/agent-name-TASK-ID` directory appears

## 📝 Summary

The Xavier Git Worktree workflow provides a robust, scalable solution for parallel development with multiple agents. It ensures code isolation, automatic PR creation, and clean sprint management, making it ideal for team-based agile development with AI agents.

**Key Points:**
- ✅ Worktrees are created automatically when agents start tasks
- ✅ Each worktree is isolated in the `trees/` directory
- ✅ Each task gets its own branch: `agent-name/task-id`
- ✅ Use `verify_worktree.py` to check functionality
- ✅ Clean up old worktrees with `cleanup_worktrees()`

---

*For more information, see the [Xavier Framework Documentation](../README.md)*