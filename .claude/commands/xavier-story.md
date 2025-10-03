---
description: Create a new user story in the backlog
argument-hint: <title> <as_a> <i_want> <so_that> [points]
allowed-tools: Bash(python3:*), Write, Read
---

Create a new user story in the Xavier backlog. Parse the arguments and execute:

```bash
python3 xavier_slash_command.py "/create-story title='$1' as_a='$2' i_want='$3' so_that='$4' points='${5:-0}'"
```

Show the story ID and confirm creation to the user.