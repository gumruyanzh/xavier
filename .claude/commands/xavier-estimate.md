---
description: Estimate story points for backlog stories using AI
argument-hint: [story_ids]
allowed-tools: Bash(python3:*), Read, Task
---

Use Xavier's PM agent to automatically estimate story points for backlog stories:

```bash
python3 xavier_slash_command.py "/estimate story_ids='$ARGUMENTS'"
```

If no story IDs are provided, estimate all unestimated stories in the backlog.
Show the estimation results and total points.