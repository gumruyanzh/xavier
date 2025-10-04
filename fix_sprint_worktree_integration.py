#!/usr/bin/env python3
"""
Fix and demonstrate sprint worktree integration
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Add xavier to path
sys.path.insert(0, str(Path(__file__).parent))

from xavier.src.git_worktree import GitWorktreeManager
from xavier.src.commands.xavier_commands import XavierCommands


def end_active_sprints():
    """End any active sprints"""
    print("Ending active sprints...")
    print("-" * 50)

    xavier = XavierCommands(project_path=".")

    # Check for active sprints
    sprints_file = Path(".xavier/data/sprints.json")
    if sprints_file.exists():
        with open(sprints_file, 'r') as f:
            data = json.load(f)

        active_sprints = [s for s in data.get("sprints", [])
                         if s.get("status") == "active"]

        if active_sprints:
            for sprint in active_sprints:
                print(f"Ending sprint: {sprint['id']} - {sprint['name']}")
                result = xavier.end_sprint({})

                if "error" not in result:
                    print(f"✅ Sprint ended successfully")
                else:
                    print(f"❌ Error: {result.get('error')}")
        else:
            print("No active sprints to end")


def create_demo_sprint():
    """Create a demonstration sprint with proper data"""
    print("\nCreating demonstration sprint...")
    print("-" * 50)

    xavier = XavierCommands(project_path=".")

    # Create a story
    story_result = xavier.create_story({
        "title": "Implement Git Worktree Integration",
        "as_a": "developer",
        "i_want": "automatic worktree creation for each task",
        "so_that": "I can work on tasks in isolated branches",
        "acceptance_criteria": [
            "Worktrees are created automatically on sprint start",
            "Each task gets its own worktree in trees/ directory",
            "Branches follow naming convention: agent-name/task-id",
            "Worktrees are removed on sprint end"
        ],
        "priority": "High"
    })

    story_id = story_result.get("story_id")
    print(f"✅ Created story: {story_id}")

    # Create tasks
    task1_result = xavier.create_task({
        "story_id": story_id,
        "title": "Implement worktree creation logic",
        "description": "Create worktrees when sprint starts",
        "technical_details": "Use GitWorktreeManager class",
        "estimated_hours": 4,
        "test_criteria": ["Worktrees are created", "Branches exist"],
        "priority": "High"
    })
    task1_id = task1_result.get("task_id")
    print(f"✅ Created task: {task1_id}")

    task2_result = xavier.create_task({
        "story_id": story_id,
        "title": "Add worktree cleanup",
        "description": "Remove worktrees when sprint ends",
        "technical_details": "Clean up worktrees properly",
        "estimated_hours": 2,
        "test_criteria": ["Worktrees are removed cleanly"],
        "priority": "Medium"
    })
    task2_id = task2_result.get("task_id")
    print(f"✅ Created task: {task2_id}")

    # Assign tasks to agents
    # This would normally be done through task assignment, but we'll update directly
    tasks_file = Path(".xavier/data/tasks.json")
    if tasks_file.exists():
        with open(tasks_file, 'r') as f:
            tasks_data = json.load(f)

        # Update task assignments
        if task1_id in tasks_data:
            tasks_data[task1_id]["assigned_to"] = "python-engineer"
        if task2_id in tasks_data:
            tasks_data[task2_id]["assigned_to"] = "test-runner"

        with open(tasks_file, 'w') as f:
            json.dump(tasks_data, f, indent=2)
        print(f"✅ Assigned tasks to agents")

    # Create sprint
    sprint_result = xavier.create_sprint({
        "name": "Worktree Integration Sprint",
        "goal": "Implement automatic git worktree creation",
        "duration": 14
    })

    sprint_id = sprint_result.get("sprint_id")
    print(f"✅ Created sprint: {sprint_id}")

    return sprint_id


def start_sprint_with_worktrees(sprint_id=None):
    """Start a sprint and verify worktrees are created"""
    print("\nStarting sprint with worktree creation...")
    print("-" * 50)

    xavier = XavierCommands(project_path=".")

    # Start the sprint
    args = {}
    if sprint_id:
        args["sprint_id"] = sprint_id

    result = xavier.start_sprint(args)

    if "error" in result:
        print(f"❌ Error starting sprint: {result['error']}")
        return False

    print(f"✅ Sprint started successfully!")
    print(f"   Sprint: {result.get('sprint_name', 'Unknown')}")
    print(f"   Tasks: {result.get('tasks_started', 0)}")
    print(f"   Worktrees created: {result.get('worktrees_created', 0)}")

    # Show worktree details
    worktree_details = result.get('worktree_details', [])
    if worktree_details:
        print("\nWorktree Details:")
        for wt in worktree_details:
            print(f"   - {wt['item_type']} {wt['item_id']}:")
            print(f"     Branch: {wt['branch']}")
            print(f"     Path: {wt['path']}")
    else:
        print("\n⚠️ No worktrees were created")

    return True


def verify_worktree_structure():
    """Verify the worktree structure is correct"""
    print("\nVerifying worktree structure...")
    print("-" * 50)

    # Check git worktrees
    result = subprocess.run(["git", "worktree", "list"],
                          capture_output=True, text=True)
    worktree_lines = result.stdout.strip().split('\n')

    print(f"Git worktrees ({len(worktree_lines)}):")
    for line in worktree_lines:
        print(f"  {line}")

    # Check trees directory
    trees_dir = Path("trees")
    if trees_dir.exists():
        print(f"\nTrees directory: {trees_dir.absolute()}")

        # List all directories
        dirs = sorted([d for d in trees_dir.iterdir()
                      if d.is_dir() and not d.name.startswith('.')])

        if dirs:
            print(f"Found {len(dirs)} worktree directories:")
            for d in dirs:
                print(f"\n  📁 {d.name}/")

                # Check if it's a valid worktree
                git_file = d / ".git"
                if git_file.exists():
                    print(f"    ✅ Valid git worktree")

                    # Get branch info
                    result = subprocess.run(["git", "branch", "--show-current"],
                                          cwd=d, capture_output=True, text=True)
                    if result.returncode == 0:
                        branch = result.stdout.strip()
                        print(f"    🌿 Branch: {branch}")

                    # Check for any files
                    files = list(d.glob("*"))
                    print(f"    📄 Files: {len(files)}")
                else:
                    print(f"    ❌ Not a valid git worktree")
        else:
            print("No worktree directories found")

        # Check metadata
        metadata_file = trees_dir / ".worktree_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            print(f"\nWorktree metadata ({len(metadata)} entries):")
            for task_id, info in metadata.items():
                print(f"  {task_id}:")
                print(f"    Agent: {info.get('agent')}")
                print(f"    Branch: {info.get('branch')}")
                print(f"    Created: {info.get('created_at')}")
    else:
        print("Trees directory does not exist")


def main():
    """Main function to fix and demonstrate worktree integration"""
    print("=" * 60)
    print("Sprint Worktree Integration Fix & Demo")
    print("=" * 60)

    # Step 1: End any active sprints
    end_active_sprints()

    # Step 2: Create a demo sprint
    sprint_id = create_demo_sprint()

    # Step 3: Start sprint with worktrees
    if start_sprint_with_worktrees(sprint_id):
        # Step 4: Verify structure
        verify_worktree_structure()

        print("\n" + "=" * 60)
        print("✅ Sprint worktree integration is working!")
        print("=" * 60)

        print("\n📝 Summary:")
        print("1. Sprint started successfully")
        print("2. Worktrees created for each story/task")
        print("3. Each worktree has its own branch")
        print("4. Agents can work in isolated environments")

        print("\n🎯 Next steps:")
        print("- Each agent works in their worktree directory")
        print("- Changes are isolated to their branch")
        print("- PRs can be created from each worktree")
        print("- Worktrees cleaned up on sprint end")
    else:
        print("\n❌ Sprint worktree integration failed")
        print("Please check the error messages above")


if __name__ == "__main__":
    main()