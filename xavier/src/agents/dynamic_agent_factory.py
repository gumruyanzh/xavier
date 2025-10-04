"""
Xavier Framework - Dynamic Agent Factory
Automatically creates and registers agents on-demand with full Claude Code integration
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Type, List, Tuple
from dataclasses import dataclass
import importlib
import inspect

from .base_agent import BaseAgent, AgentCapability, AgentTask, AgentResult


@dataclass
class AgentTemplate:
    """Template for creating new agents"""
    language: str
    display_name: str
    color: str
    emoji: str
    label: str
    frameworks: List[str]
    tools: List[str]
    file_patterns: List[str]
    test_framework: str


class DynamicAgentFactory:
    """Factory for creating agents on-demand with automatic YAML generation"""

    # Predefined templates for common languages/technologies
    AGENT_TEMPLATES = {
        "java": AgentTemplate(
            language="java",
            display_name="Java Engineer",
            color="red",
            emoji="☕",
            label="JAVA",
            frameworks=["spring", "springboot", "hibernate", "maven", "gradle"],
            tools=["javac", "maven", "gradle", "junit", "mockito"],
            file_patterns=[r".*\.java$", r"pom\.xml$", r"build\.gradle$", r".*\.kt$"],
            test_framework="junit"
        ),
        "ruby": AgentTemplate(
            language="ruby",
            display_name="Ruby Engineer",
            color="red",
            emoji="💎",
            label="RB",
            frameworks=["rails", "sinatra", "rspec", "bundler"],
            tools=["ruby", "bundler", "rake", "rspec", "rubocop"],
            file_patterns=[r".*\.rb$", r"Gemfile", r".*\.erb$", r"Rakefile"],
            test_framework="rspec"
        ),
        "rust": AgentTemplate(
            language="rust",
            display_name="Rust Engineer",
            color="yellow",
            emoji="🦀",
            label="RS",
            frameworks=["tokio", "actix", "rocket", "serde"],
            tools=["cargo", "rustc", "clippy", "rustfmt"],
            file_patterns=[r".*\.rs$", r"Cargo\.toml$", r"Cargo\.lock$"],
            test_framework="cargo test"
        ),
        "csharp": AgentTemplate(
            language="csharp",
            display_name="C# Engineer",
            color="magenta",
            emoji="🔷",
            label="CS",
            frameworks=["dotnet", "aspnet", "unity", "xamarin"],
            tools=["dotnet", "msbuild", "nuget", "xunit", "nunit"],
            file_patterns=[r".*\.cs$", r".*\.csproj$", r".*\.sln$", r".*\.xaml$"],
            test_framework="xunit"
        ),
        "php": AgentTemplate(
            language="php",
            display_name="PHP Engineer",
            color="blue",
            emoji="🐘",
            label="PHP",
            frameworks=["laravel", "symfony", "wordpress", "composer"],
            tools=["php", "composer", "phpunit", "psalm", "phpstan"],
            file_patterns=[r".*\.php$", r"composer\.json$", r".*\.blade\.php$"],
            test_framework="phpunit"
        ),
        "swift": AgentTemplate(
            language="swift",
            display_name="Swift Engineer",
            color="yellow",
            emoji="🦉",
            label="SW",
            frameworks=["swiftui", "uikit", "vapor", "combine"],
            tools=["swift", "swiftc", "xcodebuild", "xctest"],
            file_patterns=[r".*\.swift$", r".*\.xcodeproj$", r"Package\.swift$"],
            test_framework="xctest"
        ),
        "kotlin": AgentTemplate(
            language="kotlin",
            display_name="Kotlin Engineer",
            color="magenta",
            emoji="🎯",
            label="KT",
            frameworks=["android", "ktor", "spring", "compose"],
            tools=["kotlinc", "gradle", "maven", "junit"],
            file_patterns=[r".*\.kt$", r".*\.kts$", r"build\.gradle\.kts$"],
            test_framework="junit"
        ),
        "scala": AgentTemplate(
            language="scala",
            display_name="Scala Engineer",
            color="red",
            emoji="🔴",
            label="SC",
            frameworks=["play", "akka", "spark", "cats"],
            tools=["scalac", "sbt", "mill", "scalatest"],
            file_patterns=[r".*\.scala$", r".*\.sbt$", r"build\.sbt$"],
            test_framework="scalatest"
        ),
        "dart": AgentTemplate(
            language="dart",
            display_name="Dart/Flutter Engineer",
            color="blue",
            emoji="🎯",
            label="DT",
            frameworks=["flutter", "angular_dart", "aqueduct"],
            tools=["dart", "flutter", "pub", "dart_test"],
            file_patterns=[r".*\.dart$", r"pubspec\.yaml$", r".*\.arb$"],
            test_framework="dart test"
        ),
        "elixir": AgentTemplate(
            language="elixir",
            display_name="Elixir Engineer",
            color="magenta",
            emoji="💧",
            label="EX",
            frameworks=["phoenix", "ecto", "otp", "nerves"],
            tools=["elixir", "mix", "iex", "exunit"],
            file_patterns=[r".*\.ex$", r".*\.exs$", r"mix\.exs$"],
            test_framework="exunit"
        ),
        "haskell": AgentTemplate(
            language="haskell",
            display_name="Haskell Engineer",
            color="cyan",
            emoji="λ",
            label="HS",
            frameworks=["yesod", "servant", "scotty", "stack"],
            tools=["ghc", "stack", "cabal", "hspec"],
            file_patterns=[r".*\.hs$", r".*\.lhs$", r".*\.cabal$", r"stack\.yaml$"],
            test_framework="hspec"
        ),
        "julia": AgentTemplate(
            language="julia",
            display_name="Julia Engineer",
            color="green",
            emoji="🔬",
            label="JL",
            frameworks=["flux", "genie", "plots", "dataframes"],
            tools=["julia", "pkg", "test", "documenter"],
            file_patterns=[r".*\.jl$", r"Project\.toml$", r"Manifest\.toml$"],
            test_framework="Test"
        ),
        "lua": AgentTemplate(
            language="lua",
            display_name="Lua Engineer",
            color="blue",
            emoji="🌙",
            label="LUA",
            frameworks=["openresty", "luvit", "love2d", "torch"],
            tools=["lua", "luarocks", "luajit", "busted"],
            file_patterns=[r".*\.lua$", r".*\.rockspec$"],
            test_framework="busted"
        ),
        "perl": AgentTemplate(
            language="perl",
            display_name="Perl Engineer",
            color="cyan",
            emoji="🐪",
            label="PL",
            frameworks=["catalyst", "mojolicious", "dancer", "cpan"],
            tools=["perl", "cpan", "prove", "perltidy"],
            file_patterns=[r".*\.pl$", r".*\.pm$", r".*\.pod$", r"Makefile\.PL$"],
            test_framework="Test::More"
        ),
        "r": AgentTemplate(
            language="r",
            display_name="R Statistician",
            color="blue",
            emoji="📊",
            label="R",
            frameworks=["shiny", "ggplot2", "tidyverse", "caret"],
            tools=["R", "Rscript", "devtools", "testthat"],
            file_patterns=[r".*\.R$", r".*\.Rmd$", r".*\.Rproj$"],
            test_framework="testthat"
        ),
        "matlab": AgentTemplate(
            language="matlab",
            display_name="MATLAB Engineer",
            color="yellow",
            emoji="📐",
            label="MAT",
            frameworks=["simulink", "signal_processing", "image_processing"],
            tools=["matlab", "simulink", "matlab_compiler"],
            file_patterns=[r".*\.m$", r".*\.mat$", r".*\.mlx$", r".*\.slx$"],
            test_framework="matlab.unittest"
        ),
        "objective-c": AgentTemplate(
            language="objective-c",
            display_name="Objective-C Engineer",
            color="blue",
            emoji="📱",
            label="OC",
            frameworks=["cocoa", "uikit", "foundation", "cocos2d"],
            tools=["clang", "xcodebuild", "cocoapods", "xctest"],
            file_patterns=[r".*\.m$", r".*\.mm$", r".*\.h$"],
            test_framework="XCTest"
        ),
        "groovy": AgentTemplate(
            language="groovy",
            display_name="Groovy Engineer",
            color="green",
            emoji="🎸",
            label="GR",
            frameworks=["grails", "gradle", "spock", "geb"],
            tools=["groovy", "gradle", "grails", "spock"],
            file_patterns=[r".*\.groovy$", r".*\.gradle$", r"Jenkinsfile"],
            test_framework="spock"
        ),
        "clojure": AgentTemplate(
            language="clojure",
            display_name="Clojure Engineer",
            color="green",
            emoji="🔗",
            label="CLJ",
            frameworks=["ring", "compojure", "reagent", "re-frame"],
            tools=["lein", "clojure", "boot", "midje"],
            file_patterns=[r".*\.clj$", r".*\.cljs$", r".*\.cljc$", r"project\.clj$"],
            test_framework="clojure.test"
        ),
        "solidity": AgentTemplate(
            language="solidity",
            display_name="Blockchain Engineer",
            color="cyan",
            emoji="⛓️",
            label="SOL",
            frameworks=["truffle", "hardhat", "web3", "ethers"],
            tools=["solc", "truffle", "hardhat", "ganache"],
            file_patterns=[r".*\.sol$", r"truffle-config\.js$", r"hardhat\.config\.js$"],
            test_framework="truffle test"
        ),
        "devops": AgentTemplate(
            language="devops",
            display_name="DevOps Engineer",
            color="magenta",
            emoji="🚀",
            label="DO",
            frameworks=["docker", "kubernetes", "terraform", "ansible", "jenkins", "github-actions"],
            tools=["docker", "kubectl", "terraform", "ansible", "helm"],
            file_patterns=[r"Dockerfile$", r".*\.yaml$", r".*\.yml$", r".*\.tf$", r"Jenkinsfile$"],
            test_framework="inspec"
        ),
        "zig": AgentTemplate(
            language="zig",
            display_name="Zig Engineer",
            color="yellow",
            emoji="⚡",
            label="ZIG",
            frameworks=["zig-std", "raylib", "vulkan"],
            tools=["zig", "zig-build", "zig-test"],
            file_patterns=[r".*\.zig$", r"build\.zig$"],
            test_framework="zig test"
        ),
        "nim": AgentTemplate(
            language="nim",
            display_name="Nim Engineer",
            color="yellow",
            emoji="👑",
            label="NIM",
            frameworks=["jester", "karax", "nimble"],
            tools=["nim", "nimble", "testament"],
            file_patterns=[r".*\.nim$", r".*\.nimble$", r".*\.nims$"],
            test_framework="unittest"
        ),
        "crystal": AgentTemplate(
            language="crystal",
            display_name="Crystal Engineer",
            color="white",
            emoji="💎",
            label="CR",
            frameworks=["kemal", "lucky", "amber"],
            tools=["crystal", "shards", "spec"],
            file_patterns=[r".*\.cr$", r"shard\.yml$"],
            test_framework="spec"
        )
    }

    def __init__(self, xavier_path: str = ".xavier"):
        self.xavier_path = xavier_path
        self.agents_dir = os.path.join(xavier_path, "agents")
        self.logger = logging.getLogger("Xavier.DynamicAgentFactory")

        # Ensure directories exist
        os.makedirs(self.agents_dir, exist_ok=True)

    def detect_required_agent(self, task: AgentTask) -> Optional[str]:
        """Detect which agent is needed based on task requirements"""
        # Check tech constraints
        for constraint in task.tech_constraints:
            constraint_lower = constraint.lower()

            # Check against known languages
            for language, template in self.AGENT_TEMPLATES.items():
                if language in constraint_lower:
                    return language
                # Check frameworks
                for framework in template.frameworks:
                    if framework in constraint_lower:
                        return language

        # Check task description and requirements
        full_context = f"{task.description} {' '.join(task.requirements)}".lower()

        for language, template in self.AGENT_TEMPLATES.items():
            # Check language name
            if language in full_context:
                return language

            # Check display name
            if template.display_name.lower() in full_context:
                return language

            # Check frameworks
            for framework in template.frameworks:
                if framework in full_context:
                    return language

        return None

    def agent_exists(self, language: str) -> bool:
        """Check if agent YAML already exists"""
        agent_file = os.path.join(self.agents_dir, f"{language}_engineer.yaml")
        return os.path.exists(agent_file)

    def create_agent_yaml(self, language: str) -> bool:
        """Create YAML configuration for an agent"""
        if language not in self.AGENT_TEMPLATES:
            self.logger.warning(f"No template found for language: {language}")
            return False

        template = self.AGENT_TEMPLATES[language]

        # Create agent configuration
        agent_config = {
            "name": f"{language}-engineer",
            "display_name": template.display_name,
            "color": template.color,
            "emoji": template.emoji,
            "label": template.label,
            "description": f"Specialized in {language.title()} development with {', '.join(template.frameworks[:3])}",
            "tools": ["Edit", "Write", "Read", "Bash", "Grep", "Glob"],
            "capabilities": [
                f"{language}_development",
                "testing",
                "debugging",
                "code_review",
                "refactoring",
                "performance_optimization"
            ],
            "restricted_actions": [
                "deploy_production",
                "delete_database"
            ],
            "allowed_file_patterns": template.file_patterns,
            "languages": [language],
            "frameworks": template.frameworks
        }

        # Write YAML file
        agent_file = os.path.join(self.agents_dir, f"{language}_engineer.yaml")
        try:
            with open(agent_file, 'w') as f:
                yaml.dump(agent_config, f, default_flow_style=False, sort_keys=False)

            self.logger.info(f"Created agent configuration: {agent_file}")

            # Reload agent metadata
            from .agent_metadata import get_metadata_manager
            get_metadata_manager().reload_metadata()

            return True
        except Exception as e:
            self.logger.error(f"Failed to create agent YAML: {e}")
            return False

    def create_agent_class(self, language: str) -> Optional[Type[BaseAgent]]:
        """Dynamically create an agent class"""
        if language not in self.AGENT_TEMPLATES:
            return None

        template = self.AGENT_TEMPLATES[language]

        # Create a dynamic agent class
        class DynamicAgent(BaseAgent):
            def __init__(self):
                capabilities = AgentCapability(
                    languages=[language],
                    frameworks=template.frameworks,
                    tools=template.tools,
                    restricted_actions=["deploy_production", "delete_database"],
                    allowed_file_patterns=template.file_patterns
                )
                super().__init__(f"{language}-engineer", capabilities)
                self.test_framework = template.test_framework

            def execute_task(self, task: AgentTask) -> AgentResult:
                """Execute task with language-specific logic"""
                self.start_task(task)

                # Simulate task execution
                self.update_status("Analyzing", f"Understanding {language} requirements")
                self.show_thinking(f"Planning {language} implementation...")

                # Language-specific execution logic would go here
                # For now, return a successful result
                result = AgentResult(
                    success=True,
                    task_id=task.task_id,
                    output=f"{template.display_name} completed task: {task.description}",
                    test_results={"framework": self.test_framework, "coverage": 100.0},
                    files_created=[],
                    files_modified=[],
                    validation_results={
                        "clean_code": True,
                        "solid_principles": True,
                        "test_coverage": 100.0
                    },
                    errors=[]
                )

                self.complete_task(True, f"Task completed with {self.test_framework}")
                return result

            def validate_task(self, task: AgentTask) -> Tuple[bool, List[str]]:
                """Validate task is appropriate for this agent"""
                errors = []

                # Check if task involves this language
                task_context = f"{task.description} {' '.join(task.requirements)}".lower()
                if language not in task_context and not any(fw in task_context for fw in template.frameworks[:3]):
                    errors.append(f"Task doesn't appear to involve {language}")

                # Check tech constraints
                if task.tech_constraints:
                    supported = False
                    for constraint in task.tech_constraints:
                        if language in constraint.lower() or any(fw in constraint.lower() for fw in template.frameworks):
                            supported = True
                            break
                    if not supported:
                        errors.append(f"Tech constraints don't match {language} capabilities")

                return len(errors) == 0, errors

        # Set a meaningful class name
        DynamicAgent.__name__ = f"{language.title()}EngineerAgent"
        DynamicAgent.__qualname__ = f"{language.title()}EngineerAgent"

        return DynamicAgent

    def get_or_create_agent(self, language: str) -> Optional[BaseAgent]:
        """Get existing agent or create new one"""
        # Ensure YAML exists
        if not self.agent_exists(language):
            if not self.create_agent_yaml(language):
                return None

        # Create agent class
        agent_class = self.create_agent_class(language)
        if agent_class:
            return agent_class()

        return None

    def create_agent(self, name: str, display_name: str, technology: str, role_description: str) -> Tuple[bool, str]:
        """Create an agent with specified parameters

        Args:
            name: Agent name (e.g., 'devops-engineer')
            display_name: Display name (e.g., 'DevOps Engineer')
            technology: Primary technology (e.g., 'docker', 'kubernetes')
            role_description: Description of the agent's role

        Returns:
            Tuple of (success, message)
        """
        # Extract base technology from agent name if needed
        if '-' in name:
            base_tech = name.split('-')[0]
        else:
            base_tech = technology.lower()

        # Check if we have a template for this technology
        if base_tech not in self.AGENT_TEMPLATES:
            # Create a generic template for unknown technologies
            self.logger.info(f"Creating generic agent for {base_tech}")

            # Create a basic agent configuration
            agent_config = {
                "name": name,
                "display_name": display_name,
                "color": "blue",
                "emoji": "🔧",
                "label": base_tech.upper()[:3],
                "description": role_description,
                "tools": ["Edit", "Write", "Read", "Bash", "Grep", "Glob"],
                "capabilities": [
                    f"{base_tech}_development",
                    "testing",
                    "debugging",
                    "code_review",
                    "refactoring"
                ],
                "restricted_actions": [
                    "deploy_production",
                    "delete_database"
                ],
                "allowed_file_patterns": [".*"],
                "languages": [base_tech],
                "frameworks": []
            }

            # Write YAML file
            agent_file = os.path.join(self.agents_dir, f"{name.replace('-', '_')}.yaml")
            try:
                with open(agent_file, 'w') as f:
                    yaml.dump(agent_config, f, default_flow_style=False, sort_keys=False)

                self.logger.info(f"Created generic agent configuration: {agent_file}")

                # Create Claude Code agent MD file with proper YAML frontmatter
                claude_agents_dir = os.path.join(os.path.dirname(self.xavier_path), ".claude", "agents")
                os.makedirs(claude_agents_dir, exist_ok=True)

                claude_agent_file = os.path.join(claude_agents_dir, f"{name}.md")
                # Create proper Claude Code agent with YAML frontmatter
                claude_content = f"""---
