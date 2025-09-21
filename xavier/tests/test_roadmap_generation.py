"""
Unit tests for Xavier Framework roadmap auto-generation
Tests the automatic roadmap creation during project setup
"""

import unittest
import tempfile
import shutil
import json
import os
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrum.scrum_manager import SCRUMManager


class TestRoadmapGeneration(unittest.TestCase):
    """Test automatic roadmap generation during project creation"""

    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.scrum = SCRUMManager(data_dir=self.test_dir)

    def tearDown(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir)

    def test_roadmap_creation(self):
        """Test that roadmaps can be created and saved"""
        # Create roadmap
        roadmap = self.scrum.create_roadmap(
            name="Test Project Roadmap",
            vision="Building an amazing test project"
        )

        # Verify roadmap properties
        self.assertIsNotNone(roadmap.id)
        self.assertTrue(roadmap.id.startswith("RM-"))
        self.assertEqual(roadmap.name, "Test Project Roadmap")
        self.assertEqual(roadmap.vision, "Building an amazing test project")

        # Verify roadmap is stored
        self.assertIn(roadmap.id, self.scrum.roadmaps)

        # Check that roadmap.json file was created
        roadmap_file = os.path.join(self.test_dir, "roadmaps.json")
        self.assertTrue(os.path.exists(roadmap_file))

        # Verify file contents
        with open(roadmap_file, 'r') as f:
            data = json.load(f)

        self.assertIn(roadmap.id, data)
        roadmap_data = data[roadmap.id]
        self.assertEqual(roadmap_data["name"], "Test Project Roadmap")
        self.assertEqual(roadmap_data["vision"], "Building an amazing test project")

    def test_milestone_addition_to_roadmap(self):
        """Test adding milestones to roadmap"""
        # Create roadmap
        roadmap = self.scrum.create_roadmap(
            name="Test Roadmap",
            vision="Test vision"
        )

        # Add milestone
        target_date = datetime.now()
        self.scrum.add_milestone_to_roadmap(
            roadmap_id=roadmap.id,
            milestone_name="Test Milestone",
            target_date=target_date,
            epics=[],
            success_criteria=["Criterion 1", "Criterion 2"]
        )

        # Verify milestone was added
        updated_roadmap = self.scrum.roadmaps[roadmap.id]
        self.assertEqual(len(updated_roadmap.milestones), 1)

        milestone = updated_roadmap.milestones[0]
        self.assertEqual(milestone["name"], "Test Milestone")
        self.assertEqual(milestone["target_date"], target_date.isoformat())
        self.assertEqual(milestone["success_criteria"], ["Criterion 1", "Criterion 2"])

    def test_multiple_roadmaps(self):
        """Test creating multiple roadmaps"""
        # Create first roadmap
        roadmap1 = self.scrum.create_roadmap(
            name="Roadmap 1",
            vision="Vision 1"
        )

        # Create second roadmap
        roadmap2 = self.scrum.create_roadmap(
            name="Roadmap 2",
            vision="Vision 2"
        )

        # Verify both exist and are different
        self.assertNotEqual(roadmap1.id, roadmap2.id)
        self.assertEqual(len(self.scrum.roadmaps), 2)
        self.assertIn(roadmap1.id, self.scrum.roadmaps)
        self.assertIn(roadmap2.id, self.scrum.roadmaps)


if __name__ == '__main__':
    unittest.main()