#!/usr/bin/env python3
"""PreToolUse guard for Bash.

Enforces three project rules mechanically:
  1. No commits on `main`.
  2. Every commit message starts with `#<issue-nr> `.
  3. The issue number in the message matches the issue number in the branch name.

Also blocks force pushes to `main` and direct pushes from `main`.

Exit code 2 denies the tool call and feeds stderr back to Claude.
"""

import json
import re
import subprocess
import sys

# Splits a compound command into segments we can inspect individually, so
# `cd foo && git commit -m "..."` is still caught. Newlines are deliberately not
# separators: a `-m "$(cat <<'EOF' ... )"` message spans lines, and splitting on
# them would detach the message body from its flag.
SEGMENT_SPLIT = re.compile(r"&&|\|\||;")

GIT_COMMIT = re.compile(r"\bgit\s+(?:-[^\s]+\s+)*commit\b")


def deny(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(2)


def current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def commit_subject(segment: str) -> str | None:
    """Pull the first non-empty line of a -m argument, heredocs included."""
    match = re.search(r"(?:^|\s)-[a-zA-Z]*m(?:\s+|=)(.*)", segment, re.S)
    if not match:
        return None

    rest = match.group(1)
    # Unwrap the `-m "$(cat <<'EOF' ... EOF)"` form Claude Code often emits.
    rest = re.sub(r"^\s*[\"']?\$\(\s*cat\s*<<-?\s*[\"']?\w+[\"']?\s*", "", rest)
    rest = rest.lstrip().lstrip("\"'")

    for line in rest.splitlines():
        line = line.strip().rstrip("\"'")
        if line:
            return line
    return None


def branch_issue_number(branch: str) -> str | None:
    match = re.match(r"^(\d+)-", branch)
    return match.group(1) if match else None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # Never block on a malformed payload.

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    branch = current_branch()
    on_main = branch == "main"

    # Commit checks scan the whole command, taking everything after each
    # `git commit` up to the next `&&`/`||`/`;`, so multi-line heredoc messages
    # survive intact while `git commit -m "..." && git push` still splits.
    for match in GIT_COMMIT.finditer(command):
        segment = SEGMENT_SPLIT.split(command[match.end():])[0]

        if on_main:
            deny(
                "BLOCKED: you are on `main`, which is never worked on.\n"
                "Create an issue, then branch: "
                "git checkout -b <issue-nr>-<kebab-title>"
            )

        # --amend without -m reuses an already-validated message.
        if "--amend" in segment and not re.search(r"(?:^|\s)-[a-zA-Z]*m(?:\s|=)", segment):
            continue
        if re.search(r"(?:^|\s)(--no-edit|-C|--reuse-message)\b", segment):
            continue

        subject = commit_subject(segment)
        if subject is None:
            deny(
                "BLOCKED: commit without an inline -m message.\n"
                "Use: git commit -m \"#<issue-nr> Imperative subject\""
            )

        if not re.match(r"^#\d+\s+\S", subject):
            deny(
                f"BLOCKED: commit message must start with '#<issue-nr> '.\n"
                f"Got: {subject!r}\n"
                f"Expected shape: '#42 Add controlled input for new todo text'"
            )

        expected = branch_issue_number(branch)
        actual = re.match(r"^#(\d+)", subject).group(1)
        if expected and actual != expected:
            deny(
                f"BLOCKED: issue number mismatch.\n"
                f"Branch `{branch}` is issue #{expected}, "
                f"but the commit says #{actual}.\n"
                f"Either fix the message or switch to the right branch."
            )

    # Push checks are per-segment: unlike a commit message, a push never spans
    # lines, so the finer split is safe here.
    for raw in SEGMENT_SPLIT.split(command):
        for segment in raw.strip().splitlines():
            if not re.search(r"\bgit\s+push\b", segment):
                continue

            forced = re.search(r"(?:^|\s)(--force(?!-with-lease)|-f)(?:\s|$)", segment)
            if forced and re.search(r"\bmain\b", segment):
                deny("BLOCKED: force pushing to `main` is forbidden.")
            if on_main:
                deny(
                    "BLOCKED: pushing from `main`. Work happens on issue branches.\n"
                    "`main` only ever receives merges via pull request."
                )

    sys.exit(0)


if __name__ == "__main__":
    main()
