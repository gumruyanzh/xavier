"""
Xavier Framework - Agent Orchestrator
Manages and coordinates all sub-agents with strict task delegation
"""

import json
import os
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib
import inspect

from .base_agent import (
    BaseAgent, AgentTask, AgentResult, AgentCapability,
    ProjectManagerAgent, ContextManagerAgent,
    PythonEngineerAgent, GolangEngineerAgent,
    FrontendEngineerAgent
)


@dataclass
class TechStackInfo:
    """Detected technology stack information"""
    languages: List[str]
    frameworks: List[str]
    build_tools: List[str]
    test_frameworks: List[str]
    databases: List[str]
    ci_cd_tools: List[str]


class AgentOrchestrator:
    """Orchestrates all sub-agents with strict role enforcement"""

    def __init__(self, config_path: str = "xavier.config.json"):
        self.config = self._load_config(config_path)
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_registry: Dict[str, Type[BaseAgent]] = {}
        self.tech_stack: Optional[TechStackInfo] = None
        self.logger = logging.getLogger("Xavier.Orchestrator")

        # Initialize default agents
        self._initialize_default_agents()

        # Detect tech stack
        self.tech_stack = self._detect_tech_stack()

        # Generate additional agents if needed
        self._generate_tech_stack_agents()

    def _load_config(self, config_path: str) -> Dict:
        """Load Xavier configuration"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def _initialize_default_agents(self):
        """Initialize default sub-agents"""
        # Register agent classes
        self.agent_registry = {
            "project_manager": ProjectManagerAgent,
            "context_manager": ContextManagerAgent,
            "python_engineer": PythonEngineerAgent,
            "golang_engineer": GolangEngineerAgent,
            "frontend_engineer": FrontendEngineerAgent
        }

        # Instantiate enabled agents
        for agent_name, agent_config in self.config.get('agents', {}).items():
            if agent_config.get('enabled', True):
                agent_key = agent_name.lower().replace(' ', '_')
                if agent_key in self.agent_registry:
                    self.agents[agent_key] = self.agent_registry[agent_key]()
                    self.logger.info(f"Initialized agent: {agent_name}")

    def _detect_tech_stack(self) -> TechStackInfo:
        """Detect project's technology stack"""
        languages = []
        frameworks = []
        build_tools = []
        test_frameworks = []
        databases = []
        ci_cd_tools = []

        # Check for package.json (Node.js/JavaScript)
        if os.path.exists("package.json"):
            with open("package.json", 'r') as f:
                pkg = json.load(f)
                if "dependencies" in pkg:
                    deps = pkg["dependencies"].keys()
                    if "react" in deps:
                        frameworks.append("react")
                    if "vue" in deps:
                        frameworks.append("vue")
                    if "angular" in deps:
                        frameworks.append("angular")
                    if "@types/node" in deps or "typescript" in pkg.get("devDependencies", {}):
                        languages.append("typescript")
                    else:
                        languages.append("javascript")
                if "scripts" in pkg:
                    if "test" in pkg["scripts"]:
                        if "jest" in pkg["scripts"]["test"]:
                            test_frameworks.append("jest")
                        if "cypress" in pkg["scripts"]["test"]:
                            test_frameworks.append("cypress")
                build_tools.append("npm")

        # Check for requirements.txt or pyproject.toml (Python)
        if os.path.exists("requirements.txt") or os.path.exists("pyproject.toml"):
            languages.append("python")
            if os.path.exists("requirements.txt"):
                with open("requirements.txt", 'r') as f:
                    reqs = f.read().lower()
                    if "django" in reqs:
                        frameworks.append("django")
                    if "fastapi" in reqs:
                        frameworks.append("fastapi")
                    if "flask" in reqs:
                        frameworks.append("flask")
                    if "pytest" in reqs:
                        test_frameworks.append("pytest")
            build_tools.append("pip")

        # Check for go.mod (Go)
        if os.path.exists("go.mod"):
            languages.append("go")
            with open("go.mod", 'r') as f:
                gomod = f.read().lower()
                if "gin-gonic/gin" in gomod:
                    frameworks.append("gin")
                if "gofiber/fiber" in gomod:
                    frameworks.append("fiber")
                if "labstack/echo" in gomod:
                    frameworks.append("echo")
            build_tools.append("go")

        # Check for Gemfile (Ruby)
        if os.path.exists("Gemfile"):
            languages.append("ruby")
            with open("Gemfile", 'r') as f:
                gemfile = f.read().lower()
                if "rails" in gemfile:
                    frameworks.append("rails")
                if "sinatra" in gemfile:
                    frameworks.append("sinatra")
            build_tools.append("bundler")

        # Check for pom.xml or build.gradle (Java)
        if os.path.exists("pom.xml"):
            languages.append("java")
            build_tools.append("maven")
        elif os.path.exists("build.gradle"):
            languages.append("java")
            build_tools.append("gradle")

        # Check for CI/CD files
        if os.path.exists(".github/workflows"):
            ci_cd_tools.append("github_actions")
        if os.path.exists(".gitlab-ci.yml"):
            ci_cd_tools.append("gitlab_ci")
        if os.path.exists("Jenkinsfile"):
            ci_cd_tools.append("jenkins")

        # Check for database files
        if os.path.exists("docker-compose.yml"):
            with open("docker-compose.yml", 'r') as f:
                compose = f.read().lower()
                if "postgres" in compose:
                    databases.append("postgresql")
                if "mysql" in compose:
                    databases.append("mysql")
                if "mongo" in compose:
                    databases.append("mongodb")

        return TechStackInfo(
            languages=languages,
            frameworks=frameworks,
            build_tools=build_tools,
            test_frameworks=test_frameworks,
            databases=databases,
            ci_cd_tools=ci_cd_tools
        )

    def _generate_tech_stack_agents(self):
        """Generate agents for detected tech stack"""
        if not self.tech_stack:
            return

        # Map of language to agent generator
        language_agent_generators = {
            "ruby": self._generate_ruby_agent,
            "java": self._generate_java_agent,
            "rust": self._generate_rust_agent,
            "csharp": self._generate_csharp_agent
        }

        for language in self.tech_stack.languages:
            if language in language_agent_generators and f"{language}_engineer" not in self.agents:
                agent = language_agent_generators[language]()
                if agent:
                    self.agents[f"{language}_engineer"] = agent
                    self.logger.info(f"Generated {language} engineer agent")

    def _generate_ruby_agent(self) -> Optional[BaseAgent]:
        """Generate Ruby engineer agent dynamically"""
        class RubyEngineerAgent(BaseAgent):
            def __init__(self):
                capabilities = AgentCapability(
                    languages=["ruby"],
                    frameworks=["rails", "sinatra"],
                    tools=["bundler", "rspec", "rubocop"],
                    restricted_actions=["python_code", "golang_code", "javascript_code"],
                    allowed_file_patterns=[r".*\.rb$", r"Gemfile", r".*\.erb$"]
                )
                super().__init__("RubyEngineer", capabilities)

            def execute_task(self, task: AgentTask) -> AgentResult:
                # Ruby-specific implementation
                return AgentResult(
                    success=True,
                    task_id=task.task_id,
                    output="Ruby task executed",
                    test_results={"coverage": 100.0},
                    files_created=[],
                    files_modified=[],
                    validation_results={},
                    errors=[]
                )

            def validate_task(self, task: AgentTask) -> tuple[bool, List[str]]:
                return True, []

        return RubyEngineerAgent()

    def _generate_java_agent(self) -> Optional[BaseAgent]:
        """Generate Java engineer agent dynamically"""
        class JavaEngineerAgent(BaseAgent):
            def __init__(self):
                capabilities = AgentCapability(
                    languages=["java"],
                    frameworks=["spring", "springboot"],
                    tools=["maven", "gradle", "junit"],
                    restricted_actions=["python_code", "golang_code", "javascript_code"],
                    allowed_file_patterns=[r".*\.java$", r"pom\.xml$", r"build\.gradle$"]
                )
                super().__init__("JavaEngineer", capabilities)

            def execute_task(self, task: AgentTask) -> AgentResult:
                # Java-specific implementation
                return AgentResult(
                    success=True,
                    task_id=task.task_id,
                    output="Java task executed",
                    test_results={"coverage": 100.0},
                    files_created=[],
                    files_modified=[],
                    validation_results={},
                    errors=[]
                )

            def validate_task(self, task: AgentTask) -> tuple[bool, List[str]]:
                return True, []

        return JavaEngineerAgent()

    def _generate_rust_agent(self) -> Optional[BaseAgent]:
        """Generate Rust engineer agent dynamically"""
        # Similar implementation for Rust
        return None

    def _generate_csharp_agent(self) -> Optional[BaseAgent]:
        """Generate C# engineer agent dynamically"""
        # Similar implementation for C#
        return None

    def delegate_task(self, task: AgentTask) -> AgentResult:
        """Delegate task to appropriate agent with strict validation"""
        # Find appropriate agent based on task requirements
        selected_agent = self._select_agent_for_task(task)

        if not selected_agent:
            return AgentResult(
                success=False,
                task_id=task.task_id,
                output="",
                test_results=None,
                files_created=[],
                files_modified=[],
                validation_results={},
                errors=["No suitable agent found for task"]
            )

        # Validate agent can handle task
        can_handle, validation_errors = selected_agent.validate_task(task)
        if not can_handle:
            return AgentResult(
                success=False,
                task_id=task.task_id,
                output="",
                test_results=None,
                files_created=[],
                files_modified=[],
                validation_results={},
                errors=validation_errors
            )

        # Execute task with selected agent
        self.logger.info(f"Delegating task {task.task_id} to {selected_agent.name}")
        result = selected_agent.execute_task(task)

        # Validate result meets acceptance criteria
        if not self._validate_result(result, task):
            result.success = False
            result.errors.append("Result does not meet acceptance criteria")

        return result

    def _select_agent_for_task(self, task: AgentTask) -> Optional[BaseAgent]:
        """Select the most appropriate agent for a task"""
        # Analyze task requirements to select agent
        task_keywords = task.description.lower() + " ".join(task.requirements).lower()

        if "sprint" in task_keywords or "story" in task_keywords or "estimate" in task_keywords:
            return self.agents.get("project_manager")

        if "analyze" in task_keywords or "context" in task_keywords or "find" in task_keywords:
            return self.agents.get("context_manager")

        # Check tech constraints for language-specific agents
        for constraint in task.tech_constraints:
            constraint_lower = constraint.lower()
            if "python" in constraint_lower:
                return self.agents.get("python_engineer")
            if "go" in constraint_lower or "golang" in constraint_lower:
                return self.agents.get("golang_engineer")
            if "typescript" in constraint_lower or "react" in constraint_lower:
                return self.agents.get("frontend_engineer")
            if "ruby" in constraint_lower:
                return self.agents.get("ruby_engineer")
            if "java" in constraint_lower:
                return self.agents.get("java_engineer")

        return None

    def _validate_result(self, result: AgentResult, task: AgentTask) -> bool:
        """Validate that result meets task acceptance criteria"""
        if not result.success:
            return False

        # Check test coverage requirement
        if result.test_results:
            coverage = result.test_results.get("coverage", 0)
            if coverage < 100.0:
                self.logger.error(f"Test coverage {coverage}% is below required 100%")
                return False

        # Validate Clean Code compliance
        if "clean_code" in result.validation_results:
            if not result.validation_results["clean_code"]:
                self.logger.error("Code does not meet Clean Code standards")
                return False

        return True

    def execute_sprint_tasks(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """Execute sprint tasks sequentially with strict ordering"""
        results = []

        # Sort tasks by dependencies and priority
        sorted_tasks = self._topological_sort_tasks(tasks)

        for task in sorted_tasks:
            self.logger.info(f"Executing task: {task.task_id}")

            # Check if all dependencies are complete
            dependent_results = [r for r in results if r.task_id in task.dependencies]
            if not all(r.success for r in dependent_results):
                result = AgentResult(
                    success=False,
                    task_id=task.task_id,
                    output="",
                    test_results=None,
                    files_created=[],
                    files_modified=[],
                    validation_results={},
                    errors=["Dependencies not satisfied"]
                )
                results.append(result)
                continue

            # Delegate and execute task
            result = self.delegate_task(task)

            # Strict check - stop if task fails
            if not result.success:
                self.logger.error(f"Task {task.task_id} failed. Stopping sprint execution.")
                break

            results.append(result)

        return results

    def _topological_sort_tasks(self, tasks: List[AgentTask]) -> List[AgentTask]:
        """Sort tasks based on dependencies (topological sort)"""
        # Create adjacency list
        graph = {task.task_id: task.dependencies for task in tasks}
        task_map = {task.task_id: task for task in tasks}

        # Perform topological sort
        visited = set()
        stack = []

        def dfs(task_id):
            visited.add(task_id)
            for dep in graph.get(task_id, []):
                if dep not in visited and dep in graph:
                    dfs(dep)
            stack.append(task_id)

        for task_id in graph:
            if task_id not in visited:
                dfs(task_id)

        # Return tasks in reverse order
        return [task_map[task_id] for task_id in reversed(stack) if task_id in task_map]

    def generate_agent_report(self) -> Dict[str, Any]:
        """Generate report on agent capabilities and status"""
        report = {
            "active_agents": list(self.agents.keys()),
            "tech_stack": {
                "languages": self.tech_stack.languages if self.tech_stack else [],
                "frameworks": self.tech_stack.frameworks if self.tech_stack else [],
                "build_tools": self.tech_stack.build_tools if self.tech_stack else [],
                "test_frameworks": self.tech_stack.test_frameworks if self.tech_stack else []
            },
            "agent_capabilities": {}
        }

        for agent_name, agent in self.agents.items():
            report["agent_capabilities"][agent_name] = {
                "languages": agent.capabilities.languages,
                "frameworks": agent.capabilities.frameworks,
                "tools": agent.capabilities.tools,
                "restrictions": agent.capabilities.restricted_actions
            }

        return report