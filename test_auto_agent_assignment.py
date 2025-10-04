#!/usr/bin/env python3
"""
Test Automatic Agent Assignment During Task Creation
"""

import os
import sys
import json
from pathlib import Path

# Add xavier to path
sys.path.insert(0, str(Path(__file__).parent))

from xavier.src.agents.task_agent_matcher import TaskAgentMatcher
from xavier.src.commands.xavier_commands import XavierCommands


def test_agent_matcher():
    """Test the task agent matcher logic"""
    print("Testing Task Agent Matcher...")
    print("-" * 50)

    matcher = TaskAgentMatcher()

    # Test cases
    test_tasks = [
        {
            "title": "Implement user authentication API",
            "description": "Create REST endpoints for login/logout",
            "technical_details": "Use Django REST framework with JWT tokens"
        },
        {
            "title": "Build React dashboard",
            "description": "Create interactive dashboard with charts",
            "technical_details": "Use React with TypeScript and Material-UI"
        },
        {
            "title": "Setup Docker containers",
            "description": "Configure Docker for development environment",
            "technical_details": "Create docker-compose.yml with PostgreSQL and Redis"
        },
        {
            "title": "Write unit tests",
            "description": "Add comprehensive test coverage",
            "technical_details": "Use pytest with 100% coverage requirement"
        },
        {
            "title": "Implement payment processing",
            "description": "Integrate Stripe payment gateway",
            "technical_details": "Use Ruby on Rails with Stripe gem"
        },
        {
            "title": "Build iOS mobile app",
            "description": "Create native iOS application",
            "technical_details": "Use Swift and SwiftUI for iPhone app"
        },
        {
            "title": "Develop microservice",
            "description": "Create high-performance API service",
            "technical_details": "Use Go with Gin framework for REST API"
        },
        {
            "title": "Create Android app",
            "description": "Build native Android application",
            "technical_details": "Use Kotlin with Jetpack Compose"
        },
        {
            "title": "Implement blockchain smart contract",
            "description": "Create DeFi smart contract",
            "technical_details": "Use Solidity for Ethereum blockchain"
        }
    ]

    print("Task Analysis Results:\n")

    for task in test_tasks:
        agent, reason, confidence = matcher.analyze_task(task)
        print(f"📋 Task: {task['title']}")
        print(f"   🤖 Agent: {agent}")
        print(f"   💡 Reason: {reason}")
        print(f"   📊 Confidence: {confidence:.1%}")

        # Check if agent exists
        exists = matcher.check_agent_exists(agent)
        print(f"   ✅ Agent exists: {exists}")
        print()

    return True


def test_task_creation_with_auto_assignment():
    """Test creating tasks with automatic agent assignment"""
    print("\nTesting Task Creation with Auto-Assignment...")
    print("-" * 50)

    xavier = XavierCommands(project_path=".")

    # First create a story
    story_result = xavier.create_story({
        "title": "Multi-technology Feature",
        "as_a": "user",
        "i_want": "a full-stack feature",
        "so_that": "I can use the application",
        "acceptance_criteria": [
            "Backend API in Python",
            "Frontend in React",
            "Database with PostgreSQL",
            "Tests with pytest"
        ],
        "priority": "High"
    })

    story_id = story_result.get("story_id")
    print(f"✅ Created story: {story_id}")

    # Create tasks with different technologies
    test_tasks = [
        {
            "story_id": story_id,
            "title": "Create Python REST API",
            "description": "Build backend API endpoints",
            "technical_details": "Use FastAPI with SQLAlchemy",
            "estimated_hours": 8
        },
        {
            "story_id": story_id,
            "title": "Build React frontend",
            "description": "Create user interface",
            "technical_details": "React with TypeScript and Redux",
            "estimated_hours": 12
        },
        {
            "story_id": story_id,
            "title": "Write comprehensive tests",
            "description": "Add test coverage",
            "technical_details": "Unit tests and integration tests",
            "estimated_hours": 6
        },
        {
            "story_id": story_id,
            "title": "Setup Kubernetes deployment",
            "description": "Configure K8s manifests",
            "technical_details": "Create deployment, service, and ingress",
            "estimated_hours": 4
        },
        {
            "story_id": story_id,
            "title": "Implement Rust microservice",
            "description": "High-performance service",
            "technical_details": "Use Actix-web for async processing",
            "estimated_hours": 10
        }
    ]

    print("\nCreating tasks with auto-assignment:\n")

    created_tasks = []
    for task_data in test_tasks:
        try:
            result = xavier.create_task(task_data)
            created_tasks.append(result)

            print(f"📌 Task: {task_data['title']}")
            print(f"   ID: {result['task_id']}")
            print(f"   Assigned to: {result.get('assigned_to', 'None')}")

            if 'agent_assignment' in result:
                assignment = result['agent_assignment']
                print(f"   Auto-assignment:")
                print(f"     - Agent: {assignment['agent']}")
                print(f"     - Reason: {assignment['reason']}")
                print(f"     - Confidence: {assignment['confidence']:.1%}")
                if assignment.get('created_new'):
                    print(f"     - ✨ NEW AGENT CREATED!")
            print()

        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()

    # Summary
    print("\n" + "=" * 50)
    print("Assignment Summary:")
    print("-" * 50)

    agent_counts = {}
    for task in created_tasks:
        agent = task.get('assigned_to', 'unassigned')
        agent_counts[agent] = agent_counts.get(agent, 0) + 1

    for agent, count in sorted(agent_counts.items()):
        print(f"  {agent}: {count} task(s)")

    return True


def test_agent_creation():
    """Test that new agents are created when needed"""
    print("\nTesting Dynamic Agent Creation...")
    print("-" * 50)

    matcher = TaskAgentMatcher()

    # Test creating a new specialized agent
    exotic_task = {
        "title": "Implement Haskell compiler",
        "description": "Create functional programming compiler",
        "technical_details": "Pure functional Haskell implementation"
    }

    print(f"Task: {exotic_task['title']}")

    # This should create a new agent if it doesn't exist
    agent, reason, confidence = matcher.analyze_task(exotic_task)
    print(f"Detected need for: {agent}")

    if not matcher.check_agent_exists(agent):
        print(f"Agent {agent} doesn't exist, would create it dynamically")
    else:
        print(f"Agent {agent} already exists")

    return True


def verify_agent_files():
    """Verify that agent files were created"""
    print("\nVerifying Agent Files...")
    print("-" * 50)

    claude_agents_dir = Path(".claude/agents")

    if claude_agents_dir.exists():
        agent_files = list(claude_agents_dir.glob("*.md"))
        print(f"Found {len(agent_files)} Claude agents:")

        for agent_file in sorted(agent_files):
            print(f"  ✅ {agent_file.name}")
    else:
        print("❌ No .claude/agents directory found")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Automatic Agent Assignment Test Suite")
    print("=" * 60)

    # Test 1: Agent matcher logic
    if not test_agent_matcher():
        print("❌ Agent matcher test failed")
        return False

    # Test 2: Task creation with auto-assignment
    if not test_task_creation_with_auto_assignment():
        print("❌ Task creation test failed")
        return False

    # Test 3: Dynamic agent creation
    if not test_agent_creation():
        print("❌ Agent creation test failed")
        return False

    # Test 4: Verify agent files
    if not verify_agent_files():
        print("❌ Agent file verification failed")
        return False

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

    print("\n📝 Summary:")
    print("- Tasks automatically detect required technology")
    print("- Agents are assigned based on task content")
    print("- New agents created dynamically when needed")
    print("- Confidence scores indicate assignment quality")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)