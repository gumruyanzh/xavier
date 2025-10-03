#!/usr/bin/env python3
"""
Xavier Self-Initialization Script
Initialize Xavier Framework to manage its own development
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add Xavier to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xavier.src.commands.xavier_commands import XavierCommands
from xavier.src.agents.dynamic_agent_factory import DynamicAgentFactory


class XavierSelfHost:
    """Initialize and manage Xavier's self-hosted development"""

    def __init__(self):
        self.xavier_root = Path(__file__).parent
        self.commands = XavierCommands(str(self.xavier_root))
        self.factory = DynamicAgentFactory(str(self.xavier_root / ".xavier"))

    def initialize(self):
        """Initialize Xavier for self-development"""
        print("\n" + "="*60)
        print("🔄 XAVIER SELF-HOSTING INITIALIZATION")
        print("Using Xavier to develop Xavier")
        print("="*60 + "\n")

        # Step 1: Create Xavier project
        print("📁 Creating Xavier project configuration...")
        self.create_xavier_project()

        # Step 2: Create specialized agents
        print("🤖 Creating Xavier development agents...")
        self.create_xavier_agents()

        # Step 3: Create initial epics and stories
        print("📋 Creating Xavier development stories...")
        self.create_xavier_stories()

        # Step 4: Create development roadmap
        print("🗺️ Creating Xavier development roadmap...")
        self.create_xavier_roadmap()

        # Step 5: Set up first sprint
        print("🏃 Setting up initial development sprint...")
        self.create_initial_sprint()

        print("\n" + "="*60)
        print("✅ Xavier is now self-hosted!")
        print("Use Xavier commands to develop Xavier")
        print("="*60 + "\n")

    def create_xavier_project(self):
        """Create Xavier project configuration"""
        result = self.commands.create_project({
            "name": "Xavier Framework",
            "description": """
                Enterprise-grade SCRUM development framework for Claude Code with:
                - Agent orchestration system with 25+ language support
                - Test-first development enforcement (TDD)
                - Git worktree integration for parallel development
                - Dynamic agent creation for any technology
                - Clean Code and SOLID principles validation
                - Sequential task execution with dependencies
                - Comprehensive SCRUM management (stories, tasks, bugs, sprints)
            """,
            "tech_stack": {
                "backend": {
                    "language": "python",
                    "framework": "custom",
                    "version": "3.8+"
                },
                "testing": {
                    "frameworks": ["pytest", "unittest"],
                    "coverage": "100% required"
                },
                "architecture": {
                    "patterns": ["command", "factory", "strategy", "observer"],
                    "style": "agent-based"
                },
                "ci_cd": {
                    "platforms": ["github_actions"],
                    "deployment": "pip/curl"
                }
            },
            "project_type": "framework",
            "auto_generate_stories": False,  # We'll create custom stories
            "auto_setup_agents": False  # We'll create specialized agents
        })
        print(f"  ✓ Xavier project created: {result.get('project', {}).get('name')}")

    def create_xavier_agents(self):
        """Create specialized agents for Xavier development"""

        agents = [
            {
                "name": "xavier-architect",
                "display_name": "Xavier Architect",
                "color": "yellow",
                "emoji": "🏛️",
                "skills": [
                    "framework_architecture",
                    "design_patterns",
                    "api_design",
                    "agent_orchestration",
                    "command_pattern",
                    "technical_debt_analysis"
                ],
                "experience": "Expert in framework design and agent-based architectures",
                "languages": ["python", "yaml", "json"],
                "frameworks": ["command_pattern", "factory_pattern", "observer_pattern"]
            },
            {
                "name": "xavier-core-engineer",
                "display_name": "Xavier Core Engineer",
                "color": "cyan",
                "emoji": "⚙️",
                "skills": [
                    "core_framework_development",
                    "agent_implementation",
                    "scrum_features",
                    "command_system",
                    "worktree_management",
                    "dynamic_agent_creation"
                ],
                "experience": "Specializes in Xavier Framework core functionality",
                "languages": ["python"],
                "frameworks": ["xavier", "scrum", "agent_orchestration"]
            },
            {
                "name": "xavier-test-engineer",
                "display_name": "Xavier Test Engineer",
                "color": "green",
                "emoji": "🧪",
                "skills": [
                    "meta_testing",
                    "recursive_testing",
                    "test_coverage_validation",
                    "agent_boundary_testing",
                    "integration_testing",
                    "self_testing"
                ],
                "experience": "Expert in testing frameworks testing themselves",
                "languages": ["python"],
                "frameworks": ["pytest", "unittest", "coverage"]
            },
            {
                "name": "xavier-docs-engineer",
                "display_name": "Xavier Documentation Engineer",
                "color": "blue",
                "emoji": "📚",
                "skills": [
                    "technical_documentation",
                    "api_documentation",
                    "command_documentation",
                    "agent_documentation",
                    "tutorial_creation",
                    "changelog_management"
                ],
                "experience": "Maintains Xavier's comprehensive documentation",
                "languages": ["markdown", "python"],
                "frameworks": ["mkdocs", "sphinx"]
            }
        ]

        for agent_config in agents:
            result = self.commands.create_agent(agent_config)
            if result.get("success"):
                print(f"  ✓ Created agent: {agent_config['display_name']}")
            else:
                print(f"  ✗ Failed to create agent: {agent_config['display_name']}")

    def create_xavier_stories(self):
        """Create initial stories for Xavier development"""

        # Create main epic
        epic_result = self.commands.create_epic({
            "title": "Xavier Self-Hosting Implementation",
            "description": "Enable Xavier Framework to use its own features for development",
            "business_value": "Dogfooding ensures quality and demonstrates framework capabilities"
        })
        epic_id = epic_result.get("epic_id")
        print(f"  ✓ Created epic: Xavier Self-Hosting Implementation")

        # Define stories
        stories = [
            {
                "title": "Implement meta-commands for Xavier development",
                "as_a": "Xavier developer",
                "i_want": "specialized commands for Xavier development",
                "so_that": "I can efficiently manage Xavier's own development",
                "acceptance_criteria": [
                    "/xavier-init-self command initializes Xavier for self-development",
                    "/xavier-story creates stories for Xavier features",
                    "/xavier-sprint manages Xavier development sprints",
                    "/xavier-agent creates agents for Xavier development",
                    "/xavier-test-self runs recursive self-tests"
                ],
                "priority": "High",
                "epic_id": epic_id
            },
            {
                "title": "Create recursive testing framework",
                "as_a": "Xavier developer",
                "i_want": "Xavier to test its own testing framework",
                "so_that": "we ensure complete test coverage recursively",
                "acceptance_criteria": [
                    "Xavier test runner can test itself",
                    "Agent creation tests agent creation",
                    "Command tests can test command implementation",
                    "No infinite loops in recursive testing",
                    "100% coverage of Xavier testing Xavier"
                ],
                "priority": "High",
                "epic_id": epic_id
            },
            {
                "title": "Implement self-improvement workflows",
                "as_a": "Xavier framework",
                "i_want": "to identify and implement my own improvements",
                "so_that": "I can continuously enhance myself",
                "acceptance_criteria": [
                    "Xavier identifies its own technical debt",
                    "Auto-generates stories for improvements",
                    "Prioritizes enhancements based on usage",
                    "Tracks self-improvement metrics",
                    "Creates sprints for self-development"
                ],
                "priority": "Medium",
                "epic_id": epic_id
            },
            {
                "title": "Build Xavier CI/CD using Xavier agents",
                "as_a": "Xavier developer",
                "i_want": "Xavier agents to handle Xavier's CI/CD",
                "so_that": "deployment is managed by the framework itself",
                "acceptance_criteria": [
                    "Xavier agents run tests on commits",
                    "Agents validate coverage requirements",
                    "Agents check code quality standards",
                    "Agents manage version updates",
                    "Agents deploy releases"
                ],
                "priority": "Medium",
                "epic_id": epic_id
            },
            {
                "title": "Create Xavier performance monitoring",
                "as_a": "Xavier framework",
                "i_want": "to monitor my own performance",
                "so_that": "I can optimize myself",
                "acceptance_criteria": [
                    "Track agent execution times",
                    "Monitor command response times",
                    "Measure sprint velocity",
                    "Analyze code complexity trends",
                    "Generate performance reports"
                ],
                "priority": "Low",
                "epic_id": epic_id
            }
        ]

        story_ids = []
        for story_data in stories:
            result = self.commands.create_story(story_data)
            story_id = result.get("story_id")
            story_ids.append(story_id)
            print(f"  ✓ Created story: {story_data['title'][:50]}...")

        # Add stories to epic
        if epic_id and story_ids:
            self.commands.add_to_epic({
                "epic_id": epic_id,
                "story_ids": story_ids
            })

    def create_xavier_roadmap(self):
        """Create Xavier development roadmap"""

        roadmap_result = self.commands.create_roadmap({
            "name": "Xavier Self-Hosting Roadmap",
            "vision": "Xavier Framework becomes fully self-hosted and self-improving"
        })

        roadmap_id = roadmap_result.get("roadmap_id")

        # Add milestones
        milestones = [
            {
                "name": "Foundation Phase",
                "target_date": (datetime.now() + timedelta(weeks=2)).isoformat(),
                "success_criteria": [
                    "Xavier project initialized for self-development",
                    "Specialized agents created and configured",
                    "Initial stories and sprints established",
                    "Basic meta-commands implemented"
                ]
            },
            {
                "name": "Core Implementation",
                "target_date": (datetime.now() + timedelta(weeks=4)).isoformat(),
                "success_criteria": [
                    "All meta-commands functional",
                    "Recursive testing framework complete",
                    "Self-improvement workflows active",
                    "Xavier developing Xavier successfully"
                ]
            },
            {
                "name": "Automation Phase",
                "target_date": (datetime.now() + timedelta(weeks=6)).isoformat(),
                "success_criteria": [
                    "CI/CD managed by Xavier agents",
                    "Auto-story generation from issues",
                    "Self-updating mechanisms in place",
                    "Performance monitoring active"
                ]
            },
            {
                "name": "Intelligence Phase",
                "target_date": (datetime.now() + timedelta(weeks=8)).isoformat(),
                "success_criteria": [
                    "AI-driven feature suggestions",
                    "Predictive bug detection",
                    "Self-optimization active",
                    "Xavier fully autonomous"
                ]
            }
        ]

        for milestone in milestones:
            self.commands.add_to_roadmap({
                "roadmap_id": roadmap_id,
                "milestone": milestone
            })
            print(f"  ✓ Added milestone: {milestone['name']}")

    def create_initial_sprint(self):
        """Create first Xavier development sprint"""

        sprint_result = self.commands.create_sprint({
            "name": "Xavier Self-Hosting Sprint 1",
            "goal": "Establish Xavier self-development foundation",
            "duration_days": 14,
            "auto_plan": True
        })

        print(f"  ✓ Created sprint: {sprint_result.get('name')}")
        print(f"    - Stories: {sprint_result.get('stories', 0)}")
        print(f"    - Story Points: {sprint_result.get('committed_points', 0)}")

    def create_meta_commands(self):
        """Create meta-command implementations"""

        meta_commands_code = '''
# Add to xavier_commands.py

def xavier_init_self(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize Xavier for self-development"""
    from xavier_self_init import XavierSelfHost
    host = XavierSelfHost()
    host.initialize()
    return {"success": True, "message": "Xavier initialized for self-development"}

def xavier_story(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a story for Xavier feature development"""
    # Add Xavier-specific tags and metadata
    args["tags"] = args.get("tags", []) + ["xavier-core", "self-hosting"]
    args["epic_id"] = args.get("epic_id", self._get_xavier_epic_id())
    return self.create_story(args)

def xavier_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Manage Xavier development sprints"""
    args["name"] = f"Xavier Dev: {args.get('name', 'Sprint')}"
    args["tags"] = ["xavier-development"]
    return self.create_sprint(args)

def xavier_test_self(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Run Xavier self-tests recursively"""
    from xavier.tests.test_meta import XavierMetaTest
    tester = XavierMetaTest()
    results = tester.run_recursive_tests()
    return {
        "success": results.all_passed,
        "tests_run": results.test_count,
        "coverage": results.coverage,
        "recursive_depth": results.max_depth
    }
'''

        # Save meta-commands template
        meta_commands_file = self.xavier_root / ".xavier" / "meta_commands_template.py"
        meta_commands_file.write_text(meta_commands_code)
        print(f"  ✓ Meta-commands template created: {meta_commands_file}")


def main():
    """Main entry point for Xavier self-initialization"""

    print("\n🤖 Xavier Self-Hosting Initialization")
    print("This will set up Xavier to manage its own development")

    response = input("\nProceed with initialization? (y/n): ")
    if response.lower() != 'y':
        print("Initialization cancelled")
        return

    try:
        host = XavierSelfHost()
        host.initialize()

        print("\n" + "="*60)
        print("🎉 SUCCESS!")
        print("="*60)
        print("\nXavier is now managing its own development!")
        print("\nNext steps:")
        print("1. Review created stories: /list-stories")
        print("2. Check the roadmap: /show-roadmap")
        print("3. Start development: /start-sprint")
        print("4. Use Xavier agents to develop Xavier features")
        print("\nUse Xavier to make Xavier better! 🚀")

    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        print("Please check the logs and try again")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())