#!/usr/bin/env bash
# SessionStart hook — surfaces active task state from the most recent status.json
# Receives JSON on stdin; prints to stdout (added to Claude's context); always exits 0.

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // "."')
WORKSPACE_DIR="$CWD/.claude/workspaces"

# Find the most recently modified status.json under .claude/workspaces/
STATUS_FILE=$(find "$WORKSPACE_DIR" -name "status.json" -type f -printf '%T@ %p\n' 2>/dev/null \
  | sort -rn | head -1 | cut -d' ' -f2-)

if [ -n "$STATUS_FILE" ] && [ -f "$STATUS_FILE" ]; then
  TASK_ID=$(jq -r '.task_id // "unknown"' "$STATUS_FILE")
  CURRENT_PHASE=$(jq -r '.current_phase // "unknown"' "$STATUS_FILE")
  STATUS=$(jq -r '.status // "unknown"' "$STATUS_FILE")
  GITHUB_ISSUE=$(jq -r '.github_issue_url // ""' "$STATUS_FILE")
  GITHUB_PR=$(jq -r '.github_pr_url // ""' "$STATUS_FILE")
  CONTEXT_ID=$(jq -r '.feature_developer_context_id // ""' "$STATUS_FILE")

  echo "=== Active Task State ==="
  echo "Task ID:       $TASK_ID"
  echo "Current Phase: $CURRENT_PHASE"
  echo "Status:        $STATUS"
  [ -n "$GITHUB_ISSUE" ] && [ "$GITHUB_ISSUE" != "null" ] && echo "GitHub Issue:  $GITHUB_ISSUE"
  [ -n "$GITHUB_PR" ]    && [ "$GITHUB_PR"    != "null" ] && echo "GitHub PR:     $GITHUB_PR"
  [ -n "$CONTEXT_ID" ]   && [ "$CONTEXT_ID"   != "null" ] && echo "Dev Context:   $CONTEXT_ID"
  echo "Workspace:     $WORKSPACE_DIR/$TASK_ID/"
  echo "========================="
fi

# Always exit 0 — never block session startup
exit 0
