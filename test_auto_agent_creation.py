#!/usr/bin/env python3
"""
Test script for automatic agent creation functionality
This demonstrates how Xavier automatically creates agents for unsupported languages
"""

import sys
import os
import json
from datetime import datetime

# Add xavier to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'xavier', 'src'))

from agents.orchestrator import AgentOrchestrator
from agents.base_agent import AgentTask
from agents.dynamic_agent_factory import get_agent_factory

def test_auto_agent_creation():
    """Test automatic creation of agents for various languages"""

    print("\n" + "="*70)
    print("XAVIER FRAMEWORK - AUTOMATIC AGENT CREATION TEST")
    print("="*70 + "\n")

    # Initialize orchestrator
    print("📚 Initializing Xavier Orchestrator...")
    orchestrator = AgentOrchestrator()

    # Test cases for different languages
    test_cases = [
        {
            "name": "Java Spring Boot Task",
            "task": AgentTask(
                task_id="TEST-001",
                task_type="implement_feature",
                description="Create a REST API endpoint in Java using Spring Boot",
                requirements=["Use Spring Boot framework", "Implement GET /api/users"],
                test_requirements={"framework": "junit", "coverage": 100},
                acceptance_criteria=["Endpoint returns JSON", "Unit tests pass"],
                tech_constraints=["java", "spring"],
                working_dir=None
            )
        },
        {
            "name": "Rust WebSocket Server",
            "task": AgentTask(
                task_id="TEST-002",
                task_type="implement_feature",
                description="Implement a WebSocket server in Rust using Tokio",
                requirements=["Use Tokio async runtime", "Handle multiple connections"],
                test_requirements={"framework": "cargo test", "coverage": 100},
                acceptance_criteria=["Server handles connections", "Tests pass"],
                tech_constraints=["rust", "tokio"],
                working_dir=None
            )
        },
        {
            "name": "Kotlin Android App",
            "task": AgentTask(
                task_id="TEST-003",
                task_type="implement_feature",
                description="Create an Android activity in Kotlin with Jetpack Compose",
                requirements=["Use Jetpack Compose", "Material Design 3"],
                test_requirements={"framework": "junit", "coverage": 100},
                acceptance_criteria=["UI renders correctly", "Tests pass"],
                tech_constraints=["kotlin", "android"],
                working_dir=None
            )
        },
        {
            "name": "Elixir Phoenix API",
            "task": AgentTask(
                task_id="TEST-004",
                task_type="implement_feature",
                description="Build a GraphQL API with Elixir and Phoenix",
                requirements=["Use Phoenix framework", "Implement GraphQL schema"],
                test_requirements={"framework": "exunit", "coverage": 100},
                acceptance_criteria=["GraphQL queries work", "Tests pass"],
                tech_constraints=["elixir", "phoenix"],
                working_dir=None
            )
        },
        {
            "name": "Swift iOS Feature",
            "task": AgentTask(
                task_id="TEST-005",
                task_type="implement_feature",
                description="Implement a SwiftUI view for iOS app",
                requirements=["Use SwiftUI", "Support dark mode"],
                test_requirements={"framework": "xctest", "coverage": 100},
                acceptance_criteria=["View renders", "Dark mode works"],
                tech_constraints=["swift", "swiftui"],
                working_dir=None
            )
        }
    ]

    # Run test cases
    successful = 0
    failed = 0

    for test_case in test_cases:
        print(f"\n{'='*50}")
        print(f"🧪 Testing: {test_case['name']}")
        print(f"{'='*50}")

        task = test_case["task"]

        # Check if agent exists before task
        initial_agents = list(orchestrator.agents.keys())
        print(f"📋 Initial agents: {initial_agents}")

        # Select agent for task (this should auto-create if needed)
        selected_agent = orchestrator._select_agent_for_task(task)

        if selected_agent:
            print(f"✅ Agent selected: {selected_agent.name}")
            print(f"   Display name: {selected_agent.display_name}")
            print(f"   Capabilities: {selected_agent.capabilities.languages}")

            # Check if new agent was created
            final_agents = list(orchestrator.agents.keys())
            if len(final_agents) > len(initial_agents):
                new_agents = set(final_agents) - set(initial_agents)
                print(f"🎉 NEW AGENT AUTO-CREATED: {new_agents}")

                # Check if YAML file was created
                for agent_name in new_agents:
                    yaml_file = f".xavier/agents/{agent_name.replace('-', '_')}.yaml"
                    if os.path.exists(yaml_file):
                        print(f"📄 YAML file created: {yaml_file}")
                    else:
                        print(f"⚠️  YAML file not found: {yaml_file}")

            successful += 1
        else:
            print(f"❌ Failed to select/create agent for task")
            failed += 1

    # Print summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success rate: {(successful/(successful+failed)*100):.1f}%")

    # List all available agent templates
    print(f"\n{'='*70}")
    print("🎯 AVAILABLE AGENT TEMPLATES")
    print(f"{'='*70}")
    factory = get_agent_factory()
    templates = factory.list_available_templates()

    for i, lang in enumerate(templates, 1):
        template_info = factory.get_template_info(lang)
        if template_info:
            print(f"{i:2}. {template_info['emoji']} {template_info['display_name']:<25} ({lang})")

    print(f"\nTotal templates available: {len(templates)}")

    return successful, failed

if __name__ == "__main__":
    try:
        successful, failed = test_auto_agent_creation()
        exit_code = 0 if failed == 0 else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)