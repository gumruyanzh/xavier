"""
Tests for Jira to Xavier Field Mapper
Tests field mapping and transformation logic
"""

import pytest
from datetime import datetime

from xavier.src.integrations.jira.field_mapper import FieldMapper, get_field_mapper


class TestFieldMapperInitialization:
    """Test field mapper initialization"""

    def test_init_without_custom_mappings(self):
        """Test initialization without custom mappings"""
        mapper = FieldMapper()
        assert mapper.custom_mappings == {}

    def test_init_with_custom_mappings(self):
        """Test initialization with custom mappings"""
        custom = {'customfield_10001': 'epic_link'}
        mapper = FieldMapper(custom_mappings=custom)
        assert mapper.custom_mappings == custom

    def test_singleton_pattern(self):
        """Test field mapper singleton"""
        mapper1 = get_field_mapper()
        mapper2 = get_field_mapper()
        assert mapper1 is mapper2


class TestJiraToXavierMapping:
    """Test Jira to Xavier field mapping"""

    def test_basic_field_mapping(self):
        """Test mapping of basic fields"""
        jira_issue = {
            'key': 'PROJ-123',
            'id': '10001',
            'self': 'https://test.atlassian.net/rest/api/3/issue/10001',
            'fields': {
                'summary': 'Test Issue',
                'description': 'Test description',
                'status': {'name': 'In Progress'},
                'priority': {'name': 'High'},
                'labels': ['backend', 'api'],
                'created': '2025-01-01T10:00:00.000+0000',
                'updated': '2025-01-02T15:30:00.000+0000'
            }
        }

        mapper = FieldMapper()
        result = mapper.jira_to_xavier(jira_issue)

        assert result['title'] == 'Test Issue'
        assert result['description'] == 'Test description'
        assert result['status'] == 'In Progress'
        assert result['priority'] == 'High'
        assert result['jira_key'] == 'PROJ-123'
        assert result['jira_id'] == '10001'
        assert result['labels'] == ['backend', 'api']
        assert result['created_at'] == '2025-01-01T10:00:00.000+0000'
        assert result['updated_at'] == '2025-01-02T15:30:00.000+0000'

    def test_priority_mapping(self):
        """Test priority mapping from Jira to Xavier"""
        mapper = FieldMapper()

        test_cases = [
            ({'priority': {'name': 'Highest'}}, 'Critical'),
            ({'priority': {'name': 'High'}}, 'High'),
            ({'priority': {'name': 'Medium'}}, 'Medium'),
            ({'priority': {'name': 'Low'}}, 'Low'),
            ({'priority': {'name': 'Lowest'}}, 'Low'),
        ]

        for fields, expected in test_cases:
            assert mapper._map_priority(fields) == expected

    def test_status_mapping(self):
        """Test status mapping from Jira to Xavier"""
        mapper = FieldMapper()

        test_cases = [
            ({'status': {'name': 'To Do'}}, 'Backlog'),
            ({'status': {'name': 'Backlog'}}, 'Backlog'),
            ({'status': {'name': 'In Progress'}}, 'In Progress'),
            ({'status': {'name': 'In Review'}}, 'In Review'),
            ({'status': {'name': 'Done'}}, 'Done'),
            ({'status': {'name': 'Closed'}}, 'Done'),
        ]

        for fields, expected in test_cases:
            assert mapper._map_status(fields) == expected

    def test_story_points_extraction(self):
        """Test story points extraction from various custom fields"""
        mapper = FieldMapper()

        # Test common story points field
        fields1 = {'customfield_10016': 5}
        assert mapper._extract_story_points(fields1) == 5

        # Test alternative field
        fields2 = {'customfield_10002': 8.0}
        assert mapper._extract_story_points(fields2) == 8

        # Test missing story points
        fields3 = {}
        assert mapper._extract_story_points(fields3) is None

    def test_assignee_extraction(self):
        """Test assignee extraction"""
        mapper = FieldMapper()

        fields_with_assignee = {
            'assignee': {
                'displayName': 'John Doe',
                'emailAddress': 'john@example.com'
            }
        }
        assert mapper._extract_assignee(fields_with_assignee) == 'John Doe'

        fields_without_assignee = {}
        assert mapper._extract_assignee(fields_without_assignee) is None

    def test_components_extraction(self):
        """Test component extraction"""
        mapper = FieldMapper()

        fields = {
            'components': [
                {'name': 'Backend'},
                {'name': 'API'},
                {'name': 'Database'}
            ]
        }

        components = mapper._extract_components(fields)
        assert components == ['Backend', 'API', 'Database']

    def test_jira_url_construction(self):
        """Test Jira URL construction"""
        mapper = FieldMapper()

        jira_issue = {
            'key': 'PROJ-123',
            'self': 'https://test.atlassian.net/rest/api/3/issue/10001'
        }

        url = mapper._construct_jira_url(jira_issue)
        assert url == 'https://test.atlassian.net/browse/PROJ-123'

    def test_user_story_extraction(self):
        """Test user story format extraction"""
        mapper = FieldMapper()

        fields = {
            'description': '''
            As a developer
            I want to implement feature X
            So that users can benefit from it

            Additional details here...
            '''
        }

        user_story = mapper._extract_user_story(fields)
        assert user_story is not None
        assert user_story['as_a'] == 'developer'
        assert user_story['i_want'] == 'to implement feature X'
        assert user_story['so_that'] == 'users can benefit from it'

    def test_acceptance_criteria_extraction(self):
        """Test acceptance criteria extraction"""
        mapper = FieldMapper()

        fields = {
            'description': '''
            Main description here.

            Acceptance Criteria:
            - Criterion 1
            - Criterion 2
            * Criterion 3

            Other content...
            '''
        }

        criteria = mapper._extract_acceptance_criteria(fields)
        assert len(criteria) == 3
        assert 'Criterion 1' in criteria
        assert 'Criterion 2' in criteria
        assert 'Criterion 3' in criteria

    def test_adf_text_extraction(self):
        """Test Atlassian Document Format text extraction"""
        mapper = FieldMapper()

        adf = {
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {'type': 'text', 'text': 'This is a paragraph.'}
                    ]
                },
                {
                    'type': 'heading',
                    'attrs': {'level': 2},
                    'content': [
                        {'type': 'text', 'text': 'Heading'}
                    ]
                }
            ]
        }

        text = mapper._extract_adf_text(adf)
        assert 'This is a paragraph.' in text
        assert 'Heading' in text


