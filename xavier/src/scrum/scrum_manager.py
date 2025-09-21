"""
Xavier Framework - SCRUM Management System
Enterprise-grade SCRUM implementation with strict workflow control
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
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


# Serialization utilities for dataclass persistence
def datetime_to_str(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO format string"""
    return dt.isoformat() if dt else None


def str_to_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Convert ISO format string to datetime"""
    return datetime.fromisoformat(dt_str) if dt_str else None


def serialize_dataclass(obj: Any) -> Dict[str, Any]:
    """Convert dataclass instance to JSON-serializable dict"""
    data = asdict(obj)

    # Convert datetime fields to strings
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = datetime_to_str(value)
        elif isinstance(value, Enum):
            data[key] = value.value

    return data


def deserialize_to_dataclass(data: Dict[str, Any], dataclass_type: type) -> Any:
    """Convert dict to dataclass instance with proper type conversion"""
    # Convert datetime strings back to datetime objects
    datetime_fields = {
        'created_at', 'updated_at', 'resolved_at', 'start_date', 'end_date'
    }

    for field_name in datetime_fields:
        if field_name in data and data[field_name]:
            data[field_name] = str_to_datetime(data[field_name])

    # Handle SprintStatus enum for Sprint dataclass
    if dataclass_type == Sprint and 'status' in data:
        if isinstance(data['status'], str):
            try:
                data['status'] = SprintStatus(data['status'])
            except ValueError:
                # Keep as string if not a valid enum value
                pass

    return dataclass_type(**data)


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """
    Safely get attribute from either a dataclass instance or dictionary.
    This provides compatibility between the two data representations.
    """
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def safe_set_attr(obj: Any, attr: str, value: Any) -> None:
    """
    Safely set attribute on either a dataclass instance or dictionary.
    This provides compatibility between the two data representations.
    """
    if isinstance(obj, dict):
        obj[attr] = value
    else:
        setattr(obj, attr, value)


def get_sprint_status_value(sprint: Any) -> str:
    """
    Get sprint status value handling both SprintStatus enum and string.
    Returns a string value that can be compared consistently.
    """
    status = safe_get_attr(sprint, 'status')
    if isinstance(status, SprintStatus):
        return status.value
    elif isinstance(status, str):
        return status
    return "Planning"  # Default


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

        # Initialize data structure
        self._initialize_data_structure()

        # Load existing data
        self._load_data()

    def _initialize_data_structure(self):
        """Initialize data directory structure with empty JSON files if they don't exist"""
        data_files = ["stories", "tasks", "bugs", "sprints", "epics", "roadmaps"]

        for data_type in data_files:
            file_path = os.path.join(self.data_dir, f"{data_type}.json")
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w') as f:
                        json.dump({}, f, indent=2)
                    print(f"Initialized {data_type}.json")
                except Exception as e:
                    print(f"Warning: Could not initialize {data_type}.json: {e}")

    def _load_data(self):
        """Load existing SCRUM data from disk with proper deserialization"""
        data_type_map = {
            "stories": (self.stories, UserStory),
            "tasks": (self.tasks, Task),
            "bugs": (self.bugs, Bug),
            "sprints": (self.sprints, Sprint),
            "epics": (self.epics, Epic),
            "roadmaps": (self.roadmaps, Roadmap)
        }

        for data_type, (storage, dataclass_type) in data_type_map.items():
            file_path = os.path.join(self.data_dir, f"{data_type}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        # Convert dictionaries to dataclass instances
                        for key, value in data.items():
                            try:
                                storage[key] = deserialize_to_dataclass(value, dataclass_type)
                            except Exception as e:
                                print(f"Warning: Failed to deserialize {data_type} {key}: {e}")
                                # Fall back to dict for backward compatibility
                                storage[key] = value
                except Exception as e:
                    print(f"Error loading {data_type}: {e}")

    def _save_data(self):
        """Save SCRUM data to disk with proper serialization"""
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
            try:
                serializable_data = {}
                for key, obj in storage.items():
                    # Handle both dataclass instances and dicts (for backward compatibility)
                    if hasattr(obj, '__dataclass_fields__'):
                        # It's a dataclass instance
                        serializable_data[key] = serialize_dataclass(obj)
                    else:
                        # It's already a dict (backward compatibility)
                        serializable_data[key] = obj

                with open(file_path, 'w') as f:
                    json.dump(serializable_data, f, indent=2, default=str)
            except Exception as e:
                print(f"Error saving {data_type}: {e}")

    def _generate_unique_story_id(self) -> str:
        """Generate a unique story ID, regenerating if it already exists"""
        max_attempts = 100  # Prevent infinite loop
        attempts = 0

        while attempts < max_attempts:
            story_id = f"US-{uuid.uuid4().hex[:8].upper()}"
            if story_id not in self.stories:
                return story_id
            attempts += 1

        # Fallback if UUID collision persists (extremely unlikely)
        counter = 1
        while f"US-FALLBACK-{counter:03d}" in self.stories:
            counter += 1
        return f"US-FALLBACK-{counter:03d}"

    def create_story(self, title: str, as_a: str, i_want: str, so_that: str,
                    acceptance_criteria: List[str], priority: str = "Medium",
                    epic_id: Optional[str] = None) -> UserStory:
        """Create a user story following standard format"""
        # Generate unique story ID
        story_id = self._generate_unique_story_id()

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
        safe_set_attr(story, 'story_points', points)
        safe_set_attr(story, 'updated_at', datetime.now())

        # Update epic total if part of one
        epic_id = safe_get_attr(story, 'epic_id')
        if epic_id and epic_id in self.epics:
            self._update_epic_points(epic_id)

        self._save_data()
        return story

    def _update_epic_points(self, epic_id: str):
        """Update epic total points"""
        epic = self.epics[epic_id]
        total_points = 0
        completed_points = 0

        epic_stories = safe_get_attr(epic, 'stories', [])
        for story_id in epic_stories:
            if story_id in self.stories:
                story = self.stories[story_id]
                story_points = safe_get_attr(story, 'story_points', 0)
                total_points += story_points
                if safe_get_attr(story, 'status') == "Done":
                    completed_points += story_points

        safe_set_attr(epic, 'total_points', total_points)
        safe_set_attr(epic, 'completed_points', completed_points)

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
        completed_sprints = []
        for s in self.sprints.values():
            sprint_status = safe_get_attr(s, 'status')
            # Handle both SprintStatus enum and string values
            if isinstance(sprint_status, SprintStatus):
                if sprint_status == SprintStatus.COMPLETED:
                    completed_sprints.append(s)
            elif sprint_status == "Completed":
                completed_sprints.append(s)

        if not completed_sprints:
            return 20  # Default velocity

        # Average of last 3 sprints
        def get_end_date(sprint):
            end_date = safe_get_attr(sprint, 'end_date', datetime.now())
            if isinstance(end_date, str):
                return str_to_datetime(end_date) or datetime.now()
            return end_date

        recent_sprints = sorted(completed_sprints,
                              key=get_end_date,
                              reverse=True)[:3]

        total_points = sum(safe_get_attr(s, 'completed_points', 0) for s in recent_sprints)
        return int(total_points / len(recent_sprints))

    def plan_sprint(self, sprint_id: str) -> Tuple[List[str], List[str], List[str]]:
        """Auto-plan sprint based on priority and velocity"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")

        sprint = self.sprints[sprint_id]

        # Get all available items
        available_stories = [s for s in self.stories.values()
                           if safe_get_attr(s, 'status') == "Backlog"]
        available_tasks = [t for t in self.tasks.values()
                         if safe_get_attr(t, 'status') == "Backlog" and
                         safe_get_attr(t, 'story_id') not in safe_get_attr(sprint, 'stories', [])]
        available_bugs = [b for b in self.bugs.values()
                        if safe_get_attr(b, 'status') == "Open"]

        # Sort by priority
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

        available_stories.sort(key=lambda s: (
            priority_order.get(safe_get_attr(s, 'priority', 'Medium'), 3),
            -safe_get_attr(s, 'story_points', 0)
        ))
        available_bugs.sort(key=lambda b: (
            priority_order.get(safe_get_attr(b, 'priority', 'Medium'), 3),
            safe_get_attr(b, 'severity', 'Low')
        ))
        available_tasks.sort(key=lambda t: priority_order.get(safe_get_attr(t, 'priority', 'Medium'), 3))

        # Add items to sprint up to velocity
        total_points = 0
        selected_stories = []
        selected_tasks = []
        selected_bugs = []
        sprint_velocity = safe_get_attr(sprint, 'velocity', 20)

        # First add critical bugs
        for bug in available_bugs:
            bug_severity = safe_get_attr(bug, 'severity', 'Low')
            bug_points = safe_get_attr(bug, 'story_points', 0)
            bug_id = safe_get_attr(bug, 'id')

            if bug_severity == "Critical" and total_points + bug_points <= sprint_velocity:
                selected_bugs.append(bug_id)
                total_points += bug_points

        # Then add stories
        for story in available_stories:
            story_points = safe_get_attr(story, 'story_points', 0)
            story_id = safe_get_attr(story, 'id')

            if story_points > 0 and total_points + story_points <= sprint_velocity:
                selected_stories.append(story_id)
                total_points += story_points

                # Add related tasks
                story_tasks = safe_get_attr(story, 'tasks', [])
                for task_id in story_tasks:
                    if task_id in self.tasks:
                        selected_tasks.append(task_id)

        # Add remaining bugs if capacity allows
        for bug in available_bugs:
            bug_id = safe_get_attr(bug, 'id')
            bug_points = safe_get_attr(bug, 'story_points', 0)

            if bug_id not in selected_bugs and total_points + bug_points <= sprint_velocity:
                selected_bugs.append(bug_id)
                total_points += bug_points

        # Update sprint
        safe_set_attr(sprint, 'stories', selected_stories)
        safe_set_attr(sprint, 'tasks', selected_tasks)
        safe_set_attr(sprint, 'bugs', selected_bugs)
        safe_set_attr(sprint, 'committed_points', total_points)

        self._save_data()
        return selected_stories, selected_tasks, selected_bugs

    def start_sprint(self, sprint_id: str) -> bool:
        """Start a sprint - only one can be active"""
        if self.current_sprint:
            raise ValueError(f"Sprint {self.current_sprint} is already active")

        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")

        sprint = self.sprints[sprint_id]

        if safe_get_attr(sprint, 'committed_points', 0) == 0:
            raise ValueError("Sprint has no committed work")

        safe_set_attr(sprint, 'status', SprintStatus.ACTIVE)
        safe_set_attr(sprint, 'start_date', datetime.now())
        self.current_sprint = sprint_id

        # Update status of sprint items
        sprint_stories = safe_get_attr(sprint, 'stories', [])
        for story_id in sprint_stories:
            if story_id in self.stories:
                safe_set_attr(self.stories[story_id], 'status', "In Progress")

        sprint_tasks = safe_get_attr(sprint, 'tasks', [])
        for task_id in sprint_tasks:
            if task_id in self.tasks:
                safe_set_attr(self.tasks[task_id], 'status', "In Progress")

        sprint_bugs = safe_get_attr(sprint, 'bugs', [])
        for bug_id in sprint_bugs:
            if bug_id in self.bugs:
                safe_set_attr(self.bugs[bug_id], 'status', "In Progress")

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

        safe_set_attr(task, 'completion_percentage', completion_percentage)
        safe_set_attr(task, 'test_coverage', test_coverage)

        if completion_percentage == 100:
            safe_set_attr(task, 'status', "Done")
            story_id = safe_get_attr(task, 'story_id')
            if story_id:
                self._update_story_progress(story_id)

        safe_set_attr(task, 'updated_at', datetime.now())
        self._save_data()
        return task

    def _update_story_progress(self, story_id: str):
        """Update story progress based on task completion"""
        if story_id not in self.stories:
            return

        story = self.stories[story_id]
        story_tasks = safe_get_attr(story, 'tasks', [])
        all_tasks_done = all(
            safe_get_attr(self.tasks[task_id], 'status') == "Done"
            for task_id in story_tasks
            if task_id in self.tasks
        )

        if all_tasks_done:
            safe_set_attr(story, 'status', "Done")
            safe_set_attr(story, 'updated_at', datetime.now())

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

        sprint_stories = safe_get_attr(sprint, 'stories', [])
        for story_id in sprint_stories:
            if story_id in self.stories:
                story = self.stories[story_id]
                if safe_get_attr(story, 'status') != "Done":
                    remaining_points += safe_get_attr(story, 'story_points', 0)

        sprint_bugs = safe_get_attr(sprint, 'bugs', [])
        for bug_id in sprint_bugs:
            if bug_id in self.bugs:
                bug = self.bugs[bug_id]
                if safe_get_attr(bug, 'status') != "Resolved":
                    remaining_points += safe_get_attr(bug, 'story_points', 0)

        # Update daily burndown
        today = datetime.now().date().isoformat()
        burndown = safe_get_attr(sprint, 'daily_burndown', {})
        burndown[today] = remaining_points
        safe_set_attr(sprint, 'daily_burndown', burndown)

        committed = safe_get_attr(sprint, 'committed_points', 0)
        safe_set_attr(sprint, 'completed_points', committed - remaining_points)

    def complete_sprint(self, sprint_id: str, retrospective_notes: str) -> Sprint:
        """Complete a sprint with retrospective"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")

        sprint = self.sprints[sprint_id]

        # Check sprint status - handle both enum and string
        sprint_status = safe_get_attr(sprint, 'status')
        is_active = False
        if isinstance(sprint_status, SprintStatus):
            is_active = sprint_status == SprintStatus.ACTIVE
        else:
            is_active = sprint_status == "Active"

        if not is_active:
            raise ValueError("Can only complete active sprints")

        safe_set_attr(sprint, 'status', SprintStatus.COMPLETED)
        safe_set_attr(sprint, 'end_date', datetime.now())
        safe_set_attr(sprint, 'retrospective_notes', retrospective_notes)

        # Move incomplete items back to backlog
        sprint_stories = safe_get_attr(sprint, 'stories', [])
        for story_id in sprint_stories:
            if story_id in self.stories:
                story = self.stories[story_id]
                if safe_get_attr(story, 'status') != "Done":
                    safe_set_attr(story, 'status', "Backlog")

        sprint_tasks = safe_get_attr(sprint, 'tasks', [])
        for task_id in sprint_tasks:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if safe_get_attr(task, 'status') != "Done":
                    safe_set_attr(task, 'status', "Backlog")

        sprint_bugs = safe_get_attr(sprint, 'bugs', [])
        for bug_id in sprint_bugs:
            if bug_id in self.bugs:
                bug = self.bugs[bug_id]
                if safe_get_attr(bug, 'status') != "Resolved":
                    safe_set_attr(bug, 'status', "Open")

        self.current_sprint = None
        self._save_data()
        return sprint

    def get_unestimated_stories(self) -> List[UserStory]:
        """Get all backlog stories that haven't been estimated"""
        return [
            s for s in self.stories.values()
            if safe_get_attr(s, 'status') == "Backlog" and safe_get_attr(s, 'story_points', 0) == 0
        ]

    def get_backlog_report(self) -> Dict[str, Any]:
        """Generate backlog report with metrics"""
        total_stories = len([s for s in self.stories.values() if safe_get_attr(s, 'status') == "Backlog"])
        total_bugs = len([b for b in self.bugs.values() if safe_get_attr(b, 'status') == "Open"])
        total_points = sum(
            safe_get_attr(s, 'story_points', 0)
            for s in self.stories.values()
            if safe_get_attr(s, 'status') == "Backlog"
        )
        unestimated_count = len(self.get_unestimated_stories())

        return {
            "total_stories": total_stories,
            "total_bugs": total_bugs,
            "total_points": total_points,
            "unestimated_stories": unestimated_count,
            "estimated_sprints": total_points / self._calculate_velocity() if total_points > 0 else 0,
            "critical_bugs": len([b for b in self.bugs.values()
                                if safe_get_attr(b, 'status') == "Open" and
                                safe_get_attr(b, 'severity') == "Critical"])
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