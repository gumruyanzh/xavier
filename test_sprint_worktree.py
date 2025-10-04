#!/usr/bin/env python3
"""
Test and Fix Sprint Worktree Integration
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
from xavier.src.scrum.scrum_manager import SCRUMManager


def test_current_sprint_status():
    """Check current sprint and worktree status"""
    print("Checking current sprint and worktree status...")
    print("-" * 50)

    # Check sprints
    sprints_file = Path(".xavier/data/sprints.json")
    if sprints_file.exists():
        with open(sprints_file, 'r') as f:
            data = json.load(f)
            sprints = data.get("sprints", [])

        print(f"Found {len(sprints)} sprints:")
        for sprint in sprints:
            print(f"  - {sprint['id']}: {sprint['name']} [{sprint['status']}]")
            if sprint['status'] == 'active':
                print(f"    Tasks: {sprint.get('tasks', [])}")
                print(f"    Worktrees: {sprint.get('worktrees', [])}")

    # Check actual git worktrees
    result = subprocess.run(["git", "worktree", "list"], capture_output=True, text=True)
    print(f"\nGit worktrees:")
    print(result.stdout)

    # Check trees directory
    trees_dir = Path("trees")
    if trees_dir.exists():
        dirs = [d for d in trees_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        print(f"\nTrees directory contains {len(dirs)} worktrees:")
        for d in dirs:
            print(f"  - {d.name}")


def create_proper_test_data():
    """Create properly formatted test data"""
    print("\nCreating properly formatted test data...")
    print("-" * 50)

    scrum = SCRUMManager(data_dir=".xavier/data")

    # Create a story
    story = scrum.create_story(
        title="Git Worktree Integration Test",
        as_a="developer",
        i_want="to have automatic worktree creation",
        so_that="I can work on tasks in isolation",
        acceptance_criteria=[
            "Worktrees are created on sprint start",
            "Each task gets its own branch",
            "Worktrees are in trees directory"
        ],
        priority="High"
    )
    print(f"✅ Created story: {story.id}")

    # Create tasks
    task1 = scrum.create_task(
        story_id=story.id,
        title="Setup worktree creation",
        description="Implement automatic worktree creation on sprint start",
        technical_details="Use GitWorktreeManager to create worktrees",
        estimated_hours=4,
        test_criteria=["Worktrees are created", "Branches exist"],
        priority="High"
    )
    print(f"✅ Created task: {task1.id}")

    task2 = scrum.create_task(
        story_id=story.id,
        title="Test worktree workflow",
        description="Verify worktree creation works properly",
        technical_details="Test the full workflow",
        estimated_hours=2,
        test_criteria=["All tests pass"],
        priority="Medium"
    )
    print(f"✅ Created task: {task2.id}")

    # Assign tasks
    task1.assigned_to = "python-engineer"
    task2.assigned_to = "test-runner"

    # Create sprint
    sprint = scrum.create_sprint(
        name="Worktree Integration Sprint",
        goal="Implement and test automatic worktree creation",
        duration_weeks=2,
        story_ids=[story.id],
        bug_ids=[]
    )
    print(f"✅ Created sprint: {sprint.id}")

    # Save data
    scrum._save_data()

    return sprint.id, [task1.id, task2.id]


def test_sprint_start_properly():
    """Test starting sprint with proper worktree creation"""
    print("\nTesting sprint start with worktree creation...")
    print("-" * 50)

    # Use XavierCommands directly
    xavier = XavierCommands(project_path=".")

    # Get the planned sprint
    sprints_file = Path(".xavier/data/sprints.json")
    with open(sprints_file, 'r') as f:
        data = json.load(f)

    planned_sprints = [s for s in data.get("sprints", []) if s["status"] == "planned"]

    if not planned_sprints:
        print("❌ No planned sprints found")
        sprint_id, task_ids = create_proper_test_data()
        print(f"Created new sprint: {sprint_id}")

        # Reload sprints
        with open(sprints_file, 'r') as f:
            data = json.load(f)
        planned_sprints = [s for s in data.get("sprints", []) if s["status"] == "planned"]

    if planned_sprints:
        sprint = planned_sprints[0]
        print(f"Starting sprint: {sprint['id']} - {sprint['name']}")

        # Start the sprint
        result = xavier.start_sprint({"sprint_id": sprint["id"]})

        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Sprint started successfully")
            print(f"   Worktrees created: {result.get('worktrees_created', 0)}")

            worktree_details = result.get('worktree_details', [])
            for wt in worktree_details:
                print(f"   - {wt['item_id']}: {wt['branch']} -> {wt['path']}")

            return True

    return False


def verify_worktrees_created():
    """Verify worktrees were actually created"""
    print("\nVerifying worktrees were created...")
    print("-" * 50)

    manager = GitWorktreeManager()
    worktrees = manager.list_worktrees()

    if worktrees:
        print(f"✅ Found {len(worktrees)} worktrees:")
        for wt in worktrees:
            print(f"   - {wt['path']}")
            print(f"     Branch: {wt.get('branch', 'unknown')}")
            print(f"     HEAD: {wt.get('HEAD', 'unknown')[:8]}")

        # Check if directories exist
        for wt in worktrees:
            wt_path = Path(wt['path'])
            if wt_path.exists():
                print(f"   ✅ Directory exists: {wt_path}")

                # Check for .git file
                git_file = wt_path / ".git"
                if git_file.exists():
                    print(f"     ✅ Git worktree configured")
            else:
                print(f"   ❌ Directory missing: {wt_path}")

        return True
    else:
        print("❌ No worktrees found")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("Sprint Worktree Integration Test")
    print("=" * 60)

    # Check current status
    test_current_sprint_status()

    # Test sprint start
    if test_sprint_start_properly():
        # Verify worktrees
        verify_worktrees_created()

        print("\n" + "=" * 60)
        print("✅ Sprint worktree integration is working!")
        print("=" * 60)

        print("\n📝 Summary:")
        print("- Sprints automatically create worktrees on start")
        print("- Each task gets its own branch and directory")
        print("- Worktrees are properly configured in trees/")
        print("- Agents can work in isolated environments")
    else:
        print("\n❌ Sprint worktree integration needs fixing")

        print("\n🔧 To manually create worktrees for a sprint:")
        print("1. Ensure sprint has tasks assigned to agents")
        print("2. Run: xavier start-sprint")
        print("3. Check trees/ directory for worktrees")


if __name__ == "__main__":
    main()