---
description: View and manage the product backlog
argument-hint: [action] [filter]
allowed-tools: Bash(python3:*), Read
---

Manage the Xavier product backlog:

```bash
python3 xavier_slash_command.py "/backlog action='${1:-view}' filter='${2:-}'"
```

Actions:
- view: Display backlog stories
- prioritize: Reorder stories by priority
- groom: Clean up and refine stories

Filters:
- unestimated: Show only unestimated stories
- ready: Show only estimated stories
- blocked: Show blocked stories