"""
Xavier Framework - SCRUM Management System
Enterprise-grade SCRUM implementation with strict workflow control
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os


class SprintStatus(Enum):
    PLANNING = "Planning"
    ACTIVE = "Active"
    REVIEW = "Review"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


@dataclass
class UserStory:
    """User story with acceptance criteria and tasks"""
    id: str
    title: str
    description: str
    as_a: str  # As a [role]
    i_want: str  # I want [feature]
    so_that: str  # So that [benefit]
    acceptance_criteria: List[str]
    story_points: int
    priority: str
    epic_id: Optional[str] = None
    tasks: List[str] = field(default_factory=list)
    bugs: List[str] = field(default_factory=list)
    status: str = "Backlog"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Task:
    """Task under a user story"""
    id: str
    story_id: str
    title: str
    description: str
    technical_details: str
    estimated_hours: float
    story_points: int
    priority: str
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    test_criteria: List[str] = field(default_factory=list)
    status: str = "Backlog"
    completion_percentage: int = 0
    test_coverage: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Bug:
    """Bug report with reproduction steps"""
    id: str
    title: str
    description: str
    steps_to_reproduce: List[str]
    expected_behavior: str
    actual_behavior: str
    severity: str  # Critical, High, Medium, Low
    priority: str
    story_points: int
    affected_stories: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    status: str = "Open"
    resolution: Optional[str] = None
    test_coverage: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class Sprint:
    """Sprint with goals and items"""
    id: str
    name: str
    goal: str
    start_date: datetime
    end_date: datetime
    velocity: int
    committed_points: int
    completed_points: int = 0
    status: SprintStatus = SprintStatus.PLANNING
    stories: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    bugs: List[str] = field(default_factory=list)
    daily_burndown: Dict[str, int] = field(default_factory=dict)
    retrospective_notes: Optional[str] = None


@dataclass
class Epic:
    """Epic containing multiple user stories"""
    id: str
    title: str
    description: str
    business_value: str
    target_release: Optional[str] = None
    stories: List[str] = field(default_factory=list)
    total_points: int = 0
    completed_points: int = 0
    status: str = "Planning"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Roadmap:
    """Product roadmap with milestones"""
    id: str
    name: str
    vision: str
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    epics: List[str] = field(default_factory=list)
    releases: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class SCRUMManager:
    """Manages SCRUM workflow with strict process enforcement"""

    def __init__(self, data_dir: str = "xavier_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # Data stores
        self.stories: Dict[str, UserStory] = {}
        self.tasks: Dict[str, Task] = {}
        self.bugs: Dict[str, Bug] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.epics: Dict[str, Epic] = {}
        self.roadmaps: Dict[str, Roadmap] = {}

        # Current sprint
        self.current_sprint: Optional[str] = None

        # Story point scale (Fibonacci)
        self.story_point_scale = [1, 2, 3, 5, 8, 13, 21]

        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load existing SCRUM data from disk"""
        data_files = {
            "stories": self.stories,
            "tasks": self.tasks,
            "bugs": self.bugs,
            "sprints": self.sprints,
            "epics": self.epics,
            "roadmaps": self.roadmaps
        }

        for data_type, storage in data_files.items():
            file_path = os.path.join(self.data_dir, f"{data_type}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Convert back to dataclass instances
                    # Note: In production, use proper serialization
                    storage.update(data)

    def _save_data(self):
        """Save SCRUM data to disk"""
        data_files = {
            "stories": self.stories,
            "tasks": self.tasks,
            "bugs": self.bugs,
            "sprints": self.sprints,
            "epics": self.epics,
            "roadmaps": self.roadmaps
        }

        for data_type, storage in data_files.items():
            file_path = os.path.join(self.data_dir, f"{data_type}.json")
            # Note: In production, use proper serialization for dataclasses
            # with open(file_path, 'w') as f:
            #     json.dump(storage, f, indent=2, default=str)

    def create_story(self, title: str, as_a: str, i_want: str, so_that: str,
                    acceptance_criteria: List[str], priority: str = "Medium",
                    epic_id: Optional[str] = None) -> UserStory:
        """Create a user story following standard format"""
        story_id = f"US-{uuid.uuid4().hex[:8].upper()}"

        story = UserStory(
            id=story_id,
            title=title,
            description=f"As a {as_a}, I want {i_want}, so that {so_that}",
            as_a=as_a,
            i_want=i_want,
            so_that=so_that,
            acceptance_criteria=acceptance_criteria,
            story_points=0,  # Will be estimated by PM agent
            priority=priority,
            epic_id=epic_id
        )

        self.stories[story_id] = story

        # Add to epic if specified
        if epic_id and epic_id in self.epics:
            self.epics[epic_id].stories.append(story_id)

        self._save_data()
        return story

    def create_task(self, story_id: str, title: str, description: str,
                   technical_details: str, estimated_hours: float,
                   test_criteria: List[str], priority: str = "Medium",
                   dependencies: List[str] = None) -> Task:
        """Create a task under a user story"""
        if story_id not in self.stories:
            raise ValueError(f"Story {story_id} not found")

        task_id = f"T-{uuid.uuid4().hex[:8].upper()}"

        task = Task(
            id=task_id,
            story_id=story_id,
            title=title,
            description=description,
            technical_details=technical_details,
            estimated_hours=estimated_hours,
            story_points=max(1, int(estimated_hours / 4)),  # Rough conversion
            priority=priority,
            dependencies=dependencies or [],
            test_criteria=test_criteria
        )

        self.tasks[task_id] = task
        self.stories[story_id].tasks.append(task_id)

        self._save_data()
        return task

    def create_bug(self, title: str, description: str, steps_to_reproduce: List[str],
                  expected_behavior: str, actual_behavior: str, severity: str,
                  priority: str = "High", affected_stories: List[str] = None,
                  affected_components: List[str] = None) -> Bug:
        """Create a bug report"""
        bug_id = f"BUG-{uuid.uuid4().hex[:8].upper()}"

        bug = Bug(
            id=bug_id,
            title=title,
            description=description,
            steps_to_reproduce=steps_to_reproduce,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior,
            severity=severity,
            priority=priority,
            story_points=self._estimate_bug_points(severity),
            affected_stories=affected_stories or [],
            affected_components=affected_components or []
        )

        self.bugs[bug_id] = bug

        # Link to affected stories
        for story_id in (affected_stories or []):
            if story_id in self.stories:
                self.stories[story_id].bugs.append(bug_id)

        self._save_data()
        return bug

    def _estimate_bug_points(self, severity: str) -> int:
        """Estimate story points for bug based on severity"""
        severity_points = {
            "Critical": 8,
            "High": 5,
            "Medium": 3,
            "Low": 1
        }
        return severity_points.get(severity, 3)

    def create_epic(self, title: str, description: str, business_value: str,
                   target_release: Optional[str] = None) -> Epic:
        """Create an epic"""
        epic_id = f"E-{uuid.uuid4().hex[:8].upper()}"

        epic = Epic(
            id=epic_id,
            title=title,
            description=description,
            business_value=business_value,
            target_release=target_release
        )

        self.epics[epic_id] = epic
        self._save_data()
        return epic

    def create_roadmap(self, name: str, vision: str) -> Roadmap:
        """Create a product roadmap"""
        roadmap_id = f"RM-{uuid.uuid4().hex[:8].upper()}"

        roadmap = Roadmap(
            id=roadmap_id,
            name=name,
            vision=vision
        )

        self.roadmaps[roadmap_id] = roadmap
        self._save_data()
        return roadmap

    def add_milestone_to_roadmap(self, roadmap_id: str, milestone_name: str,
                                target_date: datetime, epics: List[str],
                                success_criteria: List[str]):
        """Add a milestone to roadmap"""
        if roadmap_id not in self.roadmaps:
            raise ValueError(f"Roadmap {roadmap_id} not found")

        milestone = {
            "name": milestone_name,
            "target_date": target_date.isoformat(),
            "epics": epics,
            "success_criteria": success_criteria,
            "status": "Planning"
        }

        self.roadmaps[roadmap_id].milestones.append(milestone)
        self._save_data()

    def estimate_story(self, story_id: str, points: int) -> UserStory:
        """Estimate story points (done by PM agent)"""
        if story_id not in self.stories:
            raise ValueError(f"Story {story_id} not found")

        if points not in self.story_point_scale:
            raise ValueError(f"Points must be in Fibonacci scale: {self.story_point_scale}")

        story = self.stories[story_id]
        story.story_points = points
        story.updated_at = datetime.now()

        # Update epic total if part of one
        if story.epic_id and story.epic_id in self.epics:
            self._update_epic_points(story.epic_id)

        self._save_data()
        return story

    def _update_epic_points(self, epic_id: str):
        """Update epic total points"""
        epic = self.epics[epic_id]
        total_points = 0
        completed_points = 0

        for story_id in epic.stories:
            if story_id in self.stories:
                story = self.stories[story_id]
                total_points += story.story_points
                if story.status == "Done":
                    completed_points += story.story_points

        epic.total_points = total_points
        epic.completed_points = completed_points

    def create_sprint(self, name: str, goal: str, duration_days: int = 14) -> Sprint:
        """Create a new sprint"""
        sprint_id = f"SP-{uuid.uuid4().hex[:8].upper()}"

        sprint = Sprint(
            id=sprint_id,
            name=name,
            goal=goal,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            velocity=self._calculate_velocity(),
            committed_points=0
        )

        self.sprints[sprint_id] = sprint
        self._save_data()
        return sprint

    def _calculate_velocity(self) -> int:
        """Calculate team velocity based on past sprints"""
        completed_sprints = [s for s in self.sprints.values()
                           if s.status == SprintStatus.COMPLETED]

        if not completed_sprints:
            return 20  # Default velocity

        # Average of last 3 sprints
        recent_sprints = sorted(completed_sprints,
                              key=lambda s: s.end_date,
                              reverse=True)[:3]

        total_points = sum(s.completed_points for s in recent_sprints)
        return int(total_points / len(recent_sprints))

    def plan_sprint(self, sprint_id: str) -> Tuple[List[str], List[str], List[str]]:
        """Auto-plan sprint based on priority and velocity"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")

        sprint = self.sprints[sprint_id]

        # Get all available items
        available_stories = [s for s in self.stories.values()
                           if s.status == "Backlog"]
        available_tasks = [t for t in self.tasks.values()
                         if t.status == "Backlog" and t.story_id not in sprint.stories]
        available_bugs = [b for b in self.bugs.values()
                        if b.status == "Open"]

        # Sort by priority
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

        available_stories.sort(key=lambda s: (priority_order.get(s.priority, 3), -s.story_points))
        available_bugs.sort(key=lambda b: (priority_order.get(b.priority, 3), b.severity))
        available_tasks.sort(key=lambda t: priority_order.get(t.priority, 3))

        # Add items to sprint up to velocity
        total_points = 0
        selected_stories = []
        selected_tasks = []
        selected_bugs = []

        # First add critical bugs
        for bug in available_bugs:
            if bug.severity == "Critical" and total_points + bug.story_points <= sprint.velocity:
                selected_bugs.append(bug.id)
                total_points += bug.story_points

        # Then add stories
        for story in available_stories:
            if story.story_points > 0 and total_points + story.story_points <= sprint.velocity:
                selected_stories.append(story.id)
                total_points += story.story_points

                # Add related tasks
                for task_id in story.tasks:
                    if task_id in self.tasks:
                        selected_tasks.append(task_id)

        # Add remaining bugs if capacity allows
        for bug in available_bugs:
            if bug.id not in selected_bugs and total_points + bug.story_points <= sprint.velocity:
                selected_bugs.append(bug.id)
                total_points += bug.story_points

        # Update sprint
        sprint.stories = selected_stories
        sprint.tasks = selected_tasks
        sprint.bugs = selected_bugs
        sprint.committed_points = total_points

        self._save_data()
        return selected_stories, selected_tasks, selected_bugs

    def start_sprint(self, sprint_id: str) -> bool:
        """Start a sprint - only one can be active"""
        if self.current_sprint:
            raise ValueError(f"Sprint {self.current_sprint} is already active")

        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")

        sprint = self.sprints[sprint_id]

        if sprint.committed_points == 0:
            raise ValueError("Sprint has no committed work")

        sprint.status = SprintStatus.ACTIVE
        sprint.start_date = datetime.now()
        self.current_sprint = sprint_id

        # Update status of sprint items
        for story_id in sprint.stories:
            if story_id in self.stories:
                self.stories[story_id].status = "In Progress"

        for task_id in sprint.tasks:
            if task_id in self.tasks:
                self.tasks[task_id].status = "In Progress"

        for bug_id in sprint.bugs:
            if bug_id in self.bugs:
                self.bugs[bug_id].status = "In Progress"

        self._save_data()
        return True

    def update_task_progress(self, task_id: str, completion_percentage: int,
                           test_coverage: float) -> Task:
        """Update task progress with strict validation"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]

        # Validate test coverage before allowing progress
        if completion_percentage > 50 and test_coverage < 80:
            raise ValueError("Test coverage must be at least 80% when task is more than 50% complete")

        if completion_percentage == 100 and test_coverage < 100:
            raise ValueError("Test coverage must be 100% for completed tasks")

        task.completion_percentage = completion_percentage
        task.test_coverage = test_coverage

        if completion_percentage == 100:
            task.status = "Done"
            self._update_story_progress(task.story_id)

        task.updated_at = datetime.now()
        self._save_data()
        return task

    def _update_story_progress(self, story_id: str):
        """Update story progress based on task completion"""
        if story_id not in self.stories:
            return

        story = self.stories[story_id]
        all_tasks_done = all(
            self.tasks[task_id].status == "Done"
            for task_id in story.tasks
            if task_id in self.tasks
        )

        if all_tasks_done:
            story.status = "Done"
            story.updated_at = datetime.now()

            # Update sprint progress
            if self.current_sprint:
                self._update_sprint_burndown()

    def _update_sprint_burndown(self):
        """Update sprint burndown chart"""
        if not self.current_sprint:
            return

        sprint = self.sprints[self.current_sprint]

        # Calculate remaining points
        remaining_points = 0

        for story_id in sprint.stories:
            if story_id in self.stories and self.stories[story_id].status != "Done":
                remaining_points += self.stories[story_id].story_points

        for bug_id in sprint.bugs:
            if bug_id in self.bugs and self.bugs[bug_id].status != "Resolved":
                remaining_points += self.bugs[bug_id].story_points

        # Update daily burndown
        today = datetime.now().date().isoformat()
        sprint.daily_burndown[today] = remaining_points
        sprint.completed_points = sprint.committed_points - remaining_points

    def complete_sprint(self, sprint_id: str, retrospective_notes: str) -> Sprint:
        """Complete a sprint with retrospective"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")

        sprint = self.sprints[sprint_id]

        if sprint.status != SprintStatus.ACTIVE:
            raise ValueError("Can only complete active sprints")

        sprint.status = SprintStatus.COMPLETED
        sprint.end_date = datetime.now()
        sprint.retrospective_notes = retrospective_notes

        # Move incomplete items back to backlog
        for story_id in sprint.stories:
            if story_id in self.stories and self.stories[story_id].status != "Done":
                self.stories[story_id].status = "Backlog"

        for task_id in sprint.tasks:
            if task_id in self.tasks and self.tasks[task_id].status != "Done":
                self.tasks[task_id].status = "Backlog"

        for bug_id in sprint.bugs:
            if bug_id in self.bugs and self.bugs[bug_id].status != "Resolved":
                self.bugs[bug_id].status = "Open"

        self.current_sprint = None
        self._save_data()
        return sprint

    def get_backlog_report(self) -> Dict[str, Any]:
        """Generate backlog report with metrics"""
        total_stories = len([s for s in self.stories.values() if s.status == "Backlog"])
        total_bugs = len([b for b in self.bugs.values() if b.status == "Open"])
        total_points = sum(s.story_points for s in self.stories.values() if s.status == "Backlog")

        return {
            "total_stories": total_stories,
            "total_bugs": total_bugs,
            "total_points": total_points,
            "estimated_sprints": total_points / self._calculate_velocity() if total_points > 0 else 0,
            "critical_bugs": len([b for b in self.bugs.values()
                                if b.status == "Open" and b.severity == "Critical"])
        }

    def get_sprint_report(self, sprint_id: str) -> Dict[str, Any]:
        """Generate sprint report"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")

        sprint = self.sprints[sprint_id]

        return {
            "sprint_name": sprint.name,
            "goal": sprint.goal,
            "status": sprint.status.value,
            "velocity": sprint.velocity,
            "committed_points": sprint.committed_points,
            "completed_points": sprint.completed_points,
            "completion_percentage": (sprint.completed_points / sprint.committed_points * 100)
                                   if sprint.committed_points > 0 else 0,
            "stories_count": len(sprint.stories),
            "bugs_count": len(sprint.bugs),
            "burndown": sprint.daily_burndown
        }