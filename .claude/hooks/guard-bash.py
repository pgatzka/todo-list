#!/usr/bin/env python3
"""PreToolUse guard for Bash.

Enforces three project rules mechanically:
  1. No commits on `main`.
  2. Every commit message starts with `#<issue-nr> `.
  3. The issue number in the message matches the issue number in the branch name.

Also blocks force pushes to `main` and direct pushes from `main`.

Detection is token-based rather than substring-based. An earlier version scanned
the raw command text, so writing *about* a commit — quoting one in a `gh issue
create --body`, say — tripped the guard even though nothing was being committed.
Shell tokenisation collapses a quoted argument into a single token, so a mention
inside quotes can no longer look like an invocation.

Exit code 2 denies the tool call and feeds stderr back to Claude. Exit 0 allows.
Any other exit is a non-blocking error that would let the call through, so
`run-guard.sh` wraps this script and converts anything else into a 2.
"""

import json
import re
import shlex
import subprocess
import sys

# git's own options that consume the following token, so a subcommand scan does
# not mistake their value for the subcommand.
GIT_VALUE_FLAGS = frozenset(
    {"-c", "-C", "--git-dir", "--work-tree", "--exec-path", "--namespace", "--super-prefix"}
)

# Forms that reuse an already-validated message instead of supplying a new one.
MESSAGE_REUSING_FLAGS = frozenset({"--no-edit", "-C", "--reuse-message", "--squash", "--fixup"})


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


def branch_issue_number(branch: str) -> str | None:
    match = re.match(r"^(\d+)-", branch)
    return match.group(1) if match else None


def tokenize(command: str) -> list[str] | None:
    """Split into shell tokens, or None when the text will not parse."""
    try:
        return shlex.split(command)
    except ValueError:
        return None


def git_subcommand_args(tokens: list[str], subcommand: str) -> list[list[str]]:
    """Every argument list following a real `git <subcommand>` invocation."""
    found = []
    for index, token in enumerate(tokens):
        if token != "git":
            continue
        cursor = index + 1
        while cursor < len(tokens) and tokens[cursor].startswith("-"):
            cursor += 2 if tokens[cursor] in GIT_VALUE_FLAGS else 1
        if cursor < len(tokens) and tokens[cursor] == subcommand:
            found.append(tokens[cursor + 1 :])
    return found


def first_line(value: str) -> str | None:
    """First non-empty line of a message, unwrapping the heredoc form."""
    # `-m "$(cat <<'EOF' ... EOF)"` survives tokenisation as one token.
    value = re.sub(r"^\s*\$\(\s*cat\s*<<-?\s*[\"']?\w+[\"']?\s*", "", value)
    for line in value.splitlines():
        line = line.strip()
        if line:
            return line
    return None


def commit_subject(args: list[str]) -> str | None:
    """The subject line supplied to a commit, or None if none was."""
    for position, arg in enumerate(args):
        following = args[position + 1] if position + 1 < len(args) else None

        if arg in ("-m", "--message"):
            return first_line(following) if following is not None else None
        if arg.startswith("--message="):
            return first_line(arg.split("=", 1)[1])
        # -m"subject" collapses to a single -msubject token.
        if arg.startswith("-m") and not arg.startswith("--") and len(arg) > 2:
            return first_line(arg[2:])
        # Combined short flags such as -am take their value as the next token.
        if (
            arg.startswith("-")
            and not arg.startswith("--")
            and len(arg) > 1
            and arg[1:].isalpha()
            and "m" in arg[1:]
        ):
            return first_line(following) if following is not None else None
    return None


def check_commit(args: list[str], branch: str, on_main: bool) -> None:
    if on_main:
        deny(
            "BLOCKED: you are on `main`, which is never worked on.\n"
            "Create an issue, then branch: "
            "git checkout -b <issue-nr>-<kebab-title>"
        )

    if any(flag in MESSAGE_REUSING_FLAGS for flag in args):
        return
    if "--amend" in args and commit_subject(args) is None:
        return

    subject = commit_subject(args)
    if subject is None:
        deny(
            "BLOCKED: commit without an inline -m message.\n"
            'Use: git commit -m "#<issue-nr> Imperative subject"'
        )

    if not re.match(r"^#\d+\s+\S", subject):
        deny(
            "BLOCKED: commit message must start with '#<issue-nr> '.\n"
            f"Got: {subject!r}\n"
            "Expected shape: '#42 Add controlled input for new todo text'"
        )

    expected = branch_issue_number(branch)
    actual = re.match(r"^#(\d+)", subject).group(1)
    if expected and actual != expected:
        deny(
            "BLOCKED: issue number mismatch.\n"
            f"Branch `{branch}` is issue #{expected}, "
            f"but the commit says #{actual}.\n"
            "Either fix the message or switch to the right branch."
        )


def check_push(args: list[str], on_main: bool) -> None:
    forced = any(
        arg == "-f" or (arg.startswith("--force") and arg != "--force-with-lease")
        for arg in args
    )
    if forced and "main" in args:
        deny("BLOCKED: force pushing to `main` is forbidden.")
    if on_main:
        deny(
            "BLOCKED: pushing from `main`. Work happens on issue branches.\n"
            "`main` only ever receives merges via pull request."
        )


def fallback_scan(command: str, branch: str, on_main: bool) -> None:
    """Used only when the command will not tokenise.

    Unparseable text means the structure is unknown, so this errs toward
    blocking: a guard that guesses wrong should refuse, not wave things through.
    """
    if re.search(r"\bgit\s+(?:-\S+\s+)*commit\b", command):
        deny(
            "BLOCKED: this command mentions a commit but could not be parsed "
            "(unbalanced quotes?), so the guard cannot verify it.\n"
            "Rewrite it so the quoting is balanced, then retry."
        )
    if on_main and re.search(r"\bgit\s+push\b", command):
        deny("BLOCKED: pushing from `main`. Work happens on issue branches.")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # A malformed payload is the harness's problem, not a policy violation.
        sys.exit(0)

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    branch = current_branch()
    on_main = branch == "main"

    tokens = tokenize(command)
    if tokens is None:
        fallback_scan(command, branch, on_main)
        sys.exit(0)

    for args in git_subcommand_args(tokens, "commit"):
        check_commit(args, branch, on_main)

    for args in git_subcommand_args(tokens, "push"):
        check_push(args, on_main)

    sys.exit(0)


if __name__ == "__main__":
    main()
