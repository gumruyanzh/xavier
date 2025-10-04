"""
Jira API Client
Handles communication with Jira REST API
"""

import logging
import requests
from typing import Dict, Any, Optional, List
from requests.auth import HTTPBasicAuth
import base64

logger = logging.getLogger(__name__)


class JiraAuthenticationError(Exception):
    """Raised when Jira authentication fails"""
    pass


class JiraAPIError(Exception):
    """Raised when Jira API request fails"""
    pass


class JiraClient:
    """
    Jira API client for Xavier Framework

    Handles:
    - Authentication (OAuth 2.0 and API tokens)
    - Story/Issue synchronization
    - Webhook configuration
    """

    def __init__(
        self,
        jira_url: str,
        email: Optional[str] = None,
        api_token: Optional[str] = None,
        oauth_token: Optional[str] = None
    ):
        """
        Initialize Jira client

        Args:
            jira_url: Jira instance URL (e.g., https://your-domain.atlassian.net)
            email: User email for API token auth
            api_token: API token for authentication
            oauth_token: OAuth 2.0 token
        """
        self.jira_url = jira_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.oauth_token = oauth_token
        self.session = requests.Session()

        # Setup authentication
        if api_token and email:
            self.session.auth = HTTPBasicAuth(email, api_token)
            self.auth_type = 'api_token'
        elif oauth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {oauth_token}'
            })
            self.auth_type = 'oauth'
        else:
            self.auth_type = None

        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        logger.info(f"Jira client initialized for {self.jira_url} with {self.auth_type} auth")

    def test_connection(self) -> bool:
        """
        Test connection to Jira

        Returns:
            True if connection successful

        Raises:
            JiraAuthenticationError: If authentication fails
            JiraAPIError: If connection fails
        """
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/myself")
            response.raise_for_status()

            user_data = response.json()
            logger.info(f"Successfully connected to Jira as {user_data.get('displayName')}")
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise JiraAuthenticationError("Invalid credentials")
            raise JiraAPIError(f"Connection test failed: {e}")
        except Exception as e:
            raise JiraAPIError(f"Connection test failed: {e}")

    def create_webhook(
        self,
        name: str,
        webhook_url: str,
        events: List[str],
        filters: Optional[Dict[str, Any]] = None,
        exclude_body: bool = False
    ) -> Dict[str, Any]:
        """
        Create Jira webhook

        Args:
            name: Webhook name
            webhook_url: URL to receive webhooks
            events: List of events to subscribe to (e.g., ['jira:issue_created'])
            filters: Optional JQL filter for events
            exclude_body: If True, only send event metadata

        Returns:
            Webhook configuration with id, name, url, events

        Raises:
            JiraAPIError: If webhook creation fails
        """
        payload = {
            'name': name,
            'url': webhook_url,
            'events': events,
            'excludeBody': exclude_body
        }

        if filters:
            payload['filters'] = filters

        try:
            response = self.session.post(
                f"{self.jira_url}/rest/webhooks/1.0/webhook",
                json=payload
            )
            response.raise_for_status()

            webhook = response.json()
            logger.info(f"Created Jira webhook '{name}' with ID {webhook.get('id')}")
            return webhook

        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create webhook: {e.response.text}")
            raise JiraAPIError(f"Webhook creation failed: {e}")
        except Exception as e:
            raise JiraAPIError(f"Webhook creation failed: {e}")

    def list_webhooks(self) -> List[Dict[str, Any]]:
        """
        List all webhooks

        Returns:
            List of webhook configurations

        Raises:
            JiraAPIError: If listing fails
        """
        try:
            response = self.session.get(
                f"{self.jira_url}/rest/webhooks/1.0/webhook"
            )
            response.raise_for_status()

            webhooks = response.json()
            logger.info(f"Found {len(webhooks)} webhooks")
            return webhooks

        except Exception as e:
            raise JiraAPIError(f"Failed to list webhooks: {e}")

    def get_webhook(self, webhook_id: int) -> Dict[str, Any]:
        """
        Get webhook by ID

        Args:
            webhook_id: Webhook ID

        Returns:
            Webhook configuration

        Raises:
            JiraAPIError: If webhook not found
        """
        try:
            response = self.session.get(
                f"{self.jira_url}/rest/webhooks/1.0/webhook/{webhook_id}"
            )
            response.raise_for_status()

            webhook = response.json()
            logger.info(f"Retrieved webhook {webhook_id}: {webhook.get('name')}")
            return webhook

        except Exception as e:
            raise JiraAPIError(f"Failed to get webhook: {e}")

    def update_webhook(
        self,
        webhook_id: int,
        name: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update existing webhook

        Args:
            webhook_id: Webhook ID
            name: New webhook name
            url: New webhook URL
            events: New event list
            enabled: Enable/disable webhook

        Returns:
            Updated webhook configuration

        Raises:
            JiraAPIError: If update fails
        """
        # Get current webhook config
        current = self.get_webhook(webhook_id)

        # Update fields
        payload = {
            'name': name or current.get('name'),
            'url': url or current.get('url'),
            'events': events or current.get('events'),
            'enabled': enabled if enabled is not None else current.get('enabled', True)
        }

        try:
            response = self.session.put(
                f"{self.jira_url}/rest/webhooks/1.0/webhook/{webhook_id}",
                json=payload
            )
            response.raise_for_status()

            webhook = response.json()
            logger.info(f"Updated webhook {webhook_id}")
            return webhook

        except Exception as e:
            raise JiraAPIError(f"Failed to update webhook: {e}")

    def delete_webhook(self, webhook_id: int) -> bool:
        """
        Delete webhook

        Args:
            webhook_id: Webhook ID

        Returns:
            True if deleted successfully

        Raises:
            JiraAPIError: If deletion fails
        """
        try:
            response = self.session.delete(
                f"{self.jira_url}/rest/webhooks/1.0/webhook/{webhook_id}"
            )
            response.raise_for_status()

            logger.info(f"Deleted webhook {webhook_id}")
            return True

        except Exception as e:
            raise JiraAPIError(f"Failed to delete webhook: {e}")

    def configure_xavier_webhook(
        self,
        xavier_webhook_url: str,
        webhook_name: str = "Xavier Framework Integration"
    ) -> Dict[str, Any]:
        """
        Configure Jira webhook for Xavier integration

        Sets up webhook with all necessary events for Xavier sync:
        - jira:issue_created
        - jira:issue_updated
        - jira:issue_deleted

        Args:
            xavier_webhook_url: Xavier webhook endpoint URL
            webhook_name: Name for the webhook

        Returns:
            Created webhook configuration

        Raises:
            JiraAPIError: If configuration fails
        """
        events = [
            'jira:issue_created',
            'jira:issue_updated',
            'jira:issue_deleted',
            'comment_created',
            'comment_updated'
        ]

        logger.info(f"Configuring Xavier webhook at {xavier_webhook_url}")

        return self.create_webhook(
            name=webhook_name,
            webhook_url=xavier_webhook_url,
            events=events,
            exclude_body=False
        )

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get Jira issue by key"""
        # TODO: Implement in story sync task
        return {}

    def create_issue(self, project_key: str, summary: str, **kwargs) -> Dict[str, Any]:
        """Create Jira issue"""
        # TODO: Implement in story sync task
        return {}

    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """Update Jira issue"""
        # TODO: Implement in story sync task
        return True
