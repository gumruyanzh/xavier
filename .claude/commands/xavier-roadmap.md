---
description: View or manage the project roadmap
argument-hint: [action] [milestone] [date]
allowed-tools: Bash(python3:*), Write, Read
---

Manage the Xavier project roadmap and milestones:

```bash
python3 xavier_slash_command.py "/roadmap action='${1:-view}' milestone='${2:-}' date='${3:-}'"
```

Actions:
- view: Display current roadmap
- add: Add a new milestone (requires milestone name and date)
- update: Update existing milestone

Date format: YYYY-MM-DD