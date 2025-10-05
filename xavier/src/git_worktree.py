#!/usr/bin/env python3
"""
Git Worktree Management Module for Xavier Framework
Handles creation, deletion, and management of git worktrees for agent branching
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class GitWorktreeManager:
    """Manages git worktrees for Xavier Framework agents"""

    def __init__(self, repo_path: str = ".", worktree_dir: str = "trees"):
        """
        Initialize the Git Worktree Manager

        Args:
            repo_path: Path to the main repository
            worktree_dir: Name of directory to store worktrees (default: 'trees')
        """
        self.repo_path = Path(repo_path).resolve()
        self.worktree_dir = self.repo_path / worktree_dir
        self.metadata_file = self.worktree_dir / ".worktree_metadata.json"

    def initialize_worktree_directory(self) -> bool:
        """
        Initialize the worktree directory structure

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create worktree directory if it doesn't exist
            self.worktree_dir.mkdir(parents=True, exist_ok=True)

            # Add to .gitignore if not already present
            gitignore_path = self.repo_path / ".gitignore"
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    content = f.read()
                if f"/{self.worktree_dir.name}/" not in content:
                    with open(gitignore_path, 'a') as f:
                        f.write(f"\n# Xavier worktrees\n/{self.worktree_dir.name}/\n")

            # Initialize metadata file
            if not self.metadata_file.exists():
                self._save_metadata({})

            return True
        except Exception as e:
            print(f"Error initializing worktree directory: {e}")
            return False

    def create_worktree(self, branch_name: str, agent_name: str, task_id: str) -> Tuple[bool, str]:
        """
        Create a new git worktree for an agent

        Args:
            branch_name: Name of the branch to create
            agent_name: Name of the agent
            task_id: ID of the task being worked on

        Returns:
            Tuple[bool, str]: Success status and message/error
        """
        try:
            # Ensure worktree directory is initialized
            if not self.initialize_worktree_directory():
                return False, "Failed to initialize worktree directory"

            # Generate worktree path
            worktree_path = self.worktree_dir / f"{agent_name}-{task_id}"

            # Check if worktree already exists
            if worktree_path.exists():
                return False, f"Worktree already exists at {worktree_path}"

            # Create new branch and worktree
            full_branch_name = f"{agent_name}/{task_id}"

            # Create branch from main
            cmd = ["git", "worktree", "add", "-b", full_branch_name,
                   str(worktree_path), "main"]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True)

            if result.returncode != 0:
                return False, f"Failed to create worktree: {result.stderr}"

            # Update metadata
            metadata = self._load_metadata()
            metadata[task_id] = {
                "agent": agent_name,
                "branch": full_branch_name,
                "path": str(worktree_path.relative_to(self.repo_path)),
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            self._save_metadata(metadata)

            return True, f"Created worktree for {agent_name} at {worktree_path}"

        except Exception as e:
            return False, f"Error creating worktree: {str(e)}"

    def list_worktrees(self) -> List[Dict[str, str]]:
        """
        List all active worktrees

        Returns:
            List of worktree information dictionaries
        """
        try:
            # Get worktrees from git
            cmd = ["git", "worktree", "list", "--porcelain"]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Error listing worktrees: {result.stderr}")
                return []

            # Parse worktree output
            worktrees = []
            current = {}

            for line in result.stdout.strip().split('\n'):
                if line.startswith('worktree '):
                    if current:
                        worktrees.append(current)
                    current = {'path': line.split(' ', 1)[1]}
                elif line.startswith('HEAD '):
                    current['head'] = line.split(' ', 1)[1]
                elif line.startswith('branch '):
                    current['branch'] = line.split(' ', 1)[1]
                elif line.startswith('detached'):
                    current['detached'] = True
                elif line == '':
                    if current:
                        worktrees.append(current)
                        current = {}

            if current:
                worktrees.append(current)

            # Merge with metadata
            metadata = self._load_metadata()
            for worktree in worktrees:
                # Check if this worktree is in our managed directory
                worktree_path = Path(worktree['path'])
                if self.worktree_dir in worktree_path.parents or worktree_path == self.worktree_dir:
                    # Find matching metadata
                    for task_id, info in metadata.items():
                        if info['path'] in str(worktree_path):
                            worktree.update({
                                'task_id': task_id,
                                'agent': info['agent'],
                                'created_at': info['created_at'],
                                'status': info['status']
                            })
                            break

            return [w for w in worktrees if 'task_id' in w]

        except Exception as e:
            print(f"Error listing worktrees: {str(e)}")
            return []

    def remove_worktree(self, task_id: str, force: bool = False) -> Tuple[bool, str]:
        """
        Remove a worktree

        Args:
            task_id: Task ID associated with the worktree
            force: Force removal even if there are uncommitted changes

        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            metadata = self._load_metadata()

            if task_id not in metadata:
                return False, f"No worktree found for task {task_id}"

            worktree_info = metadata[task_id]
            worktree_path = self.repo_path / worktree_info['path']

            # Check for uncommitted changes if not forcing
            if not force:
                cmd = ["git", "status", "--porcelain"]
                result = subprocess.run(cmd, cwd=worktree_path,
                                      capture_output=True, text=True)

                if result.stdout.strip():
                    return False, f"Worktree has uncommitted changes. Use force=True to remove anyway"

            # Remove the worktree
            cmd = ["git", "worktree", "remove", str(worktree_path)]
            if force:
                cmd.append("--force")

            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True)

            if result.returncode != 0:
                # Try to prune if removal failed
                subprocess.run(["git", "worktree", "prune"], cwd=self.repo_path)
                # Try removing directory manually if it still exists
                if worktree_path.exists():
                    shutil.rmtree(worktree_path)

            # Update metadata
            del metadata[task_id]
            self._save_metadata(metadata)

            return True, f"Removed worktree for task {task_id}"

        except Exception as e:
            return False, f"Error removing worktree: {str(e)}"

    def get_worktree_status(self, task_id: str) -> Optional[Dict[str, any]]:
        """
        Get status of a specific worktree

        Args:
            task_id: Task ID to check

        Returns:
            Dictionary with worktree status or None if not found
        """
        try:
            metadata = self._load_metadata()

            if task_id not in metadata:
                return None

            worktree_info = metadata[task_id].copy()
            worktree_path = self.repo_path / worktree_info['path']

            # Check if worktree still exists
            if not worktree_path.exists():
                worktree_info['status'] = 'missing'
                return worktree_info

            # Get current branch
            cmd = ["git", "branch", "--show-current"]
            result = subprocess.run(cmd, cwd=worktree_path,
                                  capture_output=True, text=True)
            worktree_info['current_branch'] = result.stdout.strip()

            # Check for uncommitted changes
            cmd = ["git", "status", "--porcelain"]
            result = subprocess.run(cmd, cwd=worktree_path,
                                  capture_output=True, text=True)
            worktree_info['has_uncommitted_changes'] = bool(result.stdout.strip())

            # Get ahead/behind status
            cmd = ["git", "rev-list", "--left-right", "--count", "main...HEAD"]
            result = subprocess.run(cmd, cwd=worktree_path,
                                  capture_output=True, text=True)
            if result.returncode == 0:
                behind, ahead = result.stdout.strip().split('\t')
                worktree_info['commits_behind'] = int(behind)
                worktree_info['commits_ahead'] = int(ahead)

            return worktree_info

        except Exception as e:
            print(f"Error getting worktree status: {str(e)}")
            return None

    def cleanup_worktrees(self, remove_completed: bool = False) -> List[str]:
        """
        Clean up orphaned or completed worktrees

        Args:
            remove_completed: Also remove worktrees marked as completed

        Returns:
            List of cleaned up task IDs
        """
        try:
            # First, prune any worktrees that git knows are gone
            subprocess.run(["git", "worktree", "prune"], cwd=self.repo_path)

            metadata = self._load_metadata()
            cleaned = []

            for task_id, info in list(metadata.items()):
                worktree_path = self.repo_path / info['path']

                # Remove if path doesn't exist
                if not worktree_path.exists():
                    del metadata[task_id]
                    cleaned.append(task_id)
                    continue

                # Remove if marked as completed and flag is set
                if remove_completed and info.get('status') == 'completed':
                    success, _ = self.remove_worktree(task_id, force=True)
                    if success:
                        cleaned.append(task_id)

            self._save_metadata(metadata)
            return cleaned

        except Exception as e:
            print(f"Error cleaning up worktrees: {str(e)}")
            return []

    def _load_metadata(self) -> Dict:
        """Load worktree metadata from file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
        return {}

    def _save_metadata(self, metadata: Dict) -> None:
        """Save worktree metadata to file"""
        try:
            self.worktree_dir.mkdir(parents=True, exist_ok=True)
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def push_worktree_branch(self, task_id: str) -> Tuple[bool, str]:
        """
        Push worktree branch to remote

        Args:
            task_id: Task ID of the worktree

        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            metadata = self._load_metadata()

            if task_id not in metadata:
                return False, f"No worktree found for task {task_id}"

            worktree_info = metadata[task_id]
            worktree_path = self.repo_path / worktree_info['path']
            branch_name = worktree_info['branch']

            # Push the branch
            cmd = ["git", "push", "-u", "origin", branch_name]
            result = subprocess.run(cmd, cwd=worktree_path,
                                  capture_output=True, text=True)

            if result.returncode != 0:
                return False, f"Failed to push branch: {result.stderr}"

            return True, f"Pushed branch {branch_name} to origin"

        except Exception as e:
            return False, f"Error pushing branch: {str(e)}"

    def create_pr_for_worktree(self, task_id: str, pr_title: str = None,
                              pr_body: str = None, auto_push: bool = True) -> Tuple[bool, str]:
        """
        Push worktree branch and create a pull request

        Args:
            task_id: Task ID of the worktree
            pr_title: Title for the PR (auto-generated if not provided)
            pr_body: Body for the PR (auto-generated if not provided)
            auto_push: Automatically push branch if True

        Returns:
            Tuple[bool, str]: Success status and PR URL or error message
        """
        try:
            metadata = self._load_metadata()

            if task_id not in metadata:
                return False, f"No worktree found for task {task_id}"

            worktree_info = metadata[task_id]
            worktree_path = self.repo_path / worktree_info['path']
            branch_name = worktree_info['branch']

            # Push the branch if auto_push is True
            if auto_push:
                success, msg = self.push_worktree_branch(task_id)
                if not success:
                    return False, msg

            # Create PR using gh CLI if available
            if shutil.which("gh"):
                if not pr_title:
                    pr_title = f"[{task_id}] Complete task for {worktree_info['agent']}"

                if not pr_body:
                    pr_body = f"""Task: {task_id}
Agent: {worktree_info['agent']}
Branch: {branch_name}

🤖 Generated with [Claude Code](https://claude.com/claude-code) using Xavier Framework

Co-Authored-By: Claude <noreply@anthropic.com>"""

                cmd = ["gh", "pr", "create",
                       "--title", pr_title,
                       "--body", pr_body,
                       "--base", "main",
                       "--head", branch_name]

                result = subprocess.run(cmd, cwd=worktree_path,
                                      capture_output=True, text=True)

                if result.returncode == 0:
                    pr_url = result.stdout.strip()
                    # Mark worktree as completed
                    worktree_info['status'] = 'pr_created'
                    worktree_info['pr_url'] = pr_url
                    self._save_metadata(metadata)
                    return True, f"Created PR: {pr_url}"
                else:
                    return True, f"Branch pushed. Create PR manually: {result.stderr}"
            else:
                return True, f"Branch pushed to origin/{branch_name}. Install 'gh' CLI to auto-create PRs."

        except Exception as e:
            return False, f"Error creating PR: {str(e)}"


# Command-line interface for testing
if __name__ == "__main__":
    import sys

    manager = GitWorktreeManager()

    if len(sys.argv) < 2:
        print("Usage: git_worktree.py <command> [args]")
        print("Commands: init, create, list, remove, status, cleanup")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        success = manager.initialize_worktree_directory()
        print("Initialized" if success else "Failed to initialize")

    elif command == "create" and len(sys.argv) >= 5:
        branch, agent, task = sys.argv[2], sys.argv[3], sys.argv[4]
        success, msg = manager.create_worktree(branch, agent, task)
        print(msg)

    elif command == "list":
        worktrees = manager.list_worktrees()
        for wt in worktrees:
            print(f"{wt.get('task_id', 'unknown')}: {wt.get('branch', 'unknown')} at {wt.get('path', 'unknown')}")

    elif command == "remove" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        force = len(sys.argv) > 3 and sys.argv[3] == "--force"
        success, msg = manager.remove_worktree(task_id, force)
        print(msg)

    elif command == "status" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        status = manager.get_worktree_status(task_id)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print(f"No worktree found for task {task_id}")

    elif command == "cleanup":
        cleaned = manager.cleanup_worktrees(remove_completed=True)
        print(f"Cleaned up {len(cleaned)} worktrees: {cleaned}")

    else:
        print("Invalid command or missing arguments")