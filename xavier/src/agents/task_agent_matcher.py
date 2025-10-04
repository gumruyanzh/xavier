#!/usr/bin/env python3
"""
Task Agent Matcher - Automatically assigns the best agent to a task
Analyzes task requirements and creates agents if needed
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import yaml
import logging


class TaskAgentMatcher:
    """Matches tasks to appropriate agents and creates them if needed"""

    # Technology to agent mapping
    TECH_AGENT_MAP = {
        # Languages
        'python': 'python-engineer',
        'py': 'python-engineer',
        'django': 'python-engineer',
        'flask': 'python-engineer',
        'fastapi': 'python-engineer',
        'pytest': 'python-engineer',

        'javascript': 'frontend-engineer',
        'typescript': 'frontend-engineer',
        'react': 'frontend-engineer',
        'vue': 'frontend-engineer',
        'angular': 'frontend-engineer',
        'nextjs': 'frontend-engineer',
        'node': 'frontend-engineer',
        'npm': 'frontend-engineer',

        'go': 'golang-engineer',
        'golang': 'golang-engineer',
        'gin': 'golang-engineer',
        'gorilla': 'golang-engineer',

        'java': 'java-engineer',
        'spring': 'java-engineer',
        'springboot': 'java-engineer',
        'maven': 'java-engineer',
        'gradle': 'java-engineer',

        'ruby': 'ruby-engineer',
        'rails': 'ruby-engineer',
        'rspec': 'ruby-engineer',

        'rust': 'rust-engineer',
        'cargo': 'rust-engineer',
        'actix': 'rust-engineer',

        'swift': 'swift-engineer',
        'ios': 'swift-engineer',
        'swiftui': 'swift-engineer',
        'xcode': 'swift-engineer',

        'kotlin': 'kotlin-engineer',
        'android': 'kotlin-engineer',

        'csharp': 'csharp-engineer',
        'c#': 'csharp-engineer',
        'dotnet': 'csharp-engineer',
        '.net': 'csharp-engineer',
        'aspnet': 'csharp-engineer',

        'php': 'php-engineer',
        'laravel': 'php-engineer',
        'symfony': 'php-engineer',

        'elixir': 'elixir-engineer',
        'phoenix': 'elixir-engineer',

        # Testing
        'test': 'test-runner',
        'testing': 'test-runner',
        'unittest': 'test-runner',
        'integration test': 'test-runner',
        'e2e': 'test-runner',
        'coverage': 'test-runner',

        # Database
        'database': 'database-engineer',
        'sql': 'database-engineer',
        'postgres': 'database-engineer',
        'mysql': 'database-engineer',
        'mongodb': 'database-engineer',
        'redis': 'database-engineer',

        # DevOps
        'docker': 'devops-engineer',
        'kubernetes': 'devops-engineer',
        'k8s': 'devops-engineer',
        'ci/cd': 'devops-engineer',
        'jenkins': 'devops-engineer',
        'github actions': 'devops-engineer',
        'terraform': 'devops-engineer',

        # Architecture
        'architecture': 'architect',
        'design pattern': 'architect',
        'system design': 'architect',
        'microservices': 'architect',

        # Documentation
        'documentation': 'technical-writer',
        'docs': 'technical-writer',
        'readme': 'technical-writer',
        'api docs': 'technical-writer',
    }

    # Keywords that suggest task types
    TASK_TYPE_KEYWORDS = {
        'implement': ['build', 'create', 'develop', 'implement', 'code', 'write'],
        'test': ['test', 'verify', 'validate', 'check', 'ensure', 'coverage'],
        'fix': ['fix', 'debug', 'resolve', 'repair', 'patch', 'correct'],
        'refactor': ['refactor', 'optimize', 'improve', 'enhance', 'clean'],
        'document': ['document', 'describe', 'explain', 'write docs'],
        'deploy': ['deploy', 'release', 'publish', 'ship', 'launch'],
        'design': ['design', 'architect', 'plan', 'structure'],
    }

    def __init__(self, project_path: str = "."):
        """Initialize the task agent matcher"""
        self.project_path = Path(project_path)
        self.xavier_agents_dir = self.project_path / ".xavier" / "agents"
        self.claude_agents_dir = self.project_path / ".claude" / "agents"
        self.logger = logging.getLogger("Xavier.TaskAgentMatcher")

    def analyze_task(self, task_data: Dict[str, Any]) -> Tuple[Optional[str], str, float]:
        """
        Analyze a task and determine the best agent

        Returns:
            Tuple of (agent_name, reason, confidence_score)
        """
        title = task_data.get('title', '').lower()
        description = task_data.get('description', '').lower()
        technical_details = task_data.get('technical_details', '').lower()

        # Combine all text for analysis
        full_text = f"{title} {description} {technical_details}"

        # Check for technology keywords
        best_agent = None
        best_score = 0.0
        matches = []

        for tech, agent in self.TECH_AGENT_MAP.items():
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern, full_text):
                # Higher score for matches in title
                score = 2.0 if tech in title else 1.0
                matches.append((agent, tech, score))

        # Sort by score and get best match
        if matches:
            matches.sort(key=lambda x: x[2], reverse=True)
            best_agent, tech_match, best_score = matches[0]

            # Normalize confidence (0-1)
            confidence = min(best_score / 2.0, 1.0)
            reason = f"Detected '{tech_match}' technology in task"

            return best_agent, reason, confidence

        # Fallback: Check task type keywords
        for task_type, keywords in self.TASK_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in full_text:
                    if task_type == 'test':
                        return 'test-runner', f"Task involves {task_type}", 0.7
                    elif task_type == 'document':
                        return 'technical-writer', f"Task involves documentation", 0.6
                    elif task_type == 'deploy':
                        return 'devops-engineer', f"Task involves deployment", 0.7
                    elif task_type == 'design':
                        return 'architect', f"Task involves system design", 0.6

        # Default fallback
        return 'python-engineer', "Default assignment (no specific technology detected)", 0.3

    def check_agent_exists(self, agent_name: str) -> bool:
        """Check if an agent exists in either Xavier or Claude directories"""
        # Check Xavier agents
        xavier_agent_file = self.xavier_agents_dir / f"{agent_name.replace('-', '_')}.yaml"
        if xavier_agent_file.exists():
            return True

        # Check Claude agents
        claude_agent_file = self.claude_agents_dir / f"{agent_name}.md"
        if claude_agent_file.exists():
            return True

        return False

    def create_agent_if_needed(self, agent_name: str, task_context: Dict[str, Any]) -> bool:
        """
        Create an agent if it doesn't exist

        Returns:
            True if agent was created or already exists
        """
        if self.check_agent_exists(agent_name):
            self.logger.info(f"Agent {agent_name} already exists")
            return True

        # Create the agent dynamically
        try:
            from xavier.src.agents.dynamic_agent_factory import DynamicAgentFactory

            factory = DynamicAgentFactory(self.project_path)

            # Determine agent properties from name
            agent_parts = agent_name.split('-')
            if len(agent_parts) >= 2:
                tech = agent_parts[0]
                role = ' '.join(agent_parts).replace('-', ' ').title()
            else:
                tech = agent_name
                role = agent_name.replace('-', ' ').title()

            # Create agent with appropriate skills
            success, message = factory.create_agent(
                name=agent_name,
                display_name=role,
                technology=tech,
                role_description=f"Specialized {role} for {tech} development"
            )

            if success:
                self.logger.info(f"Successfully created agent: {agent_name}")
                return True
            else:
                self.logger.error(f"Failed to create agent {agent_name}: {message}")
                return False

        except Exception as e:
            self.logger.error(f"Error creating agent {agent_name}: {e}")
            return False

    def assign_agent_to_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to analyze task and assign appropriate agent

        Args:
            task_data: Dictionary containing task information

        Returns:
            Dict with assignment results
        """
        # Analyze the task
        agent_name, reason, confidence = self.analyze_task(task_data)

        # Create agent if needed
        if agent_name and not self.check_agent_exists(agent_name):
            self.logger.info(f"Agent {agent_name} doesn't exist, creating it...")
            created = self.create_agent_if_needed(agent_name, task_data)
            if not created:
                # Fallback to project manager if creation failed
                agent_name = 'project-manager'
                reason = "Failed to create specialized agent, using project manager"
                confidence = 0.5

        # Return assignment result
        return {
            'success': True,
            'agent': agent_name,
            'reason': reason,
            'confidence': confidence,
            'created_new_agent': not self.check_agent_exists(agent_name)
        }

    def suggest_agents_for_story(self, story_data: Dict[str, Any]) -> List[str]:
        """
        Suggest agents that might be needed for a story

        Args:
            story_data: Story information

        Returns:
            List of suggested agent names
        """
        description = story_data.get('description', '').lower()
        acceptance_criteria = ' '.join(story_data.get('acceptance_criteria', [])).lower()

        full_text = f"{description} {acceptance_criteria}"
        suggested_agents = set()

        # Find all matching technologies
        for tech, agent in self.TECH_AGENT_MAP.items():
            pattern = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern, full_text):
                suggested_agents.add(agent)

        # Always include test runner for TDD
        suggested_agents.add('test-runner')

        return list(suggested_agents)

    def get_agent_workload(self) -> Dict[str, int]:
        """
        Get current workload for each agent (number of assigned tasks)

        Returns:
            Dict mapping agent names to task counts
        """
        try:
            # Read tasks from data directory
            tasks_file = self.project_path / ".xavier" / "data" / "tasks.json"
            if not tasks_file.exists():
                return {}

            import json
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)

            workload = {}
            for task_id, task_data in tasks.items():
                assigned_to = task_data.get('assigned_to')
                if assigned_to:
                    workload[assigned_to] = workload.get(assigned_to, 0) + 1

            return workload

        except Exception as e:
            self.logger.error(f"Error getting agent workload: {e}")
            return {}

    def balance_assignment(self, candidates: List[str]) -> str:
        """
        Choose agent with lowest workload from candidates

        Args:
            candidates: List of possible agents

        Returns:
            Agent name with lowest workload
        """
        if not candidates:
            return 'project-manager'

        workload = self.get_agent_workload()

        # Find agent with minimum workload
        min_workload = float('inf')
        best_agent = candidates[0]

        for agent in candidates:
            current_workload = workload.get(agent, 0)
            if current_workload < min_workload:
                min_workload = current_workload
                best_agent = agent

        return best_agent


def auto_assign_agent(task_data: Dict[str, Any], project_path: str = ".") -> Dict[str, Any]:
    """
    Convenience function to auto-assign agent to a task

    Args:
        task_data: Task information
        project_path: Path to project

    Returns:
        Assignment result
    """
    matcher = TaskAgentMatcher(project_path)
    return matcher.assign_agent_to_task(task_data)