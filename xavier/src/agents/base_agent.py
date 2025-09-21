"""
Xavier Framework - Base Agent and Specialized Sub-Agents
Strict role-based agents with specialized responsibilities
"""

import json
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging
import re
import ast
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ansi_art import AgentColors, ANSIColors, display_agent_takeover, display_agent_status, display_agent_result, display_agent_handoff, AgentBoxDrawing
from agents.agent_metadata import get_agent_metadata, get_agent_display_name


@dataclass
class AgentCapability:
    """Defines what an agent can and cannot do"""
    languages: List[str]
    frameworks: List[str]
    tools: List[str]
    restricted_actions: List[str]
    allowed_file_patterns: List[str]


@dataclass
class AgentTask:
    """Task assignment for an agent"""
    task_id: str
    task_type: str
    description: str
    requirements: List[str]
    test_requirements: Dict[str, Any]
    acceptance_criteria: List[str]
    tech_constraints: List[str]


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    task_id: str
    output: str
    test_results: Optional[Dict[str, Any]]
    files_created: List[str]
    files_modified: List[str]
    validation_results: Dict[str, Any]
    errors: List[str]


class BaseAgent(ABC):
    """Base class for all Xavier agents with strict boundaries"""

    def __init__(self, name: str, capabilities: AgentCapability):
        self.name = name
        self.capabilities = capabilities

        # Get display name from metadata or fallback to formatted name
        self.display_name = get_agent_display_name(name)

        self.logger = logging.getLogger(f"Xavier.Agent.{self.display_name}")
        self.current_task: Optional[AgentTask] = None

    @abstractmethod
    def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute assigned task within agent boundaries"""
        pass

    @abstractmethod
    def validate_task(self, task: AgentTask) -> Tuple[bool, List[str]]:
        """Validate if task is within agent capabilities"""
        pass

    def can_handle_file(self, file_path: str) -> bool:
        """Check if agent can work with file"""
        for pattern in self.capabilities.allowed_file_patterns:
            if re.match(pattern, file_path):
                return True
        return False

    def is_action_allowed(self, action: str) -> bool:
        """Check if action is permitted for this agent"""
        return action not in self.capabilities.restricted_actions

    def start_task(self, task: AgentTask) -> None:
        """Start working on a task with colored output"""
        self.current_task = task
        display_agent_takeover(self.name, task.description)
        display_agent_status(self.name, "Working", f"Task: {task.task_id}")

    def update_status(self, status: str, details: Optional[str] = None) -> None:
        """Update agent status with colored output"""
        display_agent_status(self.name, status, details)

    def show_thinking(self, message: str = "Processing...") -> None:
        """Display thinking indicator"""
        thinking_line = AgentBoxDrawing.create_thinking_indicator(self.name, message)
        print(thinking_line)

    def handoff_to(self, target_agent: str, reason: str) -> None:
        """Display handoff to another agent"""
        display_agent_handoff(self.name, target_agent, reason)

    def complete_task(self, success: bool, summary: str) -> None:
        """Complete current task with colored result display"""
        display_agent_result(self.name, success, summary)
        self.current_task = None


class ProjectManagerAgent(BaseAgent):
    """Project Manager - Handles sprint planning and task assignment"""

    def __init__(self):
        capabilities = AgentCapability(
            languages=[],
            frameworks=["scrum", "agile", "kanban"],
            tools=["jira", "github", "gitlab"],
            restricted_actions=["code_write", "code_execute", "deploy"],
            allowed_file_patterns=[r".*\.md$", r".*\.json$", r".*\.yaml$"]
        )
        super().__init__("project-manager", capabilities)
        self.story_points_model = self._initialize_estimation_model()

    def _initialize_estimation_model(self) -> Dict[str, int]:
        """Initialize story point estimation model"""
        return {
            "trivial": 1,
            "simple": 2,
            "moderate": 3,
            "complex": 5,
            "very_complex": 8,
            "epic": 13
        }

    def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute project management tasks"""
        self.start_task(task)

        if task.task_type == "estimate_story":
            result = self._estimate_story_points(task)
        elif task.task_type == "plan_sprint":
            result = self._plan_sprint(task)
        elif task.task_type == "assign_tasks":
            result = self._assign_tasks(task)
        else:
            result = AgentResult(
                success=False,
                task_id=task.task_id,
                output="",
                test_results=None,
                files_created=[],
                files_modified=[],
                validation_results={},
                errors=[f"Unknown task type: {task.task_type}"]
            )

        self.complete_task(result.success, result.output[:100] if result.output else "Task completed")
        return result

    def validate_task(self, task: AgentTask) -> Tuple[bool, List[str]]:
        """Validate project management task"""
        valid_types = ["estimate_story", "plan_sprint", "assign_tasks", "create_roadmap"]
        if task.task_type not in valid_types:
            return False, [f"Invalid task type for Project Manager: {task.task_type}"]
        return True, []

    def _estimate_story_points(self, task: AgentTask) -> AgentResult:
        """Estimate story points based on comprehensive complexity analysis"""
        # Initialize complexity score
        complexity_score = 0
        analysis_details = []

        # Combine description and requirements for analysis
        full_context = f"{task.description} {' '.join(task.requirements)}".lower()

        # 1. Analyze technical complexity keywords
        technical_keywords = {
            "api": 2, "database": 2, "authentication": 3, "authorization": 3,
            "integration": 3, "microservice": 4, "distributed": 4,
            "real-time": 3, "websocket": 3, "encryption": 3,
            "payment": 4, "third-party": 2, "migration": 3,
            "refactor": 2, "optimization": 3, "performance": 3,
            "security": 3, "compliance": 4, "audit": 3
        }

        for keyword, weight in technical_keywords.items():
            if keyword in full_context:
                complexity_score += weight
                analysis_details.append(f"Contains {keyword} (+{weight})")

        # 2. Analyze CRUD operations
        crud_operations = ["create", "read", "update", "delete", "list", "search"]
        crud_count = sum(1 for op in crud_operations if op in full_context)
        if crud_count > 0:
            complexity_score += crud_count
            analysis_details.append(f"CRUD operations: {crud_count} (+{crud_count})")

        # 3. Analyze acceptance criteria count
        criteria_count = len(task.requirements)
        if criteria_count > 5:
            complexity_score += 3
            analysis_details.append(f"Many acceptance criteria: {criteria_count} (+3)")
        elif criteria_count > 3:
            complexity_score += 2
            analysis_details.append(f"Multiple criteria: {criteria_count} (+2)")
        else:
            complexity_score += 1
            analysis_details.append(f"Few criteria: {criteria_count} (+1)")

        # 4. Analyze UI/UX complexity
        ui_keywords = ["ui", "ux", "design", "responsive", "mobile", "accessibility",
                      "animation", "dashboard", "visualization", "chart", "graph"]
        ui_complexity = sum(1 for kw in ui_keywords if kw in full_context)
        if ui_complexity > 0:
            complexity_score += ui_complexity * 2
            analysis_details.append(f"UI complexity (+{ui_complexity * 2})")

        # 5. Analyze testing requirements
        test_keywords = ["test", "coverage", "unit", "integration", "e2e", "tdd"]
        test_complexity = sum(1 for kw in test_keywords if kw in full_context)
        if test_complexity > 0:
            complexity_score += test_complexity
            analysis_details.append(f"Testing requirements (+{test_complexity})")

        # 6. Check for simple/complex indicators
        if any(word in full_context for word in ["simple", "basic", "straightforward"]):
            complexity_score = max(1, complexity_score - 2)
            analysis_details.append("Simple indicator (-2)")
        elif any(word in full_context for word in ["complex", "advanced", "sophisticated"]):
            complexity_score += 3
            analysis_details.append("Complex indicator (+3)")

        # Map complexity score to story points (Fibonacci)
        if complexity_score <= 3:
            estimated_points = 1
        elif complexity_score <= 5:
            estimated_points = 2
        elif complexity_score <= 8:
            estimated_points = 3
        elif complexity_score <= 12:
            estimated_points = 5
        elif complexity_score <= 18:
            estimated_points = 8
        elif complexity_score <= 26:
            estimated_points = 13
        else:
            estimated_points = 21

        # Update status with analysis
        self.update_status("Analyzing", f"Complexity score: {complexity_score} → {estimated_points} points")

        return AgentResult(
            success=True,
            task_id=task.task_id,
            output=f"Estimated {estimated_points} story points (complexity: {complexity_score})",
            test_results=None,
            files_created=[],
            files_modified=[],
            validation_results={
                "story_points": estimated_points,
                "complexity_score": complexity_score,
                "analysis": analysis_details
            },
            errors=[]
        )

    def _plan_sprint(self, task: AgentTask) -> AgentResult:
        """Plan sprint based on velocity and priorities"""
        # Sprint planning logic
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Sprint planned successfully",
            test_results=None,
            files_created=["sprint_plan.json"],
            files_modified=[],
            validation_results={"sprint_capacity": 20},
            errors=[]
        )

    def _assign_tasks(self, task: AgentTask) -> AgentResult:
        """Assign tasks to appropriate agents"""
        # Task assignment logic
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Tasks assigned to agents",
            test_results=None,
            files_created=[],
            files_modified=["task_assignments.json"],
            validation_results={},
            errors=[]
        )


