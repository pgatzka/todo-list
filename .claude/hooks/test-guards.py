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
import tempfile
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
    # --- heredoc bodies are data, not shell syntax (issue #15) ------------
    (
        "prose heredoc mentioning a commit",
        "cat > /tmp/pr.md <<'BODY'\n"
        f"The guard's behaviour: run {GC} -m \"#1 x\" and it won't complain.\n"
        "BODY",
        ALLOW,
    ),
    (
        "bare heredoc body with apostrophes",
        "gh pr create --body-file - <<'EOF'\n"
        f"Don't worry, {GC} isn't run here.\n"
        "EOF",
        ALLOW,
    ),
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


def run(script: Path, payload: dict, cwd: Path | None = None) -> int:
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=None if cwd is None else str(cwd),
    ).returncode


def make_main_repo(parent: Path) -> Path:
    """A throwaway repository whose checked-out branch really is `main`.

    guard-edit.py short-circuits to ALLOW off main, so its path-scope rule can
    only be exercised from a working tree that is genuinely on main. The guard is
    copied to its real relative location inside that tree because it derives the
    repository root from its own path. An unborn `main` is enough for
    `git branch --show-current`, so no commit is needed.
    """
    repo = parent / "todo-list"
    (repo / ".claude" / "hooks").mkdir(parents=True)
    shutil.copy(GUARD_EDIT, repo / ".claude" / "hooks" / GUARD_EDIT.name)
    (repo / "src").mkdir()
    for args in (
        ["init", "--quiet", str(repo)],
        ["-C", str(repo), "symbolic-ref", "HEAD", "refs/heads/main"],
    ):
        subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return repo


def edit_scope_cases(repo: Path, outside: Path) -> list[tuple[str, dict, int]]:
    """Path-scope cases judged from a working tree that is on `main`.

    Each case is run with the process cwd at the fixture root, which is where a
    relative `file_path` really resolves. The payload's own `cwd` field is varied
    deliberately: the guard must not take routing advice from it.
    """

    def case(name: str, file_path: str, expected: int, cwd: Path = repo) -> tuple[str, dict, int]:
        return name, {"tool_input": {"file_path": file_path}, "cwd": str(cwd)}, expected

    return [
        case("tracked path inside the tree", str(repo / ".claude" / "hooks" / "guard-edit.py"), BLOCK),
        case("untracked path inside the tree", str(repo / "src" / "App.tsx"), BLOCK),
        case("relative path inside the tree", "src/App.tsx", BLOCK),
        case("absolute path outside the tree", str(outside / "autonomy-boundary.md"), ALLOW),
        case("relative path escaping the tree", "../outside/autonomy-boundary.md", ALLOW),
        case("relative path escaping and returning", "../todo-list/src/App.tsx", BLOCK),
        # A string prefix check would call this one inside the tree.
        case("sibling whose name extends the root", str(repo.parent / "todo-list-notes" / "x.md"), ALLOW),
        case("allowlisted path stays editable", str(repo / ".claude" / "settings.local.json"), ALLOW),
        # A payload that claims to live elsewhere must not turn an in-tree edit
        # into an out-of-tree one.
        case("payload cwd outside the tree is ignored", "src/App.tsx", BLOCK, cwd=outside),
    ]


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

    print("\nguard-edit.py — path scope on main (issue #72)")
    with tempfile.TemporaryDirectory() as temp:
        repo = make_main_repo(Path(temp))
        outside = Path(temp) / "outside"
        outside.mkdir()
        guard = repo / ".claude" / "hooks" / GUARD_EDIT.name
        scope_cases = edit_scope_cases(repo, outside)
        for name, payload, expected in scope_cases:
            actual = run(guard, payload, cwd=repo)
            ok = actual == expected
            failures += not ok
            print(f"  {'pass' if ok else 'FAIL'}  exp={expected} got={actual}  {name}")

        # A copy sitting outside any working tree cannot discover a root, which
        # is the fail-closed case: undecidable means block, not allow.
        loose = Path(temp) / "loose"
        loose.mkdir()
        shutil.copy(GUARD_EDIT, loose / GUARD_EDIT.name)
        actual = run(
            loose / GUARD_EDIT.name,
            {"tool_input": {"file_path": str(outside / "x.md")}, "cwd": str(repo)},
            cwd=repo,
        )
        ok = actual == BLOCK
        failures += not ok
        print(f"  {'pass' if ok else 'FAIL'}  exp={BLOCK} got={actual}  undiscoverable root fails closed")

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

    total = len(CASES) + 1 + len(scope_cases) + 1 + len(checks)
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
