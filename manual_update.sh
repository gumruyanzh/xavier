#!/bin/bash

# Manual Xavier Framework Update Script
# Use this to manually update Xavier when the update command isn't working

echo "======================================================================"
echo "  Xavier Framework Manual Update"
echo "======================================================================"
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    exit 1
fi

# Check if we're in a git repo
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "   Please run this from the Xavier project root directory"
    exit 1
fi

echo "📥 Fetching latest changes from remote..."
git fetch origin main

echo ""
echo "📊 Comparing versions..."
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

echo "   Local commit:  ${LOCAL_COMMIT:0:7}"
echo "   Remote commit: ${REMOTE_COMMIT:0:7}"
echo ""

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "✅ Already up to date!"
    echo ""
    echo "Current version: $(cat VERSION 2>/dev/null || echo '1.2.3')"
    exit 0
fi

echo "🔄 New changes available!"
echo ""
echo "Changes:"
git log --oneline --decorate HEAD..origin/main | head -10
echo ""

# Ask for confirmation
read -p "Do you want to update? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Update cancelled"
    exit 0
fi

echo ""
echo "🚀 Updating Xavier Framework..."

# Stash any local changes
if ! git diff-index --quiet HEAD --; then
    echo "💾 Stashing local changes..."
    git stash push -m "Auto-stash before Xavier update $(date +%Y-%m-%d_%H:%M:%S)"
    STASHED=true
fi

# Pull latest changes
echo "⬇️  Pulling latest changes..."
if git pull origin main; then
    echo ""
    echo "✅ Update successful!"
    echo ""
    echo "Updated to version: $(cat VERSION 2>/dev/null || echo '1.2.3')"
    echo "Current commit: $(git rev-parse HEAD | cut -c1-7)"

    # Restore stashed changes if any
    if [ "$STASHED" = true ]; then
        echo ""
        echo "💾 Restoring your local changes..."
        if git stash pop; then
            echo "✅ Local changes restored"
        else
            echo "⚠️  Conflicts while restoring changes"
            echo "   Your changes are in: git stash list"
            echo "   Manually apply with: git stash pop"
        fi
    fi

    echo ""
    echo "======================================================================"
    echo "  Xavier Framework updated successfully! 🎉"
    echo "======================================================================"
else
    echo ""
    echo "❌ Update failed"
    echo "   Please check the error messages above"
    exit 1
fi
