# Xavier Sprint Workflow with Git Worktrees

## Overview

When you start a sprint in Xavier, the framework automatically creates isolated git worktrees for each story and bug. This ensures parallel development without conflicts.

## Automatic Workflow

### 1. Sprint Start (`/start-sprint`)

When you start a sprint, Xavier automatically:

```bash
✓ Creates trees/ directory (if it doesn't exist)
✓ Creates git worktrees for each story/bug
✓ Names branches with convention: <type>/PROJ-<number>
  - feature/PROJ-1 (for new features)
  - fix/PROJ-2 (for bug fixes)
  - refactor/PROJ-3 (for code improvements)
```

**Example Output:**
```
======================================================================
🌳 Git Worktree Setup
======================================================================
✓ Worktree directory: /path/to/project/trees
✓ Branch naming: <type>/PROJ-<number>
  - feature/: New functionality
  - fix/: Bug fixes
  - refactor/: Code improvements
======================================================================

✓ Created: feature/PROJ-1                → User Authentication System
✓ Created: feature/PROJ-2                → Dashboard UI Components
✓ Created: fix/PROJ-3                    → Login validation bug

======================================================================
📊 Worktree Summary
======================================================================
Total worktrees created: 3

Next steps for each task:
  1. Agent implements feature in isolated worktree
  2. Tests are written and run (TDD)
  3. Branch is pushed: git push -u origin <branch-name>
  4. PR is created: gh pr create --base main
======================================================================
```

### 2. Task Implementation

Each agent works in its assigned worktree:
- **Isolated environment**: No conflicts with other work
- **Dedicated branch**: Each task has its own branch
- **TDD enforced**: Tests written before implementation
- **100% coverage required**: All code must be tested

### 3. Automatic Push & PR Creation

After task completion, Xavier can automatically:

**Push Branch:**
```python
from xavier.src.git_worktree import GitWorktreeManager

manager = GitWorktreeManager()
success, msg = manager.push_worktree_branch("TASK-001")
print(msg)  # "Pushed branch feature/PROJ-1 to origin"
```

**Create Pull Request:**
```python
success, pr_url = manager.create_pr_for_worktree(
    task_id="TASK-001",
    pr_title="[TASK-001] Implement user authentication",
    pr_body="Complete authentication system with tests"
)
print(pr_url)  # "Created PR: https://github.com/user/repo/pull/123"
```

### 4. PR Workflow

Xavier creates PRs with:
- **Task ID** in title: `[TASK-001] Implement user authentication`
- **Agent info**: Shows which agent completed the work
- **Branch name**: Clear branch naming convention
- **Auto-attribution**: Co-authored by Claude

**Example PR Body:**
```markdown
Task: TASK-001
Agent: python-engineer
Branch: feature/PROJ-1

🤖 Generated with [Claude Code](https://claude.com/claude-code) using Xavier Framework

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Manual Workflow (If Needed)

### List Active Worktrees

```bash
python3 verify_worktree.py
```

or

```python
from xavier.src.git_worktree import GitWorktreeManager

manager = GitWorktreeManager()
worktrees = manager.list_worktrees()

for wt in worktrees:
    print(f"{wt['task_id']}: {wt['branch']} at {wt['path']}")
```

### Push Branch Manually

```bash
cd trees/proj-1
git add .
git commit -m "Implement feature"
git push -u origin feature/PROJ-1
```

### Create PR Manually

```bash
cd trees/proj-1
gh pr create --title "[TASK-001] Feature complete" \\
  --body "Implementation complete with tests" \\
  --base main
```

### Clean Up Completed Worktrees

```python
from xavier.src.git_worktree import GitWorktreeManager

manager = GitWorktreeManager()
cleaned = manager.cleanup_worktrees(remove_completed=True)
print(f"Cleaned {len(cleaned)} worktrees")
```

## Directory Structure

```
project-root/
├── trees/                      # Git worktrees directory
│   ├── proj-1/                # Worktree for feature/PROJ-1
│   ├── proj-2/                # Worktree for feature/PROJ-2
│   └── proj-3/                # Worktree for fix/PROJ-3
├── .xavier/
│   ├── data/                  # All data files (JSON)
│   │   ├── sprints.json
│   │   ├── stories.json
│   │   ├── tasks.json
│   │   ├── bugs.json
│   │   ├── epics.json
│   │   └── roadmaps.json
│   └── worktrees/
│       └── metadata.json      # Worktree tracking
└── src/                       # Main codebase
```

## Best Practices

### ✅ Do:
- Let Xavier create worktrees automatically
- Use descriptive story/task titles (reflected in branch names)
- Push branches after completing tasks
- Create PRs for review before merging
- Clean up old worktrees periodically

### ❌ Don't:
- Don't manually create branches in main repo during sprint
- Don't modify trees/ directory manually
- Don't delete worktrees without using Xavier's cleanup
- Don't push directly to main (use PRs)

## Troubleshooting

### Worktree Already Exists

```bash
# Remove old worktree
python3 -c "from xavier.src.git_worktree import GitWorktreeManager; \\
  GitWorktreeManager().remove_worktree('TASK-001', force=True)"
```

### Branch Name Conflicts

Xavier automatically handles naming:
- Incremental numbering: PROJ-1, PROJ-2, PROJ-3
- Type prefix: feature/, fix/, refactor/
- Conflict-free branch creation

### PR Creation Failed

If `gh` CLI is not installed:
```bash
# Install gh CLI
brew install gh  # macOS
# or
sudo apt install gh  # Linux

# Authenticate
gh auth login
```

Then retry:
```python
manager.create_pr_for_worktree("TASK-001")
```

## Configuration

### Project Abbreviation

Xavier uses project name from `.xavier/config.json`:

```json
{
  "name": "MyProject",
  "project_type": "web_application"
}
```

Branch naming will be: `feature/MYPR-1` (first 4 uppercase letters)

### Custom Branch Naming

Modify sprint start logic in `xavier/src/commands/xavier_commands.py`:

```python
# Lines 1295-1297
branch_name = f"{branch_type}/{project_abbrev}-{idx}"
```

## Integration with CI/CD

Xavier worktrees work seamlessly with CI/CD:

```yaml
# .github/workflows/pr-check.yml
name: PR Check
on:
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: |
          pytest --cov --cov-report=xml
      - name: Upload Coverage
        uses: codecov/codecov-action@v2
```

Each PR from Xavier worktrees triggers:
- Automated tests
- Code coverage check
- Linting and formatting
- Security scanning

## Summary

Xavier's git worktree workflow ensures:
- **🔒 Isolation**: Each task in its own environment
- **🌳 Organization**: Clear branch naming and structure
- **🤖 Automation**: Auto-push and PR creation
- **✅ Quality**: TDD enforced, 100% coverage required
- **📊 Tracking**: Full visibility into all active work

---

**Quick Commands:**

```bash
# Start sprint (auto-creates worktrees)
/start-sprint

# Verify worktrees are working
python3 verify_worktree.py

# Create PR after task completion
python3 -c "from xavier.src.git_worktree import GitWorktreeManager; \\
  print(GitWorktreeManager().create_pr_for_worktree('TASK-001'))"

# Clean up old worktrees
python3 -c "from xavier.src.git_worktree import GitWorktreeManager; \\
  print(f'Cleaned: {GitWorktreeManager().cleanup_worktrees()}')"
```
