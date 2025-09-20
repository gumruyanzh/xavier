#!/usr/bin/env python3
"""
ANSI Art Display Utility for Xavier Framework
Provides beautiful terminal displays with ASCII art and colors
"""

import os
import sys
from typing import Optional, List, Dict


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


def display_welcome(version: str = "1.0.3") -> None:
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