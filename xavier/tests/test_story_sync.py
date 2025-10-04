"""
Tests for Jira Story Synchronization
Tests bi-directional sync between Jira and Xavier
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from datetime import datetime

from xavier.src.integrations.jira.story_sync import (
    StorySyncManager,
    StorySyncError,
    get_story_sync_manager
)
from xavier.src.integrations.jira.jira_client import JiraClient, JiraAPIError
from xavier.src.integrations.jira.field_mapper import FieldMapper


# Simple test story class
class MockStory:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestStorySyncManagerInitialization:
    """Test sync manager initialization"""

    def test_init_with_defaults(self):
        """Test initialization with default settings"""
        mock_client = Mock(spec=JiraClient)

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager'):
            manager = StorySyncManager(jira_client=mock_client)

            assert manager.jira_client == mock_client
            assert isinstance(manager.field_mapper, FieldMapper)
            assert manager.sync_log == []

    def test_init_with_custom_mappings(self):
        """Test initialization with custom field mappings"""
        mock_client = Mock(spec=JiraClient)
        custom_mappings = {'customfield_10001': 'epic_link'}

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager'):
            manager = StorySyncManager(
                jira_client=mock_client,
                custom_field_mappings=custom_mappings
            )

            assert manager.field_mapper.custom_mappings == custom_mappings

    def test_singleton_pattern(self):
        """Test singleton pattern"""
        mock_client = Mock(spec=JiraClient)

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager'):
            manager1 = get_story_sync_manager(mock_client)
            manager2 = get_story_sync_manager(mock_client)

            assert manager1 is manager2


class TestJiraToXavierSync:
    """Test Jira to Xavier synchronization"""

    def test_sync_new_issue_to_xavier(self):
        """Test syncing new Jira issue to Xavier story"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        # Mock Jira issue
        jira_issue = {
            'key': 'PROJ-123',
            'id': '10001',
            'fields': {
                'summary': 'Test Story',
                'description': 'Test description',
                'status': {'name': 'To Do'},
                'priority': {'name': 'High'}
            }
        }

        # Mock Xavier story
        mock_story = MockStory(id='US-ABC123', title='Test Story', jira_key='PROJ-123')

        mock_client.get_issue.return_value = jira_issue
        mock_scrum.create_story.return_value = mock_story
        mock_scrum.list_stories.return_value = []

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)
            result = manager.sync_jira_to_xavier('PROJ-123')

            assert result['id'] == 'US-ABC123'
            assert result['jira_key'] == 'PROJ-123'
            mock_client.get_issue.assert_called_once_with('PROJ-123')
            mock_scrum.create_story.assert_called_once()

    def test_sync_existing_issue_updates_story(self):
        """Test syncing existing Jira issue updates Xavier story"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        # Mock Jira issue
        jira_issue = {
            'key': 'PROJ-123',
            'id': '10001',
            'fields': {
                'summary': 'Updated Story',
                'description': 'Updated description',
                'status': {'name': 'In Progress'},
                'priority': {'name': 'High'}
            }
        }

        # Mock existing Xavier story
        mock_story = MockStory(id='US-ABC123', jira_key='PROJ-123', title='Old Title')

        mock_client.get_issue.return_value = jira_issue
        mock_scrum.list_stories.return_value = [mock_story]
        mock_scrum.get_story.return_value = mock_story

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)
            result = manager.sync_jira_to_xavier('PROJ-123')

            assert result['id'] == 'US-ABC123'
            mock_scrum.save_story.assert_called_once()
            assert mock_story.title == 'Updated Story'

    def test_sync_jira_issue_not_found(self):
        """Test syncing non-existent Jira issue"""
        mock_client = Mock(spec=JiraClient)

        mock_client.get_issue.return_value = None

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager'):
            manager = StorySyncManager(jira_client=mock_client)

            with pytest.raises(StorySyncError, match="not found"):
                manager.sync_jira_to_xavier('PROJ-999')

    def test_sync_jira_api_error(self):
        """Test handling Jira API errors"""
        mock_client = Mock(spec=JiraClient)

        mock_client.get_issue.side_effect = JiraAPIError("API error")

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager'):
            manager = StorySyncManager(jira_client=mock_client)

            with pytest.raises(StorySyncError, match="Jira API error"):
                manager.sync_jira_to_xavier('PROJ-123')


class TestXavierToJiraSync:
    """Test Xavier to Jira synchronization"""

    def test_sync_story_to_existing_jira_issue(self):
        """Test syncing Xavier story to existing Jira issue"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        # Mock Xavier story
        mock_story = MockStory(id='US-ABC123', jira_key='PROJ-123', title='Updated Title', priority='High')

        mock_scrum.get_story.return_value = mock_story
        mock_client.update_issue.return_value = True

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)
            result = manager.sync_xavier_to_jira('US-ABC123')

            assert result['key'] == 'PROJ-123'
            mock_client.update_issue.assert_called_once()

    def test_sync_story_without_jira_key_raises_error(self):
        """Test syncing story without Jira key raises NotImplementedError"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        # Mock Xavier story without Jira key
        mock_story = MockStory(id='US-ABC123', jira_key=None, title='New Story', priority='High')

        mock_scrum.get_story.return_value = mock_story

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)

            with pytest.raises(StorySyncError, match="not yet implemented"):
                manager.sync_xavier_to_jira('US-ABC123')

    def test_sync_nonexistent_story(self):
        """Test syncing non-existent Xavier story"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        mock_scrum.get_story.return_value = None

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)

            with pytest.raises(StorySyncError, match="not found"):
                manager.sync_xavier_to_jira('US-999')

    def test_sync_jira_update_fails(self):
        """Test handling failed Jira update"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        mock_story = MockStory(id='US-ABC123', jira_key='PROJ-123')

        mock_scrum.get_story.return_value = mock_story
        mock_client.update_issue.return_value = False

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)

            with pytest.raises(StorySyncError, match="Failed to update"):
                manager.sync_xavier_to_jira('US-ABC123')


class TestBidirectionalSync:
    """Test bi-directional synchronization"""

    def test_sync_both_directions(self):
        """Test syncing in both directions"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        # Mock Jira issue
        jira_issue = {
            'key': 'PROJ-123',
            'id': '10001',
            'fields': {
                'summary': 'Story',
                'status': {'name': 'In Progress'},
                'priority': {'name': 'High'}
            }
        }

        # Mock Xavier story
        mock_story = MockStory(id='US-ABC123', jira_key='PROJ-123', title='Story')

        mock_client.get_issue.return_value = jira_issue
        mock_client.update_issue.return_value = True
        mock_scrum.get_story.return_value = mock_story
        mock_scrum.list_stories.return_value = [mock_story]

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)
            result = manager.sync_story_metadata(
                story_id='US-ABC123',
                jira_issue_key='PROJ-123',
                direction='both'
            )

            assert 'xavier_story' in result
            assert 'jira_issue' in result
            assert result['story_id'] == 'US-ABC123'
            assert result['jira_key'] == 'PROJ-123'

    def test_sync_jira_to_xavier_only(self):
        """Test syncing Jira to Xavier only"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        jira_issue = {
            'key': 'PROJ-123',
            'fields': {'summary': 'Story', 'status': {'name': 'To Do'}}
        }

        mock_story = MockStory(id='US-ABC123')

        mock_client.get_issue.return_value = jira_issue
        mock_scrum.create_story.return_value = mock_story
        mock_scrum.list_stories.return_value = []

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)
            result = manager.sync_story_metadata(
                story_id='US-ABC123',
                jira_issue_key='PROJ-123',
                direction='jira_to_xavier'
            )

            assert 'xavier_story' in result
            assert 'jira_issue' not in result


class TestSyncLogging:
    """Test synchronization logging"""

    def test_sync_operations_logged(self):
        """Test that sync operations are logged"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        jira_issue = {
            'key': 'PROJ-123',
            'fields': {'summary': 'Story', 'status': {'name': 'To Do'}}
        }

        mock_story = MockStory(id='US-ABC123')

        mock_client.get_issue.return_value = jira_issue
        mock_scrum.create_story.return_value = mock_story
        mock_scrum.list_stories.return_value = []

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)
            manager.sync_jira_to_xavier('PROJ-123')

            log = manager.get_sync_log()

            assert len(log) == 1
            assert log[0]['direction'] == 'jira_to_xavier'
            assert log[0]['action'] == 'create'
            assert log[0]['source_id'] == 'PROJ-123'
            assert log[0]['target_id'] == 'US-ABC123'


