#!/usr/bin/env bash
# SessionStart hook.
#
# Injects the current working context into the session so Claude begins knowing
# which issue it is on, what is left in the active milestone, and whether the
# working tree is clean. stdout is added to the model's context.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" 2>/dev/null || exit 0
command -v gh >/dev/null 2>&1 || exit 0

BRANCH="$(git branch --show-current 2>/dev/null)"
[[ -n "$BRANCH" ]] || exit 0

echo "## Repository context"
echo

if [[ "$BRANCH" == "main" ]]; then
  echo "Branch: \`main\` — **no work happens here.** Any change needs an issue and its own branch."
else
  echo "Branch: \`$BRANCH\`"
  ISSUE_NR="${BRANCH%%-*}"
  if [[ "$ISSUE_NR" =~ ^[0-9]+$ ]]; then
    DETAIL="$(gh issue view "$ISSUE_NR" --json number,title,state,milestone,labels \
      --jq '"Issue #\(.number) [\(.state)] \(.title)\nMilestone: \(.milestone.title // "NONE — must be set")\nLabels: \(if (.labels|length) > 0 then ([.labels[].name]|join(", ")) else "NONE — at least one required" end)"' 2>/dev/null)"
    [[ -n "$DETAIL" ]] && { echo; echo "$DETAIL"; echo; echo "Commits on this branch must start with \`#$ISSUE_NR \`."; }
  fi
fi

DIRTY="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
[[ "$DIRTY" != "0" ]] && { echo; echo "Working tree: $DIRTY uncommitted change(s)."; }

OPEN="$(gh issue list --state open --limit 100 --json number,title,milestone \
  --jq '[.[] | select(.milestone != null)] | group_by(.milestone.title) | .[] | "- \(.[0].milestone.title): \(length) open"' 2>/dev/null)"
[[ -n "$OPEN" ]] && { echo; echo "Open issues by milestone:"; echo "$OPEN"; }

exit 0