class TestXavierToJiraMapping:
    """Test Xavier to Jira field mapping"""

    def test_basic_xavier_to_jira(self):
        """Test basic Xavier to Jira mapping"""
        xavier_story = {
            'title': 'Xavier Story',
            'description': 'Story description',
            'priority': 'High',
            'story_points': 5,
            'labels': ['feature', 'backend']
        }

        mapper = FieldMapper()
        result = mapper.xavier_to_jira(xavier_story)

        assert result['fields']['summary'] == 'Xavier Story'
        assert 'Story description' in result['fields']['description']
        assert result['fields']['priority']['name'] == 'High'
        assert result['fields']['customfield_10016'] == 5
        assert result['fields']['labels'] == ['feature', 'backend']

    def test_user_story_format_to_jira(self):
        """Test user story format conversion to Jira"""
        xavier_story = {
            'title': 'Story Title',
            'as_a': 'user',
            'i_want': 'to do something',
            'so_that': 'I get value',
            'priority': 'Medium'
        }

        mapper = FieldMapper()
        result = mapper.xavier_to_jira(xavier_story)

        description = result['fields']['description']
        assert 'As a user' in description
        assert 'I want to do something' in description
        assert 'So that I get value' in description

    def test_acceptance_criteria_to_jira(self):
        """Test acceptance criteria formatting for Jira"""
        xavier_story = {
            'title': 'Story',
            'priority': 'High',
            'acceptance_criteria': [
                'Criteria 1',
                'Criteria 2',
                'Criteria 3'
            ]
        }

        mapper = FieldMapper()
        result = mapper.xavier_to_jira(xavier_story)

        description = result['fields']['description']
        assert 'Acceptance Criteria:' in description
        assert '- Criteria 1' in description
        assert '- Criteria 2' in description
        assert '- Criteria 3' in description

    def test_reverse_priority_mapping(self):
        """Test reverse priority mapping from Xavier to Jira"""
        mapper = FieldMapper()

        assert mapper._reverse_map_priority('Critical') == 'Highest'
        assert mapper._reverse_map_priority('High') == 'High'
        assert mapper._reverse_map_priority('Medium') == 'Medium'
        assert mapper._reverse_map_priority('Low') == 'Low'
        assert mapper._reverse_map_priority(None) == 'Medium'


class TestCustomFieldMapping:
    """Test custom field mapping"""

    def test_custom_field_extraction(self):
        """Test extraction of custom fields"""
        custom_mappings = {
            'customfield_10001': 'epic_link',
            'customfield_10002': 'sprint'
        }

        mapper = FieldMapper(custom_mappings=custom_mappings)

        fields = {
            'customfield_10001': 'EPIC-123',
            'customfield_10002': 'Sprint 5',
            'customfield_10003': 'Ignored field'
        }

        custom_fields = mapper._extract_custom_fields(fields)

        assert custom_fields['epic_link'] == 'EPIC-123'
        assert custom_fields['sprint'] == 'Sprint 5'
        assert 'customfield_10003' not in custom_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=xavier.src.integrations.jira.field_mapper", "--cov-report=term-missing"])
