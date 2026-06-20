#!/usr/bin/env bash
# Post a comment to @btoddb when a Claude phase fails outright (e.g. the bot
# hit its usage/token limit, an API error, or a timeout). Without this, a
# hard failure mid-run leaves the Actions tab red with no comment at all —
# the silent failure this script exists to close.
#
# Usage: report-failure.sh <issue-or-pr-number> <phase-label>
#   `gh issue comment` accepts a PR number too, since PRs are issues.
#   Reads $EXECUTION_FILE (if set and present) to classify the failure.
set -euo pipefail

number="${1:?issue/PR number required}"
phase="${2:-Run}"

run_url="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-}/actions/runs/${GITHUB_RUN_ID:-}"

error_text=""
if [ -n "${EXECUTION_FILE:-}" ] && [ -f "$EXECUTION_FILE" ]; then
  # Same defensive slurp style as log-model.sh: the execution log's schema
  # isn't formally documented, so pull any error-ish text out of the last
  # result object rather than assuming a fixed shape.
  error_text="$(jq -rs '
      [.. | objects | select(has("is_error") or has("error") or has("subtype"))]
      | last
      | [.error, .subtype, (if .is_error == true then "is_error" else empty end)]
      | map(select(. != null and . != ""))
      | join(" ")
    ' "$EXECUTION_FILE" 2>/dev/null || true)"
fi

# Heuristic classification: match known usage/token/rate-limit signatures.
# This is best-effort string matching against an undocumented log format, so a
# miss here just falls through to the generic message below — never silent.
is_usage_limit=false
if printf '%s' "$error_text" | grep -qiE 'usage limit|rate.?limit|quota|token.?limit|exceeded.*usage|429'; then
  is_usage_limit=true
fi

if [ "$is_usage_limit" = true ]; then
  reason="the bot likely hit its usage/token limit"
  advice="Please wait for the limit window to reset, then re-comment \`@claude ...\` to retry."
else
  reason="this phase failed"
  advice="Please check the [Actions run](${run_url}) for details, then re-comment \`@claude ...\` to retry."
fi

snippet=""
[ -n "$error_text" ] && snippet=" Error detail: \`${error_text}\`."

gh issue comment "$number" \
  --repo "${GITHUB_REPOSITORY:?}" \
  --body "🤖 @btoddb the **${phase}** phase failed — ${reason}.${snippet} ${advice}"
