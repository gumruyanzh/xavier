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
            "/create-epic": self.create_epic,
            "/create-roadmap": self.create_roadmap,
            "/add-to-roadmap": self.add_to_roadmap,
            "/add-to-epic": self.add_to_epic,
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
            "/list-epics": self.list_epics,
            "/show-backlog": self.show_backlog,
            "/show-sprint": self.show_sprint,
            "/xavier-help": self.show_help,
            "/xavier-update": self.xavier_update,
            # Xavier self-hosting meta-commands
            "/xavier-init-self": self.xavier_init_self,
            "/xavier-story": self.xavier_story,
            "/xavier-sprint": self.xavier_sprint,
            "/xavier-test-self": self.xavier_test_self,
            "/xavier-status": self.xavier_status
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
        Create a task under a story with automatic agent assignment
        Args:
            story_id: Parent story ID
            title: Task title
            description: Task description
            technical_details: Technical implementation details
            estimated_hours: Estimated hours
            test_criteria: List of test criteria
            priority: Priority level
            dependencies: List of dependency task IDs
            assigned_to: (Optional) Manually specify agent, otherwise auto-assigned
            auto_assign: (Optional) Set to False to skip auto-assignment
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

        # Auto-assign agent if not manually specified
        agent_assigned = args.get("assigned_to")
        agent_creation_info = None

        if not agent_assigned and args.get("auto_assign", True):
            try:
                from xavier.src.agents.task_agent_matcher import TaskAgentMatcher

                matcher = TaskAgentMatcher(self.project_path)
                assignment_result = matcher.assign_agent_to_task({
                    "title": task.title,
                    "description": task.description,
                    "technical_details": task.technical_details
                })

                if assignment_result['success']:
                    agent_assigned = assignment_result['agent']
                    task.assigned_to = agent_assigned

                    # Save the assignment
                    self.scrum._save_data()

                    agent_creation_info = {
                        "agent": agent_assigned,
                        "reason": assignment_result['reason'],
                        "confidence": assignment_result['confidence'],
                        "created_new": assignment_result.get('created_new_agent', False)
                    }

                    # Log the assignment
                    self.logger.info(f"Auto-assigned task {task.id} to {agent_assigned}: {assignment_result['reason']}")

            except Exception as e:
                self.logger.warning(f"Auto-assignment failed: {e}")
                # Continue without assignment
        elif agent_assigned:
            # Manual assignment
            task.assigned_to = agent_assigned
            self.scrum._save_data()

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

        result = {
            "task_id": task.id,
            "story_id": task.story_id,
            "title": task.title,
            "estimated_hours": task.estimated_hours,
            "story_points": task.story_points,
            "status": task.status,
            "assigned_to": task.assigned_to
        }

        # Add agent assignment info if auto-assigned
        if agent_creation_info:
            result["agent_assignment"] = agent_creation_info

        return result

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

    def create_epic(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an epic to group related user stories
        Args:
            title: Epic title (required)
            description: Epic description (required)
            business_value: Business value statement (optional - will be auto-generated)
            target_release: Target release version (optional)
            initial_stories: List of story IDs to link to this epic (optional)
        """
        # Validate required fields
        if "title" not in args:
            raise ValueError("Epic title is required")
        if "description" not in args:
            raise ValueError("Epic description is required")

        # Auto-generate business value if not provided
        business_value = args.get("business_value")
        if not business_value:
            # Generate business value based on title and description
            business_value = f"Delivers {args['title'].lower()} capabilities to enhance user experience and system functionality"

        # Create the epic
        epic = self.scrum.create_epic(
            title=args["title"],
            description=args["description"],
            business_value=business_value,
            target_release=args.get("target_release")
        )

        # Link initial stories if provided
        initial_stories = args.get("initial_stories", [])
        linked_count = 0
        total_points = 0

        for story_id in initial_stories:
            if story_id in self.scrum.stories:
                story = self.scrum.stories[story_id]
                if story_id not in epic.stories:
                    epic.stories.append(story_id)
                    linked_count += 1
                    # Add story points to epic
                    if hasattr(story, 'story_points') and story.story_points:
                        total_points += story.story_points

        # Update epic points if stories were linked
        if linked_count > 0:
            epic.total_points = total_points
            self.scrum._save_data()

        return {
            "epic_id": epic.id,
            "title": epic.title,
            "description": epic.description,
            "business_value": epic.business_value,
            "target_release": epic.target_release,
            "status": epic.status,
            "stories_linked": linked_count,
            "total_points": epic.total_points,
            "message": f"Epic created successfully. Data stored in .xavier/data/epics.json"
        }

    def create_roadmap(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a product roadmap with auto-generation capability
        Args:
            name: Roadmap name (optional - will be generated from project name)
            vision: Product vision (optional - will be generated from project description)
            milestones: List of milestone definitions (optional - will be auto-generated)
            auto_generate: Auto-generate roadmap from project info (default: True)
        """
        # Auto-generate if name or vision not provided
        auto_generate = args.get("auto_generate", True)

        if auto_generate and ("name" not in args or "vision" not in args):
            # Try to load project config for auto-generation
            project_config = None
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    project_config = json.load(f)

            # Auto-generate name if not provided
            if "name" not in args:
                if project_config:
                    args["name"] = f"{project_config.get('name', 'Project')} Product Roadmap"
                else:
                    args["name"] = "Product Roadmap"

            # Auto-generate vision if not provided
            if "vision" not in args:
                if project_config and project_config.get('description'):
                    args["vision"] = project_config['description']
                elif "description" in args:
                    args["vision"] = args["description"]
                else:
                    args["vision"] = f"Building {args['name'].replace(' Product Roadmap', '')} with modern technologies"

        # Ensure required fields are present
        if "name" not in args:
            raise ValueError("Roadmap name is required or project must be initialized")
        if "vision" not in args:
            raise ValueError("Vision is required or must be provided via description")

        roadmap = self.scrum.create_roadmap(
            name=args["name"],
            vision=args["vision"]
        )

        # Add milestones if provided, otherwise auto-generate
        milestones = args.get("milestones", [])

        if not milestones and auto_generate:
            # Auto-generate milestones based on project
            project_config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    project_config = json.load(f)

            # Use helper method to generate milestones
            from ..analyzers.project_analyzer import ProjectAnalyzer
            analyzer = ProjectAnalyzer()
            # Create a simple analysis object for milestone generation
            class SimpleAnalysis:
                def __init__(self):
                    self.estimated_complexity = project_config.get('estimated_complexity', 'Medium')
                    self.project_type = project_config.get('project_type', 'web')

            milestones = self._generate_default_milestones(project_config, SimpleAnalysis())

        # Add milestones to roadmap
        for milestone in milestones:
            if isinstance(milestone, dict):
                # Handle both auto-generated and user-provided milestones
                target_date = milestone.get("target_date")
                if isinstance(target_date, str):
                    target_date = datetime.fromisoformat(target_date)

                self.scrum.add_milestone_to_roadmap(
                    roadmap_id=roadmap.id,
                    milestone_name=milestone["name"],
                    target_date=target_date,
                    epics=milestone.get("epics", []),
                    success_criteria=milestone.get("success_criteria", [])
                )

        return {
            "roadmap_id": roadmap.id,
            "name": roadmap.name,
            "vision": roadmap.vision,
            "milestones": len(roadmap.milestones),
            "message": "Roadmap created successfully. All data stored in .xavier/data/roadmaps.json"
        }

    def add_to_roadmap(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add milestones to an existing roadmap
        Args:
            roadmap_id: ID of the roadmap (optional - uses first roadmap if not specified)
            milestone: Milestone definition with name, target_date, epics, success_criteria
            milestones: List of milestones to add (alternative to single milestone)
        """
        from datetime import timedelta

        # Get roadmap ID
        roadmap_id = args.get("roadmap_id")

        if not roadmap_id:
            # Try to find existing roadmap
            if not self.scrum.roadmaps:
                return {
                    "success": False,
                    "error": "No roadmaps found. Create one with /create-roadmap first"
                }
            # Use the first (or only) roadmap
            roadmap_id = list(self.scrum.roadmaps.keys())[0]

        # Validate roadmap exists
        if roadmap_id not in self.scrum.roadmaps:
            return {
                "success": False,
                "error": f"Roadmap {roadmap_id} not found"
            }

        roadmap = self.scrum.roadmaps[roadmap_id]

        # Handle single milestone or list of milestones
        milestones = []
        if "milestone" in args:
            milestones = [args["milestone"]]
        elif "milestones" in args:
            milestones = args["milestones"]
        else:
            return {
                "success": False,
                "error": "Either 'milestone' or 'milestones' must be provided"
            }

        # Add milestones
        added_count = 0
        for milestone in milestones:
            try:
                # Parse target date
                target_date = milestone.get("target_date")
                if isinstance(target_date, str):
                    target_date = datetime.fromisoformat(target_date)
                elif not target_date:
                    # Default to 4 weeks from now if not specified
                    target_date = datetime.now() + timedelta(weeks=4)

                self.scrum.add_milestone_to_roadmap(
                    roadmap_id=roadmap_id,
                    milestone_name=milestone.get("name", f"Milestone {len(roadmap.milestones) + 1}"),
                    target_date=target_date,
                    epics=milestone.get("epics", []),
                    success_criteria=milestone.get("success_criteria", [])
                )
                added_count += 1
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to add milestone: {str(e)}"
                }

        return {
            "success": True,
            "roadmap_id": roadmap_id,
            "roadmap_name": roadmap.name,
            "milestones_added": added_count,
            "total_milestones": len(roadmap.milestones),
            "message": f"Added {added_count} milestone(s) to roadmap. Data saved in .xavier/data/roadmaps.json"
        }

    def add_to_epic(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add stories to an existing epic
        Args:
            epic_id: ID of the epic (required)
            story_ids: List of story IDs to add to the epic (required)
        """
        # Validate required fields
        if "epic_id" not in args:
            raise ValueError("Epic ID is required")
        if "story_ids" not in args:
            raise ValueError("Story IDs list is required")

        epic_id = args["epic_id"]
        story_ids = args["story_ids"]

        # Validate epic exists
        if epic_id not in self.scrum.epics:
            return {
                "success": False,
                "error": f"Epic {epic_id} not found"
            }

        epic = self.scrum.epics[epic_id]

        # Ensure story_ids is a list
        if not isinstance(story_ids, list):
            story_ids = [story_ids]

        # Link stories to epic
        linked_count = 0
        already_linked = 0
        not_found = []
        added_points = 0

        for story_id in story_ids:
            if story_id not in self.scrum.stories:
                not_found.append(story_id)
                continue

            if story_id in epic.stories:
                already_linked += 1
                continue

            # Link the story
            epic.stories.append(story_id)
            linked_count += 1

            # Update epic points
            story = self.scrum.stories[story_id]
            if hasattr(story, 'story_points') and story.story_points:
                added_points += story.story_points

        # Update epic total points
        epic.total_points += added_points
        self.scrum._save_data()

        result = {
            "success": True,
            "epic_id": epic_id,
            "epic_title": epic.title,
            "stories_linked": linked_count,
            "already_linked": already_linked,
            "total_stories": len(epic.stories),
            "total_points": epic.total_points,
            "message": f"Added {linked_count} story(ies) to epic. Data saved in .xavier/data/epics.json"
        }

        if not_found:
            result["stories_not_found"] = not_found

        return result

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
            "xavier_version": "1.2.3"
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
        agents = ["project-manager", "context-manager"]  # Always include these

        # Add language-specific agents
        if "backend" in tech_stack:
            backend_lang = tech_stack["backend"].get("language", "").lower()
            if "python" in backend_lang:
                agents.append("python-engineer")
            if "go" in backend_lang:
                agents.append("golang-engineer")
            if "node" in backend_lang or "javascript" in backend_lang:
                agents.append("nodejs-engineer")

        if "frontend" in tech_stack:
            agents.append("frontend-engineer")

        if "database" in tech_stack:
            agents.append("database-engineer")

        if "devops" in tech_stack:
            agents.append("devops-engineer")

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
        import subprocess

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

        # Create .trees folder for git worktrees
        trees_path = os.path.join(self.project_path, ".trees")
        os.makedirs(trees_path, exist_ok=True)
        self.logger.info(f"Created .trees folder at {trees_path}")

        # Get project abbreviation from config
        project_abbrev = "PROJ"
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    project_name = config.get('name', 'PROJECT')
                    # Create abbreviation from project name (first 3-4 chars uppercase)
                    project_abbrev = ''.join([c for c in project_name if c.isupper()])[:4] or project_name[:3].upper()
            except Exception:
                pass

        # Create git worktree for each story and bug in the sprint
        worktrees_created = []
        sprint_stories = safe_get_attr(sprint, 'stories', [])
        sprint_bugs = safe_get_attr(sprint, 'bugs', [])

        # Combine stories and bugs for worktree creation
        work_items = []
        for story_id in sprint_stories:
            if story_id in self.scrum.stories:
                work_items.append(('story', story_id, self.scrum.stories[story_id]))

        for bug_id in sprint_bugs:
            if bug_id in self.scrum.bugs:
                work_items.append(('bug', bug_id, self.scrum.bugs[bug_id]))

        for idx, (item_type, item_id, item) in enumerate(work_items, 1):
            item_title = safe_get_attr(item, 'title', 'untitled')

            # Determine branch type based on item type or title keywords
            branch_type = "feature"
            if item_type == 'bug':
                branch_type = "fix"
            else:
                title_lower = item_title.lower()
                if any(word in title_lower for word in ['fix', 'bug', 'issue']):
                    branch_type = "fix"
                elif any(word in title_lower for word in ['refactor', 'improve']):
                    branch_type = "refactor"

            # Create branch name like feature/CAN-1 or fix/CAN-2
            branch_name = f"{branch_type}/{project_abbrev}-{idx}"
            worktree_path = os.path.join(trees_path, f"{project_abbrev.lower()}-{idx}")

            try:
                # Create git worktree
                result = subprocess.run(
                    ["git", "worktree", "add", worktree_path, "-b", branch_name],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    check=False
                )

                if result.returncode == 0:
                    worktrees_created.append({
                        "item_type": item_type,
                        "item_id": item_id,
                        "branch": branch_name,
                        "path": worktree_path
                    })
                    self.logger.info(f"Created worktree for {item_id}: {branch_name}")
                else:
                    self.logger.warning(f"Failed to create worktree for {item_id}: {result.stderr}")
            except Exception as e:
                self.logger.error(f"Error creating worktree for {item_id}: {e}")

        # Display sprint start banner
        greeting_script = os.path.join(os.path.dirname(__file__), "..", "utils", "greeting.sh")
        if os.path.exists(greeting_script):
            subprocess.run([greeting_script, "sprint-start"], check=False)

        # Create mapping of item IDs to worktree paths
        worktree_map = {}
        for wt in worktrees_created:
            worktree_map[wt['item_id']] = wt['path']

        # Prepare tasks for agents
        agent_tasks = []

        # Process stories
        for story_id in sprint.stories:
            story = self.scrum.stories[story_id]
            story_worktree = worktree_map.get(story_id)

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
                    tech_constraints=self._detect_task_tech_constraints(task),
                    working_dir=story_worktree  # Use story's worktree
                )
                agent_tasks.append(agent_task)

        # Process bugs
        for bug_id in sprint.bugs:
            bug = self.scrum.bugs[bug_id]
            bug_worktree = worktree_map.get(bug_id)
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
                tech_constraints=[],
                working_dir=bug_worktree  # Use bug's worktree
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
            "execution_mode": "strict" if args.get("strict_mode", True) else "parallel",
            "worktrees_created": len(worktrees_created),
            "worktree_details": worktrees_created
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
        Create a custom agent with skills, experience, and visual styling
        Args:
            name: Agent name (required)
            display_name: Display name (optional, defaults to name)
            skills: List of skills/capabilities (required)
            experience: Experience description (optional)
            color: Color for agent display (optional, defaults to white)
            emoji: Emoji for agent (optional, defaults to 🤖)
            tools: List of allowed tools (optional)
            languages: List of programming languages (optional)
            frameworks: List of frameworks (optional)
        """
        import os
        import yaml

        # Validate required fields
        if not args.get("name"):
            return {
                "success": False,
                "error": "Agent name is required"
            }

        if not args.get("skills"):
            return {
                "success": False,
                "error": "Agent skills are required"
            }

        agent_name = args["name"]
        display_name = args.get("display_name", agent_name.replace("-", " ").replace("_", " ").title())

        # Convert name to agent format
        agent_key = agent_name.lower().replace(" ", "-").replace("_", "-")

        # Agent configuration
        agent_config = {
            "name": agent_key,
            "display_name": display_name,
            "color": args.get("color", "white"),
            "emoji": args.get("emoji", "🤖"),
            "label": agent_key[:3].upper(),
            "description": f"Custom agent with skills: {', '.join(args['skills'])}",
            "tools": args.get("tools", ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]),
            "capabilities": args["skills"],
            "restricted_actions": [],
            "allowed_file_patterns": [".*"],
            "languages": args.get("languages", []),
            "frameworks": args.get("frameworks", [])
        }

        # Add experience to description if provided
        if args.get("experience"):
            agent_config["description"] += f". Experience: {args['experience']}"

        # Ensure .xavier/agents directory exists
        agents_dir = ".xavier/agents"
        os.makedirs(agents_dir, exist_ok=True)

        # Write agent YAML file for Xavier
        agent_file = os.path.join(agents_dir, f"{agent_key}.yaml")

        try:
            with open(agent_file, 'w') as f:
                yaml.dump(agent_config, f, default_flow_style=False, sort_keys=False)

            # Create Claude Code agent MD file with proper YAML frontmatter
            claude_agents_dir = ".claude/agents"
            os.makedirs(claude_agents_dir, exist_ok=True)

            claude_agent_file = os.path.join(claude_agents_dir, f"{agent_key}.md")

            # Create skills description for frontmatter
            skills_str = ", ".join(args["skills"][:5])  # Limit to 5 for description
            if len(args["skills"]) > 5:
                skills_str += f", and {len(args['skills']) - 5} more"

            # Generate comprehensive description
            description = f"{display_name} specialist for {skills_str}. "
            if args.get("experience"):
                description += f"{args['experience'][:100]}. "  # Limit experience length
            description += f"Handles development, testing, debugging, optimization."

            # Create Claude Code compatible content
            claude_content = f"""---
name: {agent_key}
description: {description[:250]}
tools: {', '.join(agent_config['tools'])}
model: sonnet
---

# {display_name}

You are an expert {display_name} with specialized skills and experience.

## Core Expertise
{chr(10).join(f"- **{skill}**: Expert-level proficiency" for skill in args["skills"][:10])}

## Technical Stack
- **Languages**: {', '.join(args.get('languages', ['Multiple']))[:100]}
- **Frameworks**: {', '.join(args.get('frameworks', ['Various']))[:100]}
- **Tools**: {', '.join(agent_config['tools'])}

## Development Approach
1. **Requirements Analysis**: Thoroughly understand the problem
2. **Test-Driven Development**: Write tests before implementation
3. **Clean Code**: Follow SOLID principles and best practices
4. **Performance**: Optimize for efficiency and scalability
5. **Documentation**: Maintain clear and comprehensive docs

## Experience
{args.get('experience', f'Extensive experience in {", ".join(args["skills"][:3])}')}

I deliver high-quality solutions using industry best practices and modern development methodologies.
"""

            with open(claude_agent_file, 'w') as f:
                f.write(claude_content)

            self.logger.info(f"Created Claude Code agent: {claude_agent_file}")

            # Reload agent metadata to include new agent
            from agents.agent_metadata import get_metadata_manager
            get_metadata_manager().reload_metadata()

            return {
                "success": True,
                "agent_id": agent_key,
                "agent_name": display_name,
                "agent_file": agent_file,
                "claude_agent_file": claude_agent_file,
                "color": agent_config["color"],
                "emoji": agent_config["emoji"],
                "skills": agent_config["capabilities"],
                "message": f"Agent '{display_name}' created successfully with {len(agent_config['capabilities'])} skills"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create agent: {str(e)}"
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

    def list_epics(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        List all epics with optional filtering
        Args:
            status: Filter by status (optional)
            target_release: Filter by target release (optional)
        """
        epics = []
        for epic in self.scrum.epics.values():
            # Apply filters
            if args.get("status") and epic.status != args["status"]:
                continue
            if args.get("target_release") and epic.target_release != args["target_release"]:
                continue

            # Calculate completion percentage
            completion_percentage = 0
            if epic.total_points > 0:
                completion_percentage = int((epic.completed_points / epic.total_points) * 100)

            epics.append({
                "id": epic.id,
                "title": epic.title,
                "description": epic.description,
                "business_value": epic.business_value,
                "target_release": epic.target_release,
                "status": epic.status,
                "stories_count": len(epic.stories),
                "total_points": epic.total_points,
                "completed_points": epic.completed_points,
                "completion_percentage": completion_percentage
            })

        # Sort by target release and status
        return sorted(epics, key=lambda e: (e["target_release"] or "zzz", e["status"], e["title"]))

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
            subprocess.run([greeting_script, "welcome", "1.2.3"], check=False)

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

### /create-roadmap - Create product roadmap with auto-generation
**Example (Auto-generate from project):**
```json
{}
```

**Example (With custom vision):**
```json
{
  "description": "Build a scalable e-commerce platform with modern architecture"
}
```

**Example (Manual with milestones):**
```json
{
  "name": "Q1-Q2 Roadmap",
  "vision": "Deliver MVP with core features",
  "milestones": [
    {
      "name": "MVP Launch",
      "target_date": "2024-03-01",
      "success_criteria": ["Core features", "Testing complete"]
    }
  ]
}
```

### /add-to-roadmap - Add milestones to existing roadmap
**Example:**
```json
{
  "milestone": {
    "name": "Beta Release",
    "target_date": "2024-04-15",
    "success_criteria": ["Performance optimized", "Security audit passed"],
    "epics": ["EPIC-001"]
  }
}
```

### /create-epic - Create an epic to group related stories
**Example:**
```json
{
  "title": "User Authentication System",
  "description": "Complete authentication and authorization functionality",
  "business_value": "Critical for application security and user management",
  "target_release": "v2.0",
  "initial_stories": ["STORY-001", "STORY-002"]
}
```

### /add-to-epic - Add stories to an existing epic
**Example:**
```json
{
  "epic_id": "E-ABC123",
  "story_ids": ["STORY-003", "STORY-004"]
}
```

### /list-epics - List all epics with filtering options
**Example:**
```json
{
  "status": "Planning",
  "target_release": "v2.0"
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
### /list-epics - List all epics
### /xavier-help - Show this help message

## Xavier Self-Hosting Commands

### /xavier-init-self - Initialize Xavier for self-development
### /xavier-story - Create stories for Xavier features
### /xavier-sprint - Manage Xavier development sprints
### /xavier-test-self - Run recursive self-tests
### /xavier-status - Check Xavier self-hosting status

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
            "framework_version": "1.2.3"
        }

    def xavier_update(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check for and install Xavier Framework updates"""
        import subprocess
        import requests

        # Get current version from multiple sources (priority order)
        current_version = "1.2.3"  # Embedded fallback version

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
- `/create-epic` - Create epic to group stories
- `/add-to-epic` - Add stories to an epic
- `/list-epics` - List all epics

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

**IMPORTANT**: All data is stored exclusively in JSON format in `.xavier/data/` directory.
Xavier does NOT create Markdown files for data storage.

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
            "project-manager": {
                "filename": "project-manager.md",
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
            "python-engineer": {
                "filename": "python-engineer.md",
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
            "golang-engineer": {
                "filename": "golang-engineer.md",
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
            "frontend-engineer": {
                "filename": "frontend-engineer.md",
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
            "context-manager": {
                "filename": "context-manager.md",
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

    # ==================== XAVIER SELF-HOSTING META-COMMANDS ====================

    def xavier_init_self(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize Xavier for self-development
        Sets up Xavier to use its own features for development
        """
        import subprocess

        # Display welcome message
        print("\n" + "="*60)
        print("🔄 INITIALIZING XAVIER SELF-HOSTING")
        print("Xavier will now manage its own development")
        print("="*60 + "\n")

        try:
            # Run the self-initialization script
            script_path = os.path.join(self.project_path, "xavier_self_init.py")

            if not os.path.exists(script_path):
                # Create the initialization script if it doesn't exist
                return {
                    "success": False,
                    "error": "xavier_self_init.py not found. Please ensure the file exists.",
                    "suggestion": "Run: curl -sSL https://raw.githubusercontent.com/gumruyanzh/xavier/main/xavier_self_init.py -o xavier_self_init.py"
                }

            # Execute initialization
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                input="y\n"  # Auto-confirm
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Xavier successfully initialized for self-development!",
                    "output": result.stdout,
                    "next_steps": [
                        "Use /xavier-story to create Xavier development stories",
                        "Use /xavier-sprint to manage Xavier sprints",
                        "Use /xavier-test-self to run recursive tests",
                        "Use /xavier-status to check self-hosting status"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": "Initialization failed",
                    "details": result.stderr
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to initialize Xavier self-hosting: {str(e)}"
            }

    def xavier_story(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a story specifically for Xavier feature development
        Automatically tags and categorizes as Xavier development
        """
        # Find or create Xavier epic
        xavier_epic_id = self._get_or_create_xavier_epic()

        # Add Xavier-specific metadata
        args["epic_id"] = xavier_epic_id
        args["priority"] = args.get("priority", "High")  # Xavier development is high priority

        # Ensure Xavier-specific acceptance criteria
        criteria = args.get("acceptance_criteria", [])
        criteria.extend([
            "Maintains 100% test coverage",
            "Follows Xavier's own standards",
            "Updates documentation"
        ])
        args["acceptance_criteria"] = list(set(criteria))  # Remove duplicates

        # Prefix title to indicate Xavier story
        if not args.get("title", "").startswith("[Xavier]"):
            args["title"] = f"[Xavier] {args.get('title', 'Xavier Feature')}"

        # Create the story using standard method
        result = self.create_story(args)

        if result.get("success"):
            story_data = result.get("result", {})
            return {
                "success": True,
                "xavier_story_id": story_data.get("story_id"),
                "title": story_data.get("title"),
                "epic": "Xavier Self-Development",
                "story_points": story_data.get("story_points"),
                "message": f"Xavier story created: {story_data.get('title')}"
            }

        return result

    def xavier_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or manage Xavier development sprints
        Focuses on Xavier framework improvements
        """
        # Prefix sprint name
        sprint_name = args.get("name", "Xavier Development Sprint")
        if not sprint_name.startswith("Xavier"):
            sprint_name = f"Xavier: {sprint_name}"

        args["name"] = sprint_name
        args["goal"] = args.get("goal", "Improve Xavier Framework capabilities")

        # Create sprint with Xavier stories
        sprint_result = self.create_sprint(args)

        if sprint_result.get("success") and args.get("auto_populate", False):
            # Auto-populate with Xavier stories
            sprint_id = sprint_result.get("result", {}).get("sprint_id")
            xavier_stories = self._get_xavier_stories()

            # Add Xavier stories to sprint
            for story_id in xavier_stories[:5]:  # Add up to 5 stories
                self.scrum.add_to_sprint(sprint_id, story_id)

        return sprint_result

    def xavier_test_self(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run Xavier's recursive self-testing framework
        Tests Xavier using Xavier's own testing capabilities
        """
        import subprocess

        print("\n" + "="*60)
        print("🔄 RUNNING XAVIER RECURSIVE TESTS")
        print("Xavier testing Xavier testing Xavier...")
        print("="*60 + "\n")

        try:
            # Run meta-testing framework
            test_path = os.path.join(self.project_path, "xavier", "tests", "test_meta.py")

            if not os.path.exists(test_path):
                return {
                    "success": False,
                    "error": "test_meta.py not found",
                    "message": "Please ensure xavier/tests/test_meta.py exists"
                }

            result = subprocess.run(
                ["python3", test_path],
                capture_output=True,
                text=True
            )

            # Parse results
            output_lines = result.stdout.split("\n")
            test_count = 0
            coverage = 100.0
            paradoxes = 0
            self_refs = 0

            for line in output_lines:
                if "Total Tests Run:" in line:
                    test_count = int(line.split(":")[-1].strip())
                elif "Coverage:" in line:
                    coverage = float(line.split(":")[-1].replace("%", "").strip())
                elif "Paradoxes Found:" in line:
                    paradoxes = int(line.split(":")[-1].strip())
                elif "Self-References:" in line:
                    self_refs = int(line.split(":")[-1].strip())

            success = result.returncode == 0

            return {
                "success": success,
                "tests_run": test_count,
                "coverage": coverage,
                "paradoxes_found": paradoxes,
                "self_references": self_refs,
                "recursive_depth": 3,
                "message": "✅ Xavier successfully tested itself!" if success else "❌ Self-tests found issues",
                "output": result.stdout if args.get("verbose", False) else None
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to run self-tests: {str(e)}"
            }

    def xavier_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check Xavier self-hosting status and metrics
        Shows how Xavier is managing its own development
        """
        status = {
            "self_hosting_active": False,
            "xavier_stories": 0,
            "xavier_tasks": 0,
            "xavier_bugs": 0,
            "xavier_agents": 0,
            "current_sprint": None,
            "test_coverage": 0.0,
            "recursive_depth": 0
        }

        # Check if Xavier project exists
        xavier_config = os.path.join(self.project_path, ".xavier", "config.json")
        if os.path.exists(xavier_config):
            with open(xavier_config, 'r') as f:
                config = json.load(f)
                if config.get("name") == "Xavier Framework":
                    status["self_hosting_active"] = True

        # Count Xavier stories
        for story_id, story in self.scrum.stories.items():
            if "[Xavier]" in safe_get_attr(story, 'title', '') or \
               safe_get_attr(story, 'epic_id') == self._get_xavier_epic_id(check_only=True):
                status["xavier_stories"] += 1

        # Count Xavier tasks
        for task_id, task in self.scrum.tasks.items():
            if "[Xavier]" in safe_get_attr(task, 'title', ''):
                status["xavier_tasks"] += 1

        # Count Xavier bugs
        for bug_id, bug in self.scrum.bugs.items():
            if "Xavier" in safe_get_attr(bug, 'title', ''):
                status["xavier_bugs"] += 1

        # Count Xavier-specific agents
        agents_dir = os.path.join(self.project_path, ".xavier", "agents")
        if os.path.exists(agents_dir):
            xavier_agents = [f for f in os.listdir(agents_dir) if "xavier" in f.lower()]
            status["xavier_agents"] = len(xavier_agents)

        # Check current sprint
        if self.scrum.current_sprint:
            sprint = self.scrum.sprints.get(self.scrum.current_sprint)
            if sprint and "Xavier" in safe_get_attr(sprint, 'name', ''):
                status["current_sprint"] = safe_get_attr(sprint, 'name')

        # Generate summary
        if status["self_hosting_active"]:
            summary = "✅ Xavier is actively managing its own development!"
        else:
            summary = "❌ Xavier self-hosting is not active. Run /xavier-init-self to begin."

        return {
            "success": True,
            "status": status,
            "summary": summary,
            "metrics": {
                "Development Items": status["xavier_stories"] + status["xavier_tasks"] + status["xavier_bugs"],
                "Specialized Agents": status["xavier_agents"],
                "Active Sprint": status["current_sprint"] or "None"
            }
        }

    def _get_or_create_xavier_epic(self) -> str:
        """Get or create the main Xavier development epic"""
        return self._get_xavier_epic_id(check_only=False)

    def _get_xavier_epic_id(self, check_only: bool = False) -> Optional[str]:
        """Get Xavier epic ID, optionally creating it if it doesn't exist"""
        # Look for existing Xavier epic
        for epic_id, epic in self.scrum.epics.items():
            if "Xavier" in safe_get_attr(epic, 'title', '') and "Self" in safe_get_attr(epic, 'title', ''):
                return epic_id

        if check_only:
            return None

        # Create Xavier epic if it doesn't exist
        epic_result = self.create_epic({
            "title": "Xavier Self-Hosting Development",
            "description": "Enable Xavier Framework to manage its own development using its own features",
            "business_value": "Ultimate dogfooding - ensures quality and demonstrates capabilities"
        })

        return epic_result.get("epic_id")

    def _get_xavier_stories(self) -> List[str]:
        """Get all Xavier development stories"""
        xavier_stories = []

        for story_id, story in self.scrum.stories.items():
            if "[Xavier]" in safe_get_attr(story, 'title', '') or \
               safe_get_attr(story, 'epic_id') == self._get_xavier_epic_id(check_only=True):
                if safe_get_attr(story, 'status') == "Backlog":
                    xavier_stories.append(story_id)

        return xavier_stories