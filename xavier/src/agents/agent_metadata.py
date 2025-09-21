"""
Xavier Framework - Agent Metadata Management
Loads and manages agent metadata from YAML files for consistent display and capabilities
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging


@dataclass
class AgentMetadata:
    """Metadata for an agent loaded from YAML configuration"""
    name: str
    display_name: str
    color: str
    emoji: str
    label: str
    description: str
    tools: List[str]
    capabilities: List[str]
    restricted_actions: List[str]
    allowed_file_patterns: List[str]
    languages: List[str]
    frameworks: List[str]


class AgentMetadataManager:
    """Manages loading and caching of agent metadata"""

    def __init__(self, metadata_dir: str = ".xavier/agents"):
        self.metadata_dir = metadata_dir
        self.logger = logging.getLogger("Xavier.AgentMetadata")
        self._metadata_cache: Dict[str, AgentMetadata] = {}
        self._load_all_metadata()

    def _load_all_metadata(self) -> None:
        """Load all agent metadata from YAML files"""
        if not os.path.exists(self.metadata_dir):
            self.logger.warning(f"Agent metadata directory not found: {self.metadata_dir}")
            return

        for filename in os.listdir(self.metadata_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                agent_file = os.path.join(self.metadata_dir, filename)
                try:
                    self._load_agent_metadata(agent_file)
                except Exception as e:
                    self.logger.error(f"Failed to load agent metadata from {filename}: {e}")

    def _load_agent_metadata(self, file_path: str) -> None:
        """Load metadata for a single agent from YAML file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        # Validate required fields
        required_fields = ['name', 'display_name', 'color', 'emoji', 'label', 'description']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in {file_path}")

        # Create metadata object with defaults for optional fields
        metadata = AgentMetadata(
            name=data['name'],
            display_name=data['display_name'],
            color=data['color'],
            emoji=data['emoji'],
            label=data['label'],
            description=data['description'],
            tools=data.get('tools', []),
            capabilities=data.get('capabilities', []),
            restricted_actions=data.get('restricted_actions', []),
            allowed_file_patterns=data.get('allowed_file_patterns', []),
            languages=data.get('languages', []),
            frameworks=data.get('frameworks', [])
        )

        self._metadata_cache[data['name']] = metadata

        # Also cache by display name (for backward compatibility)
        display_key = data['display_name'].replace(' ', '').lower()
        self._metadata_cache[display_key] = metadata

        self.logger.info(f"Loaded metadata for agent: {data['display_name']}")

    def get_agent_metadata(self, agent_name: str) -> Optional[AgentMetadata]:
        """Get metadata for an agent by name"""
        # Try direct lookup first
        if agent_name in self._metadata_cache:
            return self._metadata_cache[agent_name]

        # Try normalized lookup (lowercase, no spaces/dashes)
        normalized_name = agent_name.lower().replace(' ', '').replace('-', '').replace('_', '')
        for cached_name, metadata in self._metadata_cache.items():
            cached_normalized = cached_name.lower().replace(' ', '').replace('-', '').replace('_', '')
            if cached_normalized == normalized_name:
                return metadata

        return None

    def get_agent_color(self, agent_name: str) -> str:
        """Get color for an agent (with fallback)"""
        metadata = self.get_agent_metadata(agent_name)
        if metadata:
            return self._color_name_to_ansi(metadata.color)

        # Fallback colors for unknown agents
        fallback_colors = {
            'projectmanager': '\033[1;35m',  # magenta
            'contextmanager': '\033[1;34m',  # blue
            'pythonengineer': '\033[1;32m',  # green
            'golangengineer': '\033[1;36m',  # cyan
            'frontendengineer': '\033[1;33m',  # yellow
            'testrunner': '\033[1;31m',  # red
        }

        normalized_name = agent_name.lower().replace(' ', '').replace('-', '').replace('_', '')
        return fallback_colors.get(normalized_name, '\033[1;37m')  # default white

    def get_agent_emoji(self, agent_name: str) -> str:
        """Get emoji for an agent (with fallback)"""
        metadata = self.get_agent_metadata(agent_name)
        if metadata:
            return metadata.emoji

        # Fallback emojis
        fallback_emojis = {
            'projectmanager': '📊',
            'contextmanager': '🔍',
            'pythonengineer': '🐍',
            'golangengineer': '🔷',
            'frontendengineer': '🎨',
            'testrunner': '🧪',
        }

        normalized_name = agent_name.lower().replace(' ', '').replace('-', '').replace('_', '')
        return fallback_emojis.get(normalized_name, '🤖')

    def get_agent_label(self, agent_name: str) -> str:
        """Get short label for an agent (with fallback)"""
        metadata = self.get_agent_metadata(agent_name)
        if metadata:
            return metadata.label

        # Fallback labels
        fallback_labels = {
            'projectmanager': 'PM',
            'contextmanager': 'CTX',
            'pythonengineer': 'PY',
            'golangengineer': 'GO',
            'frontendengineer': 'FE',
            'testrunner': 'TEST',
        }

        normalized_name = agent_name.lower().replace(' ', '').replace('-', '').replace('_', '')
        return fallback_labels.get(normalized_name, 'AGT')

    def get_agent_display_name(self, agent_name: str) -> str:
        """Get display name for an agent (with fallback)"""
        metadata = self.get_agent_metadata(agent_name)
        if metadata:
            return metadata.display_name
        return agent_name.replace('_', ' ').replace('-', ' ').title()

    def _color_name_to_ansi(self, color_name: str) -> str:
        """Convert color name to ANSI escape code"""
        color_map = {
            'black': '\033[1;30m',
            'red': '\033[1;31m',
            'green': '\033[1;32m',
            'yellow': '\033[1;33m',
            'blue': '\033[1;34m',
            'magenta': '\033[1;35m',
            'cyan': '\033[1;36m',
            'white': '\033[1;37m',
        }
        return color_map.get(color_name.lower(), '\033[1;37m')

    def list_available_agents(self) -> List[str]:
        """List all available agents"""
        return list(self._metadata_cache.keys())

    def reload_metadata(self) -> None:
        """Reload all metadata from files"""
        self._metadata_cache.clear()
        self._load_all_metadata()


# Global instance for easy access
_metadata_manager = None


def get_metadata_manager() -> AgentMetadataManager:
    """Get the global metadata manager instance"""
    global _metadata_manager
    if _metadata_manager is None:
        _metadata_manager = AgentMetadataManager()
    return _metadata_manager


def get_agent_metadata(agent_name: str) -> Optional[AgentMetadata]:
    """Convenience function to get agent metadata"""
    return get_metadata_manager().get_agent_metadata(agent_name)


def get_agent_color(agent_name: str) -> str:
    """Convenience function to get agent color"""
    return get_metadata_manager().get_agent_color(agent_name)


def get_agent_emoji(agent_name: str) -> str:
    """Convenience function to get agent emoji"""
    return get_metadata_manager().get_agent_emoji(agent_name)


def get_agent_label(agent_name: str) -> str:
    """Convenience function to get agent label"""
    return get_metadata_manager().get_agent_label(agent_name)


def get_agent_display_name(agent_name: str) -> str:
    """Convenience function to get agent display name"""
    return get_metadata_manager().get_agent_display_name(agent_name)