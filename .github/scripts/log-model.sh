#!/usr/bin/env bash
# Post a comment recording the ACTUAL model id Claude's API reported for this
# run — NOT the requested --model. The id is read from the action's
# execution_file (path passed via the $EXECUTION_FILE env var).
#
# Usage: log-model.sh <issue-or-pr-number> <phase-label>
#   `gh issue comment` accepts a PR number too, since PRs are issues.
set -euo pipefail

number="${1:?issue/PR number required}"
phase="${2:-Run}"

model="unknown"
if [ -n "${EXECUTION_FILE:-}" ] && [ -f "$EXECUTION_FILE" ]; then
  # The execution log's schema isn't formally documented, so be defensive:
  # slurp the whole file (-s handles both a JSON array and newline-delimited
  # JSON) and recursively take the last `model` field — the id the API returns
  # on each response. Falls back to "unknown" if the shape differs.
  found="$(jq -rs '([.. | objects | select(has("model")) | .model] | last) // empty' \
    "$EXECUTION_FILE" 2>/dev/null || true)"
  [ -n "$found" ] && model="$found"
fi

gh issue comment "$number" \
  --repo "$GITHUB_REPOSITORY" \
  --body "🤖 ${phase} ran on model \`${model}\`."
