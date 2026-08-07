#!/usr/bin/env bash
# UserPromptSubmit hook.
#
# Re-states the prime rule at the moment it matters most: right as a new request
# arrives, before Claude starts reaching for the edit tools. Kept to a few lines
# so it costs almost nothing per turn.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" 2>/dev/null || exit 0

BRANCH="$(git branch --show-current 2>/dev/null)"

echo "<project-rule>"
echo "No work without an issue. If this request changes the repository, first run"
echo "\`gh issue list --search \"<keywords>\" --state all\`. If nothing covers it, create an"
echo "issue with a milestone and at least one label, and link it to related issues."

if [[ "$BRANCH" == "main" ]]; then
  echo "Currently on \`main\`: edits and commits are hook-blocked. Branch as <issue-nr>-<kebab-title> first."
elif [[ "$BRANCH" =~ ^([0-9]+)- ]]; then
  echo "Currently on issue #${BASH_REMATCH[1]}. Commits must start with \`#${BASH_REMATCH[1]} \`."
  echo "If this request is unrelated to #${BASH_REMATCH[1]}, it needs its own issue and branch."
fi
echo "</project-rule>"

exit 0
