#!/usr/bin/env bash
# Launcher for the PreToolUse Python guards.
#
# Exists because of one asymmetry in how Claude Code treats hook exit codes:
# exit 2 blocks the tool call, but ANY OTHER non-zero code is a non-blocking
# error and the call proceeds. So a guard that cannot start — missing
# interpreter, syntax error, unhandled exception — silently stops guarding.
# That happened on 2026-08-07: four commits ran unguarded because `python3`
# was not on PATH and the hook exited 127.
#
# This wrapper makes the guards fail CLOSED. Anything other than a clean
# allow (0) or a deliberate block (2) becomes a block.
#
# bash is a safe thing to depend on here: the four shell hooks in this
# directory have never failed to start.

set -uo pipefail

SCRIPT="${1:-}"
shift || true

if [[ -z "$SCRIPT" || ! -f "$SCRIPT" ]]; then
  echo "BLOCKED: guard script '$SCRIPT' not found. Failing closed." >&2
  exit 2
fi

# PATH first, then the usual absolute locations. `command -v` on an absolute
# path returns it only when it is executable, so one loop covers both.
PYTHON=""
for candidate in python3 python "$HOME/.local/bin/python3" /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "BLOCKED: no Python interpreter found, so $(basename "$SCRIPT") cannot run." >&2
  echo "The guard fails closed rather than letting an unchecked command through." >&2
  echo "Install Python 3, or put it on PATH, then retry." >&2
  exit 2
fi

"$PYTHON" "$SCRIPT" "$@"
status=$?

case "$status" in
  0 | 2)
    # 0 = allow, 2 = the guard deliberately blocked. Both are real verdicts.
    exit "$status"
    ;;
  *)
    echo "BLOCKED: $(basename "$SCRIPT") exited $status instead of reaching a verdict." >&2
    echo "A guard that cannot decide must not allow the call. Failing closed." >&2
    exit 2
    ;;
esac
