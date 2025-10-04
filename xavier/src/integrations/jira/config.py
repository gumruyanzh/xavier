"""
Jira Integration Configuration
Manages custom field mappings and integration settings
"""

import os
import json
import logging
import copy
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class JiraConfig:
    """
    Jira integration configuration manager

    Handles:
    - Custom field mappings
    - Project key mappings
    - Sync preferences
    - Credential management
    """

    DEFAULT_CONFIG_PATH = ".xavier/jira_config.json"

    @staticmethod
    def _get_default_config():
        """Get default configuration (fresh copy each time)"""
        return {
            "custom_field_mappings": {
                "customfield_10016": "story_points",
                "customfield_10001": "epic_link",
                "customfield_10002": "sprint"
            },
            "project_mappings": {},
            "sync_preferences": {
                "auto_sync": True,
                "sync_direction": "both",
                "conflict_resolution": "jira_wins"
            },
            "field_mappings": {
                "story_points_field": "customfield_10016",
                "epic_link_field": "customfield_10001",
                "sprint_field": "customfield_10002"
            }
        }

    DEFAULT_CONFIG = _get_default_config.__func__()

    def __init__(self, config_path: Optional[str] = None, project_root: str = '.'):
        """
        Initialize Jira configuration

        Args:
            config_path: Path to config file (optional)
            project_root: Root directory of Xavier project
        """
        self.project_root = Path(project_root)
        self.config_path = Path(config_path) if config_path else self.project_root / self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Loaded Jira config from {self.config_path}")
                    return config
            except Exception as e:
                logger.error(f"Failed to load config from {self.config_path}: {e}")
                return self._get_default_config()
        else:
            logger.info("No config file found, using defaults")
            return self._get_default_config()

    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved Jira config to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_path}: {e}")
            raise

    def get_custom_field_mappings(self) -> Dict[str, str]:
        """Get custom field mappings"""
        return self.config.get('custom_field_mappings', {})

    def set_custom_field_mapping(self, jira_field: str, xavier_field: str):
        """
        Set custom field mapping

        Args:
            jira_field: Jira field ID (e.g., 'customfield_10001')
            xavier_field: Xavier field name (e.g., 'epic_link')
        """
        if 'custom_field_mappings' not in self.config:
            self.config['custom_field_mappings'] = {}

        self.config['custom_field_mappings'][jira_field] = xavier_field
        logger.info(f"Mapped {jira_field} -> {xavier_field}")

    def remove_custom_field_mapping(self, jira_field: str):
        """Remove custom field mapping"""
        if jira_field in self.config.get('custom_field_mappings', {}):
            del self.config['custom_field_mappings'][jira_field]
            logger.info(f"Removed mapping for {jira_field}")

    def get_project_mapping(self, xavier_project: str) -> Optional[str]:
        """
        Get Jira project key for Xavier project

        Args:
            xavier_project: Xavier project name

        Returns:
            Jira project key or None
        """
        return self.config.get('project_mappings', {}).get(xavier_project)

    def set_project_mapping(self, xavier_project: str, jira_project_key: str):
        """
        Map Xavier project to Jira project

        Args:
            xavier_project: Xavier project name
            jira_project_key: Jira project key (e.g., 'PROJ')
        """
        if 'project_mappings' not in self.config:
            self.config['project_mappings'] = {}

        self.config['project_mappings'][xavier_project] = jira_project_key
        logger.info(f"Mapped Xavier project '{xavier_project}' -> Jira '{jira_project_key}'")

    def get_sync_preferences(self) -> Dict[str, Any]:
        """Get sync preferences"""
        return self.config.get('sync_preferences', self._get_default_config()['sync_preferences'])

    def set_sync_preference(self, key: str, value: Any):
        """
        Set sync preference

        Args:
            key: Preference key (e.g., 'auto_sync', 'sync_direction')
            value: Preference value
        """
        if 'sync_preferences' not in self.config:
            self.config['sync_preferences'] = {}

        self.config['sync_preferences'][key] = value
        logger.info(f"Set sync preference {key} = {value}")

    def get_field_mapping(self, field_name: str) -> Optional[str]:
        """
        Get Jira field ID for a named field

        Args:
            field_name: Field name (e.g., 'story_points_field')

        Returns:
            Jira field ID or None
        """
        return self.config.get('field_mappings', {}).get(field_name)

    def set_field_mapping(self, field_name: str, jira_field_id: str):
        """
        Set field mapping

        Args:
            field_name: Field name (e.g., 'story_points_field')
            jira_field_id: Jira field ID (e.g., 'customfield_10016')
        """
        if 'field_mappings' not in self.config:
            self.config['field_mappings'] = {}

        self.config['field_mappings'][field_name] = jira_field_id
        logger.info(f"Mapped {field_name} -> {jira_field_id}")

    def get_story_points_field(self) -> str:
        """Get story points custom field ID"""
        return self.get_field_mapping('story_points_field') or 'customfield_10016'

    def get_epic_link_field(self) -> str:
        """Get epic link custom field ID"""
        return self.get_field_mapping('epic_link_field') or 'customfield_10001'

    def get_sprint_field(self) -> str:
        """Get sprint custom field ID"""
        return self.get_field_mapping('sprint_field') or 'customfield_10002'

    def initialize_default_config(self):
        """Initialize configuration file with defaults"""
        self.config = self._get_default_config()
        self.save_config()
        logger.info("Initialized default Jira configuration")

    def validate_config(self) -> bool:
        """
        Validate configuration structure

        Returns:
            True if valid, False otherwise
        """
        required_keys = ['custom_field_mappings', 'project_mappings', 'sync_preferences', 'field_mappings']

        for key in required_keys:
            if key not in self.config:
                logger.warning(f"Missing required config key: {key}")
                return False

        return True

    def get_config(self) -> Dict[str, Any]:
        """Get full configuration"""
        return copy.deepcopy(self.config)

    def update_config(self, updates: Dict[str, Any]):
        """
        Update configuration with new values

        Args:
            updates: Dictionary of configuration updates
        """
        self.config.update(updates)
        logger.info("Configuration updated")


# Singleton instance
_config_instance: Optional[JiraConfig] = None


def get_jira_config(project_root: str = '.') -> JiraConfig:
    """Get or create Jira config singleton"""
    global _config_instance

    if _config_instance is None:
        _config_instance = JiraConfig(project_root=project_root)

    return _config_instance
