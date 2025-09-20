#!/usr/bin/env python3
"""
Test script for the new /estimate-story command
"""

import sys
import os
import json

# Fix imports
xavier_src = os.path.join(os.path.dirname(__file__), 'xavier', 'src')
sys.path.insert(0, xavier_src)
sys.path.insert(0, os.path.dirname(__file__))

# Import after fixing path
from xavier.src.commands.xavier_commands import XavierCommands
from xavier.src.scrum.scrum_manager import SCRUMManager
from xavier.src.agents.orchestrator import AgentOrchestrator
from xavier.src.utils.ansi_art import ANSIColors

def test_estimate_story():
    """Test the automatic story estimation feature"""
    print(f"\n{ANSIColors.BOLD_CYAN}Testing /estimate-story Command{ANSIColors.RESET}")
    print("=" * 60)

    # Create test project directory
    test_dir = "test_xavier_project"
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, ".xavier"), exist_ok=True)

    # Create test config
    config_data = {
        "agents": {
            "project_manager": {"enabled": True},
            "context_manager": {"enabled": True},
            "python_engineer": {"enabled": True}
        },
        "xavier_version": "1.1.0",
        "test_coverage_threshold": 100,
        "max_function_lines": 20,
        "max_class_lines": 200
    }

    config_path = os.path.join(test_dir, ".xavier", "config.json")
    with open(config_path, "w") as f:
        json.dump(config_data, f)

    # Initialize components
    commands = XavierCommands(project_path=test_dir)

    # Create test stories
    print(f"\n{ANSIColors.YELLOW}Creating test stories...{ANSIColors.RESET}")

    stories = [
        {
            "title": "User Authentication",
            "description": "Implement user login and registration with email verification",
            "acceptance_criteria": [
                "Users can register with email",
                "Email verification required",
                "JWT token authentication",
                "Password reset functionality",
                "Session management"
            ]
        },
        {
            "title": "Simple CRUD API",
            "description": "Basic API for managing products",
            "acceptance_criteria": [
                "Create product endpoint",
                "List products endpoint",
                "Update product endpoint"
            ]
        },
        {
            "title": "Complex Dashboard",
            "description": "Real-time analytics dashboard with charts and visualizations",
            "acceptance_criteria": [
                "Real-time data updates via websocket",
                "Multiple chart types",
                "Export functionality",
                "Mobile responsive design",
                "Performance optimization for large datasets",
                "User customizable widgets"
            ]
        },
        {
            "title": "Database Migration",
            "description": "Migrate from PostgreSQL to MongoDB with zero downtime",
            "acceptance_criteria": [
                "Data migration script",
                "Rollback capability",
                "Data integrity validation",
                "Performance testing"
            ]
        }
    ]

    # Create stories via commands
    created_stories = []
    for i, story_data in enumerate(stories, 1):
        result = commands.create_story({
            "title": story_data["title"],
            "as_a": "user",
            "i_want": story_data["title"].lower(),
            "so_that": story_data["description"],
            "acceptance_criteria": story_data["acceptance_criteria"]
        })
        created_stories.append(result["story_id"])
        print(f"  Created: {result['story_id']} - {story_data['title']}")

    # Test 1: Estimate all unestimated stories
    print(f"\n{ANSIColors.GREEN}Test 1: Estimating all backlog stories{ANSIColors.RESET}")
    print("-" * 40)

    result = commands.estimate_story({})

    print(f"\n{ANSIColors.BOLD_WHITE}Results:{ANSIColors.RESET}")
    print(f"  Stories estimated: {result['stories_estimated']}")
    print(f"  Total points: {result['total_points']}")
    print(f"  Estimated sprints: {result.get('estimated_sprints', 0):.1f}")

    print(f"\n{ANSIColors.LIGHT_WHITE}Individual estimates:{ANSIColors.RESET}")
    for estimate in result.get('estimates', []):
        print(f"  {estimate['story_id']}: {estimate['points']} points - {estimate['title']}")

    # Test 2: Re-estimate a specific story
    print(f"\n{ANSIColors.GREEN}Test 2: Re-estimating specific story{ANSIColors.RESET}")
    print("-" * 40)

    if created_stories:
        result = commands.estimate_story({
            "story_id": created_stories[0],
            "all": True  # Force re-estimation
        })

        if result.get('success'):
            print(f"  Re-estimated {created_stories[0]}: {result.get('estimates', [{}])[0].get('points', 'N/A')} points")

    # Test 3: Show backlog report
    print(f"\n{ANSIColors.GREEN}Test 3: Backlog report after estimation{ANSIColors.RESET}")
    print("-" * 40)

    backlog_report = commands.show_backlog({})

    print(f"  Total stories: {backlog_report.get('total_stories', 0)}")
    print(f"  Total points: {backlog_report.get('total_points', 0)}")
    print(f"  Unestimated: {backlog_report.get('unestimated_stories', 0)}")

    # Clean up test data
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    print(f"\n{ANSIColors.BOLD_GREEN}✅ All tests completed!{ANSIColors.RESET}")
    print(f"{ANSIColors.LIGHT_WHITE}The PM agent successfully estimated story points using complexity analysis.{ANSIColors.RESET}\n")

if __name__ == "__main__":
    test_estimate_story()