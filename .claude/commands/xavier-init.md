---
description: Initialize Xavier Framework in the current project
argument-hint: <project-name> [type] [stack]
allowed-tools: Bash(python3:*), Write, Read
---

Initialize Xavier Framework for the project using the following command:

```bash
python3 xavier_slash_command.py "/xavier-init name='$1' type='${2:-web}' stack='${3:-python}'"
```

If successful, provide a summary of the project initialization and next steps for the user.