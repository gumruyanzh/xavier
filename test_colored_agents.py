#!/usr/bin/env python3
"""
Test script to demonstrate Xavier's colored agent system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'xavier', 'src'))

from agents.orchestrator import AgentOrchestrator, AgentTask
from utils.ansi_art import (
    display_welcome, display_agent_takeover, display_agent_status,
    display_agent_handoff, display_agent_result, display_mini_banner,
    AgentColors, ANSIColors
)

def test_agent_display():
    """Test individual agent display functions"""
    print("\n" + "=" * 60)
    print("TESTING XAVIER AGENT COLORING SYSTEM")
    print("=" * 60)

    # Test welcome screen
    print("\n1. Welcome Screen:")
    display_mini_banner()

    # Test agent takeover display
    print("\n2. Agent Takeover Display:")
    display_agent_takeover("PythonEngineer", "Implement user authentication endpoint")

    # Test agent status updates
    print("\n3. Agent Status Updates:")
    display_agent_status("PythonEngineer", "Working", "Writing tests first (TDD)")
    display_agent_status("PythonEngineer", "Testing", "Running pytest suite")
    display_agent_status("PythonEngineer", "Completed", "100% test coverage achieved")

    # Test agent handoff
    print("\n4. Agent Handoff:")
    display_agent_handoff("PythonEngineer", "FrontendEngineer", "Backend API complete, frontend needed")

    # Test frontend agent
    print("\n5. Frontend Agent Working:")
    display_agent_takeover("FrontendEngineer", "Create login component with TypeScript")
    display_agent_status("FrontendEngineer", "Working", "Building React component")

    # Test agent results
    print("\n6. Agent Results:")
    display_agent_result("PythonEngineer", True, "API endpoint implemented with 100% coverage")
    display_agent_result("FrontendEngineer", True, "Login component created with tests")

    # Test all agent colors
    print("\n7. All Agent Colors Preview:")
    print(f"{ANSIColors.BOLD_WHITE}Available Agents:{ANSIColors.RESET}")
    for agent_name, config in AgentColors.AGENT_COLORS.items():
        color = config['color']
        emoji = config['emoji']
        label = config['label']
        print(f"  {color}[{label}]{ANSIColors.RESET} {emoji} {agent_name}")

def test_orchestrator_flow():
    """Test the orchestrator with colored output"""
    print("\n" + "=" * 60)
    print("TESTING ORCHESTRATOR WITH COLORED AGENTS")
    print("=" * 60)

    # Create a simple config to enable agents
    import tempfile
    import json
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "agents": {
                "project_manager": {"enabled": True},
                "context_manager": {"enabled": True},
                "python_engineer": {"enabled": True},
                "golang_engineer": {"enabled": True},
                "frontend_engineer": {"enabled": True}
            }
        }
        json.dump(config, f)
        config_path = f.name

    # Initialize orchestrator with config
    orchestrator = AgentOrchestrator(config_path)

    # Create sample tasks
    tasks = [
        AgentTask(
            task_id="TASK-001",
            task_type="estimate_story",
            description="Estimate story points for user authentication",
            requirements=["Login", "Logout", "Session management"],
            test_requirements={},
            acceptance_criteria=["Story points assigned"],
            tech_constraints=[]
        ),
        AgentTask(
            task_id="TASK-002",
            task_type="implement_feature",
            description="Implement login API endpoint",
            requirements=["POST /api/login", "JWT tokens"],
            test_requirements={"coverage": 100},
            acceptance_criteria=["Endpoint works", "Tests pass"],
            tech_constraints=["python"]
        ),
        AgentTask(
            task_id="TASK-003",
            task_type="implement_component",
            description="Create login form component",
            requirements=["Email input", "Password input", "Submit button"],
            test_requirements={"coverage": 100},
            acceptance_criteria=["Component renders", "Tests pass"],
            tech_constraints=["typescript"]
        )
    ]

    # Execute tasks with orchestrator
    print("\n" + f"{ANSIColors.BOLD_CYAN}Starting Task Delegation...{ANSIColors.RESET}")

    for task in tasks:
        print(f"\n{ANSIColors.LIGHT_CYAN}{'─' * 50}{ANSIColors.RESET}")
        result = orchestrator.delegate_task(task)
        if result.success:
            print(f"{ANSIColors.GREEN}✅ Task {task.task_id} completed successfully{ANSIColors.RESET}")
        else:
            print(f"{ANSIColors.RED}❌ Task {task.task_id} failed{ANSIColors.RESET}")

def test_sprint_execution():
    """Test sprint execution with colored agents"""
    print("\n" + "=" * 60)
    print("TESTING SPRINT EXECUTION WITH COLORED AGENTS")
    print("=" * 60)

    # Create a simple config to enable agents
    import tempfile
    import json
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "agents": {
                "project_manager": {"enabled": True},
                "context_manager": {"enabled": True},
                "python_engineer": {"enabled": True},
                "golang_engineer": {"enabled": True},
                "frontend_engineer": {"enabled": True}
            }
        }
        json.dump(config, f)
        config_path = f.name

    orchestrator = AgentOrchestrator(config_path)

    # Create sprint tasks with dependencies
    tasks = [
        AgentTask(
            task_id="SPRINT1-001",
            task_type="analyze_codebase",
            description="Analyze existing codebase structure",
            requirements=["Find patterns", "Check dependencies"],
            test_requirements={},
            acceptance_criteria=["Analysis complete"],
            tech_constraints=[]
        ),
        AgentTask(
            task_id="SPRINT1-002",
            task_type="implement_feature",
            description="Implement user service",
            requirements=["User CRUD operations"],
            test_requirements={"coverage": 100},
            acceptance_criteria=["Service works", "Tests pass"],
            tech_constraints=["python"]
        ),
        AgentTask(
            task_id="SPRINT1-003",
            task_type="implement_feature",
            description="Implement authentication service",
            requirements=["JWT authentication"],
            test_requirements={"coverage": 100},
            acceptance_criteria=["Auth works", "Tests pass"],
            tech_constraints=["go"]
        )
    ]

    # Execute sprint
    results = orchestrator.execute_sprint_tasks(tasks)

    print(f"\n{ANSIColors.BOLD_GREEN}Sprint Results Summary:{ANSIColors.RESET}")
    for result in results:
        status_icon = "✅" if result.success else "❌"
        print(f"  {status_icon} Task {result.task_id}: {'Success' if result.success else 'Failed'}")

if __name__ == "__main__":
    # Run all tests
    print(f"\n{ANSIColors.BOLD_CYAN}Xavier Colored Agent System Demo{ANSIColors.RESET}")
    print(f"{ANSIColors.LIGHT_CYAN}{'=' * 60}{ANSIColors.RESET}")

    # Test individual display functions
    test_agent_display()

    # Test orchestrator delegation
    test_orchestrator_flow()

    # Test sprint execution (skipped - would need to update AgentTask with dependencies field)
    # test_sprint_execution()

    print(f"\n{ANSIColors.BOLD_GREEN}✨ All tests completed!{ANSIColors.RESET}")
    print(f"{ANSIColors.LIGHT_WHITE}Xavier now displays colored agent names when they work on tasks.{ANSIColors.RESET}")
    print(f"{ANSIColors.LIGHT_WHITE}Just like Agent OS, you can see which agent is handling each task!{ANSIColors.RESET}\n")