class TestStoryFieldUpdates:
    """Test story field updates during sync"""

    def test_update_story_points(self):
        """Test updating story points from Jira"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        jira_issue = {
            'key': 'PROJ-123',
            'fields': {
                'summary': 'Story',
                'customfield_10016': 8,
                'status': {'name': 'To Do'}
            }
        }

        mock_story = MockStory(id='US-ABC123', jira_key='PROJ-123', story_points=0)

        mock_client.get_issue.return_value = jira_issue
        mock_scrum.get_story.return_value = mock_story
        mock_scrum.list_stories.return_value = [mock_story]

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)
            manager.sync_jira_to_xavier('PROJ-123')

            assert mock_story.story_points == 8

    def test_update_acceptance_criteria(self):
        """Test updating acceptance criteria from Jira"""
        mock_client = Mock(spec=JiraClient)
        mock_scrum = MagicMock()

        jira_issue = {
            'key': 'PROJ-123',
            'fields': {
                'summary': 'Story',
                'description': '''
                Main description

                Acceptance Criteria:
                - Criterion 1
                - Criterion 2
                ''',
                'status': {'name': 'To Do'}
            }
        }

        mock_story = MockStory(id='US-ABC123', jira_key='PROJ-123', acceptance_criteria=[])

        mock_client.get_issue.return_value = jira_issue
        mock_scrum.get_story.return_value = mock_story
        mock_scrum.list_stories.return_value = [mock_story]

        with patch('xavier.src.integrations.jira.story_sync.SCRUMManager', return_value=mock_scrum):
            manager = StorySyncManager(jira_client=mock_client)
            manager.sync_jira_to_xavier('PROJ-123')

            assert len(mock_story.acceptance_criteria) == 2
            assert 'Criterion 1' in mock_story.acceptance_criteria
            assert 'Criterion 2' in mock_story.acceptance_criteria


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=xavier.src.integrations.jira.story_sync", "--cov-report=term-missing"])
