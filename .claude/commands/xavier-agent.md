---
description: Create a custom Xavier agent with specific skills
argument-hint: <name> <skills> [tools] [color] [emoji]
allowed-tools: Bash(python3:*), Write, Read
---

Create a custom Xavier agent with the specified skills and configuration:

```bash
python3 xavier_slash_command.py "/create-agent name='$1' skills='$2' tools='${3:-Read,Write,Edit,Bash}' color='${4:-blue}' emoji='${5:-🤖}'"
```

Confirm agent creation and show its capabilities.