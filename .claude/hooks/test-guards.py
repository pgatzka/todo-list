#!/usr/bin/env python3
"""Test matrix for the PreToolUse guards.

Run from the repository root while an issue branch is checked out:

    python3 .claude/hooks/test-guards.py

Exit code 0 means every case behaved as specified. The guards are the only thing
standing between a careless command and `main`, so they get tested like code.

Command strings are assembled from fragments rather than written literally,
because this file is itself read by the guard whenever it is edited — a literal
commit command in the source would trip the very rule under test.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
GUARD_BASH = HOOKS / "guard-bash.py"
GUARD_EDIT = HOOKS / "guard-edit.py"
RUNNER = HOOKS / "run-guard.sh"

ALLOW, BLOCK = 0, 2

GIT = "git"
COMMIT = "commit"
GC = f"{GIT} {COMMIT}"

# The branch these cases assume. The harness checks out nothing; it derives the
# real branch and skips number-sensitive cases when they cannot apply.
BRANCH = subprocess.run(
    ["git", "branch", "--show-current"], capture_output=True, text=True, check=False
).stdout.strip()
ISSUE = BRANCH.split("-", 1)[0] if BRANCH.split("-", 1)[0].isdigit() else None

HEREDOC = f"""{GC} -m "$(cat <<'EOF'
#{ISSUE} Heredoc subject

Body line
EOF
)\""""

CASES: list[tuple[str, str, int]] = [
    # --- the message rule -------------------------------------------------
    ("valid inline message", f'{GC} -m "#{ISSUE} Valid subject"', ALLOW),
    ("missing prefix", f'{GC} -m "Missing the prefix"', BLOCK),
    ("wrong issue number", f'{GC} -m "#999999 Wrong issue"', BLOCK),
    ("prefix with no subject", f'{GC} -m "#{ISSUE}"', BLOCK),
    ("heredoc message", HEREDOC, ALLOW),
    ("heredoc missing prefix", HEREDOC.replace(f"#{ISSUE} Heredoc", "Heredoc"), BLOCK),
    ("attached -m value", f'{GC} -m"#{ISSUE} Attached"', ALLOW),
    ("--message= form", f'{GC} --message="#{ISSUE} Long form"', ALLOW),
    ("combined -am flag", f'{GC} -am "#{ISSUE} Combined"', ALLOW),
    ("amend without message", f"{GC} --amend --no-edit", ALLOW),
    ("git -c before subcommand", f'{GIT} -c core.pager=cat {COMMIT} -m "#{ISSUE} Flagged"', ALLOW),
    # --- command shapes ---------------------------------------------------
    ("compound with &&", f'cd /tmp && {GC} -m "no prefix"', BLOCK),
    ("multiline block", f'git add .\n{GC} -m "#{ISSUE} After add"', ALLOW),
    ("multiline block, bad", f'git add .\n{GC} -m "bad"', BLOCK),
    # --- the over-blocking regression (issue #15) -------------------------
    (
        "commit quoted in single quotes",
        f"""gh issue create --body 'Use: {GC} -m "#<nr> Subject"'""",
        ALLOW,
    ),
    (
        "commit quoted in double quotes",
        f"gh issue create --body \"example: {GC} -m '#1 x'\"",
        ALLOW,
    ),
    ("commit inside a JSON payload", f'echo \'{{"cmd":"{GC} -m bad"}}\'', ALLOW),
    # --- pushes -----------------------------------------------------------
    ("force push to main", "git push --force origin main", BLOCK),
    ("force-with-lease to branch", "git push --force-with-lease origin 15-x", ALLOW),
    ("ordinary push", "git push -u origin some-branch", ALLOW),
    # --- unrelated --------------------------------------------------------
    ("npm test", "npm test", ALLOW),
    ("gh issue list", "gh issue list --state all", ALLOW),
    # --- unparseable text fails closed ------------------------------------
    ("unbalanced quotes near a commit", f'{GC} -m "unclosed', BLOCK),
]


def run(script: Path, payload: dict) -> int:
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    ).returncode


# Resolved while PATH is still intact: the no-interpreter case blanks PATH, which
# would otherwise hide bash from subprocess before the wrapper even starts.
BASH = shutil.which("bash") or "/bin/bash"


def run_via_wrapper(script: Path, payload: dict, env: dict | None = None) -> int:
    return subprocess.run(
        [BASH, str(RUNNER), str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    ).returncode


def main() -> int:
    if ISSUE is None:
        print(f"Refusing to run: branch {BRANCH!r} carries no issue number.")
        return 1

    failures = 0
    print(f"guard-bash.py — branch {BRANCH} (issue #{ISSUE})\n")
    for name, command, expected in CASES:
        actual = run(GUARD_BASH, {"tool_input": {"command": command}})
        ok = actual == expected
        failures += not ok
        print(f"  {'pass' if ok else 'FAIL'}  exp={expected} got={actual}  {name}")

    print("\nguard-edit.py")
    edit_payload = {"tool_input": {"file_path": "src/App.tsx"}}
    actual = run(GUARD_EDIT, edit_payload)
    ok = actual == ALLOW
    failures += not ok
    print(f"  {'pass' if ok else 'FAIL'}  exp={ALLOW} got={actual}  edit allowed off main")

    print("\nrun-guard.sh — fail-closed behaviour")
    checks = [
        ("valid command still allowed", GUARD_BASH, {"tool_input": {"command": "npm test"}}, None, ALLOW),
        ("blocked command still blocked", GUARD_BASH, {"tool_input": {"command": f'{GC} -m "bad"'}}, None, BLOCK),
        ("missing guard script", HOOKS / "does-not-exist.py", {}, None, BLOCK),
        # An empty PATH is how the 2026-08-07 failure looked from the hook's side.
        ("no interpreter on PATH", GUARD_BASH, {"tool_input": {"command": "npm test"}}, {"PATH": "/nonexistent", "HOME": "/nonexistent"}, BLOCK),
    ]
    for name, script, payload, env, expected in checks:
        actual = run_via_wrapper(script, payload, env)
        ok = actual == expected
        failures += not ok
        print(f"  {'pass' if ok else 'FAIL'}  exp={expected} got={actual}  {name}")

    total = len(CASES) + 1 + len(checks)
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