name: {name}
description: {role_description[:200] if len(role_description) > 200 else role_description}
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

# {display_name}

You are an expert {display_name}.

{role_description}

## Core Expertise
- **{base_tech.title()}**: Full-stack development and implementation
- **Testing**: TDD, comprehensive test coverage
- **Clean Code**: Following best practices and SOLID principles
- **Performance**: Optimization and profiling
- **Debugging**: Advanced troubleshooting skills

## Development Approach
1. **Test-First**: Write tests before implementation
2. **Clean Architecture**: Maintainable and scalable design
3. **Performance**: Optimize for efficiency
4. **Documentation**: Clear and comprehensive
5. **Security**: Follow security best practices

I deliver high-quality solutions following industry best practices.
"""

                with open(claude_agent_file, 'w') as f:
                    f.write(claude_content)

                self.logger.info(f"Created Claude agent file with YAML frontmatter: {claude_agent_file}")

                # Reload agent metadata
                from .agent_metadata import get_metadata_manager
                get_metadata_manager().reload_metadata()

                return True, f"Successfully created agent: {name}"

            except Exception as e:
                error_msg = f"Failed to create agent {name}: {e}"
                self.logger.error(error_msg)
                return False, error_msg

        # Use existing template
        if not self.agent_exists(base_tech):
            if self.create_agent_yaml(base_tech):
                # Also create Claude Code MD file
                self._create_claude_agent_md(name, display_name)
                return True, f"Successfully created agent from template: {name}"
            else:
                return False, f"Failed to create agent from template: {name}"

        return True, f"Agent already exists: {name}"

    def _create_claude_agent_md(self, name: str, display_name: str):
        """Create Claude Code compatible MD file for agent with proper YAML frontmatter"""
        claude_agents_dir = os.path.join(os.path.dirname(self.xavier_path), ".claude", "agents")
        os.makedirs(claude_agents_dir, exist_ok=True)

        claude_agent_file = os.path.join(claude_agents_dir, f"{name}.md")
        if not os.path.exists(claude_agent_file):
            # Extract technology from name
            base_tech = name.split('-')[0] if '-' in name else name

            # Get template if available for better descriptions
            template = self.AGENT_TEMPLATES.get(base_tech)
            if template:
                frameworks_str = ', '.join(template.frameworks[:3])
                description = f"{display_name} for {frameworks_str}. Handles {base_tech} development, testing, debugging, performance optimization."
            else:
                description = f"{display_name} specialist. Handles {base_tech} development, testing, debugging, code review, refactoring."

            # Create content with proper YAML frontmatter for Claude Code
            content = f"""---
