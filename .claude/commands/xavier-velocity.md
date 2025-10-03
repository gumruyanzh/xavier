---
description: Show team velocity and sprint metrics
argument-hint: [num_sprints]
allowed-tools: Bash(python3:*), Read
---

Display team velocity metrics and sprint performance data:

```bash
python3 xavier_slash_command.py "/velocity sprints='${1:-3}'"
```

Analyzes the specified number of past sprints to calculate average velocity, trend, and performance metrics.