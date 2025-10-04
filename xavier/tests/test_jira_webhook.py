"""
Tests for Jira Webhook Handler
Ensures webhook endpoint works correctly with async processing
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import hashlib
import hmac

from xavier.src.integrations.jira.webhook_handler import (
    JiraWebhookHandler,
    WebhookQueue,
    get_webhook_handler
)


class TestWebhookQueue:
    """Test webhook queue functionality"""

    def test_queue_creation(self):
        """Test queue is created with correct max size"""
        queue = WebhookQueue(max_size=100)
        assert queue.queue.maxsize == 100
        assert queue.size() == 0

    def test_add_event(self):
        """Test adding event to queue"""
        queue = WebhookQueue()
        event = {'type': 'test', 'data': 'test_data'}

        assert queue.add(event) is True
        assert queue.size() == 1

    def test_get_event(self):
        """Test getting event from queue"""
        queue = WebhookQueue()
        event = {'type': 'test', 'data': 'test_data'}

        queue.add(event)
        retrieved = queue.get()

        assert retrieved == event
        assert queue.size() == 0

    def test_get_empty_queue(self):
        """Test getting from empty queue returns None"""
        queue = WebhookQueue()
        assert queue.get() is None

    def test_queue_full(self):
        """Test queue handles full condition"""
        queue = WebhookQueue(max_size=2)

        assert queue.add({'event': 1}) is True
        assert queue.add({'event': 2}) is True
        assert queue.add({'event': 3}) is False  # Queue full


class TestJiraWebhookHandler:
    """Test Jira webhook handler"""

    def test_handler_initialization(self):
        """Test handler initializes correctly"""
        handler = JiraWebhookHandler(webhook_secret="test_secret")

        assert handler.webhook_secret == "test_secret"
        assert handler.queue is not None
        assert handler.app is not None

    def test_signature_validation_with_secret(self):
        """Test webhook signature validation"""
        secret = "test_secret"
        handler = JiraWebhookHandler(webhook_secret=secret)

        body = b'{"test": "data"}'
        signature = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        full_signature = f"sha256={signature}"

        assert handler._validate_signature(body, full_signature) is True

    def test_signature_validation_invalid(self):
        """Test invalid signature is rejected"""
        handler = JiraWebhookHandler(webhook_secret="test_secret")

        body = b'{"test": "data"}'
        invalid_signature = "sha256=invalid"

        assert handler._validate_signature(body, invalid_signature) is False

    def test_signature_validation_no_secret(self):
        """Test validation passes when no secret configured"""
        handler = JiraWebhookHandler()

        body = b'{"test": "data"}'
        signature = "any_signature"

        assert handler._validate_signature(body, signature) is True

    def test_webhook_endpoint_accepts_valid_request(self):
        """Test webhook endpoint accepts valid requests"""
        handler = JiraWebhookHandler()
        client = TestClient(handler.app)

        payload = {
            'webhookEvent': 'jira:issue_created',
            'issue': {
                'key': 'PROJ-123',
                'fields': {
                    'summary': 'Test Issue'
                }
            }
        }

        response = client.post("/webhooks/jira", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'accepted'
        assert data['event_type'] == 'jira:issue_created'

    def test_webhook_endpoint_rejects_invalid_signature(self):
        """Test webhook rejects invalid signature"""
        handler = JiraWebhookHandler(webhook_secret="test_secret")
        client = TestClient(handler.app)

        payload = {'webhookEvent': 'jira:issue_created'}

        response = client.post(
            "/webhooks/jira",
            json=payload,
            headers={'X-Hub-Signature-256': 'sha256=invalid'}
        )

        assert response.status_code == 401

    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        handler = JiraWebhookHandler()
        client = TestClient(handler.app)

        response = client.get("/webhooks/health")

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'queue_size' in data

    @pytest.mark.asyncio
    async def test_issue_created_handler(self):
        """Test issue created event handler"""
        handler = JiraWebhookHandler()

        payload = {
            'issue': {
                'key': 'PROJ-123',
                'fields': {'summary': 'New Issue'}
            }
        }

        # Should not raise exception
        await handler._handle_issue_created(payload)

    @pytest.mark.asyncio
    async def test_issue_updated_handler(self):
        """Test issue updated event handler"""
        handler = JiraWebhookHandler()

        payload = {
            'issue': {
                'key': 'PROJ-123',
                'fields': {'summary': 'Updated Issue'}
            }
        }

        # Should not raise exception
        await handler._handle_issue_updated(payload)

    @pytest.mark.asyncio
    async def test_issue_deleted_handler(self):
        """Test issue deleted event handler"""
        handler = JiraWebhookHandler()

        payload = {
            'issue': {
                'key': 'PROJ-123'
            }
        }

        # Should not raise exception
        await handler._handle_issue_deleted(payload)

    @pytest.mark.asyncio
    async def test_process_event_routing(self):
        """Test event routing to correct handlers"""
        handler = JiraWebhookHandler()

        # Test issue created routing
        event = {
            'event_type': 'jira:issue_created',
            'payload': {'issue': {'key': 'PROJ-123'}}
        }

        with patch.object(handler, '_handle_issue_created', new=AsyncMock()) as mock:
            await handler._process_event(event)
            mock.assert_called_once()

        # Test issue updated routing
        event = {
            'event_type': 'jira:issue_updated',
            'payload': {'issue': {'key': 'PROJ-123'}}
        }

        with patch.object(handler, '_handle_issue_updated', new=AsyncMock()) as mock:
            await handler._process_event(event)
            mock.assert_called_once()

    def test_get_app(self):
        """Test getting FastAPI app instance"""
        handler = JiraWebhookHandler()
        app = handler.get_app()

        assert app is not None
        assert app == handler.app

    def test_singleton_handler(self):
        """Test webhook handler singleton pattern"""
        handler1 = get_webhook_handler("secret1")
        handler2 = get_webhook_handler("secret2")

        assert handler1 is handler2  # Same instance


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=xavier.src.integrations.jira.webhook_handler", "--cov-report=term-missing"])
