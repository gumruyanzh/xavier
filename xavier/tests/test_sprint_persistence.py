"""
Unit tests for Xavier Framework sprint persistence
Tests all sprint-related dictionary/dataclass compatibility
"""

import unittest
import tempfile
import shutil
import os
from datetime import datetime, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrum.scrum_manager import (
    SCRUMManager, Sprint, SprintStatus,
    safe_get_attr, safe_set_attr, get_sprint_status_value
)


class TestSprintMethods(unittest.TestCase):
    """Test sprint methods with dict/dataclass compatibility"""

    def setUp(self):
        """Create temporary directory for test data"""
        self.test_dir = tempfile.mkdtemp(prefix="xavier_sprint_test_")
        self.scrum = SCRUMManager(data_dir=self.test_dir)

    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir)

    def test_create_and_plan_sprint(self):
        """Test creating and planning a sprint"""
        # Create some stories and tasks first
        story1 = self.scrum.create_story(
            title="Login Feature",
            as_a="user",
            i_want="to login",
            so_that="I can access my account",
            acceptance_criteria=["Login works"],
            priority="High"
        )
        self.scrum.estimate_story(story1.id, 8)

        story2 = self.scrum.create_story(
            title="Dashboard",
            as_a="user",
            i_want="to see dashboard",
            so_that="I can view my data",
            acceptance_criteria=["Dashboard displays"],
            priority="Medium"
        )
        self.scrum.estimate_story(story2.id, 5)

        # Create a bug
        bug = self.scrum.create_bug(
            title="Critical Login Bug",
            description="Login crashes",
            steps_to_reproduce=["Try to login"],
            expected_behavior="Should login",
            actual_behavior="Crashes",
            severity="Critical",
            priority="High"
        )

        # Create sprint
        sprint = self.scrum.create_sprint(
            name="Sprint 1",
            goal="Deliver login and dashboard",
            duration_days=14
        )

        # Verify sprint created
        self.assertIsNotNone(sprint)
        sprint_id = safe_get_attr(sprint, 'id')
        self.assertIsNotNone(sprint_id)
        self.assertEqual(safe_get_attr(sprint, 'name'), "Sprint 1")

        # Plan sprint
        stories, tasks, bugs = self.scrum.plan_sprint(sprint_id)

        # Verify planning worked
        self.assertTrue(len(stories) > 0 or len(bugs) > 0)
        self.assertGreater(safe_get_attr(sprint, 'committed_points', 0), 0)

        # Save and reload
        self.scrum._save_data()
        scrum2 = SCRUMManager(data_dir=self.test_dir)

        # Verify sprint loaded correctly
        self.assertIn(sprint_id, scrum2.sprints)
        loaded_sprint = scrum2.sprints[sprint_id]
        self.assertEqual(safe_get_attr(loaded_sprint, 'name'), "Sprint 1")
        self.assertEqual(safe_get_attr(loaded_sprint, 'goal'), "Deliver login and dashboard")

    def test_start_sprint(self):
        """Test starting a sprint"""
        # Create and plan sprint
        story = self.scrum.create_story(
            title="Feature",
            as_a="user",
            i_want="feature",
            so_that="benefit",
            acceptance_criteria=["Works"],
            priority="High"
        )
        self.scrum.estimate_story(story.id, 5)

        sprint = self.scrum.create_sprint("Sprint 2", "Test sprint")
        sprint_id = safe_get_attr(sprint, 'id')
        self.scrum.plan_sprint(sprint_id)

        # Start sprint
        result = self.scrum.start_sprint(sprint_id)
        self.assertTrue(result)

        # Verify status updated
        sprint_status = get_sprint_status_value(sprint)
        self.assertEqual(sprint_status, "Active")

        # Verify story status updated
        story = self.scrum.stories[story.id]
        self.assertEqual(safe_get_attr(story, 'status'), "In Progress")

        # Save and reload
        self.scrum._save_data()
        scrum2 = SCRUMManager(data_dir=self.test_dir)

        # Verify sprint still active after reload
        loaded_sprint = scrum2.sprints[sprint_id]
        loaded_status = get_sprint_status_value(loaded_sprint)
        self.assertEqual(loaded_status, "Active")

    def test_complete_sprint(self):
        """Test completing a sprint"""
        # Create, plan, and start sprint
        story = self.scrum.create_story(
            title="Feature",
            as_a="user",
            i_want="feature",
            so_that="benefit",
            acceptance_criteria=["Works"],
            priority="High"
        )
        self.scrum.estimate_story(story.id, 5)

        sprint = self.scrum.create_sprint("Sprint 3", "Complete test")
        sprint_id = safe_get_attr(sprint, 'id')
        self.scrum.plan_sprint(sprint_id)
        self.scrum.start_sprint(sprint_id)

        # Complete sprint
        completed_sprint = self.scrum.complete_sprint(
            sprint_id,
            "Sprint went well"
        )

        # Verify status
        status = get_sprint_status_value(completed_sprint)
        self.assertEqual(status, "Completed")
        self.assertEqual(
            safe_get_attr(completed_sprint, 'retrospective_notes'),
            "Sprint went well"
        )

        # Verify incomplete story moved back to backlog
        story = self.scrum.stories[story.id]
        self.assertEqual(safe_get_attr(story, 'status'), "Backlog")

    def test_velocity_calculation(self):
        """Test velocity calculation with mixed data"""
        # Create completed sprint with old format (dict)
        old_sprint = {
            "id": "SP-OLD",
            "name": "Old Sprint",
            "goal": "Test",
            "start_date": (datetime.now() - timedelta(days=14)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "velocity": 20,
            "committed_points": 20,
            "completed_points": 18,
            "status": "Completed",
            "stories": [],
            "tasks": [],
            "bugs": [],
            "daily_burndown": {},
            "retrospective_notes": "Good sprint"
        }
        self.scrum.sprints["SP-OLD"] = old_sprint

        # Create completed sprint with new format (dataclass)
        new_sprint = Sprint(
            id="SP-NEW",
            name="New Sprint",
            goal="Test 2",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            velocity=20,
            committed_points=20,
            completed_points=15,
            status=SprintStatus.COMPLETED
        )
        self.scrum.sprints["SP-NEW"] = new_sprint

        # Calculate velocity - should handle both formats
        velocity = self.scrum._calculate_velocity()
        self.assertIsInstance(velocity, int)
        self.assertGreater(velocity, 0)

    def test_sprint_burndown_update(self):
        """Test sprint burndown calculation"""
        # Create sprint with stories
        story = self.scrum.create_story(
            title="Feature",
            as_a="user",
            i_want="feature",
            so_that="benefit",
            acceptance_criteria=["Works"],
            priority="High"
        )
        self.scrum.estimate_story(story.id, 8)

        sprint = self.scrum.create_sprint("Sprint 4", "Burndown test")
        sprint_id = safe_get_attr(sprint, 'id')
        self.scrum.plan_sprint(sprint_id)
        self.scrum.start_sprint(sprint_id)

        # Update burndown
        self.scrum._update_sprint_burndown()

        # Verify burndown updated
        sprint = self.scrum.sprints[sprint_id]
        burndown = safe_get_attr(sprint, 'daily_burndown', {})
        today = datetime.now().date().isoformat()
        self.assertIn(today, burndown)
        self.assertEqual(burndown[today], 8)  # Story not done yet

        # Complete story
        safe_set_attr(self.scrum.stories[story.id], 'status', 'Done')
        self.scrum._update_sprint_burndown()

        # Verify burndown reflects completion
        sprint = self.scrum.sprints[sprint_id]
        burndown = safe_get_attr(sprint, 'daily_burndown', {})
        self.assertEqual(burndown[today], 0)  # Story done

    def test_mixed_format_sprints(self):
        """Test handling sprints in both dict and dataclass formats"""
        # Create dict format sprint
        dict_sprint = {
            "id": "SP-DICT",
            "name": "Dict Sprint",
            "goal": "Test dict",
            "velocity": 20,
            "committed_points": 0,
            "status": "Planning",
            "stories": [],
            "tasks": [],
            "bugs": []
        }
        self.scrum.sprints["SP-DICT"] = dict_sprint

        # Create dataclass sprint
        dataclass_sprint = Sprint(
            id="SP-CLASS",
            name="Class Sprint",
            goal="Test class",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=14),
            velocity=20,
            committed_points=0
        )
        self.scrum.sprints["SP-CLASS"] = dataclass_sprint

        # Both should be accessible
        self.assertEqual(
            safe_get_attr(self.scrum.sprints["SP-DICT"], 'name'),
            "Dict Sprint"
        )
        self.assertEqual(
            safe_get_attr(self.scrum.sprints["SP-CLASS"], 'name'),
            "Class Sprint"
        )

        # Both should work with get_sprint_status_value
        self.assertEqual(get_sprint_status_value(dict_sprint), "Planning")
        self.assertEqual(get_sprint_status_value(dataclass_sprint), "Planning")

        # Save and reload
        self.scrum._save_data()
        scrum2 = SCRUMManager(data_dir=self.test_dir)

        # Both should still work
        self.assertIn("SP-DICT", scrum2.sprints)
        self.assertIn("SP-CLASS", scrum2.sprints)


if __name__ == '__main__':
    unittest.main()