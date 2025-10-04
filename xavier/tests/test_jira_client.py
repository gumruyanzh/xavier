"""
Tests for Jira API Client
Tests webhook configuration, authentication, and API operations
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import HTTPError

from xavier.src.integrations.jira.jira_client import (
    JiraClient,
    JiraAuthenticationError,
    JiraAPIError
)


class TestJiraClientInitialization:
    """Test Jira client initialization"""

    def test_init_with_api_token(self):
        """Test initialization with API token"""
        client = JiraClient(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test_token"
        )

        assert client.jira_url == "https://test.atlassian.net"
        assert client.email == "test@example.com"
        assert client.api_token == "test_token"
        assert client.auth_type == "api_token"
        assert client.session.auth is not None

    def test_init_with_oauth(self):
        """Test initialization with OAuth token"""
        client = JiraClient(
            jira_url="https://test.atlassian.net",
            oauth_token="oauth_token_123"
        )

        assert client.oauth_token == "oauth_token_123"
        assert client.auth_type == "oauth"
        assert "Authorization" in client.session.headers

    def test_init_strips_trailing_slash(self):
        """Test URL trailing slash is removed"""
        client = JiraClient(jira_url="https://test.atlassian.net/")

        assert client.jira_url == "https://test.atlassian.net"


class TestJiraClientConnectionTest:
    """Test Jira connection testing"""

    @patch('xavier.src.integrations.jira.jira_client.requests.Session.get')
    def test_connection_success(self, mock_get):
        """Test successful connection"""
        mock_response = Mock()
        mock_response.json.return_value = {"displayName": "Test User", "emailAddress": "test@example.com"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = JiraClient(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test_token"
        )

        assert client.test_connection() is True

    @patch('xavier.src.integrations.jira.jira_client.requests.Session.get')
    def test_connection_authentication_failure(self, mock_get):
        """Test connection with invalid credentials"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        client = JiraClient(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="invalid_token"
        )

        with pytest.raises(JiraAuthenticationError):
            client.test_connection()

    @patch('xavier.src.integrations.jira.jira_client.requests.Session.get')
    def test_connection_api_error(self, mock_get):
        """Test connection with API error"""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        client = JiraClient(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test_token"
        )

        with pytest.raises(JiraAPIError):
            client.test_connection()


class TestJiraWebhookConfiguration:
    """Test Jira webhook configuration"""

    @patch('xavier.src.integrations.jira.jira_client.requests.Session.post')
    def test_create_webhook_success(self, mock_post):
        """Test successful webhook creation"""
        webhook_response = {
            "id": 12345,
            "name": "Test Webhook",
            "url": "https://webhook.example.com",
            "events": ["jira:issue_created"],
            "enabled": True
        }

        mock_response = Mock()
        mock_response.json.return_value = webhook_response
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        client = JiraClient(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test_token"
        )

        result = client.create_webhook(
            name="Test Webhook",
            webhook_url="https://webhook.example.com",
            events=["jira:issue_created"]
        )

        assert result["id"] == 12345
        assert result["name"] == "Test Webhook"
        assert result["url"] == "https://webhook.example.com"

    @patch('xavier.src.integrations.jira.jira_client.requests.Session.post')
    def test_configure_xavier_webhook(self, mock_post):
        """Test configuring Xavier-specific webhook"""
        webhook_response = {
            "id": 12345,
            "name": "Xavier Framework Integration",
            "url": "https://xavier.example.com/webhooks/jira",
            "events": [
                "jira:issue_created",
                "jira:issue_updated",
                "jira:issue_deleted",
                "comment_created",
                "comment_updated"
            ],
            "enabled": True
        }

        mock_response = Mock()
        mock_response.json.return_value = webhook_response
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        client = JiraClient(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test_token"
        )

        result = client.configure_xavier_webhook(
            xavier_webhook_url="https://xavier.example.com/webhooks/jira"
        )

        assert result["id"] == 12345
        assert result["name"] == "Xavier Framework Integration"
        assert len(result["events"]) == 5
        assert "jira:issue_created" in result["events"]
        assert "jira:issue_updated" in result["events"]
        assert "jira:issue_deleted" in result["events"]

    @patch('xavier.src.integrations.jira.jira_client.requests.Session.get')
    def test_list_webhooks(self, mock_get):
        """Test listing all webhooks"""
        webhooks_response = [
            {"id": 1, "name": "Webhook 1", "url": "https://webhook1.example.com"},
            {"id": 2, "name": "Webhook 2", "url": "https://webhook2.example.com"}
        ]

        mock_response = Mock()
        mock_response.json.return_value = webhooks_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = JiraClient(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test_token"
        )

        result = client.list_webhooks()

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    @patch('xavier.src.integrations.jira.jira_client.requests.Session.delete')
    def test_delete_webhook(self, mock_delete):
        """Test deleting webhook"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        client = JiraClient(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test_token"
        )

        result = client.delete_webhook(12345)

        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=xavier.src.integrations.jira.jira_client", "--cov-report=term-missing"])
