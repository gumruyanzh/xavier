"""
Xavier Framework Core Engine
Enterprise-grade SCRUM development framework with strict execution control
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging


class TaskStatus(Enum):
    BACKLOG = "Backlog"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    REVIEW = "Review"
    DONE = "Done"


class Priority(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ItemType(Enum):
    STORY = "Story"
    TASK = "Task"
    BUG = "Bug"


@dataclass
class TestResult:
    """Test execution result with strict validation"""
    passed: bool
    coverage: float
    test_count: int
    failed_tests: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)

    def is_production_ready(self) -> bool:
        """Check if tests meet production standards"""
        return self.passed and self.coverage >= 100.0 and len(self.failed_tests) == 0


@dataclass
class WorkItem:
    """Base work item for SCRUM management"""
    id: str
    type: ItemType
    title: str
    description: str
    priority: Priority
    story_points: int
    status: TaskStatus
    acceptance_criteria: List[str]
    test_results: Optional[TestResult] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None
    sprint_id: Optional[str] = None
    parent_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    def is_complete(self) -> bool:
        """Strict completion check"""
        if self.status != TaskStatus.DONE:
            return False
        if not self.test_results:
            return False
        return self.test_results.is_production_ready()

    def can_start(self, completed_items: List[str]) -> bool:
        """Check if all dependencies are complete"""
        return all(dep in completed_items for dep in self.dependencies)


class InjectionContainer:
    """Inversion of Control container for dependency management"""

    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(self, interface: Type, implementation: Any, singleton: bool = True):
        """Register a service with the container"""
        if singleton:
            self._singletons[interface] = implementation
        else:
            self._services[interface] = implementation

    def resolve(self, interface: Type) -> Any:
        """Resolve a service from the container"""
        if interface in self._singletons:
            return self._singletons[interface]
        if interface in self._services:
            return self._services[interface]()
        raise ValueError(f"Service {interface} not registered")


class IValidator(ABC):
    """Interface for code validators"""

    @abstractmethod
    def validate(self, code: str, file_path: str) -> tuple[bool, List[str]]:
        """Validate code and return result with messages"""
        pass


class CleanCodeValidator(IValidator):
    """Validates code against Clean Code principles"""

    def validate(self, code: str, file_path: str) -> tuple[bool, List[str]]:
        """Check for Clean Code violations"""
        violations = []
        lines = code.split('\n')

        # Check function length
        function_lines = 0
        in_function = False
        for line in lines:
            if 'def ' in line or 'function ' in line:
                in_function = True
                function_lines = 0
            elif in_function:
                function_lines += 1
                if function_lines > 20:
                    violations.append("Function exceeds 20 lines (Clean Code principle)")
                    in_function = False

        # Check line length
        for i, line in enumerate(lines):
            if len(line) > 120:
                violations.append(f"Line {i+1} exceeds 120 characters")

        # Check for meaningful names
        import re
        single_letter_vars = re.findall(r'\b[a-z]\b(?!\w)', code)
        if len(single_letter_vars) > 3:
            violations.append("Too many single-letter variable names")

        return len(violations) == 0, violations


class ITestRunner(ABC):
    """Interface for test execution"""

    @abstractmethod
    def run_tests(self, test_path: str, coverage_required: float) -> TestResult:
        """Run tests and return results"""
        pass


class XavierEngine:
    """Core engine for Xavier Framework with strict execution control"""

    def __init__(self, config_path: str = "xavier.config.json"):
        self.config = self._load_config(config_path)
        self.container = InjectionContainer()
        self.work_items: Dict[str, WorkItem] = {}
        self.sprints: Dict[str, Dict] = {}
        self.current_sprint: Optional[str] = None
        self.completed_items: List[str] = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("Xavier")

        # Register services
        self._register_services()

    def _load_config(self, config_path: str) -> Dict:
        """Load Xavier configuration"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def _register_services(self):
        """Register all services with IoC container"""
        self.container.register(IValidator, CleanCodeValidator())

    def create_work_item(self, item_type: ItemType, title: str, description: str,
                        priority: Priority, story_points: int,
                        acceptance_criteria: List[str], parent_id: Optional[str] = None,
                        dependencies: List[str] = None) -> WorkItem:
        """Create a new work item with strict validation"""
        item_id = f"{item_type.value.upper()}_{datetime.now().timestamp()}"

        work_item = WorkItem(
            id=item_id,
            type=item_type,
            title=title,
            description=description,
            priority=priority,
            story_points=story_points,
            status=TaskStatus.BACKLOG,
            acceptance_criteria=acceptance_criteria,
            parent_id=parent_id,
            dependencies=dependencies or []
        )

        self.work_items[item_id] = work_item
        self.logger.info(f"Created {item_type.value}: {title} with ID: {item_id}")
        return work_item

    def execute_work_item(self, item_id: str) -> bool:
        """Execute a work item with strict sequential control"""
        if item_id not in self.work_items:
            raise ValueError(f"Work item {item_id} not found")

        work_item = self.work_items[item_id]

        # Check dependencies
        if not work_item.can_start(self.completed_items):
            incomplete_deps = [d for d in work_item.dependencies if d not in self.completed_items]
            self.logger.error(f"Cannot start {item_id}. Incomplete dependencies: {incomplete_deps}")
            return False

        # Strict execution control - no parallel execution
        in_progress_items = [w for w in self.work_items.values()
                           if w.status == TaskStatus.IN_PROGRESS]
        if in_progress_items:
            self.logger.error(f"Cannot start {item_id}. Item {in_progress_items[0].id} is still in progress")
            return False

        work_item.status = TaskStatus.IN_PROGRESS
        self.logger.info(f"Starting execution of {item_id}: {work_item.title}")

        return True

    def complete_work_item(self, item_id: str, test_result: TestResult) -> bool:
        """Mark work item as complete with strict validation"""
        if item_id not in self.work_items:
            raise ValueError(f"Work item {item_id} not found")

        work_item = self.work_items[item_id]

        # Validate test results
        if not test_result.is_production_ready():
            self.logger.error(f"Cannot complete {item_id}. Tests not production ready: "
                            f"Coverage: {test_result.coverage}%, Failed: {test_result.failed_tests}")
            work_item.status = TaskStatus.TESTING
            return False

        # Validate Clean Code standards
        validator = self.container.resolve(IValidator)
        # Note: In real implementation, we'd validate actual code files

        work_item.test_results = test_result
        work_item.status = TaskStatus.DONE
        work_item.updated_at = datetime.now()
        self.completed_items.append(item_id)

        self.logger.info(f"Completed {item_id} with 100% test coverage")
        return True

    def create_sprint(self, sprint_name: str, duration_days: int = 14) -> str:
        """Create a new sprint with automatic work item selection"""
        sprint_id = f"SPRINT_{datetime.now().timestamp()}"

        # Calculate sprint capacity
        velocity = self.config.get('settings', {}).get('sprint_velocity', 20)

        # Select work items by priority
        available_items = [w for w in self.work_items.values()
                         if w.status == TaskStatus.BACKLOG and not w.sprint_id]

        # Sort by priority and dependencies
        sorted_items = sorted(available_items,
                            key=lambda x: (x.priority.value, -x.story_points))

        sprint_items = []
        total_points = 0

        for item in sorted_items:
            if total_points + item.story_points <= velocity:
                sprint_items.append(item.id)
                item.sprint_id = sprint_id
                item.status = TaskStatus.READY
                total_points += item.story_points

        self.sprints[sprint_id] = {
            'id': sprint_id,
            'name': sprint_name,
            'duration': duration_days,
            'start_date': None,
            'end_date': None,
            'items': sprint_items,
            'total_points': total_points,
            'completed_points': 0,
            'status': 'CREATED'
        }

        self.logger.info(f"Created sprint {sprint_name} with {len(sprint_items)} items "
                        f"totaling {total_points} story points")
        return sprint_id

    def start_sprint(self, sprint_id: str) -> bool:
        """Start sprint execution with strict sequential processing"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")

        sprint = self.sprints[sprint_id]

        if self.current_sprint:
            self.logger.error(f"Cannot start {sprint_id}. Sprint {self.current_sprint} is active")
            return False

        sprint['start_date'] = datetime.now()
        sprint['status'] = 'ACTIVE'
        self.current_sprint = sprint_id

        self.logger.info(f"Started sprint {sprint['name']}")

        # Execute items sequentially
        for item_id in sprint['items']:
            self._execute_sprint_item(item_id)

        return True

    def _execute_sprint_item(self, item_id: str):
        """Execute a single sprint item with full test-first approach"""
        work_item = self.work_items[item_id]

        self.logger.info(f"Processing {item_id}: {work_item.title}")

        # This would trigger the appropriate sub-agent based on item type
        # and enforce test-first development
        pass


class XavierCLI:
    """Command-line interface for Xavier Framework"""

    def __init__(self):
        self.engine = XavierEngine()

    def execute_command(self, command: str, args: Dict[str, Any]):
        """Execute Xavier command"""
        commands = {
            'create-story': self._create_story,
            'create-task': self._create_task,
            'create-bug': self._create_bug,
            'create-roadmap': self._create_roadmap,
            'create-project': self._create_project,
            'learn-project': self._learn_project,
            'create-sprint': self._create_sprint,
            'start-sprint': self._start_sprint
        }

        if command in commands:
            return commands[command](args)
        else:
            raise ValueError(f"Unknown command: {command}")

    def _create_story(self, args: Dict[str, Any]):
        """Create a user story"""
        return self.engine.create_work_item(
            ItemType.STORY,
            args['title'],
            args['description'],
            Priority[args.get('priority', 'MEDIUM').upper()],
            args.get('points', 5),
            args.get('acceptance_criteria', [])
        )

    def _create_task(self, args: Dict[str, Any]):
        """Create a task"""
        return self.engine.create_work_item(
            ItemType.TASK,
            args['title'],
            args['description'],
            Priority[args.get('priority', 'MEDIUM').upper()],
            args.get('points', 3),
            args.get('acceptance_criteria', []),
            parent_id=args.get('story_id'),
            dependencies=args.get('dependencies', [])
        )

    def _create_bug(self, args: Dict[str, Any]):
        """Create a bug"""
        return self.engine.create_work_item(
            ItemType.BUG,
            args['title'],
            args['description'],
            Priority[args.get('priority', 'HIGH').upper()],
            args.get('points', 2),
            args.get('acceptance_criteria', [])
        )

    def _create_roadmap(self, args: Dict[str, Any]):
        """Create project roadmap"""
        # Implementation for roadmap creation
        pass

    def _create_project(self, args: Dict[str, Any]):
        """Initialize new project"""
        # Implementation for project creation
        pass

    def _learn_project(self, args: Dict[str, Any]):
        """Learn existing project structure"""
        # Implementation for project learning
        pass

    def _create_sprint(self, args: Dict[str, Any]):
        """Create a new sprint"""
        return self.engine.create_sprint(
            args['name'],
            args.get('duration', 14)
        )

    def _start_sprint(self, args: Dict[str, Any]):
        """Start sprint execution"""
        return self.engine.start_sprint(args['sprint_id'])


if __name__ == "__main__":
    # Initialize Xavier
    xavier = XavierCLI()
    print("Xavier Framework initialized successfully")