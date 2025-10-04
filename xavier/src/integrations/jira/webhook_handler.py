"""
Jira Webhook Handler
Receives and processes Jira webhook events for Xavier Framework
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from queue import Queue
from threading import Thread
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import hashlib
import hmac

logger = logging.getLogger(__name__)


class WebhookQueue:
    """Thread-safe queue for webhook event processing"""

    def __init__(self, max_size: int = 1000):
        self.queue = Queue(maxsize=max_size)
        self.processing = False

    def add(self, event: Dict[str, Any]) -> bool:
        """Add event to processing queue"""
        try:
            self.queue.put(event, block=False)
            return True
        except:
            logger.error("Webhook queue full, dropping event")
            return False

    def get(self) -> Optional[Dict[str, Any]]:
        """Get next event from queue"""
        if not self.queue.empty():
            return self.queue.get()
        return None

    def size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()


class JiraWebhookHandler:
    """
    Handles Jira webhook events with async processing

    Features:
    - FastAPI endpoint for receiving webhooks
    - Signature validation for security
    - Async event processing with queue management
    - Event logging and monitoring
    """

    def __init__(self, webhook_secret: Optional[str] = None):
        """
        Initialize webhook handler

        Args:
            webhook_secret: Secret key for webhook signature validation
        """
        self.app = FastAPI(title="Xavier Jira Webhook Handler")
        self.webhook_secret = webhook_secret
        self.queue = WebhookQueue()
        self.processors = []

        # Setup routes
        self._setup_routes()

        # Start background processor
        self._start_processor()

        logger.info("Jira Webhook Handler initialized")

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.post("/webhooks/jira")
        async def receive_jira_webhook(
            request: Request,
            background_tasks: BackgroundTasks
        ):
            """Receive Jira webhook event"""
            try:
                # Get request body
                body = await request.body()
                payload = await request.json()

                # Validate signature if secret is configured
                if self.webhook_secret:
                    signature = request.headers.get('X-Hub-Signature-256', '')
                    if not self._validate_signature(body, signature):
                        logger.warning(f"Invalid webhook signature from {request.client.host}")
                        raise HTTPException(status_code=401, detail="Invalid signature")

                # Extract event type
                event_type = payload.get('webhookEvent', 'unknown')

                # Create event object
                event = {
                    'event_type': event_type,
                    'timestamp': datetime.now().isoformat(),
                    'payload': payload,
                    'source_ip': request.client.host if request.client else 'unknown'
                }

                # Add to processing queue
                if self.queue.add(event):
                    logger.info(f"Received Jira webhook: {event_type}")

                    # Process in background
                    background_tasks.add_task(self._process_event, event)

                    return JSONResponse({
                        'status': 'accepted',
                        'event_type': event_type,
                        'queue_size': self.queue.size()
                    })
                else:
                    logger.error("Failed to queue webhook event")
                    raise HTTPException(status_code=503, detail="Queue full")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/webhooks/health")
        async def health_check():
            """Health check endpoint"""
            return JSONResponse({
                'status': 'healthy',
                'queue_size': self.queue.size(),
                'processors': len(self.processors)
            })

    def _validate_signature(self, body: bytes, signature: str) -> bool:
        """
        Validate webhook signature

        Args:
            body: Raw request body
            signature: Signature from X-Hub-Signature-256 header

        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            return True

        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        expected = f"sha256={expected_signature}"
        return hmac.compare_digest(expected, signature)

    async def _process_event(self, event: Dict[str, Any]):
        """
        Process webhook event asynchronously

        Args:
            event: Webhook event data
        """
        event_type = event['event_type']
        payload = event['payload']

        try:
            # Route event to appropriate handler
            if event_type == 'jira:issue_created':
                await self._handle_issue_created(payload)
            elif event_type == 'jira:issue_updated':
                await self._handle_issue_updated(payload)
            elif event_type == 'jira:issue_deleted':
                await self._handle_issue_deleted(payload)
            else:
                logger.info(f"Unhandled event type: {event_type}")

            logger.info(f"Processed event: {event_type}")

        except Exception as e:
            logger.error(f"Error processing event {event_type}: {e}")

    async def _handle_issue_created(self, payload: Dict[str, Any]):
        """Handle issue created event"""
        issue = payload.get('issue', {})
        issue_key = issue.get('key')

        logger.info(f"Jira issue created: {issue_key}")

        # TODO: Sync to Xavier stories
        # This will be implemented in story sync task

    async def _handle_issue_updated(self, payload: Dict[str, Any]):
        """Handle issue updated event"""
        issue = payload.get('issue', {})
        issue_key = issue.get('key')

        logger.info(f"Jira issue updated: {issue_key}")

        # TODO: Sync updates to Xavier
        # This will be implemented in status sync task

    async def _handle_issue_deleted(self, payload: Dict[str, Any]):
        """Handle issue deleted event"""
        issue = payload.get('issue', {})
        issue_key = issue.get('key')

        logger.info(f"Jira issue deleted: {issue_key}")

        # TODO: Handle deletion in Xavier

    def _start_processor(self):
        """Start background event processor"""
        def processor_loop():
            while True:
                event = self.queue.get()
                if event:
                    asyncio.run(self._process_event(event))

        processor_thread = Thread(target=processor_loop, daemon=True)
        processor_thread.start()
        self.processors.append(processor_thread)

    def register_event_handler(self, event_type: str, handler):
        """Register custom event handler"""
        # TODO: Implement custom handler registration
        pass

    def get_app(self) -> FastAPI:
        """Get FastAPI application instance"""
        return self.app


# Singleton instance
_handler_instance: Optional[JiraWebhookHandler] = None


def get_webhook_handler(webhook_secret: Optional[str] = None) -> JiraWebhookHandler:
    """Get or create webhook handler singleton"""
    global _handler_instance

    if _handler_instance is None:
        _handler_instance = JiraWebhookHandler(webhook_secret)

    return _handler_instance
