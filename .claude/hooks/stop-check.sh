#!/usr/bin/env bash
# Stop hook.
#
# Surfaces work that is finished in the transcript but not yet in the repository:
# uncommitted changes, unpushed commits, or a branch with no pull request. Emits a
# systemMessage so the user sees it. Deliberately never blocks — a warning that
# forces the model to keep going would loop.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" 2>/dev/null || exit 0

BRANCH="$(git branch --show-current 2>/dev/null)"
[[ -n "$BRANCH" && "$BRANCH" != "main" ]] || exit 0

WARNINGS=()

DIRTY="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
[[ "$DIRTY" != "0" ]] && WARNINGS+=("$DIRTY uncommitted change(s)")

if git rev-parse --abbrev-ref "@{upstream}" >/dev/null 2>&1; then
  AHEAD="$(git rev-list --count "@{upstream}..HEAD" 2>/dev/null || echo 0)"
  [[ "$AHEAD" != "0" ]] && WARNINGS+=("$AHEAD unpushed commit(s)")
else
  WARNINGS+=("branch has never been pushed")
fi

if [[ ${#WARNINGS[@]} -eq 0 ]] && command -v gh >/dev/null 2>&1; then
  PR="$(gh pr list --head "$BRANCH" --state open --json number --jq 'length' 2>/dev/null || echo "")"
  [[ "$PR" == "0" ]] && WARNINGS+=("no open pull request for this branch")
fi

[[ ${#WARNINGS[@]} -eq 0 ]] && exit 0

# IFS joining only ever uses the first character, so build the list explicitly.
JOINED="${WARNINGS[0]}"
for ((i = 1; i < ${#WARNINGS[@]}; i++)); do JOINED+="; ${WARNINGS[$i]}"; done

MSG="Branch \`$BRANCH\` is not fully shipped: $JOINED. Run /ship <issue-nr> to finish."
python3 -c 'import json,sys; print(json.dumps({"systemMessage": sys.argv[1]}))' "$MSG"

exit 0
