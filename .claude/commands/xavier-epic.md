---
description: Create a new epic to group related stories
argument-hint: <title> <description> [story_ids]
allowed-tools: Bash(python3:*), Write, Read
---

Create a new epic in Xavier to group related user stories:

```bash
python3 xavier_slash_command.py "/create-epic title='$1' description='$2' stories='${3:-}'"
```

The epic will be assigned a unique ID. You can optionally include comma-separated story IDs to add to the epic.