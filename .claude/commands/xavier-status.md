---
description: Show Xavier project status and metrics
argument-hint: [verbose]
allowed-tools: Bash(python3:*), Read
---

Display Xavier project status, including sprint information, backlog summary, and agent configuration:

```bash
python3 xavier_slash_command.py "/xavier-status verbose='${1:-false}'"
```

Show project overview, active sprint, backlog metrics, and available agents.