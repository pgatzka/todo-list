---
description: Verify the branch, push it and open the pull request
argument-hint: <issue-nr>
allowed-tools: Bash, Read, Grep, Glob, Task
---

## State

Branch: !`git branch --show-current`
Uncommitted: !`git status --porcelain | wc -l | tr -d ' '` file(s)
Commits vs main: !`git log main..HEAD --format='%s' 2>/dev/null || echo "none"`
Changed files: !`git diff main...HEAD --stat 2>/dev/null | tail -20 || echo "none"`

## Issue

!`gh issue view $1 --json number,title,body --jq '"#\(.number) \(.title)\n\n\(.body)"' 2>/dev/null || echo "Issue $1 not found."`

## Task

Ship issue #$1. Delegate to `release-manager`.

**Refuse to open the PR and report which check failed if any of these do not hold:**

- Branch is `$1-<something>`, not `main`
- Working tree is clean
- Every commit subject above starts with `#$1 `
- No file in the diff is unrelated to #$1
- The issue's Definition of Done is genuinely satisfied
- `npm run lint && npm run typecheck && npm test && npm run build` all pass — run them, do not assume

Then:

```bash
git push -u origin "$(git branch --show-current)"

gh pr create --base main \
  --title "#$1 <issue title>" \
  --body "$(cat <<'EOF'
Closes #$1

## What changed
<summary>

## Definition of Done
- [x] <each line from the issue, checked>

## Verification
<actual output of lint, typecheck, test, build>
EOF
)"
```

`Closes #$1` is mandatory — CI fails the PR without it and the issue will not auto-close.

Finally, watch CI: `gh pr checks --watch`. If it goes red, diagnose and fix on the branch. Never merge red and never bypass a failing check with `--admin`.

Report the PR URL and the CI result.