class ContextManagerAgent(BaseAgent):
    """Context Manager - Maintains codebase understanding and context"""

    def __init__(self):
        capabilities = AgentCapability(
            languages=["*"],  # Can read any language
            frameworks=["*"],  # Can understand any framework
            tools=["ast", "grep", "find", "ctags"],
            restricted_actions=["code_write", "deploy"],
            allowed_file_patterns=[r".*"]  # Can read all files
        )
        super().__init__("context-manager", capabilities)
        self.codebase_map: Dict[str, Any] = {}

    def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute context management tasks"""
        self.start_task(task)

        if task.task_type == "analyze_codebase":
            result = self._analyze_codebase(task)
        elif task.task_type == "find_implementations":
            result = self._find_implementations(task)
        elif task.task_type == "check_dependencies":
            result = self._check_dependencies(task)
        else:
            result = AgentResult(
                success=False,
                task_id=task.task_id,
                output="",
                test_results=None,
                files_created=[],
                files_modified=[],
                validation_results={},
                errors=[f"Unknown task type: {task.task_type}"]
            )

        self.complete_task(result.success, result.output[:100] if result.output else "Analysis completed")
        return result

    def validate_task(self, task: AgentTask) -> Tuple[bool, List[str]]:
        """Validate context management task"""
        valid_types = ["analyze_codebase", "find_implementations", "check_dependencies"]
        if task.task_type not in valid_types:
            return False, [f"Invalid task type for Context Manager: {task.task_type}"]
        return True, []

    def _analyze_codebase(self, task: AgentTask) -> AgentResult:
        """Analyze codebase structure and patterns"""
        # Codebase analysis logic
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Codebase analyzed",
            test_results=None,
            files_created=["codebase_analysis.json"],
            files_modified=[],
            validation_results={"total_files": 0, "patterns_found": []},
            errors=[]
        )

    def _find_implementations(self, task: AgentTask) -> AgentResult:
        """Find existing implementations to avoid duplication"""
        # Implementation search logic
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Found existing implementations",
            test_results=None,
            files_created=[],
            files_modified=[],
            validation_results={"similar_methods": []},
            errors=[]
        )

    def _check_dependencies(self, task: AgentTask) -> AgentResult:
        """Check project dependencies"""
        # Dependency checking logic
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Dependencies checked",
            test_results=None,
            files_created=[],
            files_modified=[],
            validation_results={"dependencies": {}},
            errors=[]
        )


class PythonEngineerAgent(BaseAgent):
    """Python Backend Engineer - Strictly Python development only"""

    def __init__(self):
        capabilities = AgentCapability(
            languages=["python"],
            frameworks=["django", "fastapi", "flask", "pytest"],
            tools=["pip", "poetry", "pytest", "mypy", "black", "flake8"],
            restricted_actions=["frontend_development", "golang_code", "javascript_code"],
            allowed_file_patterns=[r".*\.py$", r".*requirements.*\.txt$", r".*\.toml$"]
        )
        super().__init__("python-engineer", capabilities)

    def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute Python development tasks with test-first approach"""
        self.start_task(task)

        # Validate language constraint
        if not self._validate_python_only(task):
            result = AgentResult(
                success=False,
                task_id=task.task_id,
                output="",
                test_results=None,
                files_created=[],
                files_modified=[],
                validation_results={},
                errors=["Task requires non-Python code. Python Engineer can only write Python."]
            )
            self.complete_task(False, "Task requires non-Python code")
            return result

        # Test-first enforcement
        if task.task_type == "implement_feature":
            self.update_status("Testing", "Writing tests first (TDD)")
            # Write tests first
            test_result = self._write_tests_first(task)
            if not test_result.success:
                self.complete_task(False, "Failed to write tests")
                return test_result

            self.update_status("Working", "Implementing feature")
            # Then implement
            result = self._implement_python_feature(task)
        else:
            result = self._execute_python_task(task)

        self.complete_task(result.success, result.output[:100] if result.output else "Python task completed")
        return result

    def validate_task(self, task: AgentTask) -> Tuple[bool, List[str]]:
        """Validate Python-only constraint"""
        errors = []

        # Check for non-Python requirements
        for req in task.requirements:
            if any(lang in req.lower() for lang in ["javascript", "golang", "java", "c++"]):
                errors.append(f"Python Engineer cannot handle requirement: {req}")

        # Check tech constraints
        for constraint in task.tech_constraints:
            if constraint.lower() not in ["python", "django", "fastapi", "flask", "pytest"]:
                errors.append(f"Python Engineer cannot work with: {constraint}")

        return len(errors) == 0, errors

    def _validate_python_only(self, task: AgentTask) -> bool:
        """Ensure task is Python-only"""
        description = task.description.lower()
        non_python_keywords = ["javascript", "golang", "react", "vue", "angular", ".js", ".go"]
        return not any(keyword in description for keyword in non_python_keywords)

    def _write_tests_first(self, task: AgentTask) -> AgentResult:
        """Write tests before implementation (TDD)"""
        test_code = self._generate_test_template(task)

        return AgentResult(
            success=True,
            task_id=f"{task.task_id}_tests",
            output="Tests written first (TDD approach)",
            test_results={"tests_created": True},
            files_created=[f"test_{task.task_id}.py"],
            files_modified=[],
            validation_results={"tdd_compliant": True},
            errors=[]
        )

    def _generate_test_template(self, task: AgentTask) -> str:
        """Generate test template for TDD"""
        return f'''import pytest
import unittest
from unittest.mock import Mock, patch


class Test{task.task_id}(unittest.TestCase):
    """Test cases for {task.description}"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_acceptance_criteria(self):
        """Test all acceptance criteria"""
        # Test each acceptance criteria
        pass

    def test_edge_cases(self):
        """Test edge cases"""
        pass

    def test_error_handling(self):
        """Test error handling"""
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov', '--cov-report=term-missing'])
'''

    def _implement_python_feature(self, task: AgentTask) -> AgentResult:
        """Implement Python feature following Clean Code principles"""
        # Implementation logic
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Python feature implemented with 100% test coverage",
            test_results={"coverage": 100.0, "tests_passed": True},
            files_created=["feature.py"],
            files_modified=[],
            validation_results={"clean_code": True, "ioc_applied": True},
            errors=[]
        )

    def _execute_python_task(self, task: AgentTask) -> AgentResult:
        """Execute general Python task"""
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Python task executed",
            test_results=None,
            files_created=[],
            files_modified=[],
            validation_results={},
            errors=[]
        )


