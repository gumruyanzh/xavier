#!/usr/bin/env python3
"""
Xavier Slash Command Handler for Claude Code
This script acts as the bridge between Claude Code's SlashCommand tool and Xavier Framework
"""

import sys
import json
import argparse
from pathlib import Path

# Add xavier to path
sys.path.insert(0, str(Path(__file__).parent))

from xavier.src.commands.claude_code_integration import ClaudeCodeXavierIntegration


def parse_command_string(command_string: str):
    """Parse a slash command string into command name and arguments"""
    import shlex

    parts = command_string.strip().split(None, 1)

    if not parts:
        return None, {}

    command = parts[0]
    args_string = parts[1] if len(parts) > 1 else ""

    # Parse arguments (simple key=value pairs or positional)
    args = {}
    if args_string:
        # Try to parse as key=value pairs first
        if "=" in args_string:
            # Use shlex to handle quoted values properly
            try:
                tokens = shlex.split(args_string)
            except ValueError:
                tokens = args_string.split()

            for token in tokens:
                if "=" in token:
                    key, value = token.split("=", 1)
                    # Try to parse value as appropriate type
                    if value.lower() in ["true", "false"]:
                        args[key] = value.lower() == "true"
                    elif value.isdigit():
                        args[key] = int(value)
                    else:
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        args[key] = value
        else:
            # Handle positional arguments based on command
            args = parse_positional_args(command, args_string)

    return command, args


def parse_positional_args(command: str, args_string: str):
    """Parse positional arguments for specific commands"""
    import shlex

    args = {}

    # Use shlex to properly handle quoted strings
    try:
        parts = shlex.split(args_string)
    except ValueError:
        # Fallback to simple split if shlex fails
        parts = args_string.strip().split(None)

    # Define positional argument mappings for common commands
    positional_mappings = {
        "/xavier-init": ["name", "type", "stack"],
        "/create-agent": ["name", "skills"],
        "/create-story": ["title"],
        "/start-task": ["task_id", "agent"],
        "/sprint": ["action", "name"],
        "/create-epic": ["title", "description"],
        "/bug": ["title", "description", "priority"],
    }

    if command in positional_mappings:
        mapping = positional_mappings[command]
        for i, value in enumerate(parts):
            if i < len(mapping):
                args[mapping[i]] = value
    else:
        # Default: treat as single argument
        if parts:
            args["value"] = " ".join(parts)

    return args


def format_output(result: dict) -> str:
    """Format the command result for display"""
    if result.get("status") == "error":
        output = f"❌ Error: {result.get('message', 'Unknown error')}\n"
        if result.get("available_commands"):
            output += "\nAvailable commands:\n"
            for cmd in result["available_commands"]:
                output += f"  • {cmd}\n"
    else:
        output = f"✅ {result.get('message', 'Command executed successfully')}\n"

        # Add any additional data
        for key, value in result.items():
            if key not in ["status", "message"]:
                if isinstance(value, dict):
                    output += f"\n{key.title()}:\n"
                    output += json.dumps(value, indent=2) + "\n"
                elif isinstance(value, list):
                    output += f"\n{key.title()}:\n"
                    for item in value:
                        output += f"  • {item}\n"
                else:
                    output += f"{key.title()}: {value}\n"

    return output


def main():
    """Main entry point for Xavier slash commands"""
    parser = argparse.ArgumentParser(description="Xavier Slash Command Handler")
    parser.add_argument("command", nargs="?", help="Full slash command string")
    parser.add_argument("--list", action="store_true", help="List available commands")
    parser.add_argument("--help-command", help="Get help for a specific command")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Initialize the integration
    integration = ClaudeCodeXavierIntegration()

    # Handle listing commands
    if args.list:
        print("🎯 Xavier Framework Slash Commands\n")
        commands = integration.list_commands()
        for cmd in commands:
            print(f"{cmd['name']}")
            print(f"  {cmd['description']}")
            if cmd.get('args'):
                required_args = [name for name, spec in cmd['args'].items() if spec.get('required')]
                optional_args = [name for name, spec in cmd['args'].items() if not spec.get('required')]
                if required_args:
                    print(f"  Required: {', '.join(required_args)}")
                if optional_args:
                    print(f"  Optional: {', '.join(optional_args)}")
            print()
        return

    # Handle command help
    if args.help_command:
        commands = integration.list_commands()
        cmd_info = next((c for c in commands if c['name'] == args.help_command), None)
        if cmd_info:
            print(f"Help for {cmd_info['name']}:\n")
            print(f"Description: {cmd_info['description']}\n")
            if cmd_info.get('args'):
                print("Arguments:")
                for arg_name, arg_spec in cmd_info['args'].items():
                    required = "required" if arg_spec.get('required') else "optional"
                    default = f" (default: {arg_spec.get('default')})" if 'default' in arg_spec else ""
                    print(f"  {arg_name} ({required}): {arg_spec.get('description', 'No description')}{default}")
        else:
            print(f"Command '{args.help_command}' not found")
        return

    # Handle command execution
    if not args.command:
        print("Usage: xavier_slash_command.py '<command> [arguments]'")
        print("       xavier_slash_command.py --list")
        print("       xavier_slash_command.py --help-command <command>")
        return

    # Parse the command string
    command, cmd_args = parse_command_string(args.command)

    if not command:
        print("❌ Invalid command format")
        return

    # Execute the command
    result = integration.execute_command(command, cmd_args)

    # Output the result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()