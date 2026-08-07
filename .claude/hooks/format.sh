#!/usr/bin/env bash
# PostToolUse hook for Edit / Write.
#
# Formats the file that was just written, so formatting never shows up as diff
# noise in a review. Silent and non-blocking: if Prettier is not installed yet
# (before the project is scaffolded) or the file is not a type it handles, this
# exits cleanly without complaining.
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PRETTIER="$ROOT/node_modules/.bin/prettier"

[[ -x "$PRETTIER" ]] || exit 0

FILE="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)"

[[ -n "$FILE" && -f "$FILE" ]] || exit 0

case "$FILE" in
  *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.scss|*.html|*.md|*.yml|*.yaml) ;;
  *) exit 0 ;;
esac

"$PRETTIER" --write --ignore-unknown "$FILE" >/dev/null 2>&1

exit 0
