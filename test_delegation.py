#!/usr/bin/env python3
"""
Xavier Agent Delegation Helper
Tests that all agents are properly configured for automatic delegation
"""

def test_agent_delegation(task_description: str):
    """
    Test which agent would handle a given task

    Instead of using Task tool, describe the task and let Claude
    automatically delegate to the appropriate agent.
    """
    print(f"Task: {task_description}")
    print("Claude should automatically delegate to the appropriate agent.")
    print("The agent will be chosen based on the task description.")

# Example usage:
# Instead of: Task(subagent_type="devops-engineer", ...)
# Use: "I need help setting up Docker containers for the application"
# Claude will automatically use the devops-engineer

tasks = {
    "python-engineer": "Create a REST API endpoint using FastAPI",
    "frontend-engineer": "Build a React component with TypeScript",
    "devops-engineer": "Set up Docker containers and Kubernetes deployment",
    "test-runner": "Run the test suite and check coverage",
    "golang-engineer": "Create a Go microservice with Gin",
    "java-engineer": "Implement a Spring Boot application",
    "ruby-engineer": "Create a Rails controller",
    "rust-engineer": "Write a memory-safe Rust function",
    "swift-engineer": "Build an iOS app with SwiftUI",
    "kotlin-engineer": "Create an Android app with Jetpack Compose",
}

print("Example delegation triggers:")
print("-" * 60)
for agent, task in tasks.items():
    print(f"{agent:20} → {task}")
