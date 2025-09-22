#!/usr/bin/env python3
"""
ANSI Art Display Utility for Xavier Framework
Provides beautiful terminal displays with ASCII art and colors
"""

import os
import sys
from typing import Optional, List, Dict
from datetime import datetime

# Try to import agent metadata, fallback if not available
try:
    from ..agents.agent_metadata import get_agent_color, get_agent_emoji, get_agent_label, get_agent_display_name
    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False


class ANSIColors:
    """ANSI color codes for terminal output"""
    # Reset
    RESET = '\033[0m'

    # Regular colors
    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'

    # Bold colors
    BOLD_BLACK = '\033[1;30m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    BOLD_MAGENTA = '\033[1;35m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_WHITE = '\033[1;37m'

    # Light colors (high intensity)
    LIGHT_BLACK = '\033[0;90m'
    LIGHT_RED = '\033[0;91m'
    LIGHT_GREEN = '\033[0;92m'
    LIGHT_YELLOW = '\033[0;93m'
    LIGHT_BLUE = '\033[0;94m'
    LIGHT_MAGENTA = '\033[0;95m'
    LIGHT_CYAN = '\033[0;96m'
    LIGHT_WHITE = '\033[0;97m'


class AgentColors:
    """Color assignments for different agent types with metadata system integration"""

    # Legacy fallback colors
    AGENT_COLORS = {
        'ProjectManager': {
            'color': ANSIColors.BOLD_MAGENTA,
            'emoji': '📊',
            'label': 'PM'
        },
        'ContextManager': {
            'color': ANSIColors.BOLD_BLUE,
            'emoji': '🔍',
            'label': 'CTX'
        },
        'PythonEngineer': {
            'color': ANSIColors.BOLD_GREEN,
            'emoji': '🐍',
            'label': 'PY'
        },
        'GolangEngineer': {
            'color': ANSIColors.BOLD_CYAN,
            'emoji': '🔷',
            'label': 'GO'
        },
        'FrontendEngineer': {
            'color': ANSIColors.BOLD_YELLOW,
            'emoji': '🎨',
            'label': 'FE'
        },
        'TestRunner': {
            'color': ANSIColors.BOLD_RED,
            'emoji': '🧪',
            'label': 'TEST'
        }
    }

    @classmethod
    def get_agent_color(cls, agent_name: str) -> str:
        """Get color for an agent using metadata system with fallback"""
        if METADATA_AVAILABLE:
            return get_agent_color(agent_name)
        return cls.AGENT_COLORS.get(agent_name, {}).get('color', ANSIColors.WHITE)

    @classmethod
    def get_agent_emoji(cls, agent_name: str) -> str:
        """Get emoji for an agent using metadata system with fallback"""
        if METADATA_AVAILABLE:
            return get_agent_emoji(agent_name)
        return cls.AGENT_COLORS.get(agent_name, {}).get('emoji', '🤖')

    @classmethod
    def get_agent_label(cls, agent_name: str) -> str:
        """Get short label for an agent using metadata system with fallback"""
        if METADATA_AVAILABLE:
            return get_agent_label(agent_name)
        return cls.AGENT_COLORS.get(agent_name, {}).get('label', 'AGT')

    @classmethod
    def get_agent_display_name(cls, agent_name: str) -> str:
        """Get display name for an agent using metadata system with fallback"""
        if METADATA_AVAILABLE:
            return get_agent_display_name(agent_name)
        return agent_name.replace('_', ' ').replace('-', ' ').title()


class XavierArt:
    """ASCII art components for Xavier Framework"""

    XAVIER_LOGO = [
        "██╗  ██╗ █████╗ ██╗   ██╗██╗███████╗██████╗ ",
        "╚██╗██╔╝██╔══██╗██║   ██║██║██╔════╝██╔══██╗",
        " ╚███╔╝ ███████║╚██╗ ██╔╝██║█████╗  ██████╔╝",
        " ██╔██╗ ██╔══██║ ╚████╔╝ ██║██╔══╝  ██╔══██╗",
        "██╔╝ ██╗██║  ██║  ╚██╔╝  ██║███████╗██║  ██║",
        "╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚══════╝╚═╝  ╚═╝"
    ]

    XAVIER_COMPACT = [
        "╔╗ ╔╗╔═══╗╦  ╦╦╔═══╗╔═══╗",
        "╚╗╔╝ ╠═══╣╚╗╔╝║╠═══ ╠═╦═╝",
        "╔╝╚╗ ║   ║ ╚╝ ║║    ║ ║  ",
        "╚══╝ ╚   ╝    ╚╚═══╝╚ ╩  "
    ]

    @staticmethod
    def get_terminal_width() -> int:
        """Get terminal width, default to 80 if unable to determine"""
        try:
            return os.get_terminal_size().columns
        except:
            return 80

    @staticmethod
    def center_text(text: str, width: Optional[int] = None) -> str:
        """Center text within given width"""
        if width is None:
            width = XavierArt.get_terminal_width()
        return text.center(width)

    @staticmethod
    def create_box(content: List[str], width: Optional[int] = None,
                   title: Optional[str] = None, color: str = ANSIColors.LIGHT_CYAN) -> List[str]:
        """Create a box around content with optional title"""
        if width is None:
            width = max(len(line) for line in content) + 4

        lines = []

        # Top border
        if title:
            title_line = f"═ {title} ═"
            padding = width - len(title_line) - 2
            left_padding = padding // 2
            right_padding = padding - left_padding
            lines.append(f"{color}╔{'═' * left_padding}{title_line}{'═' * right_padding}╗{ANSIColors.RESET}")
        else:
            lines.append(f"{color}╔{'═' * (width - 2)}╗{ANSIColors.RESET}")

        # Content lines
        for line in content:
            padding = width - len(line) - 2
            lines.append(f"{color}║{ANSIColors.RESET} {line}{' ' * padding}{color}║{ANSIColors.RESET}")

        # Bottom border
        lines.append(f"{color}╚{'═' * (width - 2)}╝{ANSIColors.RESET}")

        return lines

    @staticmethod
    def create_separator(width: Optional[int] = None, color: str = ANSIColors.LIGHT_CYAN) -> str:
        """Create a separator line"""
        if width is None:
            width = XavierArt.get_terminal_width()
        return f"{color}{'═' * width}{ANSIColors.RESET}"


class AgentBoxDrawing:
    """Enhanced box drawing utilities for agent displays"""

    @staticmethod
    def create_agent_box(agent_name: str, content: List[str], width: int = 70,
                        status: Optional[str] = None, timestamp: bool = True) -> List[str]:
        """Create a bordered box for agent output"""
        # Get agent styling
        color = AgentColors.get_agent_color(agent_name)
        emoji = AgentColors.get_agent_emoji(agent_name)
        label = AgentColors.get_agent_label(agent_name)
        display_name = AgentColors.get_agent_display_name(agent_name)

        box = []

        # Top border with agent info
        header_content = f" {emoji} [{label}] {display_name}"
        if status:
            header_content += f" - {status}"
        if timestamp:
            time_str = datetime.now().strftime("%H:%M:%S")
            header_content += f" ({time_str})"

        # Ensure header fits in box
        if len(header_content) > width - 4:
            header_content = header_content[:width - 7] + "..."

        padding = max(0, width - len(header_content) - 2)
        top_line = f"{color}╔{header_content}{'═' * padding}╗{ANSIColors.RESET}"
        box.append(top_line)

        # Content lines
        for line in content:
            # Strip ANSI codes to calculate real length
            clean_line = line
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            clean_text = ansi_escape.sub('', clean_line)

            if len(clean_text) > width - 4:
                # Wrap long lines
                wrapped_lines = []
                while len(clean_text) > width - 4:
                    cut_point = width - 4
                    wrapped_lines.append(line[:cut_point])
                    line = line[cut_point:]
                    clean_text = clean_text[cut_point:]
                wrapped_lines.append(line)

                for wrapped_line in wrapped_lines:
                    clean_wrapped = ansi_escape.sub('', wrapped_line)
                    padding = max(0, width - len(clean_wrapped) - 4)
                    box_line = f"{color}║{ANSIColors.RESET} {wrapped_line}{' ' * padding} {color}║{ANSIColors.RESET}"
                    box.append(box_line)
            else:
                padding = max(0, width - len(clean_text) - 4)
                box_line = f"{color}║{ANSIColors.RESET} {line}{' ' * padding} {color}║{ANSIColors.RESET}"
                box.append(box_line)

        # Bottom border
        bottom_line = f"{color}╚{'═' * (width - 2)}╝{ANSIColors.RESET}"
        box.append(bottom_line)

        return box

    @staticmethod
    def create_handoff_separator(from_agent: str, to_agent: str, reason: str, width: int = 70) -> List[str]:
        """Create a visual separator for agent handoffs"""
        from_color = AgentColors.get_agent_color(from_agent)
        from_emoji = AgentColors.get_agent_emoji(from_agent)
        from_label = AgentColors.get_agent_label(from_agent)

        to_color = AgentColors.get_agent_color(to_agent)
        to_emoji = AgentColors.get_agent_emoji(to_agent)
        to_label = AgentColors.get_agent_label(to_agent)

        separator = []

        # Handoff line
        handoff_text = f"{from_color}[{from_label}]{ANSIColors.RESET} {from_emoji} → {to_color}[{to_label}]{ANSIColors.RESET} {to_emoji}"
        separator.append(f"{ANSIColors.LIGHT_CYAN}{'─' * width}{ANSIColors.RESET}")
        separator.append(f"{ANSIColors.LIGHT_WHITE}🔄 HANDOFF: {handoff_text}{ANSIColors.RESET}")
        separator.append(f"{ANSIColors.LIGHT_WHITE}Reason: {reason}{ANSIColors.RESET}")
        separator.append(f"{ANSIColors.LIGHT_CYAN}{'─' * width}{ANSIColors.RESET}")

        return separator

    @staticmethod
    def create_thinking_indicator(agent_name: str, message: str = "Processing...") -> str:
        """Create a thinking indicator for an agent"""
        color = AgentColors.get_agent_color(agent_name)
        emoji = AgentColors.get_agent_emoji(agent_name)
        label = AgentColors.get_agent_label(agent_name)

        return f"{color}[{label}]{ANSIColors.RESET} {emoji} {ANSIColors.LIGHT_WHITE}⚙️ {message}{ANSIColors.RESET}"


def display_welcome(version: str = "1.1.9") -> None:
    """Display welcome screen for Xavier Framework"""
    width = XavierArt.get_terminal_width()

    # Create centered logo
    logo_lines = []
    for line in XavierArt.XAVIER_LOGO:
        logo_lines.append(XavierArt.center_text(line, width))

    # Create content
    content = []
    content.append("")  # Empty line
    for line in logo_lines:
        content.append(f"{ANSIColors.BOLD_CYAN}{line}{ANSIColors.RESET}")
    content.append("")  # Empty line
    content.append(XavierArt.center_text(f"{ANSIColors.BOLD_WHITE}Enterprise SCRUM Framework{ANSIColors.RESET}", width))
    content.append(XavierArt.center_text(f"{ANSIColors.LIGHT_WHITE}Version {version}{ANSIColors.RESET}", width))
    content.append("")  # Empty line

    # Create box
    box = XavierArt.create_box(content, width=min(width, 80))

    # Display
    print()
    for line in box:
        print(line)
    print()


def display_update_announcement(old_version: str, new_version: str) -> None:
    """Display update announcement"""
    width = min(XavierArt.get_terminal_width(), 80)

    # Create content
    content = []
    content.append(f"{ANSIColors.BOLD_GREEN}✨ Update Successful!{ANSIColors.RESET}")
    content.append("")
    content.append(f"Updated from {ANSIColors.YELLOW}v{old_version}{ANSIColors.RESET} to {ANSIColors.GREEN}v{new_version}{ANSIColors.RESET}")
    content.append("")
    content.append(f"{ANSIColors.BOLD_WHITE}What's New:{ANSIColors.RESET}")
    content.append(f"  • Intelligent project creation with AI")
    content.append(f"  • Automatic update system")
    content.append(f"  • Strict command boundaries")
    content.append(f"  • Enhanced documentation")
    content.append("")
    content.append(f"{ANSIColors.LIGHT_CYAN}Run /xavier-help to see all commands{ANSIColors.RESET}")

    # Create box with title
    box = XavierArt.create_box(content, width=width, title="Xavier Framework Updated")

    # Display
    print()
    for line in box:
        print(line)
    print()


def display_installation_complete() -> None:
    """Display installation complete message"""
    width = min(XavierArt.get_terminal_width(), 80)

    # Create content
    content = []
    content.append(f"{ANSIColors.BOLD_GREEN}✅ Installation Complete!{ANSIColors.RESET}")
    content.append("")
    content.append(f"{ANSIColors.BOLD_WHITE}Xavier Framework is ready to use{ANSIColors.RESET}")
    content.append("")
    content.append(f"{ANSIColors.LIGHT_WHITE}Quick Start:{ANSIColors.RESET}")
    content.append(f"  1. Create a story:   {ANSIColors.CYAN}/create-story{ANSIColors.RESET}")
    content.append(f"  2. Create tasks:     {ANSIColors.CYAN}/create-task{ANSIColors.RESET}")
    content.append(f"  3. Plan sprint:      {ANSIColors.CYAN}/create-sprint{ANSIColors.RESET}")
    content.append(f"  4. Start coding:     {ANSIColors.CYAN}/start-sprint{ANSIColors.RESET}")
    content.append("")
    content.append(f"  📖 Documentation:    {ANSIColors.LIGHT_BLUE}gumruyan.com/xavier{ANSIColors.RESET}")
    content.append(f"  💬 Get help:         {ANSIColors.CYAN}/xavier-help{ANSIColors.RESET}")

    # Create box
    box = XavierArt.create_box(content, width=width, title="Welcome to Xavier",
                               color=ANSIColors.BOLD_CYAN)

    # Display
    print()
    for line in box:
        print(line)
    print()


def display_sprint_start(sprint_name: str, story_count: int, total_points: int) -> None:
    """Display sprint start announcement"""
    width = min(XavierArt.get_terminal_width(), 70)

    # Create content
    content = []
    content.append(f"{ANSIColors.BOLD_WHITE}🚀 Sprint Started{ANSIColors.RESET}")
    content.append("")
    content.append(f"Sprint: {ANSIColors.CYAN}{sprint_name}{ANSIColors.RESET}")
    content.append(f"Stories: {ANSIColors.YELLOW}{story_count}{ANSIColors.RESET}")
    content.append(f"Points: {ANSIColors.YELLOW}{total_points}{ANSIColors.RESET}")
    content.append("")
    content.append(f"{ANSIColors.LIGHT_WHITE}Sequential execution enabled{ANSIColors.RESET}")
    content.append(f"{ANSIColors.LIGHT_WHITE}100% test coverage required{ANSIColors.RESET}")

    # Create box
    box = XavierArt.create_box(content, width=width, color=ANSIColors.GREEN)

    # Display
    print()
    for line in box:
        print(line)
    print()


def display_mini_banner() -> None:
    """Display a compact Xavier banner"""
    print(f"{ANSIColors.BOLD_CYAN}╔═══════════════════════════════════════╗{ANSIColors.RESET}")
    print(f"{ANSIColors.BOLD_CYAN}║  XAVIER  │  Enterprise SCRUM Framework ║{ANSIColors.RESET}")
    print(f"{ANSIColors.BOLD_CYAN}╚═══════════════════════════════════════╝{ANSIColors.RESET}")


def display_agent_takeover(agent_name: str, task_description: str) -> None:
    """Display when an agent takes over a task"""
    width = min(XavierArt.get_terminal_width(), 80)

    # Create content
    content = [
        f"{ANSIColors.BOLD_WHITE}🎯 Taking over task:{ANSIColors.RESET}",
        f"  {task_description[:width-6] if len(task_description) > width-6 else task_description}"
    ]

    # Create enhanced agent box
    box = AgentBoxDrawing.create_agent_box(agent_name, content, width, status="Active", timestamp=True)

    # Display
    print()
    for line in box:
        print(line)
    print()


def display_agent_status(agent_name: str, status: str, details: Optional[str] = None) -> None:
    """Display agent status update"""
    # Get agent styling
    color = AgentColors.get_agent_color(agent_name)
    emoji = AgentColors.get_agent_emoji(agent_name)
    label = AgentColors.get_agent_label(agent_name)

    # Status icons
    status_icons = {
        'working': '⚙️',
        'completed': '✅',
        'failed': '❌',
        'waiting': '⏳',
        'testing': '🧪',
        'reviewing': '👀'
    }

    status_icon = status_icons.get(status.lower(), '•')

    # For simple status updates, use a compact format
    status_line = f"{color}[{label}]{ANSIColors.RESET} {emoji} {AgentColors.get_agent_display_name(agent_name)} {status_icon} {status}"

    if details:
        status_line += f" - {ANSIColors.LIGHT_WHITE}{details}{ANSIColors.RESET}"

    print(status_line)


def display_agent_handoff(from_agent: str, to_agent: str, reason: str) -> None:
    """Display handoff between agents"""
    width = min(XavierArt.get_terminal_width(), 80)

    # Use enhanced handoff separator
    handoff_box = AgentBoxDrawing.create_handoff_separator(from_agent, to_agent, reason, width)

    # Display
    print()
    for line in handoff_box:
        print(line)
    print()


def display_agent_result(agent_name: str, success: bool, summary: str) -> None:
    """Display agent task result"""
    width = min(XavierArt.get_terminal_width(), 70)

    result_icon = '✅' if success else '❌'
    result_status = f"{result_icon} {'Completed' if success else 'Failed'}"

    # Create content
    content = [
        f"{ANSIColors.BOLD_WHITE}Task Result:{ANSIColors.RESET}",
        f"  {summary[:width-6] if len(summary) > width-6 else summary}"
    ]

    # Create enhanced agent box
    box = AgentBoxDrawing.create_agent_box(agent_name, content, width, status=result_status, timestamp=True)

    # Display
    print()
    for line in box:
        print(line)
    print()


if __name__ == "__main__":
    # Test displays
    print("\n=== Welcome Screen ===")
    display_welcome()

    print("\n=== Update Announcement ===")
    display_update_announcement("1.0.1", "1.0.2")

    print("\n=== Installation Complete ===")
    display_installation_complete()

    print("\n=== Sprint Start ===")
    display_sprint_start("Sprint 1: Authentication", 5, 34)

    print("\n=== Mini Banner ===")
    display_mini_banner()