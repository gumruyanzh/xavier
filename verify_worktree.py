#!/usr/bin/env python3
"""
Verify Git Worktree Functionality
Run this script to check if git worktrees are working correctly
"""

import sys
from pathlib import Path

# Add xavier to path
sys.path.insert(0, str(Path(__file__).parent))

from xavier.src.git_worktree import GitWorktreeManager

def main():
    print("=" * 70)
    print("Git Worktree Status Check")
    print("=" * 70)

    manager = GitWorktreeManager()

    # Initialize worktree directory
    if manager.initialize_worktree_directory():
        print(f"✓ Worktree directory: {manager.worktree_dir}")
    else:
        print("✗ Failed to initialize worktree directory")
        return False

    # List all worktrees
    worktrees = manager.list_worktrees()

    if worktrees:
        print(f"\n✓ Found {len(worktrees)} active worktree(s):")
        print("-" * 70)
        for wt in worktrees:
            status = wt.get('status', 'unknown')
            print(f"  Task:   {wt['task_id']}")
            print(f"  Agent:  {wt['agent']}")
            print(f"  Branch: {wt['branch']}")
            print(f"  Path:   {wt['path']}")
            print(f"  Status: {status}")
            print("-" * 70)
    else:
        print("\n✓ No active worktrees (this is normal if no tasks are running)")

    print("\n" + "=" * 70)
    print("Git worktree functionality is working correctly!")
    print("=" * 70)
    print("\nHow worktrees work:")
    print("  1. When an agent starts a task, a worktree is created automatically")
    print("  2. Worktrees are in the 'trees/' directory")
    print("  3. Each worktree has its own branch: <agent-name>/<task-id>")
    print("  4. Agents work in isolated worktrees to avoid conflicts")
    print("  5. When a task completes, you can create a PR or remove the worktree")
    print("\nTo see worktree activity, start a task with an agent!")
    print("=" * 70)

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
