#!/usr/bin/env python3
"""PreToolUse guard for Edit / Write / NotebookEdit.

Blocks modification of files inside this repository while `main` is checked out.
Work belongs on an issue branch; `main` only ever receives merges via pull
request.

Paths outside the working tree — agent memory under `~/.claude`, scratch files
in `/tmp` — are none of that rule's business: they have no commit to belong to,
so no branch can gate them. They are left alone.

Exit code 2 denies the tool call and feeds stderr back to Claude.
"""

import json
import subprocess
import sys
from pathlib import Path

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


def repository_root() -> Path | None:
    """The working tree this guard defends, or None when it cannot be found.

    Derived from the guard's own location — it lives at `<root>/.claude/hooks/`
    — rather than from the payload's cwd, which may point anywhere on the
    filesystem and would make git report a different repository or none at all.
    git confirms the directory really is a working tree and canonicalises it.
    """
    result = subprocess.run(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    root = result.stdout.strip()
    if result.returncode != 0 or not root:
        return None
    return Path(root).resolve()


def inside_repository(path: str) -> bool:
    """Whether `path` lands inside the working tree.

    Both sides are resolved before comparison, so symlinks and `..` segments are
    judged by where they actually point, and the comparison is by path component
    rather than by string prefix — `todo-list-notes` is not inside `todo-list`.

    A relative path resolves against the process cwd, which is the session
    directory the Edit tool itself resolves against. The payload's `cwd` field
    would be the same directory, but it travels with the tool call and so could
    contradict it; a guard must not take routing advice from what it is judging.

    Fails closed: an undiscoverable root or an unresolvable path counts as
    inside, because a guard that cannot tell must block rather than wave through.
    """
    root = repository_root()
    if root is None:
        return True
    try:
        return (Path.cwd() / path).resolve().is_relative_to(root)
    except (OSError, ValueError, RuntimeError):
        return True


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

    if not inside_repository(path):
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
