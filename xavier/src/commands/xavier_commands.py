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
from ..scrum.scrum_manager import SCRUMManager
from ..agents.orchestrator import AgentOrchestrator, AgentTask


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
            "/xavier-help": self.show_help
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
        Initialize a new Xavier project
        Args:
            name: Project name
            description: Project description
            tech_stack: Technology stack definition
            team_size: Team size
            methodology: Development methodology (Scrum/Kanban)
        """
        # Create project configuration
        project_config = {
            "name": args["name"],
            "description": args["description"],
            "tech_stack": args.get("tech_stack", {}),
            "team_size": args.get("team_size", 5),
            "methodology": args.get("methodology", "Scrum"),
            "created_at": datetime.now().isoformat(),
            "xavier_version": "1.0.0"
        }

        # Save project configuration
        with open(self.config_path, 'w') as f:
            json.dump(project_config, f, indent=2)

        # Initialize project structure
        directories = [
            "src", "tests", "docs", "scripts",
            ".xavier/agents", ".xavier/sprints", ".xavier/reports"
        ]
        for directory in directories:
            os.makedirs(os.path.join(self.project_path, directory), exist_ok=True)

        # Generate agents for tech stack
        if "tech_stack" in args:
            self.orchestrator._generate_tech_stack_agents()

        return {
            "project": project_config,
            "directories_created": directories,
            "agents_available": list(self.orchestrator.agents.keys())
        }

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
            stories, tasks, bugs = self.scrum.plan_sprint(sprint.id)
            return {
                "sprint_id": sprint.id,
                "name": sprint.name,
                "goal": sprint.goal,
                "velocity": sprint.velocity,
                "committed_points": sprint.committed_points,
                "stories": len(stories),
                "tasks": len(tasks),
                "bugs": len(bugs),
                "status": "Planned"
            }

        return {
            "sprint_id": sprint.id,
            "name": sprint.name,
            "goal": sprint.goal,
            "velocity": sprint.velocity,
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
            planned_sprints = [s for s in self.scrum.sprints.values()
                             if s.status.value == "Planning"]
            if not planned_sprints:
                raise ValueError("No planned sprint found")
            sprint_id = planned_sprints[0].id

        # Start sprint in SCRUM manager
        self.scrum.start_sprint(sprint_id)
        sprint = self.scrum.sprints[sprint_id]

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

    def estimate_story(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate story points
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
            if story.status == "Backlog":
                priority_items.append({
                    "type": "Story",
                    "id": story.id,
                    "title": story.title,
                    "points": story.story_points,
                    "priority": story.priority
                })

        for bug in self.scrum.bugs.values():
            if bug.status == "Open" and bug.severity in ["Critical", "High"]:
                priority_items.append({
                    "type": "Bug",
                    "id": bug.id,
                    "title": bug.title,
                    "points": bug.story_points,
                    "priority": bug.priority,
                    "severity": bug.severity
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

    def show_help(self, args: Dict[str, Any]) -> Dict[str, str]:
        """Show Xavier help and commands"""
        return {
            "/create-story": "Create a user story with acceptance criteria",
            "/create-task": "Create a task under a story",
            "/create-bug": "Report a bug with reproduction steps",
            "/create-roadmap": "Create product roadmap with milestones",
            "/create-project": "Initialize new Xavier project",
            "/learn-project": "Learn existing project structure",
            "/create-sprint": "Create a new sprint with auto-planning",
            "/start-sprint": "Start sprint execution with agents",
            "/end-sprint": "Complete sprint with retrospective",
            "/estimate-story": "Estimate story points",
            "/assign-task": "Assign task to agent",
            "/review-code": "Trigger code review",
            "/generate-report": "Generate various reports",
            "/tech-stack-analyze": "Analyze project tech stack",
            "/create-agent": "Create custom agent for tech stack",
            "/list-stories": "List all user stories",
            "/list-tasks": "List all tasks",
            "/list-bugs": "List all bugs",
            "/show-backlog": "Show backlog overview",
            "/show-sprint": "Show sprint details",
            "/xavier-help": "Show this help message"
        }

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

### Project
- `/learn-project` - Analyze existing codebase
- `/tech-stack-analyze` - Detect technologies
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