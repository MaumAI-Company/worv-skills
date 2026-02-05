#!/bin/bash

# Worktree 상태 조회 스크립트
# 각 worktree의 PR 상태, 변경사항, 미푸시 커밋을 확인

set -e

# Get the main repo directory (scripts → worktree-cleanup → skills → .claude → repo)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MAIN_REPO="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
REPO_NAME="$(basename "$MAIN_REPO")"

cd "$MAIN_REPO"

echo ""
echo "=========================================="
echo "Worktree 상태"
echo "=========================================="
echo ""

# Get worktree list (skip the main repo)
WORKTREES=$(git worktree list --porcelain | grep "^worktree " | sed 's/^worktree //' | grep -Fxv "$MAIN_REPO" || true)

if [ -z "$WORKTREES" ]; then
    echo "활성 worktree가 없습니다."
    echo ""
    exit 0
fi

for WORKTREE_PATH in $WORKTREES; do
    WORKTREE_NAME=$(basename "$WORKTREE_PATH")

    # Get branch name
    BRANCH=$(git -C "$WORKTREE_PATH" branch --show-current 2>/dev/null || echo "unknown")

    # Check for uncommitted changes
    CHANGES=$(git -C "$WORKTREE_PATH" status --porcelain 2>/dev/null | wc -l | tr -d ' ')

    # Check for unpushed commits
    UNPUSHED=$(git -C "$WORKTREE_PATH" log @{u}..HEAD --oneline 2>/dev/null | wc -l | tr -d ' ' || echo "?")

    # Check PR status using gh (if available)
    PR_STATUS="확인 필요"
    PR_INFO=""
    if command -v gh &> /dev/null; then
        PR_JSON=$(gh pr list --head "$BRANCH" --json number,state,merged --limit 1 2>/dev/null || echo "[]")
        if [ "$PR_JSON" != "[]" ] && [ -n "$PR_JSON" ]; then
            PR_NUM=$(echo "$PR_JSON" | grep -o '"number":[0-9]*' | head -1 | cut -d':' -f2)
            PR_STATE=$(echo "$PR_JSON" | grep -o '"state":"[^"]*"' | head -1 | cut -d'"' -f4)
            PR_MERGED=$(echo "$PR_JSON" | grep -o '"merged":true' | head -1 || echo "")

            if [ -n "$PR_MERGED" ]; then
                PR_STATUS="merged"
                PR_INFO="#$PR_NUM"
            elif [ "$PR_STATE" = "OPEN" ]; then
                PR_STATUS="open"
                PR_INFO="#$PR_NUM"
            elif [ "$PR_STATE" = "CLOSED" ]; then
                PR_STATUS="closed"
                PR_INFO="#$PR_NUM"
            fi
        else
            PR_STATUS="none"
        fi
    fi

    # Determine status icon
    ICON="⚠️"
    STATUS_MSG=""

    if [ "$PR_STATUS" = "merged" ] && [ "$CHANGES" = "0" ] && [ "$UNPUSHED" = "0" ]; then
        ICON="✅"
        STATUS_MSG="정리 가능"
    else
        if [ "$PR_STATUS" = "open" ]; then
            STATUS_MSG="PR 열림"
        elif [ "$PR_STATUS" = "none" ]; then
            STATUS_MSG="PR 없음"
        elif [ "$CHANGES" != "0" ]; then
            STATUS_MSG="변경사항 있음"
        elif [ "$UNPUSHED" != "0" ] && [ "$UNPUSHED" != "?" ]; then
            STATUS_MSG="미푸시 커밋"
        else
            STATUS_MSG="확인 필요"
        fi
    fi

    # Output
    echo "$ICON $WORKTREE_NAME"
    echo "   Branch: $BRANCH"
    if [ -n "$PR_INFO" ]; then
        echo "   PR: $PR_INFO ($PR_STATUS)"
    else
        echo "   PR: $PR_STATUS"
    fi
    echo "   Changes: ${CHANGES} uncommitted, ${UNPUSHED} unpushed"
    echo "   → $STATUS_MSG"
    echo ""
done

echo "=========================================="
echo ""
echo "정리하려면:"
echo "  git worktree remove ../.worktrees/<repo>/<type>-<name>"
echo "  git branch -d <type>/<name>"
echo ""