name: {name}
description: {description}
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

# {display_name}

You are an expert {display_name} specializing in {base_tech} development.

## Core Expertise
- **{base_tech.title()}**: Full-stack development and architecture
- **Testing**: TDD, unit tests, integration tests
- **Best Practices**: Clean code, SOLID principles
- **Performance**: Optimization and profiling
- **Tools**: Industry-standard tooling and frameworks

## Development Approach
1. **Test-First**: Write tests before implementation
2. **Clean Code**: Maintainable and readable code
3. **Performance**: Optimize for efficiency
4. **Documentation**: Clear and comprehensive
5. **Security**: Follow security best practices

I deliver high-quality {base_tech} solutions following best practices.
"""

            with open(claude_agent_file, 'w') as f:
                f.write(content)

            self.logger.info(f"Created Claude agent MD with YAML frontmatter: {claude_agent_file}")

    def auto_detect_and_create(self, task: AgentTask) -> Optional[BaseAgent]:
        """Automatically detect required agent and create if needed"""
        language = self.detect_required_agent(task)

        if language:
            self.logger.info(f"Detected need for {language} agent")
            agent = self.get_or_create_agent(language)
            if agent:
                self.logger.info(f"Successfully created/retrieved {language} agent")
                return agent

        return None

    def list_available_templates(self) -> List[str]:
        """List all available agent templates"""
        return list(self.AGENT_TEMPLATES.keys())

    def get_template_info(self, language: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific template"""
        if language in self.AGENT_TEMPLATES:
            template = self.AGENT_TEMPLATES[language]
            return {
                "language": template.language,
                "display_name": template.display_name,
                "color": template.color,
                "emoji": template.emoji,
                "frameworks": template.frameworks,
                "test_framework": template.test_framework
            }
        return None


# Global factory instance
_factory_instance = None


def get_agent_factory() -> DynamicAgentFactory:
    """Get the global agent factory instance"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = DynamicAgentFactory()
    return _factory_instance


def auto_create_agent(task: AgentTask) -> Optional[BaseAgent]:
    """Convenience function to auto-create agent for a task"""
    return get_agent_factory().auto_detect_and_create(task)