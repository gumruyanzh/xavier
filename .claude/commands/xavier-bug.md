---
description: Report and track bugs
argument-hint: <title> <description> [priority] [component]
allowed-tools: Bash(python3:*), Write, Read
---

Report a bug in the Xavier bug tracking system:

```bash
python3 xavier_slash_command.py "/bug title='$1' description='$2' priority='${3:-medium}' component='${4:-unknown}'"
```

Priority levels: low, medium, high, critical
The bug will be assigned a unique ID and added to the tracking system.