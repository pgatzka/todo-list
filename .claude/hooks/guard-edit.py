#!/usr/bin/env python3
"""PreToolUse guard for Edit / Write / NotebookEdit.

Blocks any file modification while `main` is checked out. Work belongs on an
issue branch; `main` only ever receives merges via pull request.

Exit code 2 denies the tool call and feeds stderr back to Claude.
"""

import json
import subprocess
import sys

# Editing these while on main is harmless and sometimes necessary (for example
# a scratch note before an issue exists).
ALLOWED_ON_MAIN = (".claude/settings.local.json",)


def current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if current_branch() != "main":
        sys.exit(0)

    path = payload.get("tool_input", {}).get("file_path", "")
    if any(path.endswith(suffix) for suffix in ALLOWED_ON_MAIN):
        sys.exit(0)

    print(
        f"BLOCKED: `main` is checked out, so `{path}` cannot be edited.\n"
        "\n"
        "The project rule is: no work on main, and no work without an issue.\n"
        "  1. Find or create the issue:  gh issue list --search \"<keywords>\"\n"
        "  2. Branch off main:           git checkout -b <issue-nr>-<kebab-title>\n"
        "  3. Then make the edit.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
