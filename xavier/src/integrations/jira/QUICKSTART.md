# Jira Integration Quick Start Guide

Get started with Xavier-Jira integration in 5 minutes.

## Prerequisites

- Jira Cloud account
- Xavier Framework installed
- Python 3.8+

## 1. Get Jira API Token (2 minutes)

1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Name: `Xavier Integration`
4. **Copy the token** (you won't see it again!)

## 2. Basic Setup (1 minute)

```python
from xavier.src.integrations.jira import (
    JiraClient,
    get_jira_config,
    get_story_sync_manager
)

# Initialize Jira client
client = JiraClient(
    jira_url="https://your-domain.atlassian.net",
    email="your@email.com",
    api_token="paste_your_token_here"
)

# Test connection
if client.test_connection():
    print("✅ Connected!")
```

## 3. Initialize Configuration (30 seconds)

```python
# Create default configuration
config = get_jira_config()
config.initialize_default_config()
config.save_config()

print("✅ Configuration saved to .xavier/jira_config.json")
```

## 4. Sync Your First Story (30 seconds)

```python
# Create sync manager
sync_manager = get_story_sync_manager(jira_client=client)

# Sync a Jira issue to Xavier
story = sync_manager.sync_jira_to_xavier("PROJ-123")
print(f"✅ Created story: {story['title']}")
```

## 5. Setup Webhook (Optional - 1 minute)

For real-time sync when Jira issues change:

```python
# Configure webhook in Jira
webhook = client.configure_xavier_webhook(
    xavier_webhook_url="https://your-server.com/webhooks/jira"
)
print(f"✅ Webhook ID: {webhook['id']}")
```

## Common Tasks

### Sync Multiple Issues

```python
issue_keys = ["PROJ-123", "PROJ-124", "PROJ-125"]

for key in issue_keys:
    story = sync_manager.sync_jira_to_xavier(key)
    print(f"✅ {key} → {story['id']}")
```

### Update Xavier Story in Jira

```python
# Sync Xavier story back to Jira
sync_manager.sync_xavier_to_jira("US-ABC123")
print("✅ Story updated in Jira")
```

### Bi-directional Sync

```python
result = sync_manager.sync_story_metadata(
    story_id="US-ABC123",
    jira_issue_key="PROJ-123",
    direction="both"
)
print("✅ Synced both ways")
```

### Configure Custom Fields

```python
# Map your Jira custom fields
config.set_custom_field_mapping('customfield_10020', 'story_points')
config.set_custom_field_mapping('customfield_10001', 'epic_link')
config.save_config()
```

### Set Project Mapping

```python
# Map Xavier project to Jira project
config.set_project_mapping('my-xavier-project', 'PROJ')
config.save_config()
```

## Troubleshooting

### Authentication Failed?

```python
try:
    client.test_connection()
except Exception as e:
    print(f"Error: {e}")
    # Check: email, API token, Jira URL
```

### Can't find custom fields?

```python
# Inspect a Jira issue
issue = client.get_issue("PROJ-123")
for field, value in issue['fields'].items():
    if field.startswith('customfield_'):
        print(f"{field}: {value}")
```

### Sync not working?

```python
# Check sync log
log = sync_manager.get_sync_log()
for entry in log:
    print(entry)
```

## Next Steps

- 📖 Read [README.md](./README.md) for complete documentation
- 🧪 Run tests: `pytest xavier/tests/test_jira*.py -v`
- ⚙️ Customize `.xavier/jira_config.json`
- 🔄 Setup webhook for real-time sync

## Configuration File Reference

`.xavier/jira_config.json`:

```json
{
  "custom_field_mappings": {
    "customfield_10016": "story_points",
    "customfield_10001": "epic_link"
  },
  "project_mappings": {
    "xavier-project": "PROJ"
  },
  "sync_preferences": {
    "auto_sync": true,
    "sync_direction": "both",
    "conflict_resolution": "jira_wins"
  },
  "field_mappings": {
    "story_points_field": "customfield_10016",
    "epic_link_field": "customfield_10001",
    "sprint_field": "customfield_10002"
  }
}
```

## Complete Example Script

Save as `sync_jira.py`:

```python
#!/usr/bin/env python3
from xavier.src.integrations.jira import (
    JiraClient,
    get_jira_config,
    get_story_sync_manager
)

# Configuration
JIRA_URL = "https://your-domain.atlassian.net"
EMAIL = "your@email.com"
API_TOKEN = "your_api_token"

def main():
    # 1. Connect to Jira
    client = JiraClient(
        jira_url=JIRA_URL,
        email=EMAIL,
        api_token=API_TOKEN
    )

    if not client.test_connection():
        print("❌ Connection failed")
        return

    print("✅ Connected to Jira")

    # 2. Initialize config
    config = get_jira_config()
    config.initialize_default_config()
    config.save_config()
    print("✅ Configuration initialized")

    # 3. Create sync manager
    sync_manager = get_story_sync_manager(jira_client=client)

    # 4. Sync issues
    issues = ["PROJ-123", "PROJ-124"]

    for issue_key in issues:
        try:
            story = sync_manager.sync_jira_to_xavier(issue_key)
            print(f"✅ {issue_key} → {story['id']}: {story['title']}")
        except Exception as e:
            print(f"❌ {issue_key}: {e}")

    # 5. Show sync log
    print("\n📊 Sync Log:")
    for entry in sync_manager.get_sync_log():
        print(f"  {entry['timestamp']}: {entry['source_id']} → {entry['target_id']}")

if __name__ == "__main__":
    main()
```

Run it:
```bash
chmod +x sync_jira.py
python3 sync_jira.py
```

---

Need help? Check the [full documentation](./README.md) or run the tests to see examples.
