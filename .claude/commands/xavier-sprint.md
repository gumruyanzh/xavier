---
description: Manage sprints (create, start, end, status)
argument-hint: <action> [name] [duration]
allowed-tools: Bash(python3:*), Write, Read
---

Manage Xavier sprints based on the action specified:

```bash
python3 xavier_slash_command.py "/sprint action='$1' name='${2:-}' duration='${3:-14}'"
```

Actions available:
- create: Create a new sprint
- start: Start the current sprint
- end: End the active sprint
- status: Show sprint status

Provide appropriate feedback based on the action performed.