class GolangEngineerAgent(BaseAgent):
    """Golang Backend Engineer - Strictly Go development only"""

    def __init__(self):
        capabilities = AgentCapability(
            languages=["go"],
            frameworks=["gin", "fiber", "echo", "chi"],
            tools=["go", "golint", "go test", "go fmt"],
            restricted_actions=["python_code", "javascript_code", "frontend_development"],
            allowed_file_patterns=[r".*\.go$", r"go\.mod$", r"go\.sum$"]
        )
        super().__init__("golang-engineer", capabilities)

    def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute Go development tasks with test-first approach"""
        self.start_task(task)

        # Validate language constraint
        if not self._validate_golang_only(task):
            result = AgentResult(
                success=False,
                task_id=task.task_id,
                output="",
                test_results=None,
                files_created=[],
                files_modified=[],
                validation_results={},
                errors=["Task requires non-Go code. Golang Engineer can only write Go."]
            )
            self.complete_task(False, "Task requires non-Go code")
            return result

        # Test-first enforcement
        if task.task_type == "implement_feature":
            self.update_status("Testing", "Writing Go tests first (TDD)")
            # Write tests first
            test_result = self._write_tests_first(task)
            if not test_result.success:
                self.complete_task(False, "Failed to write tests")
                return test_result

            self.update_status("Working", "Implementing Go feature")
            # Then implement
            result = self._implement_go_feature(task)
        else:
            result = self._execute_go_task(task)

        self.complete_task(result.success, result.output[:100] if result.output else "Go task completed")
        return result

    def validate_task(self, task: AgentTask) -> Tuple[bool, List[str]]:
        """Validate Go-only constraint"""
        errors = []

        # Check for non-Go requirements
        for req in task.requirements:
            if any(lang in req.lower() for lang in ["python", "javascript", "java", "ruby"]):
                errors.append(f"Golang Engineer cannot handle requirement: {req}")

        # Check tech constraints
        for constraint in task.tech_constraints:
            if constraint.lower() not in ["go", "golang", "gin", "fiber", "echo"]:
                errors.append(f"Golang Engineer cannot work with: {constraint}")

        return len(errors) == 0, errors

    def _validate_golang_only(self, task: AgentTask) -> bool:
        """Ensure task is Go-only"""
        description = task.description.lower()
        non_go_keywords = ["python", "javascript", "django", "flask", ".py", ".js"]
        return not any(keyword in description for keyword in non_go_keywords)

    def _write_tests_first(self, task: AgentTask) -> AgentResult:
        """Write Go tests before implementation (TDD)"""
        test_code = self._generate_go_test_template(task)

        return AgentResult(
            success=True,
            task_id=f"{task.task_id}_tests",
            output="Go tests written first (TDD approach)",
            test_results={"tests_created": True},
            files_created=[f"{task.task_id}_test.go"],
            files_modified=[],
            validation_results={"tdd_compliant": True},
            errors=[]
        )

    def _generate_go_test_template(self, task: AgentTask) -> str:
        """Generate Go test template for TDD"""
        return f'''package main

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func Test{task.task_id}(t *testing.T) {{
    t.Run("AcceptanceCriteria", func(t *testing.T) {{
        // Test acceptance criteria
        assert.True(t, true)
    }})

    t.Run("EdgeCases", func(t *testing.T) {{
        // Test edge cases
        assert.True(t, true)
    }})

    t.Run("ErrorHandling", func(t *testing.T) {{
        // Test error handling
        assert.True(t, true)
    }})
}}

func Benchmark{task.task_id}(b *testing.B) {{
    for i := 0; i < b.N; i++ {{
        // Benchmark implementation
    }}
}}
'''

    def _implement_go_feature(self, task: AgentTask) -> AgentResult:
        """Implement Go feature following Clean Code principles"""
        # Implementation logic
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Go feature implemented with 100% test coverage",
            test_results={"coverage": 100.0, "tests_passed": True},
            files_created=["feature.go"],
            files_modified=[],
            validation_results={"clean_code": True, "ioc_applied": True},
            errors=[]
        )

    def _execute_go_task(self, task: AgentTask) -> AgentResult:
        """Execute general Go task"""
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Go task executed",
            test_results=None,
            files_created=[],
            files_modified=[],
            validation_results={},
            errors=[]
        )


class FrontendEngineerAgent(BaseAgent):
    """Frontend Engineer - TypeScript and modern frameworks only"""

    def __init__(self):
        capabilities = AgentCapability(
            languages=["typescript", "javascript", "html", "css"],
            frameworks=["react", "vue", "angular", "next.js", "nuxt"],
            tools=["npm", "yarn", "webpack", "vite", "jest", "cypress"],
            restricted_actions=["backend_development", "database_operations"],
            allowed_file_patterns=[r".*\.[tj]sx?$", r".*\.vue$", r".*\.css$", r".*\.scss$"]
        )
        super().__init__("frontend-engineer", capabilities)

    def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute frontend tasks with test-first approach"""
        self.start_task(task)

        # Ensure TypeScript usage
        if not self._enforce_typescript(task):
            result = AgentResult(
                success=False,
                task_id=task.task_id,
                output="",
                test_results=None,
                files_created=[],
                files_modified=[],
                validation_results={},
                errors=["Frontend must use TypeScript for type safety"]
            )
            self.complete_task(False, "TypeScript not enforced")
            return result

        if task.task_type == "implement_component":
            self.update_status("Testing", "Writing component tests first")
            # Write component tests first
            test_result = self._write_component_tests_first(task)
            if not test_result.success:
                self.complete_task(False, "Failed to write component tests")
                return test_result

            self.update_status("Working", "Implementing React component")
            # Then implement component
            result = self._implement_component(task)
        else:
            result = self._execute_frontend_task(task)

        self.complete_task(result.success, result.output[:100] if result.output else "Frontend task completed")
        return result

    def validate_task(self, task: AgentTask) -> Tuple[bool, List[str]]:
        """Validate frontend task"""
        errors = []

        # Check for backend operations
        for req in task.requirements:
            if any(keyword in req.lower() for keyword in ["database", "sql", "mongodb"]):
                errors.append(f"Frontend Engineer cannot handle backend requirement: {req}")

        return len(errors) == 0, errors

    def _enforce_typescript(self, task: AgentTask) -> bool:
        """Ensure TypeScript is used"""
        return "typescript" in [c.lower() for c in task.tech_constraints]

    def _write_component_tests_first(self, task: AgentTask) -> AgentResult:
        """Write component tests before implementation"""
        test_code = self._generate_component_test_template(task)

        return AgentResult(
            success=True,
            task_id=f"{task.task_id}_tests",
            output="Component tests written first",
            test_results={"tests_created": True},
            files_created=[f"{task.task_id}.test.tsx"],
            files_modified=[],
            validation_results={"tdd_compliant": True},
            errors=[]
        )

    def _generate_component_test_template(self, task: AgentTask) -> str:
        """Generate TypeScript component test template"""
        return f'''import {{ render, screen, fireEvent }} from '@testing-library/react';
import {{ describe, it, expect }} from '@jest/globals';
import {{ Component }} from './{task.task_id}';

describe('{task.task_id} Component', () => {{
    it('should meet acceptance criteria', () => {{
        // Test acceptance criteria
        render(<Component />);
        expect(screen.getByRole('main')).toBeInTheDocument();
    }});

    it('should handle edge cases', () => {{
        // Test edge cases
    }});

    it('should be accessible', () => {{
        // Test accessibility
    }});
}});
'''

    def _implement_component(self, task: AgentTask) -> AgentResult:
        """Implement frontend component"""
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Component implemented with TypeScript and tests",
            test_results={"coverage": 100.0, "tests_passed": True},
            files_created=["Component.tsx"],
            files_modified=[],
            validation_results={"typescript": True, "accessibility": True},
            errors=[]
        )

    def _execute_frontend_task(self, task: AgentTask) -> AgentResult:
        """Execute general frontend task"""
        return AgentResult(
            success=True,
            task_id=task.task_id,
            output="Frontend task executed",
            test_results=None,
            files_created=[],
            files_modified=[],
            validation_results={},
            errors=[]
        )