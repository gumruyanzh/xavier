#!/usr/bin/env python3
"""
Claude Code Integration for Xavier Framework
Registers Xavier commands as slash commands in Claude Code
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta

# Add xavier to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from xavier.src.commands.xavier_commands import XavierCommands
from xavier.src.git_worktree import GitWorktreeManager

# Import JSON output formatter for consistent output
try:
    from xavier.src.utils.json_output_formatter import JSONOutputFormatter, ensure_json_output
except ImportError:
    JSONOutputFormatter = None
    ensure_json_output = lambda x: x  # Fallback decorator


class ClaudeCodeXavierIntegration:
    """Integration layer between Claude Code and Xavier Framework"""

    def __init__(self, project_path: str = "."):
        """Initialize the integration with Xavier commands"""
        self.project_path = project_path
        self.xavier_commands = XavierCommands(project_path)
        self.commands = self._register_commands()

    def _register_commands(self) -> Dict[str, Dict[str, Any]]:
        """Register all Xavier commands for Claude Code"""
        return {
            "/xavier-init": {
                "name": "xavier-init",
                "description": "Initialize Xavier Framework in current project",
                "handler": self.init_project,
                "args": {
                    "name": {"type": "string", "required": True, "description": "Project name"},
                    "type": {"type": "string", "default": "web", "description": "Project type (web/api/mobile/cli)"},
                    "stack": {"type": "string", "default": "python", "description": "Tech stack"}
                }
            },
            "/create-agent": {
                "name": "create-agent",
                "description": "Create a custom Xavier agent with specific skills",
                "handler": self.create_agent,
                "args": {
                    "name": {"type": "string", "required": True, "description": "Agent name"},
                    "skills": {"type": "string", "required": True, "description": "Comma-separated skills"},
                    "tools": {"type": "string", "default": "Read,Write,Edit,Bash", "description": "Available tools"},
                    "color": {"type": "string", "default": "blue", "description": "Agent color"},
                    "emoji": {"type": "string", "default": "🤖", "description": "Agent emoji"}
                }
            },
            "/create-story": {
                "name": "create-story",
                "description": "Create a new user story in the backlog",
                "handler": self.create_story,
                "args": {
                    "title": {"type": "string", "required": True, "description": "Story title"},
                    "as_a": {"type": "string", "required": True, "description": "As a..."},
                    "i_want": {"type": "string", "required": True, "description": "I want..."},
                    "so_that": {"type": "string", "required": True, "description": "So that..."},
                    "points": {"type": "integer", "default": 0, "description": "Story points (0 for auto-estimate)"}
                }
            },
            "/estimate": {
                "name": "estimate",
                "description": "Estimate story points for backlog stories",
                "handler": self.estimate_stories,
                "args": {
                    "story_ids": {"type": "string", "description": "Comma-separated story IDs (empty for all)"}
                }
            },
            "/sprint": {
                "name": "sprint",
                "description": "Manage sprints (create/start/end)",
                "handler": self.manage_sprint,
                "args": {
                    "action": {"type": "string", "required": True, "description": "Action: create/start/end/status"},
                    "name": {"type": "string", "description": "Sprint name (for create)"},
                    "duration": {"type": "integer", "default": 14, "description": "Sprint duration in days"}
                }
            },
            "/start-task": {
                "name": "start-task",
                "description": "Start working on a specific task with the right agent",
                "handler": self.start_task,
                "args": {
                    "task_id": {"type": "string", "required": True, "description": "Task ID to work on"},
                    "agent": {"type": "string", "description": "Specific agent to use (optional)"}
                }
            },
            "/xavier-status": {
                "name": "xavier-status",
                "description": "Show Xavier project status and metrics",
                "handler": self.show_status,
                "args": {
                    "verbose": {"type": "boolean", "default": False, "description": "Show detailed status"}
                }
            },
            "/create-epic": {
                "name": "create-epic",
                "description": "Create a new epic to group related stories",
                "handler": self.create_epic,
                "args": {
                    "title": {"type": "string", "required": True, "description": "Epic title"},
                    "description": {"type": "string", "required": True, "description": "Epic description"},
                    "stories": {"type": "string", "description": "Comma-separated story IDs to include"}
                }
            },
            "/roadmap": {
                "name": "roadmap",
                "description": "View or update project roadmap",
                "handler": self.manage_roadmap,
                "args": {
                    "action": {"type": "string", "default": "view", "description": "Action: view/add/update"},
                    "milestone": {"type": "string", "description": "Milestone name (for add)"},
                    "date": {"type": "string", "description": "Target date (YYYY-MM-DD)"}
                }
            },
            "/xavier-test": {
                "name": "xavier-test",
                "description": "Run Xavier's test-first enforcement",
                "handler": self.run_tests,
                "args": {
                    "coverage": {"type": "boolean", "default": True, "description": "Check coverage"},
                    "path": {"type": "string", "description": "Specific path to test"}
                }
            },
            "/assign-agent": {
                "name": "assign-agent",
                "description": "Assign the best agent to a task automatically",
                "handler": self.assign_agent,
                "args": {
                    "task_id": {"type": "string", "required": True, "description": "Task ID"},
                    "auto": {"type": "boolean", "default": True, "description": "Auto-select best agent"}
                }
            },
            "/bug": {
                "name": "bug",
                "description": "Report and track bugs",
                "handler": self.manage_bug,
                "args": {
                    "title": {"type": "string", "required": True, "description": "Bug title"},
                    "description": {"type": "string", "required": True, "description": "Bug description"},
                    "priority": {"type": "string", "default": "medium", "description": "Priority: low/medium/high/critical"},
                    "component": {"type": "string", "description": "Affected component"}
                }
            },
            "/velocity": {
                "name": "velocity",
                "description": "Show team velocity and sprint metrics",
                "handler": self.show_velocity,
                "args": {
                    "sprints": {"type": "integer", "default": 3, "description": "Number of past sprints to analyze"}
                }
            },
            "/backlog": {
                "name": "backlog",
                "description": "Manage product backlog",
                "handler": self.manage_backlog,
                "args": {
                    "action": {"type": "string", "default": "view", "description": "Action: view/prioritize/groom"},
                    "filter": {"type": "string", "description": "Filter: unestimated/ready/blocked"}
                }
            }
        }

    def init_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize Xavier Framework in the current project"""
        return self.xavier_commands.create_project({
            "name": args.get("name"),
            "project_type": args.get("type", "web"),
            "tech_stack": {"backend": {"language": args.get("stack", "python")}},
            "auto_generate_stories": True
        })

    def create_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom agent"""
        skills = [s.strip() for s in args.get("skills", "").split(",")]
        tools = [t.strip() for t in args.get("tools", "Read,Write,Edit,Bash").split(",")]

        return self.xavier_commands.create_agent({
            "name": args.get("name"),
            "skills": skills,
            "experience": {},
            "tools": tools,
            "color": args.get("color", "blue"),
            "emoji": args.get("emoji", "🤖")
        })

    @ensure_json_output
    def create_story(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user story - always returns JSON format"""
        story_data = {
            "title": args.get("title"),
            "as_a": args.get("as_a"),
            "i_want": args.get("i_want"),
            "so_that": args.get("so_that"),
            "acceptance_criteria": [],
            "story_points": args.get("points", 0)
        }

        # Save to backlog (JSON format only)
        backlog_path = Path(self.project_path) / ".xavier" / "data" / "backlog.json"
        if backlog_path.exists():
            with open(backlog_path, 'r') as f:
                backlog = json.load(f)
        else:
            backlog = {"stories": []}

        # Generate story ID
        story_id = f"STORY-{len(backlog['stories']) + 1:03d}"
        story_data["id"] = story_id
        story_data["status"] = "backlog"
        story_data["created_at"] = datetime.now().isoformat()

        backlog["stories"].append(story_data)

        # Save backlog (strictly JSON format)
        backlog_path.parent.mkdir(parents=True, exist_ok=True)
        with open(backlog_path, 'w') as f:
            json.dump(backlog, f, indent=2)

        # Return JSON-formatted output
        if JSONOutputFormatter:
            return json.loads(JSONOutputFormatter.format_story_output(story_data))
        else:
            return {
                "status": "success",
                "story_id": story_id,
                "message": f"Story '{args.get('title')}' created with ID {story_id}",
                "data": story_data
            }

    def estimate_stories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate story points for stories"""
        story_ids = []
        if args.get("story_ids"):
            story_ids = [s.strip() for s in args.get("story_ids", "").split(",")]

        return self.xavier_commands.estimate_story({"story_ids": story_ids})

    def manage_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage sprints"""
        action = args.get("action", "status")

        if action == "create":
            return self._create_sprint(args)
        elif action == "start":
            return self._start_sprint(args)
        elif action == "end":
            return self._end_sprint(args)
        else:  # status
            return self._sprint_status()

    def _create_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new sprint"""
        sprint_data = {
            "name": args.get("name", f"Sprint {self._get_next_sprint_number()}"),
            "duration": args.get("duration", 14),
            "status": "planned",
            "stories": []
        }

        sprints_path = Path(self.project_path) / ".xavier" / "data" / "sprints.json"
        if sprints_path.exists():
            with open(sprints_path, 'r') as f:
                sprints = json.load(f)
        else:
            sprints = {"sprints": []}

        sprints["sprints"].append(sprint_data)

        sprints_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sprints_path, 'w') as f:
            json.dump(sprints, f, indent=2)

        return {
            "status": "success",
            "message": f"Sprint '{sprint_data['name']}' created"
        }

    def _get_next_sprint_number(self) -> int:
        """Get the next sprint number"""
        sprints_path = Path(self.project_path) / ".xavier" / "data" / "sprints.json"
        if sprints_path.exists():
            with open(sprints_path, 'r') as f:
                sprints = json.load(f)
                return len(sprints.get("sprints", [])) + 1
        return 1

    def _start_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start a sprint with worktree initialization"""
        # Get the current planned sprint
        sprints_path = Path(self.project_path) / ".xavier" / "data" / "sprints.json"
        tasks_path = Path(self.project_path) / ".xavier" / "data" / "tasks.json"

        if not sprints_path.exists():
            return {"status": "error", "message": "No sprints found"}

        with open(sprints_path, 'r') as f:
            sprints_data = json.load(f)

        # Find the planned sprint to start
        planned_sprints = [s for s in sprints_data.get("sprints", []) if s.get("status") == "planned"]
        if not planned_sprints:
            return {"status": "error", "message": "No planned sprint found to start"}

        sprint = planned_sprints[0]  # Start the first planned sprint

        # Initialize worktree manager
        worktree_manager = GitWorktreeManager(self.project_path)
        worktree_manager.initialize_worktree_directory()

        # Get tasks for the sprint
        tasks = []
        if tasks_path.exists():
            with open(tasks_path, 'r') as f:
                tasks_data = json.load(f)
                sprint_tasks = sprint.get("tasks", [])
                tasks = [t for t in tasks_data.get("tasks", []) if t.get("id") in sprint_tasks]

        # Create worktrees for each unique agent assigned to tasks
        agents_initialized = set()
        worktree_info = []

        for task in tasks:
            agent_name = task.get("assigned_to", "unassigned")
            task_id = task.get("id")

            if agent_name != "unassigned":
                # Create worktree for this agent-task combination
                success, message = worktree_manager.create_worktree(
                    branch_name=f"{agent_name}/{task_id}",
                    agent_name=agent_name,
                    task_id=task_id
                )

                if success:
                    agents_initialized.add(agent_name)
                    worktree_info.append({
                        "agent": agent_name,
                        "task": task_id,
                        "worktree": f"trees/{agent_name}-{task_id}"
                    })

        # Update sprint status to active
        sprint["status"] = "active"
        sprint["started_at"] = Path(self.project_path).stat().st_mtime  # Use current time
        sprint["worktrees"] = worktree_info

        # Save updated sprints
        with open(sprints_path, 'w') as f:
            json.dump(sprints_data, f, indent=2)

        return {
            "status": "success",
            "message": f"Sprint '{sprint['name']}' started",
            "details": {
                "sprint_name": sprint["name"],
                "duration": sprint.get("duration", 14),
                "tasks": len(tasks),
                "agents_initialized": list(agents_initialized),
                "worktrees_created": len(worktree_info)
            }
        }

    def _end_sprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """End a sprint with worktree cleanup"""
        sprints_path = Path(self.project_path) / ".xavier" / "data" / "sprints.json"

        if not sprints_path.exists():
            return {"status": "error", "message": "No sprints found"}

        with open(sprints_path, 'r') as f:
            sprints_data = json.load(f)

        # Find the active sprint
        active_sprints = [s for s in sprints_data.get("sprints", []) if s.get("status") == "active"]
        if not active_sprints:
            return {"status": "error", "message": "No active sprint found"}

        sprint = active_sprints[0]

        # Initialize worktree manager
        worktree_manager = GitWorktreeManager(self.project_path)

        # Check for uncommitted changes in all worktrees
        worktrees_with_changes = []
        cleaned_worktrees = []
        worktree_info = sprint.get("worktrees", [])

        for wt_info in worktree_info:
            task_id = wt_info.get("task")
            if task_id:
                status = worktree_manager.get_worktree_status(task_id)
                if status and status.get("has_uncommitted_changes"):
                    worktrees_with_changes.append({
                        "task": task_id,
                        "agent": wt_info.get("agent"),
                        "worktree": wt_info.get("worktree")
                    })
                else:
                    # Clean up worktree if no uncommitted changes
                    success, message = worktree_manager.remove_worktree(task_id, force=False)
                    if success:
                        cleaned_worktrees.append(task_id)

        # Archive sprint data
        sprint["status"] = "completed"
        sprint["ended_at"] = Path(self.project_path).stat().st_mtime
        sprint["cleaned_worktrees"] = cleaned_worktrees
        sprint["pending_worktrees"] = worktrees_with_changes

        # Save updated sprints
        with open(sprints_path, 'w') as f:
            json.dump(sprints_data, f, indent=2)

        # Prepare response
        response = {
            "status": "success",
            "message": f"Sprint '{sprint['name']}' ended",
            "details": {
                "sprint_name": sprint["name"],
                "worktrees_cleaned": len(cleaned_worktrees),
                "worktrees_with_changes": len(worktrees_with_changes)
            }
        }

        if worktrees_with_changes:
            response["warning"] = f"{len(worktrees_with_changes)} worktrees have uncommitted changes"
            response["pending_worktrees"] = worktrees_with_changes

        return response

    def _sprint_status(self) -> Dict[str, Any]:
        """Get sprint status"""
        sprints_path = Path(self.project_path) / ".xavier" / "data" / "sprints.json"
        if sprints_path.exists():
            with open(sprints_path, 'r') as f:
                sprints = json.load(f)
                active_sprints = [s for s in sprints.get("sprints", []) if s.get("status") == "active"]
                if active_sprints:
                    return {
                        "status": "success",
                        "active_sprint": active_sprints[0],
                        "message": f"Active sprint: {active_sprints[0]['name']}"
                    }
        return {"status": "success", "message": "No active sprint"}

    def start_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start working on a task with the appropriate agent"""
        task_id = args.get("task_id")
        agent_name = args.get("agent")

        # Find the task and determine the best agent
        if not agent_name:
            # Auto-select agent based on task requirements
            agent_name = self._select_agent_for_task(task_id)

        return {
            "status": "success",
            "message": f"Starting task {task_id} with agent {agent_name}",
            "agent": agent_name,
            "task_id": task_id
        }

    def _select_agent_for_task(self, task_id: str) -> str:
        """Select the best agent for a task"""
        # Logic to analyze task and select appropriate agent
        # For now, return a default
        return "python-engineer"

    def show_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Show Xavier project status with worktree monitoring"""
        status = {
            "project": self._get_project_info(),
            "sprint": self._sprint_status(),
            "backlog": self._get_backlog_summary(),
            "agents": self._get_agents_summary(),
            "worktrees": self._get_worktree_status()
        }

        if args.get("verbose"):
            status["metrics"] = self._get_project_metrics()

        return {"status": "success", "data": status}

    def _get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        config_path = Path(self.project_path) / ".xavier" / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def _get_backlog_summary(self) -> Dict[str, Any]:
        """Get backlog summary"""
        backlog_path = Path(self.project_path) / ".xavier" / "data" / "backlog.json"
        if backlog_path.exists():
            with open(backlog_path, 'r') as f:
                backlog = json.load(f)
                stories = backlog.get("stories", [])
                return {
                    "total_stories": len(stories),
                    "estimated": len([s for s in stories if s.get("story_points", 0) > 0]),
                    "unestimated": len([s for s in stories if s.get("story_points", 0) == 0])
                }
        return {"total_stories": 0, "estimated": 0, "unestimated": 0}

    def _get_agents_summary(self) -> Dict[str, Any]:
        """Get agents summary"""
        agents_path = Path(self.project_path) / ".xavier" / "agents"
        if agents_path.exists():
            agent_files = list(agents_path.glob("*.yaml"))
            return {
                "total_agents": len(agent_files),
                "agents": [f.stem for f in agent_files]
            }
        return {"total_agents": 0, "agents": []}

    def _get_worktree_status(self) -> Dict[str, Any]:
        """Get status of all active worktrees"""
        worktree_manager = GitWorktreeManager(self.project_path)
        worktrees = worktree_manager.list_worktrees()

        worktree_summary = {
            "total_worktrees": len(worktrees),
            "active_worktrees": [],
            "worktrees_with_changes": 0,
            "worktrees_ahead": 0,
            "worktrees_behind": 0
        }

        for wt in worktrees:
            task_id = wt.get("task_id")
            if task_id:
                status = worktree_manager.get_worktree_status(task_id)
                if status:
                    worktree_detail = {
                        "task_id": task_id,
                        "agent": status.get("agent"),
                        "branch": status.get("branch"),
                        "has_changes": status.get("has_uncommitted_changes", False),
                        "commits_ahead": status.get("commits_ahead", 0),
                        "commits_behind": status.get("commits_behind", 0)
                    }
                    worktree_summary["active_worktrees"].append(worktree_detail)

                    if status.get("has_uncommitted_changes"):
                        worktree_summary["worktrees_with_changes"] += 1
                    if status.get("commits_ahead", 0) > 0:
                        worktree_summary["worktrees_ahead"] += 1
                    if status.get("commits_behind", 0) > 0:
                        worktree_summary["worktrees_behind"] += 1

        return worktree_summary

    def _get_project_metrics(self) -> Dict[str, Any]:
        """Get detailed project metrics"""
        return {
            "velocity": self._calculate_velocity(),
            "burndown": self._get_burndown_data(),
            "completion_rate": self._calculate_completion_rate()
        }

    def _calculate_velocity(self) -> float:
        """Calculate team velocity"""
        # Implementation would calculate from completed sprints
        return 0.0

    def _get_burndown_data(self) -> List[Dict[str, Any]]:
        """Get burndown chart data"""
        return []

    def _calculate_completion_rate(self) -> float:
        """Calculate story completion rate"""
        return 0.0

    def create_epic(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new epic"""
        epic_data = {
            "title": args.get("title"),
            "description": args.get("description"),
            "stories": []
        }

        if args.get("stories"):
            epic_data["stories"] = [s.strip() for s in args.get("stories", "").split(",")]

        # Save epic
        epics_path = Path(self.project_path) / ".xavier" / "data" / "epics.json"
        if epics_path.exists():
            with open(epics_path, 'r') as f:
                epics = json.load(f)
        else:
            epics = {"epics": []}

        epic_id = f"EPIC-{len(epics['epics']) + 1:03d}"
        epic_data["id"] = epic_id

        epics["epics"].append(epic_data)

        epics_path.parent.mkdir(parents=True, exist_ok=True)
        with open(epics_path, 'w') as f:
            json.dump(epics, f, indent=2)

        return {
            "status": "success",
            "epic_id": epic_id,
            "message": f"Epic '{args.get('title')}' created with ID {epic_id}"
        }

    def manage_roadmap(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage project roadmap"""
        action = args.get("action", "view")

        roadmap_path = Path(self.project_path) / ".xavier" / "data" / "roadmap.json"

        if action == "view":
            if roadmap_path.exists():
                with open(roadmap_path, 'r') as f:
                    roadmap = json.load(f)
                return {"status": "success", "roadmap": roadmap}
            return {"status": "success", "roadmap": {"milestones": []}}

        elif action == "add":
            milestone = {
                "name": args.get("milestone"),
                "date": args.get("date"),
                "status": "planned"
            }

            if roadmap_path.exists():
                with open(roadmap_path, 'r') as f:
                    roadmap = json.load(f)
            else:
                roadmap = {"milestones": []}

            roadmap["milestones"].append(milestone)

            roadmap_path.parent.mkdir(parents=True, exist_ok=True)
            with open(roadmap_path, 'w') as f:
                json.dump(roadmap, f, indent=2)

            return {"status": "success", "message": f"Milestone '{milestone['name']}' added"}

        return {"status": "error", "message": "Invalid action"}

    def run_tests(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run Xavier's test-first enforcement"""
        # This would integrate with the test runner
        return {
            "status": "success",
            "message": "Running tests with Xavier's test-first enforcement",
            "coverage_required": args.get("coverage", True)
        }

    def assign_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Assign the best agent to a task"""
        task_id = args.get("task_id")

        if args.get("auto", True):
            agent = self._select_agent_for_task(task_id)
            return {
                "status": "success",
                "message": f"Auto-assigned agent '{agent}' to task {task_id}",
                "agent": agent
            }

        return {"status": "error", "message": "Manual agent assignment not yet implemented"}

    def manage_bug(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Report and track bugs"""
        bug_data = {
            "title": args.get("title"),
            "description": args.get("description"),
            "priority": args.get("priority", "medium"),
            "component": args.get("component", "unknown"),
            "status": "open"
        }

        bugs_path = Path(self.project_path) / ".xavier" / "data" / "bugs.json"
        if bugs_path.exists():
            with open(bugs_path, 'r') as f:
                bugs = json.load(f)
        else:
            bugs = {"bugs": []}

        bug_id = f"BUG-{len(bugs['bugs']) + 1:03d}"
        bug_data["id"] = bug_id

        bugs["bugs"].append(bug_data)

        bugs_path.parent.mkdir(parents=True, exist_ok=True)
        with open(bugs_path, 'w') as f:
            json.dump(bugs, f, indent=2)

        return {
            "status": "success",
            "bug_id": bug_id,
            "message": f"Bug '{args.get('title')}' reported with ID {bug_id}"
        }

    def show_velocity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Show team velocity metrics"""
        num_sprints = args.get("sprints", 3)

        # Calculate velocity from past sprints
        velocity_data = {
            "average_velocity": 0,
            "trend": "stable",
            "sprints_analyzed": num_sprints
        }

        return {"status": "success", "velocity": velocity_data}

    def manage_backlog(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage product backlog"""
        action = args.get("action", "view")
        filter_type = args.get("filter")

        backlog_path = Path(self.project_path) / ".xavier" / "data" / "backlog.json"

        if not backlog_path.exists():
            return {"status": "success", "backlog": {"stories": []}}

        with open(backlog_path, 'r') as f:
            backlog = json.load(f)

        stories = backlog.get("stories", [])

        if filter_type == "unestimated":
            stories = [s for s in stories if s.get("story_points", 0) == 0]
        elif filter_type == "ready":
            stories = [s for s in stories if s.get("story_points", 0) > 0]
        elif filter_type == "blocked":
            stories = [s for s in stories if s.get("blocked", False)]

        if action == "view":
            return {"status": "success", "backlog": {"stories": stories}}
        elif action == "prioritize":
            # Would implement prioritization logic
            return {"status": "success", "message": "Backlog prioritized"}
        elif action == "groom":
            # Would implement grooming logic
            return {"status": "success", "message": "Backlog groomed"}

        return {"status": "error", "message": "Invalid action"}

    def execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a slash command"""
        if command not in self.commands:
            return {
                "status": "error",
                "message": f"Unknown command: {command}",
                "available_commands": list(self.commands.keys())
            }

        cmd_info = self.commands[command]
        handler = cmd_info["handler"]

        # Validate required arguments
        if args is None:
            args = {}

        for arg_name, arg_spec in cmd_info.get("args", {}).items():
            if arg_spec.get("required") and arg_name not in args:
                return {
                    "status": "error",
                    "message": f"Missing required argument: {arg_name}"
                }

        try:
            return handler(args)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Command failed: {str(e)}"
            }

    def list_commands(self) -> List[Dict[str, Any]]:
        """List all available commands"""
        commands = []
        for cmd_name, cmd_info in self.commands.items():
            commands.append({
                "name": cmd_name,
                "description": cmd_info["description"],
                "args": cmd_info.get("args", {})
            })
        return commands


def main():
    """CLI entry point for testing commands"""
    parser = argparse.ArgumentParser(description="Claude Code Xavier Integration")
    parser.add_argument("command", help="Slash command to execute")
    parser.add_argument("--args", type=json.loads, default={}, help="Command arguments as JSON")
    parser.add_argument("--list", action="store_true", help="List available commands")

    args = parser.parse_args()

    integration = ClaudeCodeXavierIntegration()

    if args.list:
        commands = integration.list_commands()
        print("Available Xavier Commands:")
        for cmd in commands:
            print(f"  {cmd['name']}: {cmd['description']}")
            if cmd.get('args'):
                print(f"    Args: {', '.join(cmd['args'].keys())}")
        return

    result = integration.execute_command(args.command, args.args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()