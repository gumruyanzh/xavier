"""
Jira to Xavier Field Mapper
Handles mapping and transformation between Jira issues and Xavier stories
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class FieldMapper:
    """
    Maps Jira issue fields to Xavier story fields

    Handles:
    - Standard field mapping (summary, description, status, etc.)
    - Priority mapping between Jira and Xavier
    - Status mapping between systems
    - Story points extraction
    - Custom field mapping
    """

    # Jira to Xavier priority mapping
    PRIORITY_MAP = {
        'Highest': 'Critical',
        'High': 'High',
        'Medium': 'Medium',
        'Low': 'Low',
        'Lowest': 'Low'
    }

    # Jira to Xavier status mapping
    STATUS_MAP = {
        'To Do': 'Backlog',
        'Backlog': 'Backlog',
        'Selected for Development': 'Backlog',
        'In Progress': 'In Progress',
        'In Review': 'In Review',
        'Done': 'Done',
        'Closed': 'Done',
        'Blocked': 'Blocked'
    }

    def __init__(self, custom_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize field mapper

        Args:
            custom_mappings: Optional custom field mappings
        """
        self.custom_mappings = custom_mappings or {}
        logger.info("Field mapper initialized")

    def jira_to_xavier(self, jira_issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Jira issue to Xavier story format

        Args:
            jira_issue: Jira issue data

        Returns:
            Xavier story data
        """
        fields = jira_issue.get('fields', {})

        # Extract basic fields
        story_data = {
            'title': self._extract_title(fields),
            'description': self._extract_description(fields),
            'status': self._map_status(fields),
            'priority': self._map_priority(fields),
            'story_points': self._extract_story_points(fields),
            'assignee': self._extract_assignee(fields),
            'reporter': self._extract_reporter(fields),
            'created_at': self._extract_created_date(fields),
            'updated_at': self._extract_updated_date(fields),
            'labels': self._extract_labels(fields),
            'components': self._extract_components(fields),
            'jira_key': jira_issue.get('key'),
            'jira_id': jira_issue.get('id'),
            'jira_url': self._construct_jira_url(jira_issue)
        }

        # Extract user story format if available
        user_story = self._extract_user_story(fields)
        if user_story:
            story_data.update(user_story)

        # Extract acceptance criteria
        acceptance_criteria = self._extract_acceptance_criteria(fields)
        if acceptance_criteria:
            story_data['acceptance_criteria'] = acceptance_criteria

        # Apply custom field mappings
        if self.custom_mappings:
            custom_fields = self._extract_custom_fields(fields)
            story_data['custom_fields'] = custom_fields

        logger.info(f"Mapped Jira issue {jira_issue.get('key')} to Xavier story")
        return story_data

    def xavier_to_jira(self, xavier_story: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Xavier story to Jira issue format

        Args:
            xavier_story: Xavier story data

        Returns:
            Jira issue fields
        """
        jira_fields = {
            'summary': xavier_story.get('title', ''),
            'description': self._format_description_for_jira(xavier_story),
            'priority': {'name': self._reverse_map_priority(xavier_story.get('priority'))},
            'labels': xavier_story.get('labels', [])
        }

        # Add story points if available
        story_points = xavier_story.get('story_points')
        if story_points is not None:
            jira_fields['customfield_10016'] = story_points  # Common story points field

        # Add acceptance criteria if available
        acceptance_criteria = xavier_story.get('acceptance_criteria', [])
        if acceptance_criteria:
            jira_fields['description'] += self._format_acceptance_criteria(acceptance_criteria)

        logger.info(f"Mapped Xavier story to Jira issue fields")
        return {'fields': jira_fields}

    def _extract_title(self, fields: Dict[str, Any]) -> str:
        """Extract issue summary/title"""
        return fields.get('summary', '')

    def _extract_description(self, fields: Dict[str, Any]) -> str:
        """Extract and clean description"""
        description = fields.get('description', '')

        # Handle different description formats (plain text, ADF, etc.)
        if isinstance(description, dict):
            # Atlassian Document Format
            return self._extract_adf_text(description)

        return str(description) if description else ''

    def _extract_adf_text(self, adf: Dict[str, Any]) -> str:
        """Extract plain text from Atlassian Document Format"""
        content = adf.get('content', [])
        text_parts = []

        for block in content:
            if block.get('type') == 'paragraph':
                for node in block.get('content', []):
                    if node.get('type') == 'text':
                        text_parts.append(node.get('text', ''))
            elif block.get('type') == 'heading':
                for node in block.get('content', []):
                    if node.get('type') == 'text':
                        text_parts.append(f"\n{node.get('text', '')}\n")

        return ' '.join(text_parts)

    def _map_status(self, fields: Dict[str, Any]) -> str:
        """Map Jira status to Xavier status"""
        jira_status = fields.get('status', {}).get('name', 'Backlog')
        return self.STATUS_MAP.get(jira_status, 'Backlog')

    def _map_priority(self, fields: Dict[str, Any]) -> str:
        """Map Jira priority to Xavier priority"""
        jira_priority = fields.get('priority', {}).get('name', 'Medium')
        return self.PRIORITY_MAP.get(jira_priority, 'Medium')

    def _reverse_map_priority(self, xavier_priority: Optional[str]) -> str:
        """Map Xavier priority back to Jira priority"""
        if not xavier_priority:
            return 'Medium'

        # Manual reverse mapping to avoid ambiguity with duplicate values
        reverse_map = {
            'Critical': 'Highest',
            'High': 'High',
            'Medium': 'Medium',
            'Low': 'Low'  # Map to 'Low' not 'Lowest' for better bidirectional consistency
        }
        return reverse_map.get(xavier_priority, 'Medium')

    def _extract_story_points(self, fields: Dict[str, Any]) -> Optional[int]:
        """Extract story points from Jira custom field"""
        # Try common story points field IDs
        story_point_fields = [
            'customfield_10016',  # Common in Jira Cloud
            'customfield_10002',  # Alternative
            'story_points',
            'storyPoints'
        ]

        for field_id in story_point_fields:
            points = fields.get(field_id)
            if points is not None:
                try:
                    return int(float(points))
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_assignee(self, fields: Dict[str, Any]) -> Optional[str]:
        """Extract assignee information"""
        assignee = fields.get('assignee')
        if assignee:
            return assignee.get('displayName') or assignee.get('emailAddress')
        return None

    def _extract_reporter(self, fields: Dict[str, Any]) -> Optional[str]:
        """Extract reporter information"""
        reporter = fields.get('reporter')
        if reporter:
            return reporter.get('displayName') or reporter.get('emailAddress')
        return None

    def _extract_created_date(self, fields: Dict[str, Any]) -> Optional[str]:
        """Extract creation date"""
        created = fields.get('created')
        if created:
            # Jira returns ISO format
            return created
        return None

    def _extract_updated_date(self, fields: Dict[str, Any]) -> Optional[str]:
        """Extract last updated date"""
        updated = fields.get('updated')
        if updated:
            return updated
        return None

    def _extract_labels(self, fields: Dict[str, Any]) -> List[str]:
        """Extract labels/tags"""
        return fields.get('labels', [])

    def _extract_components(self, fields: Dict[str, Any]) -> List[str]:
        """Extract component names"""
        components = fields.get('components', [])
        return [comp.get('name') for comp in components if comp.get('name')]

    def _construct_jira_url(self, jira_issue: Dict[str, Any]) -> str:
        """Construct Jira issue URL"""
        key = jira_issue.get('key')
        self_url = jira_issue.get('self', '')

        if self_url:
            # Extract base URL from self link
            # Example: https://your-domain.atlassian.net/rest/api/3/issue/10001
            base_url = self_url.split('/rest/api')[0]
            return f"{base_url}/browse/{key}"

        return ''

    def _extract_user_story(self, fields: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Extract user story format (As a... I want... So that...)

        Looks for patterns in description or custom fields
        """
        description = self._extract_description(fields)

        # Try to parse user story format from description
        lines = description.split('\n')
        user_story = {}

        for line in lines:
            line = line.strip()
            if line.lower().startswith('as a'):
                user_story['as_a'] = line.replace('As a', '').replace('as a', '').strip()
            elif line.lower().startswith('i want'):
                user_story['i_want'] = line.replace('I want', '').replace('i want', '').strip()
            elif line.lower().startswith('so that'):
                user_story['so_that'] = line.replace('So that', '').replace('so that', '').strip()

        return user_story if user_story else None

    def _extract_acceptance_criteria(self, fields: Dict[str, Any]) -> List[str]:
        """Extract acceptance criteria from description or custom field"""
        description = self._extract_description(fields)
        criteria = []

        # Look for acceptance criteria section
        lines = description.split('\n')
        in_criteria_section = False

        for line in lines:
            line = line.strip()

            if 'acceptance criteria' in line.lower():
                in_criteria_section = True
                continue

            if in_criteria_section:
                if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                    criteria.append(line.lstrip('-*• '))
                elif line.startswith(('[', '[')):
                    # Checkbox format
                    criteria.append(line.lstrip('[x] ').lstrip('[ ] '))
                elif not line:
                    # Empty line might end criteria section
                    if criteria:
                        break

        return criteria

    def _extract_custom_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Extract custom fields based on custom mappings"""
        custom_data = {}

        for jira_field, xavier_field in self.custom_mappings.items():
            value = fields.get(jira_field)
            if value is not None:
                custom_data[xavier_field] = value

        return custom_data

    def _format_description_for_jira(self, xavier_story: Dict[str, Any]) -> str:
        """Format Xavier story description for Jira"""
        parts = []

        # Add user story format if available
        if xavier_story.get('as_a'):
            parts.append(f"As a {xavier_story['as_a']}")
        if xavier_story.get('i_want'):
            parts.append(f"I want {xavier_story['i_want']}")
        if xavier_story.get('so_that'):
            parts.append(f"So that {xavier_story['so_that']}")

        # Add main description
        if xavier_story.get('description'):
            if parts:
                parts.append('\n')
            parts.append(xavier_story['description'])

        return '\n'.join(parts)

    def _format_acceptance_criteria(self, criteria: List[str]) -> str:
        """Format acceptance criteria for Jira"""
        if not criteria:
            return ''

        formatted = ['\n\nAcceptance Criteria:']
        for criterion in criteria:
            formatted.append(f"- {criterion}")

        return '\n'.join(formatted)


# Singleton instance
_mapper_instance: Optional[FieldMapper] = None


def get_field_mapper(custom_mappings: Optional[Dict[str, str]] = None) -> FieldMapper:
    """Get or create field mapper singleton"""
    global _mapper_instance

    if _mapper_instance is None:
        _mapper_instance = FieldMapper(custom_mappings)

    return _mapper_instance
