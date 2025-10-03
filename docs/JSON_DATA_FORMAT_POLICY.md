# Xavier Framework JSON Data Format Policy

## Overview

Xavier Framework enforces a **strict JSON-only data format policy** for all data stored in the `.xavier/data` directory. This ensures consistency, machine-readability, and prevents format ambiguity.

## Policy Statement

**All data files in `.xavier/data` MUST be in JSON format. No exceptions.**

## Why JSON Only?

1. **Consistency**: Single format eliminates confusion
2. **Machine Readable**: Easy to parse and process programmatically
3. **Structured Data**: Enforces proper data structure
4. **Version Control**: Clean diffs in Git
5. **API Compatible**: Direct integration with REST APIs
6. **Cross-Platform**: Works identically on all operating systems

## Enforcement Mechanisms

### 1. Data Format Validator
Located at: `xavier/src/validators/data_format_validator.py`

- Validates all files are JSON format
- Detects and rejects Markdown content
- Automatically converts MD files to JSON
- Runs on every data operation

### 2. JSON Output Formatter
Located at: `xavier/src/utils/json_output_formatter.py`

- Ensures all command outputs are JSON
- Provides consistent formatting
- Prevents accidental Markdown generation

### 3. SCRUM Manager Integration
- Validates data format on save
- Rejects non-JSON data
- Automatic format enforcement

## Data Files

All data files in `.xavier/data/` are strictly JSON:

| File | Purpose | Format |
|------|---------|--------|
| `stories.json` | User stories | JSON object |
| `tasks.json` | Development tasks | JSON object |
| `bugs.json` | Bug reports | JSON object |
| `sprints.json` | Sprint data | JSON object |
| `epics.json` | Epic definitions | JSON object |
| `roadmaps.json` | Product roadmaps | JSON object |
| `backlog.json` | Product backlog | JSON array |

## Example Formats

### Story (JSON)
```json
{
  "id": "US-001",
  "title": "User Authentication",
  "as_a": "user",
  "i_want": "to log in",
  "so_that": "I can access my account",
  "acceptance_criteria": [
    "Login with email",
    "Password validation"
  ],
  "story_points": 5,
  "status": "backlog"
}
```

### Task (JSON)
```json
{
  "id": "TASK-001",
  "story_id": "US-001",
  "title": "Implement login API",
  "description": "Create REST endpoint for authentication",
  "estimated_hours": 8,
  "status": "pending",
  "assigned_to": "python-engineer"
}
```

## What NOT to Do

❌ **Never create Markdown files in data directory**
```markdown
## User Story US-001
**As a** user
**I want** to log in
```

❌ **Never mix formats**
```
stories.md  # Wrong!
tasks.txt   # Wrong!
bugs.yaml   # Wrong!
```

## Validation

Run validation at any time:

```python
from xavier.src.validators.data_format_validator import validate_xavier_data_format

# Returns True if all data is valid JSON
is_valid = validate_xavier_data_format()
```

Or from command line:
```bash
python3 test_json_format.py
```

## Migration

If you have existing Markdown files, the validator will:
1. Detect non-JSON files
2. Convert them to JSON automatically
3. Back up originals to `.backup_*` files
4. Report all changes

## Benefits

1. **Consistent API responses** - All commands return JSON
2. **Easy integration** - Direct parsing without format detection
3. **Reliable data storage** - No format ambiguity
4. **Better tooling** - JSON validators, linters, formatters
5. **Performance** - Faster parsing than Markdown

## Implementation Details

### Decorators
Use `@ensure_json_output` on any function that returns data:

```python
from xavier.src.utils.json_output_formatter import ensure_json_output

@ensure_json_output
def create_story(self, args):
    # Function automatically returns JSON
    return story_data
```

### Formatters
Use specific formatters for each data type:

```python
from xavier.src.utils.json_output_formatter import JSONOutputFormatter

# Format story data
json_output = JSONOutputFormatter.format_story_output(story_data)

# Format task data
json_output = JSONOutputFormatter.format_task_output(task_data)
```

## Compliance

All Xavier Framework components MUST comply with this policy:
- ✅ Command handlers
- ✅ Data managers
- ✅ API endpoints
- ✅ CLI outputs
- ✅ File operations

## Questions?

If you encounter any issues with JSON format enforcement, check:
1. Validator is initialized in SCRUM manager
2. Formatters are imported in command handlers
3. Data directory contains only `.json` files
4. All outputs are valid JSON

---

**Policy Version**: 1.0.0
**Effective Date**: October 2025
**Last Updated**: October 3, 2025