#!/bin/bash

# Usage: setup-worktree.sh <feature-name> [branch-type]
# branch-type: feature (default) or fix

set -e

FEATURE_NAME="$1"
BRANCH_TYPE="${2:-feature}"

if [ -z "$FEATURE_NAME" ]; then
    echo "Error: Feature name is required"
    echo "Usage: setup-worktree.sh <feature-name> [feature|fix]"
    exit 1
fi

if [ "$BRANCH_TYPE" != "feature" ] && [ "$BRANCH_TYPE" != "fix" ]; then
    echo "Error: Branch type must be 'feature' or 'fix'"
    exit 1
fi

# Get the main repo directory from current working directory (not script location)
MAIN_REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
REPO_NAME="$(basename "$MAIN_REPO")"
PARENT_DIR="$(dirname "$MAIN_REPO")"

WORKTREES_BASE="$PARENT_DIR/.worktrees/${REPO_NAME}"
WORKTREE_DIR="$WORKTREES_BASE/${BRANCH_TYPE}-${FEATURE_NAME}"
BRANCH_NAME="${BRANCH_TYPE}/${FEATURE_NAME}"

echo "Setting up worktree for: $BRANCH_NAME"
echo "Worktree directory: $WORKTREE_DIR"

# Check if worktree already exists
if [ -d "$WORKTREE_DIR" ]; then
    echo "Error: Worktree directory already exists: $WORKTREE_DIR"
    exit 1
fi

# Create .worktrees base directory if not exists
mkdir -p "$WORKTREES_BASE"

# Update main branch
cd "$MAIN_REPO"
echo "Fetching latest changes..."
git fetch origin

# Check if we're on main, if so pull
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "Pulling latest main..."
    git pull origin main
fi

# Create worktree with new branch from origin/main
echo "Creating worktree..."
git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" origin/main

# Install dependencies (conditional)
cd "$WORKTREE_DIR"
if [ -f "package.json" ]; then
    echo "Installing npm dependencies..."
    npm install
fi
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    if [ -d ".venv" ]; then
        .venv/bin/pip install -r requirements.txt
    elif command -v uv &> /dev/null; then
        uv pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
fi

echo ""
echo "=========================================="
echo "Worktree created successfully!"
echo "=========================================="
echo ""
echo "Directory: $WORKTREE_DIR"
echo "Branch: $BRANCH_NAME"
echo ""
echo "Continue working in this session by changing directory:"
echo "  cd $WORKTREE_DIR"
echo ""
