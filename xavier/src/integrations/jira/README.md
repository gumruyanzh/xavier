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

## Jira Webhook Configuration ✅ (Completed)

### JiraClient

Full-featured Jira API client with webhook management.

**Authentication Methods:**
- API Token (HTTPBasicAuth)
- OAuth 2.0 (Bearer token)

**Webhook Operations:**
- Create webhooks with event filtering
- List all configured webhooks
- Get specific webhook details
- Update existing webhooks
- Delete webhooks
- One-click Xavier integration setup

### Quick Start: Configure Xavier Webhook

```python
from xavier.src.integrations.jira import JiraClient

# Initialize client with API token
client = JiraClient(
    jira_url="https://your-domain.atlassian.net",
    email="your@email.com",
    api_token="your_api_token"
)

# Test connection
client.test_connection()

# Configure Xavier webhook (one command!)
webhook = client.configure_xavier_webhook(
    xavier_webhook_url="https://your-xavier-instance.com/webhooks/jira"
)

print(f"Webhook created with ID: {webhook['id']}")
```

### Manual Webhook Configuration

For more control, create webhooks manually:

```python
# Create custom webhook
webhook = client.create_webhook(
    name="My Custom Webhook",
    webhook_url="https://example.com/webhook",
    events=[
        "jira:issue_created",
        "jira:issue_updated",
        "jira:issue_deleted"
    ],
    filters={"issue-related-events-section": "project = MYPROJECT"},
    exclude_body=False
)

# List all webhooks
webhooks = client.list_webhooks()
for wh in webhooks:
    print(f"{wh['id']}: {wh['name']}")

# Update webhook
updated = client.update_webhook(
    webhook_id=12345,
    name="New Name",
    url="https://new-url.com/webhook",
    enabled=True
)

# Delete webhook
client.delete_webhook(webhook_id=12345)
```

### Supported Events

- `jira:issue_created` - New issue created
- `jira:issue_updated` - Issue fields updated
- `jira:issue_deleted` - Issue deleted
- `comment_created` - Comment added to issue
- `comment_updated` - Comment edited

### Error Handling

```python
from xavier.src.integrations.jira import JiraAuthenticationError, JiraAPIError

try:
    client.test_connection()
except JiraAuthenticationError:
    print("Invalid credentials")
except JiraAPIError as e:
    print(f"API error: {e}")
```

## Next Steps

- [ ] Implement OAuth 2.0 authentication flow
- [ ] Add story synchronization logic
- [ ] Add status synchronization
- [ ] Add task synchronization
- [x] Configure Jira webhooks automatically ✅
