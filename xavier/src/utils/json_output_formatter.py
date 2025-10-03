"""
Xavier JSON Output Formatter
Ensures all command outputs are in JSON format, never markdown
"""

import json
from typing import Any, Dict, Union


class JSONOutputFormatter:
    """Formats all Xavier command outputs as JSON"""

    @staticmethod
    def format_story_output(story_data: Dict[str, Any]) -> str:
        """Format story creation output as JSON"""
        output = {
            "type": "story",
            "id": story_data.get("story_id", story_data.get("id")),
            "title": story_data.get("title"),
            "as_a": story_data.get("as_a"),
            "i_want": story_data.get("i_want"),
            "so_that": story_data.get("so_that"),
            "acceptance_criteria": story_data.get("acceptance_criteria", []),
            "story_points": story_data.get("story_points", 0),
            "status": story_data.get("status", "backlog"),
            "epic_id": story_data.get("epic_id"),
            "created_at": story_data.get("created_at", "")
        }
        return json.dumps(output, indent=2, default=str)

    @staticmethod
    def format_task_output(task_data: Dict[str, Any]) -> str:
        """Format task creation output as JSON"""
        output = {
            "type": "task",
            "id": task_data.get("task_id", task_data.get("id")),
            "story_id": task_data.get("story_id"),
            "title": task_data.get("title"),
            "description": task_data.get("description"),
            "technical_details": task_data.get("technical_details", ""),
            "estimated_hours": task_data.get("estimated_hours", 0),
            "story_points": task_data.get("story_points", 0),
            "test_criteria": task_data.get("test_criteria", []),
            "priority": task_data.get("priority", "Medium"),
            "status": task_data.get("status", "pending"),
            "assigned_to": task_data.get("assigned_to"),
            "dependencies": task_data.get("dependencies", []),
            "created_at": task_data.get("created_at", "")
        }
        return json.dumps(output, indent=2, default=str)

    @staticmethod
    def format_sprint_output(sprint_data: Dict[str, Any]) -> str:
        """Format sprint output as JSON"""
        output = {
            "type": "sprint",
            "id": sprint_data.get("sprint_id", sprint_data.get("id")),
            "name": sprint_data.get("name"),
            "goal": sprint_data.get("goal"),
            "start_date": sprint_data.get("start_date"),
            "end_date": sprint_data.get("end_date"),
            "status": sprint_data.get("status"),
            "velocity": sprint_data.get("velocity", 0),
            "planned_points": sprint_data.get("planned_points", 0),
            "completed_points": sprint_data.get("completed_points", 0),
            "stories": sprint_data.get("stories", []),
            "tasks": sprint_data.get("tasks", [])
        }
        return json.dumps(output, indent=2, default=str)

    @staticmethod
    def format_backlog_output(backlog_data: Union[list, dict]) -> str:
        """Format backlog output as JSON"""
        if isinstance(backlog_data, list):
            output = {
                "type": "backlog",
                "items": backlog_data,
                "total_count": len(backlog_data)
            }
        else:
            output = backlog_data

        return json.dumps(output, indent=2, default=str)

    @staticmethod
    def format_epic_output(epic_data: Dict[str, Any]) -> str:
        """Format epic output as JSON"""
        output = {
            "type": "epic",
            "id": epic_data.get("epic_id", epic_data.get("id")),
            "title": epic_data.get("title"),
            "description": epic_data.get("description"),
            "stories": epic_data.get("stories", []),
            "total_points": epic_data.get("total_points", 0),
            "completed_points": epic_data.get("completed_points", 0),
            "status": epic_data.get("status", "active"),
            "created_at": epic_data.get("created_at", "")
        }
        return json.dumps(output, indent=2, default=str)

    @staticmethod
    def format_bug_output(bug_data: Dict[str, Any]) -> str:
        """Format bug output as JSON"""
        output = {
            "type": "bug",
            "id": bug_data.get("bug_id", bug_data.get("id")),
            "title": bug_data.get("title"),
            "description": bug_data.get("description"),
            "steps_to_reproduce": bug_data.get("steps_to_reproduce", []),
            "expected_behavior": bug_data.get("expected_behavior"),
            "actual_behavior": bug_data.get("actual_behavior"),
            "severity": bug_data.get("severity", "Medium"),
            "priority": bug_data.get("priority", "Medium"),
            "status": bug_data.get("status", "new"),
            "assigned_to": bug_data.get("assigned_to"),
            "created_at": bug_data.get("created_at", "")
        }
        return json.dumps(output, indent=2, default=str)

    @staticmethod
    def format_error_output(error_message: str, additional_info: Dict = None) -> str:
        """Format error output as JSON"""
        output = {
            "type": "error",
            "status": "error",
            "message": error_message,
            "additional_info": additional_info or {}
        }
        return json.dumps(output, indent=2)

    @staticmethod
    def format_success_output(message: str, data: Dict = None) -> str:
        """Format success output as JSON"""
        output = {
            "type": "success",
            "status": "success",
            "message": message,
            "data": data or {}
        }
        return json.dumps(output, indent=2, default=str)

    @staticmethod
    def format_generic_output(data: Any, output_type: str = "generic") -> str:
        """Format any generic output as JSON"""
        if isinstance(data, str):
            # If it's already a string, check if it's markdown
            if JSONOutputFormatter._looks_like_markdown(data):
                # Convert markdown-like string to JSON structure
                output = {
                    "type": output_type,
                    "content": data,
                    "format": "text"
                }
            else:
                # Try to parse as JSON, otherwise wrap it
                try:
                    parsed = json.loads(data)
                    return json.dumps(parsed, indent=2, default=str)
                except:
                    output = {
                        "type": output_type,
                        "content": data
                    }
        else:
            # Already structured data
            output = data

        return json.dumps(output, indent=2, default=str)

    @staticmethod
    def _looks_like_markdown(text: str) -> bool:
        """Check if text appears to be markdown format"""
        markdown_indicators = ['##', '**', '```', '- [ ]', '- [x]', '![', '[](']
        return any(indicator in text for indicator in markdown_indicators)


def ensure_json_output(func):
    """
    Decorator to ensure function outputs JSON format
    Use this to wrap any function that returns command output
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # If result is already a string, validate it's JSON
        if isinstance(result, str):
            try:
                json.loads(result)
                return result
            except json.JSONDecodeError:
                # Convert to JSON format
                return JSONOutputFormatter.format_generic_output(result)

        # If result is a dict, ensure it's JSON-serializable
        if isinstance(result, dict):
            return json.dumps(result, indent=2, default=str)

        # For any other type, convert to JSON
        return JSONOutputFormatter.format_generic_output(result)

    return wrapper