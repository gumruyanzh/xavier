"""
Jira Story Synchronization
Handles bi-directional sync between Jira issues and Xavier stories
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from xavier.src.integrations.jira.jira_client import JiraClient, JiraAPIError
from xavier.src.integrations.jira.field_mapper import FieldMapper
from xavier.src.scrum.scrum_manager import SCRUMManager

logger = logging.getLogger(__name__)


class StorySyncError(Exception):
    """Raised when story synchronization fails"""
    pass


class StorySyncManager:
    """
    Manages bi-directional synchronization between Jira and Xavier

    Features:
    - Sync Jira issues to Xavier stories
    - Sync Xavier stories to Jira issues
    - Update existing stories with Jira changes
    - Push Xavier changes to Jira
    """

    def __init__(
        self,
        jira_client: JiraClient,
        xavier_project_path: str = '.',
        custom_field_mappings: Optional[Dict[str, str]] = None
    ):
        """
        Initialize story sync manager

        Args:
            jira_client: Configured JiraClient instance
            xavier_project_path: Path to Xavier project
            custom_field_mappings: Optional custom field mappings
        """
        self.jira_client = jira_client
        self.scrum_manager = SCRUMManager(xavier_project_path)
        self.field_mapper = FieldMapper(custom_mappings=custom_field_mappings)
        self.sync_log: List[Dict[str, Any]] = []

        logger.info("Story sync manager initialized")

    def sync_jira_to_xavier(self, jira_issue_key: str) -> Dict[str, Any]:
        """
        Sync Jira issue to Xavier story

        Creates new Xavier story or updates existing one based on Jira data.

        Args:
            jira_issue_key: Jira issue key (e.g., 'PROJ-123')

        Returns:
            Xavier story data

        Raises:
            StorySyncError: If sync fails
        """
        try:
            # Fetch Jira issue
            jira_issue = self.jira_client.get_issue(jira_issue_key)

            if not jira_issue:
                raise StorySyncError(f"Jira issue {jira_issue_key} not found")

            # Transform to Xavier format
            story_data = self.field_mapper.jira_to_xavier(jira_issue)

            # Check if story already exists
            existing_story = self._find_story_by_jira_key(jira_issue_key)

            if existing_story:
                # Update existing story
                logger.info(f"Updating existing story {existing_story.id} from Jira {jira_issue_key}")
                updated_story = self._update_xavier_story(existing_story.id, story_data)

                self._log_sync('jira_to_xavier', 'update', jira_issue_key, updated_story.id)
                return updated_story.__dict__
            else:
                # Create new story
                logger.info(f"Creating new Xavier story from Jira {jira_issue_key}")
                new_story = self._create_xavier_story(story_data)

                self._log_sync('jira_to_xavier', 'create', jira_issue_key, new_story.id)
                return new_story.__dict__

        except JiraAPIError as e:
            logger.error(f"Failed to fetch Jira issue {jira_issue_key}: {e}")
            raise StorySyncError(f"Jira API error: {e}")
        except Exception as e:
            logger.error(f"Failed to sync Jira issue {jira_issue_key} to Xavier: {e}")
            raise StorySyncError(f"Sync failed: {e}")

    def sync_xavier_to_jira(self, story_id: str) -> Dict[str, Any]:
        """
        Sync Xavier story to Jira issue

        Creates new Jira issue or updates existing one based on Xavier story.

        Args:
            story_id: Xavier story ID

        Returns:
            Jira issue data

        Raises:
            StorySyncError: If sync fails
        """
        try:
            # Get Xavier story
            story = self.scrum_manager.get_story(story_id)

            if not story:
                raise StorySyncError(f"Xavier story {story_id} not found")

            # Transform to Jira format
            jira_fields = self.field_mapper.xavier_to_jira(story.__dict__)

            # Check if story has Jira key (already synced)
            jira_key = getattr(story, 'jira_key', None)

            if jira_key:
                # Update existing Jira issue
                logger.info(f"Updating Jira issue {jira_key} from Xavier story {story_id}")
                success = self.jira_client.update_issue(jira_key, jira_fields['fields'])

                if not success:
                    raise StorySyncError(f"Failed to update Jira issue {jira_key}")

                self._log_sync('xavier_to_jira', 'update', story_id, jira_key)
                return {'key': jira_key, 'fields': jira_fields['fields']}
            else:
                # Create new Jira issue
                # Note: Requires project_key - should be in config
                raise NotImplementedError("Creating new Jira issues from Xavier not yet implemented")

        except Exception as e:
            logger.error(f"Failed to sync Xavier story {story_id} to Jira: {e}")
            raise StorySyncError(f"Sync failed: {e}")

    def sync_story_metadata(
        self,
        story_id: str,
        jira_issue_key: str,
        direction: str = 'both'
    ) -> Dict[str, Any]:
        """
        Sync story metadata between Jira and Xavier

        Args:
            story_id: Xavier story ID
            jira_issue_key: Jira issue key
            direction: Sync direction ('jira_to_xavier', 'xavier_to_jira', 'both')

        Returns:
            Sync result with both story and issue data

        Raises:
            StorySyncError: If sync fails
        """
        result = {
            'story_id': story_id,
            'jira_key': jira_issue_key,
            'direction': direction,
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            if direction in ('jira_to_xavier', 'both'):
                result['xavier_story'] = self.sync_jira_to_xavier(jira_issue_key)

            if direction in ('xavier_to_jira', 'both'):
                result['jira_issue'] = self.sync_xavier_to_jira(story_id)

            return result

        except Exception as e:
            logger.error(f"Metadata sync failed for {story_id} <-> {jira_issue_key}: {e}")
            raise StorySyncError(f"Metadata sync failed: {e}")

    def _create_xavier_story(self, story_data: Dict[str, Any]) -> Any:
        """Create Xavier story from Jira data"""
        # Extract user story components
        title = story_data.get('title', 'Untitled Story')
        as_a = story_data.get('as_a', 'user')
        i_want = story_data.get('i_want', title)
        so_that = story_data.get('so_that', 'deliver value')

        # Create story
        story = self.scrum_manager.create_story(
            title=title,
            as_a=as_a,
            i_want=i_want,
            so_that=so_that
        )

        # Update with additional fields
        if story_data.get('story_points'):
            story.story_points = story_data['story_points']

        if story_data.get('priority'):
            story.priority = story_data['priority']

        if story_data.get('status'):
            story.status = story_data['status']

        # Store Jira metadata
        story.jira_key = story_data.get('jira_key')
        story.jira_id = story_data.get('jira_id')
        story.jira_url = story_data.get('jira_url')

        if story_data.get('acceptance_criteria'):
            story.acceptance_criteria = story_data['acceptance_criteria']

        if story_data.get('labels'):
            story.labels = story_data['labels']

        # Save story
        self.scrum_manager.save_story(story)

        return story

    def _update_xavier_story(self, story_id: str, story_data: Dict[str, Any]) -> Any:
        """Update Xavier story with Jira data"""
        story = self.scrum_manager.get_story(story_id)

        if not story:
            raise StorySyncError(f"Story {story_id} not found")

        # Update fields
        if story_data.get('title'):
            story.title = story_data['title']

        if story_data.get('description'):
            # Update user story components if available
            if story_data.get('as_a'):
                story.as_a = story_data['as_a']
            if story_data.get('i_want'):
                story.i_want = story_data['i_want']
            if story_data.get('so_that'):
                story.so_that = story_data['so_that']

        if story_data.get('story_points') is not None:
            story.story_points = story_data['story_points']

        if story_data.get('priority'):
            story.priority = story_data['priority']

        if story_data.get('status'):
            story.status = story_data['status']

        if story_data.get('acceptance_criteria'):
            story.acceptance_criteria = story_data['acceptance_criteria']

        if story_data.get('labels'):
            story.labels = story_data['labels']

        # Update Jira metadata
        story.jira_key = story_data.get('jira_key')
        story.jira_id = story_data.get('jira_id')
        story.jira_url = story_data.get('jira_url')

        # Save story
        self.scrum_manager.save_story(story)

        return story

    def _find_story_by_jira_key(self, jira_key: str) -> Optional[Any]:
        """Find Xavier story by Jira key"""
        stories = self.scrum_manager.list_stories()

        for story in stories:
            if hasattr(story, 'jira_key') and story.jira_key == jira_key:
                return story

        return None

    def _log_sync(
        self,
        direction: str,
        action: str,
        source_id: str,
        target_id: str
    ):
        """Log sync operation"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'direction': direction,
            'action': action,
            'source_id': source_id,
            'target_id': target_id
        }

        self.sync_log.append(log_entry)
        logger.info(f"Sync logged: {direction} {action} {source_id} -> {target_id}")

    def get_sync_log(self) -> List[Dict[str, Any]]:
        """Get synchronization log"""
        return self.sync_log


# Singleton instance
_sync_manager_instance: Optional[StorySyncManager] = None


def get_story_sync_manager(
    jira_client: JiraClient,
    xavier_project_path: str = '.',
    custom_field_mappings: Optional[Dict[str, str]] = None
) -> StorySyncManager:
    """Get or create story sync manager singleton"""
    global _sync_manager_instance

    if _sync_manager_instance is None:
        _sync_manager_instance = StorySyncManager(
            jira_client,
            xavier_project_path,
            custom_field_mappings
        )

    return _sync_manager_instance
