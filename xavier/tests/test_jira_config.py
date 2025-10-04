"""
Tests for Jira Configuration
Tests custom field mapping and configuration management
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from xavier.src.integrations.jira.config import JiraConfig, get_jira_config
import xavier.src.integrations.jira.config as config_module


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton before each test"""
    config_module._config_instance = None
    yield
    config_module._config_instance = None


class TestJiraConfigInitialization:
    """Test Jira config initialization"""

    def test_init_with_defaults(self):
        """Test initialization with default config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)

            assert config.project_root == Path(tmpdir)
            assert 'custom_field_mappings' in config.config
            assert 'project_mappings' in config.config
            assert 'sync_preferences' in config.config

    def test_init_creates_config_path(self):
        """Test config path is created correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            expected_path = Path(tmpdir) / '.xavier' / 'jira_config.json'

            assert config.config_path == expected_path

    def test_load_existing_config(self):
        """Test loading existing configuration file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_data = {
                'custom_field_mappings': {'customfield_12345': 'test_field'},
                'project_mappings': {'myproject': 'PROJ'},
                'sync_preferences': {'auto_sync': False},
                'field_mappings': {}
            }

            config_path = Path(tmpdir) / '.xavier' / 'jira_config.json'
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w') as f:
                json.dump(config_data, f)

            config = JiraConfig(project_root=tmpdir)

            assert config.config['custom_field_mappings']['customfield_12345'] == 'test_field'
            assert config.config['project_mappings']['myproject'] == 'PROJ'
            assert config.config['sync_preferences']['auto_sync'] is False


class TestCustomFieldMappings:
    """Test custom field mapping management"""

    def test_get_custom_field_mappings(self):
        """Test getting custom field mappings"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            mappings = config.get_custom_field_mappings()

            assert isinstance(mappings, dict)
            assert 'customfield_10016' in mappings

    def test_set_custom_field_mapping(self):
        """Test setting custom field mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.set_custom_field_mapping('customfield_99999', 'my_custom_field')

            assert config.config['custom_field_mappings']['customfield_99999'] == 'my_custom_field'

    def test_remove_custom_field_mapping(self):
        """Test removing custom field mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.set_custom_field_mapping('customfield_99999', 'my_custom_field')

            assert 'customfield_99999' in config.config['custom_field_mappings']

            config.remove_custom_field_mapping('customfield_99999')

            assert 'customfield_99999' not in config.config['custom_field_mappings']


class TestProjectMappings:
    """Test project mapping management"""

    def test_get_project_mapping(self):
        """Test getting project mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.set_project_mapping('xavier-project', 'JIRA')

            assert config.get_project_mapping('xavier-project') == 'JIRA'

    def test_get_nonexistent_project_mapping(self):
        """Test getting non-existent project mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)

            assert config.get_project_mapping('nonexistent') is None

    def test_set_project_mapping(self):
        """Test setting project mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.set_project_mapping('myapp', 'APP')

            assert config.config['project_mappings']['myapp'] == 'APP'


class TestSyncPreferences:
    """Test sync preference management"""

    def test_get_sync_preferences(self):
        """Test getting sync preferences"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            prefs = config.get_sync_preferences()

            assert 'auto_sync' in prefs
            assert 'sync_direction' in prefs
            assert 'conflict_resolution' in prefs

    def test_set_sync_preference(self):
        """Test setting sync preference"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.set_sync_preference('auto_sync', False)

            assert config.config['sync_preferences']['auto_sync'] is False

    def test_set_custom_sync_preference(self):
        """Test setting custom sync preference"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.set_sync_preference('custom_pref', 'custom_value')

            assert config.config['sync_preferences']['custom_pref'] == 'custom_value'


class TestFieldMappings:
    """Test field mapping management"""

    def test_get_field_mapping(self):
        """Test getting field mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            field_id = config.get_field_mapping('story_points_field')

            assert field_id == 'customfield_10016'

    def test_set_field_mapping(self):
        """Test setting field mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.set_field_mapping('custom_field', 'customfield_88888')

            assert config.config['field_mappings']['custom_field'] == 'customfield_88888'

    def test_get_story_points_field(self):
        """Test getting story points field ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)

            assert config.get_story_points_field() == 'customfield_10016'

    def test_get_epic_link_field(self):
        """Test getting epic link field ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)

            assert config.get_epic_link_field() == 'customfield_10001'

    def test_get_sprint_field(self):
        """Test getting sprint field ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)

            assert config.get_sprint_field() == 'customfield_10002'


class TestConfigPersistence:
    """Test configuration persistence"""

    def test_save_config(self):
        """Test saving configuration to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.set_custom_field_mapping('customfield_11111', 'test_field')
            config.save_config()

            assert config.config_path.exists()

            # Load and verify
            with open(config.config_path, 'r') as f:
                saved_config = json.load(f)

            assert saved_config['custom_field_mappings']['customfield_11111'] == 'test_field'

    def test_initialize_default_config(self):
        """Test initializing default configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.initialize_default_config()

            assert config.config_path.exists()

            # Verify defaults
            assert 'customfield_10016' in config.config['custom_field_mappings']
            assert config.config['sync_preferences']['auto_sync'] is True


class TestConfigValidation:
    """Test configuration validation"""

    def test_validate_valid_config(self):
        """Test validating valid configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)

            assert config.validate_config() is True

    def test_validate_invalid_config(self):
        """Test validating invalid configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            config.config = {'custom_field_mappings': {}}  # Missing required keys

            assert config.validate_config() is False


class TestConfigSingleton:
    """Test config singleton pattern"""

    def test_singleton_pattern(self):
        """Test config singleton"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config1 = get_jira_config(tmpdir)
            config2 = get_jira_config(tmpdir)

            assert config1 is config2


class TestConfigUtilities:
    """Test configuration utility methods"""

    def test_get_config(self):
        """Test getting full configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)
            full_config = config.get_config()

            assert isinstance(full_config, dict)
            assert 'custom_field_mappings' in full_config
            assert 'project_mappings' in full_config

    def test_update_config(self):
        """Test updating configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = JiraConfig(project_root=tmpdir)

            updates = {
                'new_section': {'key': 'value'},
                'sync_preferences': {'new_pref': True}
            }

            config.update_config(updates)

            assert 'new_section' in config.config
            assert config.config['new_section']['key'] == 'value'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=xavier.src.integrations.jira.config", "--cov-report=term-missing"])
