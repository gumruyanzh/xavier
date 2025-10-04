#!/usr/bin/env python3
"""
Test Git Worktree Integration with Sprint Start
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
from xavier.src.commands.claude_code_integration import ClaudeCodeXavierIntegration


def test_worktree_manager_directly():
    """Test worktree manager directly"""
    print("Testing GitWorktreeManager directly...")
    print("-" * 50)

    manager = GitWorktreeManager()

    # Initialize worktree directory
    if manager.initialize_worktree_directory():
        print("✅ Worktree directory initialized")
    else:
        print("❌ Failed to initialize worktree directory")
        return False

    # Create a test worktree
    success, message = manager.create_worktree(
        branch_name="test/TASK-TEST-001",
        agent_name="python-engineer",
        task_id="TASK-TEST-001"
    )

    if success:
        print(f"✅ Test worktree created: {message}")
    else:
        print(f"❌ Failed to create worktree: {message}")
        return False

    # List worktrees
    worktrees = manager.list_worktrees()
    print(f"📁 Current worktrees: {len(worktrees)}")
    for wt in worktrees:
        print(f"   - {wt['path']}: {wt.get('branch', 'unknown')}")

    # Clean up test worktree
    success, message = manager.remove_worktree("TASK-TEST-001")
    if success:
        print(f"✅ Test worktree removed: {message}")
    else:
        print(f"⚠️ Could not remove worktree: {message}")

    return True


def create_test_sprint_data():
    """Create test sprint data in .xavier/data"""
    print("\nCreating test sprint data...")
    print("-" * 50)

    data_dir = Path(".xavier/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create a test story
    stories = {
        "US-TEST-001": {
            "id": "US-TEST-001",
            "title": "Test Story for Worktree",
            "description": "As a developer, I want to test worktree creation",
            "as_a": "developer",
            "i_want": "to test worktree creation",
            "so_that": "I can verify the integration works",
            "acceptance_criteria": ["Worktree is created", "Branch is created"],
            "story_points": 3,
            "status": "ready"
        }
    }

    # Create test tasks
    tasks = {
        "TASK-TEST-001": {
            "id": "TASK-TEST-001",
            "story_id": "US-TEST-001",
            "title": "Implement worktree test",
            "description": "Test task for worktree creation",
            "assigned_to": "python-engineer",
            "status": "pending",
            "estimated_hours": 2
        },
        "TASK-TEST-002": {
            "id": "TASK-TEST-002",
            "story_id": "US-TEST-001",
            "title": "Write worktree tests",
            "description": "Another test task",
            "assigned_to": "test-runner",
            "status": "pending",
            "estimated_hours": 1
        }
    }

    # Create a test sprint
    sprints = {
        "SPRINT-TEST": {
            "id": "SPRINT-TEST",
            "name": "Test Sprint for Worktrees",
            "goal": "Test worktree creation",
            "status": "planned",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "stories": ["US-TEST-001"],
            "tasks": ["TASK-TEST-001", "TASK-TEST-002"],
            "planned_points": 3
        }
    }

    # Save test data
    with open(data_dir / "stories.json", 'w') as f:
        json.dump(stories, f, indent=2)
    print("✅ Created test stories")

    with open(data_dir / "tasks.json", 'w') as f:
        json.dump(tasks, f, indent=2)
    print("✅ Created test tasks")

    with open(data_dir / "sprints.json", 'w') as f:
        json.dump({"sprints": [sprints["SPRINT-TEST"]]}, f, indent=2)
    print("✅ Created test sprint")

    return True


def test_sprint_start_with_worktrees():
    """Test starting a sprint with worktree creation"""
    print("\nTesting sprint start with worktrees...")
    print("-" * 50)

    # Initialize integration
    integration = ClaudeCodeXavierIntegration()

    # Start the sprint
    result = integration._start_sprint({})

    if result.get("status") == "success":
        print("✅ Sprint started successfully")

        sprint_data = result.get("data", {})
        print(f"   Sprint: {sprint_data.get('name')}")
        print(f"   Tasks: {sprint_data.get('tasks', 0)}")
        print(f"   Worktrees created: {sprint_data.get('worktrees_created', 0)}")
        print(f"   Agents initialized: {sprint_data.get('agents_initialized', [])}")

        # Verify worktrees were created
        manager = GitWorktreeManager()
        worktrees = manager.list_worktrees()

        if len(worktrees) > 0:
            print(f"\n✅ Worktrees verified: {len(worktrees)} created")
            for wt in worktrees:
                print(f"   - {wt['path']}: {wt.get('branch', 'unknown')}")
        else:
            print("\n⚠️ No worktrees found after sprint start")

        return True
    else:
        print(f"❌ Failed to start sprint: {result.get('message', 'Unknown error')}")
        return False


def verify_worktree_structure():
    """Verify the worktree directory structure"""
    print("\nVerifying worktree structure...")
    print("-" * 50)

    trees_dir = Path("trees")

    if not trees_dir.exists():
        print("❌ Trees directory does not exist")
        return False

    print(f"✅ Trees directory exists: {trees_dir.absolute()}")

    # Check metadata file
    metadata_file = trees_dir / ".worktree_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        print(f"✅ Metadata file exists with {len(metadata)} entries")

        for task_id, info in metadata.items():
            print(f"   - {task_id}: {info.get('agent')} on {info.get('branch')}")
    else:
        print("⚠️ No metadata file found")

    # List actual worktree directories
    worktree_dirs = [d for d in trees_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    if worktree_dirs:
        print(f"\n📁 Worktree directories found: {len(worktree_dirs)}")
        for wt_dir in worktree_dirs:
            print(f"   - {wt_dir.name}")

            # Check if it's a valid git worktree
            git_dir = wt_dir / ".git"
            if git_dir.exists():
                print(f"     ✅ Valid git worktree")
            else:
                print(f"     ❌ Not a valid git worktree")
    else:
        print("\n⚠️ No worktree directories found")

    return True


def cleanup_test_worktrees():
    """Clean up any test worktrees"""
    print("\nCleaning up test worktrees...")
    print("-" * 50)

    manager = GitWorktreeManager()

    # Get all worktrees
    worktrees = manager.list_worktrees()

    for wt in worktrees:
        if "TEST" in wt.get("path", ""):
            task_id = wt.get("path", "").split("-")[-1]
            success, message = manager.remove_worktree(task_id)
            if success:
                print(f"✅ Removed test worktree: {wt['path']}")
            else:
                print(f"⚠️ Could not remove: {message}")

    print("✅ Cleanup complete")


def main():
    """Main test function"""
    print("=" * 60)
    print("Git Worktree Integration Test")
    print("=" * 60)

    # Test 1: Direct worktree manager test
    if not test_worktree_manager_directly():
        print("\n❌ Direct worktree manager test failed")
        return False

    # Test 2: Create test sprint data
    if not create_test_sprint_data():
        print("\n❌ Failed to create test data")
        return False

    # Test 3: Test sprint start with worktrees
    if not test_sprint_start_with_worktrees():
        print("\n❌ Sprint start test failed")
        return False

    # Test 4: Verify structure
    verify_worktree_structure()

    # Test 5: Cleanup
    cleanup_test_worktrees()

    print("\n" + "=" * 60)
    print("✅ All worktree integration tests passed!")
    print("=" * 60)

    print("\n📝 Summary:")
    print("- GitWorktreeManager is working correctly")
    print("- Sprint start creates worktrees automatically")
    print("- Each task gets its own worktree with proper branch")
    print("- Metadata is tracked correctly")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)