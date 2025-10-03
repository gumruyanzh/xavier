---
description: Start working on a specific task with the appropriate agent
argument-hint: <task_id> [agent]
allowed-tools: Bash(python3:*), Read, Task
---

Start working on a Xavier task with the appropriate agent:

```bash
python3 xavier_slash_command.py "/start-task task_id='$1' agent='${2:-}'"
```

If no agent is specified, Xavier will auto-select the best agent for the task.
The agent will begin working on the task implementation.