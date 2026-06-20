#!/usr/bin/env bash
# Post a comment recording the ACTUAL model id Claude's API reported for this
# run — NOT the requested --model. The id is read from the action's
# execution_file (path passed via the $EXECUTION_FILE env var).
#
# Usage: log-model.sh <issue-or-pr-number> <phase-label> [effort]
#   `gh issue comment` accepts a PR number too, since PRs are issues.
#   `effort` is the --effort value the job requested (e.g. "medium"); pass it
#   along so the comment records what was actually configured, not just the
#   model id. Omit it for jobs that don't pass --effort.
set -euo pipefail

number="${1:?issue/PR number required}"
phase="${2:-Run}"
effort="${3:-}"

model="unknown"
if [ -n "${EXECUTION_FILE:-}" ] && [ -f "$EXECUTION_FILE" ]; then
  # The execution log's schema isn't formally documented, so be defensive:
  # slurp the whole file (-s handles both a JSON array and newline-delimited
  # JSON) and recursively take the last real `model` field — the id the API
  # returns on each response. The SDK tags locally-generated messages with the
  # model "<synthetic>"; ignore those (and anything not a claude-* id) so we
  # report the actual API model, not a synthetic stub. Falls back to "unknown".
  found="$(jq -rs '([.. | objects | select(has("model")) | .model | select(startswith("claude"))] | last) // empty' \
    "$EXECUTION_FILE" 2>/dev/null || true)"
  [ -n "$found" ] && model="$found"
fi

effort_suffix=""
[ -n "$effort" ] && effort_suffix=" at \`${effort}\` effort"

gh issue comment "$number" \
  --repo "$GITHUB_REPOSITORY" \
  --body "🤖 ${phase} ran on model \`${model}\`${effort_suffix}."
