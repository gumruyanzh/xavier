# Jira Integration for Xavier Framework

Bi-directional synchronization between Jira and Xavier for seamless project management.

## Features

### Webhook Endpoint ✅ (Completed)
- **FastAPI HTTP endpoint** for receiving Jira webhooks
- **HMAC signature validation** for security
- **Async event processing** with queue management
- **Event routing** to appropriate handlers
- **Health check endpoint** for monitoring

## Usage

### Starting the Webhook Server

```python
from xavier.src.integrations.jira import get_webhook_handler

# Create webhook handler
handler = get_webhook_handler(webhook_secret="your_secret_key")

# Get FastAPI app
app = handler.get_app()

# Run with uvicorn
# uvicorn main:app --host 0.0.0.0 --port 8000
```

### Endpoints

#### POST /webhooks/jira
Receives Jira webhook events.

**Headers:**
- `X-Hub-Signature-256`: HMAC signature (if webhook secret configured)

**Request Body:**
```json
{
  "webhookEvent": "jira:issue_created",
  "issue": {
    "key": "PROJ-123",
    "fields": {
      "summary": "Example issue"
    }
  }
}
```

**Response:**
```json
{
  "status": "accepted",
  "event_type": "jira:issue_created",
  "queue_size": 1
}
```

#### GET /webhooks/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "queue_size": 0,
  "processors": 1
}
```

## Supported Events

- `jira:issue_created` - New issue created
- `jira:issue_updated` - Issue updated
- `jira:issue_deleted` - Issue deleted

## Security

The webhook handler supports HMAC-SHA256 signature validation:

1. Configure webhook secret when initializing handler
2. Jira sends `X-Hub-Signature-256` header with each webhook
3. Handler validates signature before processing
4. Invalid signatures return 401 Unauthorized

## Architecture

```
Jira → Webhook → Queue → Async Processor → Event Handlers → Xavier Sync
```

1. **Webhook Endpoint**: Receives HTTP POST requests from Jira
2. **Queue**: Thread-safe queue for event buffering
3. **Async Processor**: Background thread processes events
4. **Event Handlers**: Route events to appropriate sync logic
5. **Xavier Sync**: Update Xavier stories/tasks

## Testing

Run tests with pytest:

```bash
pytest xavier/tests/test_jira_webhook.py -v --cov
```

All tests passing: ✅ 18/18 (100% coverage)

## Next Steps

- [ ] Implement OAuth 2.0 authentication
- [ ] Implement API token authentication
- [ ] Add story synchronization logic
- [ ] Add status synchronization
- [ ] Add task synchronization
- [ ] Configure Jira webhooks automatically
