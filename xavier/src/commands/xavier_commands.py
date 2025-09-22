"""
Xavier Framework - Command Handlers for Claude Code
Enterprise-grade command system for SCRUM workflow
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import logging
from datetime import datetime

from ..core.xavier_engine import XavierEngine, ItemType, Priority
from ..scrum.scrum_manager import SCRUMManager, safe_get_attr, safe_set_attr, get_sprint_status_value
from ..agents.orchestrator import AgentOrchestrator, AgentTask

# Try to import ANSI art module
try:
    from ..utils.ansi_art import display_welcome, display_sprint_start, display_mini_banner
except ImportError:
    display_welcome = None
    display_sprint_start = None
    display_mini_banner = None


class XavierCommands:
    """Command handlers for Xavier Framework integration with Claude Code"""

    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        self.config_path = os.path.join(project_path, ".xavier", "config.json")
        self.data_path = os.path.join(project_path, ".xavier", "data")
        self.claude_path = os.path.join(project_path, ".claude")

        # Create Xavier directories
        os.makedirs(os.path.join(project_path, ".xavier"), exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)

        # Create Claude directories
        os.makedirs(self.claude_path, exist_ok=True)
        os.makedirs(os.path.join(self.claude_path, "agents"), exist_ok=True)

        # Initialize components
        self.engine = XavierEngine(self.config_path)
        self.scrum = SCRUMManager(self.data_path)
        self.orchestrator = AgentOrchestrator(self.config_path)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("Xavier.Commands")

        # Command registry
        self.commands = {
            "/create-story": self.create_story,
            "/create-task": self.create_task,
            "/create-bug": self.create_bug,
            "/create-roadmap": self.create_roadmap,
            "/create-project": self.create_project,
            "/learn-project": self.learn_project,
            "/create-sprint": self.create_sprint,
            "/start-sprint": self.start_sprint,
            "/end-sprint": self.end_sprint,
            "/set-story-points": self.set_story_points,
            "/estimate-story": self.estimate_story,
            "/assign-task": self.assign_task,
            "/review-code": self.review_code,
            "/generate-report": self.generate_report,
            "/tech-stack-analyze": self.tech_stack_analyze,
            "/create-agent": self.create_agent,
            "/list-stories": self.list_stories,
            "/list-tasks": self.list_tasks,
            "/list-bugs": self.list_bugs,
            "/show-backlog": self.show_backlog,
            "/show-sprint": self.show_sprint,
            "/xavier-help": self.show_help,
            "/xavier-update": self.xavier_update
        }

    def execute(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a Xavier command"""
        if command not in self.commands:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "available_commands": list(self.commands.keys())
            }

        try:
            result = self.commands[command](args or {})
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"success": False, "error": str(e)}

    def create_story(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a user story
        Args:
            title: Story title
            as_a: User role
            i_want: Feature description
            so_that: Business value
            acceptance_criteria: List of acceptance criteria
            priority: Priority level (Critical/High/Medium/Low)
            epic_id: Optional epic ID
        """
        # Validate required fields
        required = ["title", "as_a", "i_want", "so_that", "acceptance_criteria"]
        for field in required:
            if field not in args:
                raise ValueError(f"Required field missing: {field}")

        # Create story in SCRUM manager
        story = self.scrum.create_story(
            title=args["title"],
            as_a=args["as_a"],
            i_want=args["i_want"],
            so_that=args["so_that"],
            acceptance_criteria=args["acceptance_criteria"],
            priority=args.get("priority", "Medium"),
            epic_id=args.get("epic_id")
        )

        # Request story point estimation from PM agent
        estimation_task = AgentTask(
            task_id=f"EST_{story.id}",
            task_type="estimate_story",
            description=story.description,
            requirements=story.acceptance_criteria,
            test_requirements={},
            acceptance_criteria=["Provide story point estimate"],
            tech_constraints=[]
        )

        estimation_result = self.orchestrator.delegate_task(estimation_task)

        if estimation_result.success:
            points = estimation_result.validation_results.get("story_points", 5)
            self.scrum.estimate_story(story.id, points)
            story.story_points = points

        return {
            "story_id": story.id,
            "title": story.title,
            "description": story.description,
            "story_points": story.story_points,
            "status": story.status
        }

    def create_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a task under a story
        Args:
            story_id: Parent story ID
            title: Task title
            description: Task description
            technical_details: Technical implementation details
            estimated_hours: Estimated hours
            test_criteria: List of test criteria
            priority: Priority level
            dependencies: List of dependency task IDs
        """
        # Validate story exists
        if "story_id" not in args or args["story_id"] not in self.scrum.stories:
            raise ValueError(f"Invalid or missing story_id")

        # Create task in SCRUM manager
        task = self.scrum.create_task(
            story_id=args["story_id"],
            title=args["title"],
            description=args["description"],
            technical_details=args.get("technical_details", ""),
            estimated_hours=args.get("estimated_hours", 4.0),
            test_criteria=args.get("test_criteria", []),
            priority=args.get("priority", "Medium"),
            dependencies=args.get("dependencies", [])
        )

        # Create work item in engine for tracking
        self.engine.create_work_item(
            item_type=ItemType.TASK,
            title=task.title,
            description=task.description,
            priority=Priority[task.priority.upper()],
            story_points=task.story_points,
            acceptance_criteria=task.test_criteria,
            parent_id=task.story_id,
            dependencies=task.dependencies
        )

        return {
            "task_id": task.id,
            "story_id": task.story_id,
            "title": task.title,
            "estimated_hours": task.estimated_hours,
            "story_points": task.story_points,
            "status": task.status
        }

    def create_bug(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a bug report
        Args:
            title: Bug title
            description: Bug description
            steps_to_reproduce: List of reproduction steps
            expected_behavior: Expected behavior
            actual_behavior: Actual behavior
            severity: Severity (Critical/High/Medium/Low)
            priority: Priority level
            affected_stories: List of affected story IDs
            affected_components: List of affected components
        """
        # Create bug in SCRUM manager
        bug = self.scrum.create_bug(
            title=args["title"],
            description=args["description"],
            steps_to_reproduce=args["steps_to_reproduce"],
            expected_behavior=args["expected_behavior"],
            actual_behavior=args["actual_behavior"],
            severity=args["severity"],
            priority=args.get("priority", "High"),
            affected_stories=args.get("affected_stories", []),
            affected_components=args.get("affected_components", [])
        )

        # Create work item in engine
        self.engine.create_work_item(
            item_type=ItemType.BUG,
            title=bug.title,
            description=bug.description,
            priority=Priority[bug.priority.upper()],
            story_points=bug.story_points,
            acceptance_criteria=[
                f"Fix: {bug.expected_behavior}",
                "Add tests to prevent regression",
                "Verify fix across affected components"
            ]
        )

        return {
            "bug_id": bug.id,
            "title": bug.title,
            "severity": bug.severity,
            "priority": bug.priority,
            "story_points": bug.story_points,
            "status": bug.status
        }

    def create_roadmap(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a product roadmap
        Args:
            name: Roadmap name
            vision: Product vision
            milestones: List of milestone definitions
        """
        roadmap = self.scrum.create_roadmap(
            name=args["name"],
            vision=args["vision"]
        )

        # Add milestones if provided
        for milestone in args.get("milestones", []):
            self.scrum.add_milestone_to_roadmap(
                roadmap_id=roadmap.id,
                milestone_name=milestone["name"],
                target_date=datetime.fromisoformat(milestone["target_date"]),
                epics=milestone.get("epics", []),
                success_criteria=milestone.get("success_criteria", [])
            )

        return {
            "roadmap_id": roadmap.id,
            "name": roadmap.name,
            "vision": roadmap.vision,
            "milestones": len(roadmap.milestones)
        }

    def create_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize a new Xavier project with intelligent analysis
        Args:
            name: Project name (required)
            description: Detailed project description (can be multi-line)
            tech_stack: Technology stack definition (optional - will be suggested if not provided)
            project_type: Type of project (web, api, mobile, ecommerce, blog, etc.)
            auto_generate_stories: Generate initial stories from description (default: True)
            auto_setup_agents: Configure agents based on tech stack (default: True)
            template: Use a pre-defined template (optional)
            team_size: Team size
            methodology: Development methodology (Scrum/Kanban)
        """
        from ..analyzers.project_analyzer import ProjectAnalyzer
        from ..analyzers.project_templates import ProjectTemplates

        # Validate required fields
        if "name" not in args:
            raise ValueError("Project name is required")

        project_name = args["name"]
        description = args.get("description", f"Project {project_name}")
        tech_stack = args.get("tech_stack", None)
        project_type = args.get("project_type", None)
        auto_generate_stories = args.get("auto_generate_stories", True)
        auto_setup_agents = args.get("auto_setup_agents", True)
        template_name = args.get("template", None)

        # If template is specified, use it as base
        if template_name:
            template = ProjectTemplates.get_template(template_name)
            if not tech_stack:
                tech_stack = template.tech_stack
            initial_structure = template.initial_structure
            initial_files = template.initial_files
            template_stories = template.default_stories
        else:
            initial_structure = []
            initial_files = {}
            template_stories = []

        # Analyze project if description is provided
        analyzer = ProjectAnalyzer()
        analysis = analyzer.analyze(project_name, description, tech_stack)

        # Use analysis results
        if not tech_stack:
            tech_stack = analysis.suggested_tech_stack

        if not project_type:
            project_type = analysis.project_type

        # Create enhanced project configuration
        project_config = {
            "name": project_name,
            "description": description,
            "project_type": project_type,
            "tech_stack": tech_stack,
            "detected_features": analysis.detected_features,
            "performance_requirements": analysis.performance_requirements,
            "estimated_complexity": analysis.estimated_complexity,
            "team_size": args.get("team_size", 5),
            "methodology": args.get("methodology", "Scrum"),
            "created_at": datetime.now().isoformat(),
            "xavier_version": "1.1.9"
        }

        # Save project configuration
        with open(self.config_path, 'w') as f:
            json.dump(project_config, f, indent=2)

        # Initialize project structure based on tech stack
        directories = self._generate_project_structure(tech_stack, project_type)

        # Add template directories if using template
        if initial_structure:
            directories.extend(initial_structure)

        # Remove duplicates while preserving order
        seen = set()
        unique_directories = []
        for d in directories:
            if d not in seen:
                seen.add(d)
                unique_directories.append(d)

        # Create all directories
        for directory in unique_directories:
            os.makedirs(os.path.join(self.project_path, directory), exist_ok=True)

        # Create initial files from template
        files_created = []
        for file_path, content in initial_files.items():
            full_path = os.path.join(self.project_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
            files_created.append(file_path)

        # Setup agents based on tech stack
        agents_created = []
        if auto_setup_agents:
            agents_created = self._setup_project_agents(tech_stack)
            # Generate agents for tech stack
            self.orchestrator._generate_tech_stack_agents()

        # Generate initial stories and epics
        stories_created = []
        epics_created = []

        if auto_generate_stories:
            # Create epics
            for epic_data in analysis.suggested_epics:
                epic = self.scrum.create_epic(
                    title=epic_data["title"],
                    description=epic_data["description"],
                    business_value=100  # High value for auto-generated epics
                )
                epics_created.append({
                    "id": epic.id,
                    "title": epic.title
                })

            # Create stories from analysis
            for story_data in analysis.suggested_stories:
                story = self.scrum.create_story(
                    title=story_data["title"],
                    as_a=story_data.get("as_a", "user"),
                    i_want=story_data.get("i_want", story_data["title"]),
                    so_that=story_data.get("so_that", "I can use the system"),
                    acceptance_criteria=story_data.get("acceptance_criteria", []),
                    priority=story_data.get("priority", "Medium")
                )

                # Auto-estimate story points
                if "story_points" in story_data:
                    self.scrum.estimate_story(story.id, story_data["story_points"])

                stories_created.append({
                    "id": story.id,
                    "title": story.title,
                    "points": story_data.get("story_points", 0)
                })

            # Add template stories if any
            for story_data in template_stories:
                story = self.scrum.create_story(
                    title=story_data["title"],
                    as_a="developer",
                    i_want=f"to {story_data['title'].lower()}",
                    so_that="the project has proper foundation",
                    acceptance_criteria=[],
                    priority=story_data.get("priority", "Medium")
                )

                if "story_points" in story_data:
                    self.scrum.estimate_story(story.id, story_data["story_points"])

                stories_created.append({
                    "id": story.id,
                    "title": story.title,
                    "points": story_data.get("story_points", 0)
                })

        # Auto-generate roadmap for the project
        roadmap_created = self._generate_default_roadmap(project_config, analysis)

        # Create README.md with project information
        readme_content = self._generate_readme(project_config, analysis)
        with open(os.path.join(self.project_path, "README.md"), 'w') as f:
            f.write(readme_content)

        # Generate project summary
        summary = analyzer.generate_project_summary(analysis)

        return {
            "project": project_config,
            "analysis_summary": summary,
            "directories_created": len(unique_directories),
            "files_created": files_created,
            "agents_configured": agents_created,
            "epics_created": len(epics_created),
            "stories_created": len(stories_created),
            "roadmap_created": roadmap_created,
            "total_story_points": sum(s["points"] for s in stories_created),
            "next_steps": [
                f"Review generated stories with /show-backlog",
                f"Review generated roadmap with /xavier-help roadmap",
                f"Create first sprint with /create-sprint",
                f"Start development with /start-sprint",
                f"View project details in README.md"
            ]
        }

    def _generate_project_structure(self, tech_stack: Dict[str, Any],
                                   project_type: str) -> List[str]:
        """Generate project directory structure based on tech stack"""
        directories = [
            ".xavier",
            ".xavier/data",
            ".xavier/agents",
            ".xavier/sprints",
            ".xavier/reports",
            ".claude",
            ".claude/commands",
            "docs",
            "scripts",
            "tests"
        ]

        # Add frontend directories if needed
        if "frontend" in tech_stack:
            frontend_framework = tech_stack["frontend"].get("framework", "").lower()
            if "react" in frontend_framework or "next" in frontend_framework:
                directories.extend([
                    "frontend",
                    "frontend/src",
                    "frontend/src/components",
                    "frontend/src/pages",
                    "frontend/src/services",
                    "frontend/src/utils",
                    "frontend/public"
                ])
            elif "vue" in frontend_framework:
                directories.extend([
                    "frontend",
                    "frontend/src",
                    "frontend/src/components",
                    "frontend/src/views",
                    "frontend/src/services",
                    "frontend/public"
                ])

        # Add backend directories
        if "backend" in tech_stack:
            backend_lang = tech_stack["backend"].get("language", "").lower()
            if "python" in backend_lang:
                directories.extend([
                    "backend",
                    "backend/app",
                    "backend/app/api",
                    "backend/app/core",
                    "backend/app/models",
                    "backend/app/services",
                    "backend/tests"
                ])
            elif "go" in backend_lang:
                directories.extend([
                    "backend",
                    "backend/cmd",
                    "backend/internal",
                    "backend/pkg",
                    "backend/api"
                ])
            elif "node" in backend_lang or "javascript" in backend_lang:
                directories.extend([
                    "backend",
                    "backend/src",
                    "backend/src/routes",
                    "backend/src/models",
                    "backend/src/services",
                    "backend/src/middleware"
                ])

        # Add Docker support
        if "devops" in tech_stack:
            if "docker" in str(tech_stack["devops"]).lower():
                directories.append("docker")
            if "kubernetes" in str(tech_stack["devops"]).lower():
                directories.append("k8s")

        # Add CI/CD
        directories.append(".github/workflows")

        return directories

    def _setup_project_agents(self, tech_stack: Dict[str, Any]) -> List[str]:
        """Setup agents based on project tech stack"""
        agents = ["project_manager", "context_manager"]  # Always include these

        # Add language-specific agents
        if "backend" in tech_stack:
            backend_lang = tech_stack["backend"].get("language", "").lower()
            if "python" in backend_lang:
                agents.append("python_engineer")
            if "go" in backend_lang:
                agents.append("golang_engineer")
            if "node" in backend_lang or "javascript" in backend_lang:
                agents.append("nodejs_engineer")

        if "frontend" in tech_stack:
            agents.append("frontend_engineer")

        if "database" in tech_stack:
            agents.append("database_engineer")

        if "devops" in tech_stack:
            agents.append("devops_engineer")

        # Configure agents in Xavier config
        agent_config = {}
        for agent in agents:
            agent_config[agent] = {"enabled": True}

        # Update configuration
        config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)

        config["agents"] = agent_config

        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

        return agents

    def _generate_default_roadmap(self, project_config: Dict[str, Any], analysis: Any) -> Dict[str, Any]:
        """Generate a default roadmap for the project"""
        # Create roadmap using SCRUM manager
        roadmap_name = f"{project_config['name']} Product Roadmap"
        vision = project_config.get('description', f"Building {project_config['name']} with modern technologies")

        roadmap = self.scrum.create_roadmap(
            name=roadmap_name,
            vision=vision
        )

        # Generate default milestones based on project type and complexity
        milestones = self._generate_default_milestones(project_config, analysis)

        # Add milestones to roadmap
        for milestone in milestones:
            self.scrum.add_milestone_to_roadmap(
                roadmap_id=roadmap.id,
                milestone_name=milestone["name"],
                target_date=milestone["target_date"],
                epics=milestone.get("epics", []),
                success_criteria=milestone["success_criteria"]
            )

        return {
            "id": roadmap.id,
            "name": roadmap.name,
            "vision": roadmap.vision,
            "milestones_count": len(milestones)
        }

    def _generate_default_milestones(self, project_config: Dict[str, Any], analysis: Any) -> List[Dict[str, Any]]:
        """Generate default milestones based on project type"""
        from datetime import datetime, timedelta

        milestones = []
        start_date = datetime.now()

        # Basic milestones that apply to most projects
        milestones.append({
            "name": "MVP Foundation",
            "target_date": start_date + timedelta(weeks=4),
            "success_criteria": [
                "Core architecture established",
                "Basic authentication system",
                "Initial database schema",
                "Development environment setup"
            ]
        })

        milestones.append({
            "name": "Core Features Complete",
            "target_date": start_date + timedelta(weeks=8),
            "success_criteria": [
                "Primary user workflows implemented",
                "API endpoints functional",
                "Basic UI/UX complete",
                "Unit tests coverage > 70%"
            ]
        })

        milestones.append({
            "name": "Beta Release",
            "target_date": start_date + timedelta(weeks=12),
            "success_criteria": [
                "Feature complete",
                "Performance testing complete",
                "Security audit passed",
                "Documentation complete"
            ]
        })

        milestones.append({
            "name": "Production Launch",
            "target_date": start_date + timedelta(weeks=16),
            "success_criteria": [
                "Deployment pipeline established",
                "Monitoring and logging active",
                "User acceptance testing passed",
                "Go-live checklist complete"
            ]
        })

        return milestones

    def _generate_readme(self, project_config: Dict[str, Any],
                        analysis: Any) -> str:
        """Generate README.md content for the project"""
        readme = f"""# {project_config['name']}

{project_config['description']}

## Project Overview

- **Type**: {project_config['project_type'].replace('_', ' ').title()}
- **Complexity**: {project_config['estimated_complexity']}
- **Methodology**: {project_config['methodology']}
- **Created**: {project_config['created_at']}

## Tech Stack

"""

        for component, details in project_config['tech_stack'].items():
            readme += f"### {component.title()}\n"
            if isinstance(details, dict):
                for key, value in details.items():
                    if value and key != "alternatives":
                        readme += f"- **{key.title()}**: {value}\n"
            else:
                readme += f"- {details}\n"
            readme += "\n"

        if project_config['detected_features']:
            readme += "## Features\n\n"
            for feature in project_config['detected_features']:
                readme += f"- {feature.replace('_', ' ').title()}\n"
            readme += "\n"

        if project_config['performance_requirements']:
            readme += "## Performance Requirements\n\n"
            for req in project_config['performance_requirements']:
                readme += f"- {req.replace('_', ' ').title()}\n"
            readme += "\n"

        readme += """## Getting Started

### Prerequisites

- Python 3.8+
- Xavier Framework installed
- Claude Code

### Installation

```bash
# Install dependencies
./scripts/setup.sh

# Initialize Xavier
/xavier-help
```

### Development

```bash
# View backlog
/show-backlog

# Create sprint
/create-sprint "Sprint 1" "Initial development" 14

# Start sprint
/start-sprint
```

## Xavier Commands

- `/create-story` - Create user stories
- `/create-task` - Create tasks
- `/create-bug` - Report bugs
- `/create-sprint` - Plan sprints
- `/start-sprint` - Begin development
- `/show-backlog` - View backlog
- `/xavier-help` - Get help

## Project Structure

```
.
├── .xavier/          # Xavier framework data
├── .claude/          # Claude Code integration
├── backend/          # Backend application
├── frontend/         # Frontend application (if applicable)
├── tests/            # Test suites
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## Contributing

This project follows Xavier Framework standards:
- 100% test coverage required
- Test-first development (TDD)
- Clean Code principles
- Sequential task execution
- SOLID design patterns

## License

[Add your license here]
"""
        return readme

    def learn_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn existing project structure and tech stack
        Args:
            deep_scan: Perform deep analysis (default: True)
            generate_agents: Generate missing agents (default: True)
        """
        # Use context manager agent to analyze codebase
        analysis_task = AgentTask(
            task_id="LEARN_PROJECT",
            task_type="analyze_codebase",
            description="Analyze existing project structure and patterns",
            requirements=["Identify tech stack", "Find patterns", "Detect frameworks"],
            test_requirements={},
            acceptance_criteria=["Complete codebase analysis"],
            tech_constraints=[]
        )

        result = self.orchestrator.delegate_task(analysis_task)

        # Detect tech stack
        tech_stack = self.orchestrator.tech_stack

        # Generate report
        report = {
            "languages": tech_stack.languages if tech_stack else [],
            "frameworks": tech_stack.frameworks if tech_stack else [],
            "build_tools": tech_stack.build_tools if tech_stack else [],
            "test_frameworks": tech_stack.test_frameworks if tech_stack else [],
            "databases": tech_stack.databases if tech_stack else [],
            "ci_cd_tools": tech_stack.ci_cd_tools if tech_stack else [],
            "agents_created": [],
            "patterns_found": result.validation_results.get("patterns_found", [])
        }

        # Generate agents if requested
        if args.get("generate_agents", True):
            self.orchestrator._generate_tech_stack_agents()
            report["agents_created"] = list(self.orchestrator.agents.keys())

        return report

    def create_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new sprint
        Args:
            name: Sprint name
            goal: Sprint goal
            duration_days: Sprint duration in days (default: 14)
            auto_plan: Automatically plan sprint (default: True)
        """
        sprint = self.scrum.create_sprint(
            name=args["name"],
            goal=args["goal"],
            duration_days=args.get("duration_days", 14)
        )

        # Auto-plan if requested
        if args.get("auto_plan", True):
            sprint_id = safe_get_attr(sprint, 'id')
            stories, tasks, bugs = self.scrum.plan_sprint(sprint_id)
            return {
                "sprint_id": sprint_id,
                "name": safe_get_attr(sprint, 'name'),
                "goal": safe_get_attr(sprint, 'goal'),
                "velocity": safe_get_attr(sprint, 'velocity'),
                "committed_points": safe_get_attr(sprint, 'committed_points', 0),
                "stories": len(stories),
                "tasks": len(tasks),
                "bugs": len(bugs),
                "status": "Planned"
            }

        return {
            "sprint_id": safe_get_attr(sprint, 'id'),
            "name": safe_get_attr(sprint, 'name'),
            "goal": safe_get_attr(sprint, 'goal'),
            "velocity": safe_get_attr(sprint, 'velocity'),
            "status": "Created - Ready for planning"
        }

    def start_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start sprint execution
        Args:
            sprint_id: Sprint ID (optional, uses current sprint if not provided)
            strict_mode: Enable strict sequential execution (default: True)
        """
        sprint_id = args.get("sprint_id")

        # Find sprint
        if not sprint_id:
            # Find latest planned sprint
            planned_sprints = []
            for s in self.scrum.sprints.values():
                status_value = get_sprint_status_value(s)
                if status_value == "Planning":
                    planned_sprints.append(s)

            if not planned_sprints:
                raise ValueError("No planned sprint found")
            sprint_id = safe_get_attr(planned_sprints[0], 'id')

        # Start sprint in SCRUM manager
        self.scrum.start_sprint(sprint_id)
        sprint = self.scrum.sprints[sprint_id]

        # Display sprint start banner
        import subprocess
        greeting_script = os.path.join(os.path.dirname(__file__), "..", "utils", "greeting.sh")
        if os.path.exists(greeting_script):
            subprocess.run([greeting_script, "sprint-start"], check=False)

        # Prepare tasks for agents
        agent_tasks = []

        # Process stories
        for story_id in sprint.stories:
            story = self.scrum.stories[story_id]

            # Create agent tasks for each story task
            for task_id in story.tasks:
                task = self.scrum.tasks[task_id]
                agent_task = AgentTask(
                    task_id=task_id,
                    task_type="implement_feature",
                    description=task.description,
                    requirements=[task.technical_details],
                    test_requirements={"criteria": task.test_criteria},
                    acceptance_criteria=task.test_criteria,
                    tech_constraints=self._detect_task_tech_constraints(task)
                )
                agent_tasks.append(agent_task)

        # Process bugs
        for bug_id in sprint.bugs:
            bug = self.scrum.bugs[bug_id]
            agent_task = AgentTask(
                task_id=bug_id,
                task_type="fix_bug",
                description=f"Fix: {bug.title}",
                requirements=[bug.description],
                test_requirements={
                    "reproduce_steps": bug.steps_to_reproduce,
                    "expected": bug.expected_behavior
                },
                acceptance_criteria=[
                    bug.expected_behavior,
                    "Add regression tests"
                ],
                tech_constraints=[]
            )
            agent_tasks.append(agent_task)

        # Execute tasks with orchestrator
        if args.get("strict_mode", True):
            # Sequential execution with strict validation
            results = self.orchestrator.execute_sprint_tasks(agent_tasks)
        else:
            # Parallel execution where possible
            results = []
            for task in agent_tasks:
                result = self.orchestrator.delegate_task(task)
                results.append(result)

        return {
            "sprint_id": sprint_id,
            "status": "Active",
            "tasks_started": len(agent_tasks),
            "execution_mode": "strict" if args.get("strict_mode", True) else "parallel"
        }

    def end_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        End current sprint
        Args:
            retrospective_notes: Sprint retrospective notes
        """
        if not self.scrum.current_sprint:
            raise ValueError("No active sprint")

        sprint = self.scrum.complete_sprint(
            self.scrum.current_sprint,
            args.get("retrospective_notes", "")
        )

        return {
            "sprint_id": sprint.id,
            "name": sprint.name,
            "completed_points": sprint.completed_points,
            "committed_points": sprint.committed_points,
            "completion_percentage": (sprint.completed_points / sprint.committed_points * 100)
                                   if sprint.committed_points > 0 else 0,
            "status": "Completed"
        }

    def set_story_points(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manually set story points for a story
        Args:
            story_id: Story ID
            points: Story points (must be Fibonacci: 1,2,3,5,8,13,21)
        """
        story = self.scrum.estimate_story(
            args["story_id"],
            args["points"]
        )

        return {
            "story_id": story.id,
            "title": story.title,
            "story_points": story.story_points,
            "priority": story.priority
        }

    def estimate_story(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use PM agent to automatically estimate story points for backlog stories
        Args:
            story_id: Optional specific story to estimate
            all: Optional flag to re-estimate all stories (default: False)
        """
        from agents.base_agent import AgentTask

        story_id = args.get("story_id", None)
        estimate_all = args.get("all", False)

        # Get stories to estimate
        stories_to_estimate = []

        if story_id:
            # Estimate specific story
            if story_id not in self.scrum.stories:
                return {
                    "success": False,
                    "error": f"Story {story_id} not found"
                }
            stories_to_estimate = [self.scrum.stories[story_id]]
        else:
            # Estimate all unestimated backlog stories
            stories_to_estimate = [
                s for s in self.scrum.stories.values()
                if safe_get_attr(s, 'status') == "Backlog" and
                (safe_get_attr(s, 'story_points', 0) == 0 or estimate_all)
            ]

        if not stories_to_estimate:
            return {
                "success": True,
                "message": "No stories need estimation",
                "stories_estimated": 0
            }

        # Show PM agent starting
        print(f"\n📊 Project Manager starting story estimation...")
        print(f"Stories to estimate: {len(stories_to_estimate)}\n")

        # Delegate to PM agent for each story
        results = []
        for story in stories_to_estimate:
            # Create estimation task for PM agent
            story_id = safe_get_attr(story, 'id')
            story_title = safe_get_attr(story, 'title', 'Untitled Story')
            story_description = safe_get_attr(story, 'description', '')
            story_criteria = safe_get_attr(story, 'acceptance_criteria', [])

            task = AgentTask(
                task_id=f"ESTIMATE-{story_id}",
                task_type="estimate_story",
                description=f"{story_title}. {story_description}",
                requirements=story_criteria,
                test_requirements={},
                acceptance_criteria=["Provide story point estimate"],
                tech_constraints=[]
            )

            # Delegate to orchestrator for colored agent display
            result = self.orchestrator.delegate_task(task)

            if result.success:
                points = result.validation_results.get("story_points", 5)
                self.scrum.estimate_story(story_id, points)
                safe_set_attr(story, 'story_points', points)

                results.append({
                    "story_id": story_id,
                    "title": story_title,
                    "points": points
                })

        # Calculate sprint planning metrics
        total_points = sum(r["points"] for r in results)
        velocity = self.scrum._calculate_velocity() if hasattr(self.scrum, '_calculate_velocity') else 20

        return {
            "success": True,
            "stories_estimated": len(results),
            "total_points": total_points,
            "estimated_sprints": total_points / velocity if velocity > 0 else 0,
            "estimates": results,
            "message": f"Estimated {len(results)} stories with total {total_points} points"
        }

    def assign_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign task to an agent
        Args:
            task_id: Task ID
            agent: Agent name (optional, auto-assigns if not provided)
        """
        if args["task_id"] not in self.scrum.tasks:
            raise ValueError(f"Task {args['task_id']} not found")

        task = self.scrum.tasks[args["task_id"]]

        # Auto-assign if no agent specified
        if "agent" not in args:
            # Detect appropriate agent
            agent_task = AgentTask(
                task_id=task.id,
                task_type="implement_feature",
                description=task.description,
                requirements=[task.technical_details],
                test_requirements={},
                acceptance_criteria=task.test_criteria,
                tech_constraints=self._detect_task_tech_constraints(task)
            )
            agent = self.orchestrator._select_agent_for_task(agent_task)
            if agent:
                task.assigned_to = agent.name
        else:
            task.assigned_to = args["agent"]

        self.scrum._save_data()

        return {
            "task_id": task.id,
            "assigned_to": task.assigned_to,
            "title": task.title
        }

    def review_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger code review for task
        Args:
            task_id: Task ID
            files: List of files to review
        """
        # This would integrate with code review agents
        return {
            "task_id": args["task_id"],
            "review_status": "In Progress",
            "files_reviewed": len(args.get("files", []))
        }

    def generate_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate various reports
        Args:
            report_type: Type of report (backlog/sprint/velocity/burndown)
            sprint_id: Sprint ID (for sprint-specific reports)
        """
        report_type = args.get("report_type", "backlog")

        if report_type == "backlog":
            return self.scrum.get_backlog_report()
        elif report_type == "sprint" and "sprint_id" in args:
            return self.scrum.get_sprint_report(args["sprint_id"])
        elif report_type == "agents":
            return self.orchestrator.generate_agent_report()
        else:
            return {"error": f"Unknown report type: {report_type}"}

    def tech_stack_analyze(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project tech stack"""
        tech_stack = self.orchestrator.tech_stack
        return {
            "languages": tech_stack.languages if tech_stack else [],
            "frameworks": tech_stack.frameworks if tech_stack else [],
            "build_tools": tech_stack.build_tools if tech_stack else [],
            "test_frameworks": tech_stack.test_frameworks if tech_stack else [],
            "databases": tech_stack.databases if tech_stack else [],
            "agents_available": list(self.orchestrator.agents.keys())
        }

    def create_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom agent
        Args:
            name: Agent name
            language: Primary language
            frameworks: List of frameworks
            responsibilities: Agent responsibilities
        """
        # This would dynamically create a new agent
        return {
            "agent_name": args["name"],
            "status": "Created",
            "capabilities": {
                "language": args["language"],
                "frameworks": args.get("frameworks", [])
            }
        }

    def list_stories(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List all stories with optional filtering"""
        stories = []
        for story in self.scrum.stories.values():
            if args.get("status") and story.status != args["status"]:
                continue
            if args.get("priority") and story.priority != args["priority"]:
                continue

            stories.append({
                "id": story.id,
                "title": story.title,
                "points": story.story_points,
                "priority": story.priority,
                "status": story.status,
                "tasks": len(story.tasks),
                "bugs": len(story.bugs)
            })

        return sorted(stories, key=lambda s: s["priority"])

    def list_tasks(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List all tasks with optional filtering"""
        tasks = []
        for task in self.scrum.tasks.values():
            if args.get("status") and task.status != args["status"]:
                continue
            if args.get("story_id") and task.story_id != args["story_id"]:
                continue

            tasks.append({
                "id": task.id,
                "title": task.title,
                "story_id": task.story_id,
                "points": task.story_points,
                "priority": task.priority,
                "status": task.status,
                "completion": task.completion_percentage,
                "test_coverage": task.test_coverage,
                "assigned_to": task.assigned_to
            })

        return sorted(tasks, key=lambda t: (t["priority"], -t["completion"]))

    def list_bugs(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List all bugs with optional filtering"""
        bugs = []
        for bug in self.scrum.bugs.values():
            if args.get("status") and bug.status != args["status"]:
                continue
            if args.get("severity") and bug.severity != args["severity"]:
                continue

            bugs.append({
                "id": bug.id,
                "title": bug.title,
                "severity": bug.severity,
                "priority": bug.priority,
                "points": bug.story_points,
                "status": bug.status,
                "affected_stories": len(bug.affected_stories)
            })

        return sorted(bugs, key=lambda b: (b["severity"], b["priority"]))

    def show_backlog(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Show backlog overview"""
        report = self.scrum.get_backlog_report()
        report["top_priority_items"] = []

        # Get top priority items
        priority_items = []
        for story in self.scrum.stories.values():
            if safe_get_attr(story, 'status') == "Backlog":
                priority_items.append({
                    "type": "Story",
                    "id": safe_get_attr(story, 'id'),
                    "title": safe_get_attr(story, 'title'),
                    "points": safe_get_attr(story, 'story_points', 0),
                    "priority": safe_get_attr(story, 'priority', 'Medium')
                })

        for bug in self.scrum.bugs.values():
            status = safe_get_attr(bug, 'status')
            severity = safe_get_attr(bug, 'severity', 'Medium')
            if status == "Open" and severity in ["Critical", "High"]:
                priority_items.append({
                    "type": "Bug",
                    "id": safe_get_attr(bug, 'id'),
                    "title": safe_get_attr(bug, 'title'),
                    "points": safe_get_attr(bug, 'story_points', 0),
                    "priority": safe_get_attr(bug, 'priority', 'Medium'),
                    "severity": severity
                })

        report["top_priority_items"] = sorted(
            priority_items,
            key=lambda x: x.get("priority", "Low")
        )[:10]

        return report

    def show_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Show sprint details"""
        sprint_id = args.get("sprint_id", self.scrum.current_sprint)
        if not sprint_id:
            return {"error": "No active sprint and no sprint_id provided"}

        return self.scrum.get_sprint_report(sprint_id)

    def show_help(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Show Xavier help and commands"""
        # Display ANSI art greeting
        import subprocess
        greeting_script = os.path.join(os.path.dirname(__file__), "..", "utils", "greeting.sh")
        if os.path.exists(greeting_script):
            subprocess.run([greeting_script, "welcome", "1.1.9"], check=False)

        help_text = """# Xavier Framework Commands

## Project Management

### /create-project - Intelligently initialize a new Xavier project
Creates a new project with AI-powered analysis of requirements and automatic tech stack selection.

**Example:**
```json
{
  "name": "TodoApp",
  "description": "A task management app with user auth, real-time updates, and team collaboration"
}
```

**With tech stack:**
```json
{
  "name": "TodoApp",
  "description": "Task management application",
  "tech_stack": {
    "backend": "python/fastapi",
    "frontend": "react",
    "database": "postgresql"
  }
}
```

## Story Management

### /create-story - Create a user story with acceptance criteria
**Example:**
```json
{
  "title": "User Authentication",
  "as_a": "user",
  "i_want": "to log in securely",
  "so_that": "I can access my account",
  "acceptance_criteria": ["Email validation", "Password check"],
  "priority": "High"
}
```

### /create-task - Create a task under a story
**Example:**
```json
{
  "story_id": "STORY-001",
  "title": "Implement login endpoint",
  "description": "Create POST /api/login endpoint",
  "estimated_hours": 4
}
```

### /create-bug - Report a bug with reproduction steps
**Example:**
```json
{
  "title": "Login fails with special characters",
  "description": "Users cannot log in if password contains @",
  "steps_to_reproduce": ["Go to login", "Enter password with @", "Click login"],
  "severity": "High"
}
```

## Sprint Management

### /create-sprint - Create a new sprint with auto-planning
**Example:**
```json
{
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "duration_days": 14
}
```

### /start-sprint - Start sprint execution with agents
### /end-sprint - Complete sprint with retrospective

## Reporting & Analysis

### /show-backlog - Show backlog overview

### /estimate-story - Automatically estimate story points using PM agent
Triggers the Project Manager agent to analyze and estimate story points for backlog stories.

**Usage:**
```
/estimate-story              # Estimate all unestimated backlog stories
/estimate-story STORY-001    # Estimate specific story
/estimate-story --all        # Re-estimate all stories
```

The PM agent analyzes:
- Technical complexity (API, database, authentication, etc.)
- Number and complexity of acceptance criteria
- UI/UX requirements
- Testing requirements
- Integration points

**Example:**
```
/estimate-story

📊 [PM] ProjectManager
Taking over task: Estimating backlog stories
Analyzing: Complexity score 12 → 5 points

Stories estimated: 3
Total points: 13
Estimated sprints: 0.7
```
### /show-sprint - Show sprint details
### /tech-stack-analyze - Analyze project tech stack
### /learn-project - Learn existing project structure
### /generate-report - Generate various reports

## Other Commands

### /create-roadmap - Create product roadmap
### /estimate-story - Use PM agent to automatically estimate backlog stories
### /set-story-points - Manually set story points for a specific story
### /assign-task - Assign task to agent
### /review-code - Trigger code review
### /create-agent - Create custom agent
### /list-stories - List all user stories
### /list-tasks - List all tasks
### /list-bugs - List all bugs
### /xavier-help - Show this help message

## Quick Tips

1. Use `/create-project` first to initialize your project with intelligent analysis
2. Xavier will suggest the best tech stack based on your requirements
3. All commands accept JSON arguments
4. Stories are automatically estimated and prioritized
5. Agents work sequentially following TDD and Clean Code principles
"""
        return {
            "help": help_text,
            "commands_count": 22,
            "framework_version": "1.1.9"
        }

    def xavier_update(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check for and install Xavier Framework updates"""
        import subprocess
        import requests

        # Get current version from multiple sources (priority order)
        current_version = "1.1.9"  # Embedded fallback version

        # 1. Try VERSION file first (most reliable)
        version_file = os.path.join(self.project_path, "VERSION")
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    current_version = f.read().strip()
            except:
                pass

        # 2. Try .xavier/config.json as secondary source
        elif os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    current_version = config.get("xavier_version", current_version)
            except:
                pass

        # Check for latest version
        try:
            response = requests.get("https://raw.githubusercontent.com/gumruyanzh/xavier/main/VERSION")
            latest_version = response.text.strip()
        except:
            return {
                "success": False,
                "error": "Unable to check for updates. Please check your internet connection.",
                "current_version": current_version
            }

        # Compare versions
        def version_tuple(v):
            return tuple(map(int, (v.split("."))))

        # Prevent downgrades
        try:
            current_tuple = version_tuple(current_version)
            latest_tuple = version_tuple(latest_version)
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid version format: {e}",
                "current_version": current_version
            }

        if latest_tuple < current_tuple:
            return {
                "success": False,
                "error": f"Cannot downgrade from {current_version} to {latest_version}",
                "current_version": current_version,
                "latest_version": latest_version,
                "message": f"❌ Your version ({current_version}) is newer than the remote version ({latest_version})\n\n" +
                          "This usually means:\n" +
                          "• You're using a development version\n" +
                          "• The remote repository has an older version\n" +
                          "• There's a caching issue\n\n" +
                          "No action needed - you're already on a newer version!"
            }

        if latest_tuple > current_tuple:
            # New version available
            changelog = self._get_update_changelog(current_version, latest_version)

            return {
                "success": True,
                "update_available": True,
                "current_version": current_version,
                "latest_version": latest_version,
                "changelog": changelog,
                "update_command": "curl -sSL https://raw.githubusercontent.com/gumruyanzh/xavier/main/update.sh | bash",
                "message": f"Xavier Framework update available: {current_version} → {latest_version}\n\n" +
                          f"What's new:\n{changelog}\n\n" +
                          f"To update, run:\n  curl -sSL https://raw.githubusercontent.com/gumruyanzh/xavier/main/update.sh | bash"
            }
        else:
            return {
                "success": True,
                "update_available": False,
                "current_version": current_version,
                "message": f"✅ Xavier Framework is up to date (version {current_version})"
            }

    def _get_update_changelog(self, current_version: str, latest_version: str) -> str:
        """Get changelog for version update"""
        # This could fetch from CHANGELOG.md in the future
        changelog = ""

        if current_version in ["1.0.0", "1.0.1"]:
            changelog += "• Intelligent /create-project command with AI-powered analysis\n"
            changelog += "• Strict command boundaries preventing auto-implementation\n"
            changelog += "• /xavier-update command for easy updates\n"
            changelog += "• Enhanced project templates and tech stack detection\n"
            changelog += "• Improved command documentation with examples\n"

        if not changelog:
            changelog = "• Bug fixes and improvements"

        return changelog

    def _detect_task_tech_constraints(self, task) -> List[str]:
        """Detect technology constraints from task description"""
        constraints = []
        description = (task.description + task.technical_details).lower()

        # Language detection
        if "python" in description or ".py" in description:
            constraints.append("python")
        if "golang" in description or "go " in description or ".go" in description:
            constraints.append("go")
        if "typescript" in description or "react" in description:
            constraints.append("typescript")
        if "javascript" in description or ".js" in description:
            constraints.append("javascript")

        # Framework detection
        if "django" in description:
            constraints.append("django")
        if "fastapi" in description:
            constraints.append("fastapi")
        if "react" in description:
            constraints.append("react")
        if "vue" in description:
            constraints.append("vue")

        return constraints

    def setup_claude_integration(self):
        """Setup Claude Code integration files"""
        # Create instructions
        instructions = self._generate_claude_instructions()
        with open(os.path.join(self.claude_path, "instructions.md"), 'w') as f:
            f.write(instructions)

        # Create command reference
        commands = self._generate_command_reference()
        with open(os.path.join(self.claude_path, "xavier_commands.md"), 'w') as f:
            f.write(commands)

        # Create agent definitions based on config
        self._create_claude_agents()

        return {
            "success": True,
            "message": "Claude integration created in .claude/",
            "files_created": [
                ".claude/instructions.md",
                ".claude/xavier_commands.md",
                ".claude/agents/*.md"
            ]
        }

    def _generate_claude_instructions(self) -> str:
        """Generate Claude instructions based on current configuration"""
        return """# Xavier Framework Integration

This project uses Xavier Framework for enterprise-grade SCRUM development with Claude Code.

## Framework Rules

Xavier enforces the following strict rules:
1. **Test-First Development (TDD)**: Tests must be written before implementation
2. **100% Test Coverage Required**: No task is complete without full coverage
3. **Sequential Task Execution**: One task at a time, no parallel work
4. **Clean Code Standards**: Functions ≤20 lines, classes ≤200 lines
5. **SOLID Principles**: All code must follow SOLID design patterns
6. **Agent Language Boundaries**: Each agent works only in their assigned language

## Available Commands

### Project Management
- `/create-project` - Intelligently initialize new project with AI analysis
- `/learn-project` - Analyze existing codebase
- `/tech-stack-analyze` - Detect technologies

### Story Management
- `/create-story` - Create user story with acceptance criteria
- `/create-task` - Create task under a story
- `/create-bug` - Report a bug

### Sprint Management
- `/create-sprint` - Plan a new sprint
- `/start-sprint` - Begin sprint execution
- `/end-sprint` - Complete current sprint

### Reporting
- `/show-backlog` - View prioritized backlog
- `/show-sprint` - Current sprint status
- `/generate-report` - Generate various reports
- `/xavier-help` - Show all commands

## Workflow

1. Create stories with `/create-story`
2. Break into tasks with `/create-task`
3. Plan sprint with `/create-sprint`
4. Execute with `/start-sprint` (agents work sequentially)
5. Complete with `/end-sprint`

## Important Notes

- Xavier commands are executed through the framework in `.xavier/`
- All data is stored in `.xavier/data/`
- Sprint information in `.xavier/sprints/`
- Reports generated in `.xavier/reports/`
"""

    def _generate_command_reference(self) -> str:
        """Generate command reference documentation"""
        return """# Xavier Commands Reference

All commands use JSON arguments. Examples provided for each command.

## /create-project
Intelligently initialize a new Xavier project with automatic tech stack analysis.

```json
{
  "name": "TodoApp",
  "description": "A task management application with user authentication, real-time updates, and team collaboration features. Should support mobile devices and have offline capabilities."
}
```

With custom tech stack:
```json
{
  "name": "TodoApp",
  "description": "Task management app",
  "tech_stack": {
    "backend": "python/fastapi",
    "frontend": "react",
    "database": "postgresql"
  }
}
```

## /create-story
Create a user story following SCRUM methodology.

```json
{
  "title": "User Authentication",
  "as_a": "user",
  "i_want": "to log in securely",
  "so_that": "I can access my account",
  "acceptance_criteria": [
    "Email validation",
    "Password strength check",
    "Remember me option"
  ],
  "priority": "High"
}
```

## /create-task
Create a task under an existing story.

```json
{
  "story_id": "US-ABC123",
  "title": "Implement email validation",
  "description": "Add email format validation",
  "technical_details": "Use regex pattern matching",
  "estimated_hours": 4,
  "test_criteria": [
    "Valid emails pass",
    "Invalid emails rejected"
  ],
  "dependencies": []
}
```

## /create-bug
Report a bug with reproduction steps.

```json
{
  "title": "Login fails with special characters",
  "description": "Users cannot log in if password contains @",
  "steps_to_reproduce": [
    "Go to login page",
    "Enter email",
    "Enter password with @",
    "Click login"
  ],
  "expected_behavior": "User logs in successfully",
  "actual_behavior": "Error: Invalid credentials",
  "severity": "High",
  "priority": "High"
}
```

## /create-sprint
Create and plan a sprint.

```json
{
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "duration_days": 14,
  "auto_plan": true
}
```

## /start-sprint
Begin sprint execution with agents.

```json
{
  "sprint_id": "SP-123",
  "strict_mode": true
}
```
"""

    def _create_claude_agents(self):
        """Create agent definition files for Claude based on enabled agents"""
        agents_path = os.path.join(self.claude_path, "agents")

        # Define agent templates
        agent_templates = {
            "project_manager": {
                "filename": "project_manager.md",
                "content": """# Project Manager Agent

## Role
Responsible for sprint planning, story point estimation, and task assignment.

## Capabilities
- Estimate story points using Fibonacci scale (1,2,3,5,8,13,21)
- Plan sprints based on velocity and priority
- Assign tasks to appropriate agents
- Track sprint progress

## Restrictions
- Cannot write code
- Cannot modify implementations
- Cannot deploy
"""
            },
            "python_engineer": {
                "filename": "python_engineer.md",
                "content": """# Python Engineer Agent

## Role
Python backend development with strict language boundaries.

## Capabilities
- Python development ONLY
- Frameworks: Django, FastAPI, Flask
- Testing: pytest with 100% coverage
- Clean Code enforcement

## Restrictions
- CANNOT write JavaScript, TypeScript, Go, or any other language
- CANNOT modify frontend code
- Must write tests before implementation (TDD)
- Must achieve 100% test coverage
"""
            },
            "golang_engineer": {
                "filename": "golang_engineer.md",
                "content": """# Golang Engineer Agent

## Role
Go backend development with strict language boundaries.

## Capabilities
- Go development ONLY
- Frameworks: Gin, Fiber, Echo
- Testing: go test with full coverage
- Clean Code enforcement

## Restrictions
- CANNOT write Python, JavaScript, TypeScript, or any other language
- CANNOT modify non-Go code
- Must write tests before implementation (TDD)
- Must achieve 100% test coverage
"""
            },
            "frontend_engineer": {
                "filename": "frontend_engineer.md",
                "content": """# Frontend Engineer Agent

## Role
Frontend development with TypeScript and modern frameworks.

## Capabilities
- TypeScript/JavaScript ONLY
- Frameworks: React, Vue, Angular
- Testing: Jest, Cypress with full coverage
- Component-based architecture

## Restrictions
- CANNOT write backend code (Python, Go, etc.)
- CANNOT modify API implementations
- Must use TypeScript for type safety
- Must write tests before implementation
- Must achieve 100% test coverage
"""
            },
            "context_manager": {
                "filename": "context_manager.md",
                "content": """# Context Manager Agent

## Role
Maintains codebase understanding and finds existing implementations.

## Capabilities
- Analyze any language/framework
- Find similar implementations
- Detect patterns and conventions
- Check for code duplication

## Restrictions
- Cannot write new code
- Cannot modify existing code
- Read-only operations only
"""
            }
        }

        # Load config to check enabled agents
        config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)

        # Create agent files for enabled agents
        for agent_name, agent_config in config.get("agents", {}).items():
            if agent_config.get("enabled", False):
                agent_key = agent_name.lower().replace(" ", "_")
                if agent_key in agent_templates:
                    template = agent_templates[agent_key]
                    file_path = os.path.join(agents_path, template["filename"])
                    with open(file_path, 'w') as f:
                        f.write(template["content"])