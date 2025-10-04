#!/usr/bin/env python3
"""
Test Agent Colors and Delegation System
"""

import sys
from pathlib import Path

# Add xavier to path
sys.path.insert(0, str(Path(__file__).parent))

from xavier.src.agents.agent_metadata import get_metadata_manager
from xavier.src.utils.ansi_art import display_agent_status, display_agent_takeover, display_agent_handoff


def test_agent_colors():
    """Test that all agents display with correct colors"""
    print("="*70)
    print("Testing Agent Color Display System")
    print("="*70)

    # Reload metadata to pick up the new DevOps engineer
    metadata_manager = get_metadata_manager()
    metadata_manager.reload_metadata()

    # List of all agents to test
    agents = [
        ('python-engineer', 'Implementing Python API'),
        ('frontend-engineer', 'Building React dashboard'),
        ('golang-engineer', 'Creating Go microservice'),
        ('test-runner', 'Running test suite'),
        ('devops-engineer', 'Configuring Docker containers'),
        ('java-engineer', 'Building Spring application'),
        ('ruby-engineer', 'Developing Rails app'),
        ('rust-engineer', 'Implementing Rust service'),
        ('swift-engineer', 'Creating iOS app'),
        ('kotlin-engineer', 'Building Android app'),
        ('project-manager', 'Managing sprint tasks'),
        ('context-manager', 'Analyzing codebase'),
    ]

    print("\n📋 Agent Status Display:")
    print("-"*70)

    for agent_name, task in agents:
        display_agent_status(agent_name, 'working', task)

    print("\n🎯 Agent Takeover Display:")
    print("-"*70)

    # Test agent takeover display
    display_agent_takeover('python-engineer', 'Create REST API endpoints for user authentication')

    print("\n🔄 Agent Handoff Display:")
    print("-"*70)

    # Test agent handoff display
    display_agent_handoff(
        'python-engineer',
        'test-runner',
        'Implementation complete, ready for testing'
    )

    print("\n✅ Color System Test Complete!")
    print("="*70)

    # Show color legend
    print("\n📊 Agent Color Legend:")
    print("-"*70)

    color_info = []
    for agent_name, _ in agents:
        metadata = metadata_manager.get_agent_metadata(agent_name)
        if metadata:
            emoji = metadata.emoji
            label = metadata.label
            color = metadata.color
            color_info.append((agent_name, emoji, label, color))

    for name, emoji, label, color in color_info:
        print(f"  {emoji} [{label:5}] {name:20} → {color}")

    print("="*70)


if __name__ == "__main__":
    test_agent_colors()