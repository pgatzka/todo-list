---
name: github-workflow
description: The canonical issue-to-merge workflow for this repository, with exact gh commands for creating issues, linking sub-issues and dependencies, branching, committing, opening PRs and closing milestones. Use whenever interacting with GitHub issues, branches, pull requests or milestones in this project.
---

# GitHub workflow

The full path from a user request to merged code. Every step is mandatory; skipping one produces work that cannot be traced.

## Environment note

The installed `gh` is **2.46**, which predates native sub-issue and dependency commands. Both relationships must go through `gh api`. Both take the issue's **database id**, not its number — this is the single most common mistake.

```bash
gh api repos/{owner}/{repo}/issues/<nr> --jq '.id'   # 5089574331, not 2
```

`{owner}/{repo}` is substituted automatically by `gh` inside the repository.

## 1. Find or create the issue

Search first, closed issues included:

```bash
gh issue list --search "<keywords>" --state all --limit 30 \
  --json number,title,state,milestone
```

If nothing covers it:

```bash
gh issue create \
  --title "Todos persist across reloads" \
  --milestone "M2 Persistence" \
  --label type/feature --label area/state --label priority/p1 --label size/m \
  --body '## Scope

<what is in and what is out>

## Definition of Done

- [ ] <verifiable outcome>
- [ ] <verifiable outcome>'
```

Required on every issue: a milestone, one `type/*` label, one `area/*` label, and a `## Definition of Done` checklist.

## 2. Link it

Ask three questions and act on each:

**Is it part of something bigger?**

```bash
CHILD_ID=$(gh api repos/{owner}/{repo}/issues/14 --jq '.id')
gh api --method POST repos/{owner}/{repo}/issues/1/sub_issues -F sub_issue_id=$CHILD_ID
```

**Does something have to land first?**

```bash
BLOCKER_ID=$(gh api repos/{owner}/{repo}/issues/3 --jq '.id')
gh api --method POST repos/{owner}/{repo}/issues/14/dependencies/blocked_by -F issue_id=$BLOCKER_ID
```

**Reading relationships back:**

```bash
gh api repos/{owner}/{repo}/issues/1/sub_issues --jq '.[] | "#\(.number) [\(.state)] \(.title)"'
gh api repos/{owner}/{repo}/issues/14/dependencies/blocked_by --jq '.[] | "#\(.number) [\(.state)]"'
gh api repos/{owner}/{repo}/issues/3/dependencies/blocking --jq '.[] | "#\(.number)"'
```

Removing a sub-issue: `gh api --method DELETE repos/{owner}/{repo}/issues/1/sub_issues -F sub_issue_id=$CHILD_ID`

## 3. Branch

Never from a stale `main`, never while dirty:

```bash
git checkout main && git pull
git checkout -b 14-todos-persist-across-reloads
```

Pattern: `<issue-nr>-<kebab-case-title>`.

## 4. Commit

Every message starts with `#<issue-nr>` and a space:

```bash
git commit -m "#14 Add localStorage adapter for the todo list"
```

A hook blocks anything else, including a `#<nr>` that does not match the branch. One logical change per commit; imperative subject under 72 characters; no tool advertising or `Co-Authored-By` trailers.

## 5. Verify

```bash
npm run lint && npm run typecheck && npm test && npm run build
```

Run it, read the output, report it truthfully. Do not open a PR on red.

## 6. Pull request

```bash
git push -u origin "$(git branch --show-current)"

gh pr create --base main \
  --title "#14 Todos persist across reloads" \
  --body "$(cat <<'EOF'
Closes #14

## What changed
<summary>

## Definition of Done
- [x] <each line from the issue>

## Verification
<actual command output>
EOF
)"
```

`Closes #14` is mandatory. CI fails the PR without it, and the issue will not auto-close on merge.

## 7. Land it

```bash
gh pr checks --watch
gh pr merge 14 --squash --delete-branch
```

Green CI only. Never `--admin` past a failing check. Afterwards, confirm the issue actually closed — if it did not, the link was wrong.

## 8. Close the milestone

When every issue in it is closed:

```bash
gh api repos/{owner}/{repo}/milestones --jq '.[] | "\(.number) \(.title) — \(.open_issues) open"'
gh api --method PATCH repos/{owner}/{repo}/milestones/2 -f state=closed
```

## Reference

**Labels** — `type/`: feature, bug, chore, docs, test, refactor · `area/`: ui, state, build, ci, workflow, docs, testing, a11y · `priority/`: p0–p3 · `size/`: xs, s, m, l, xl · `status/`: blocked, needs-decision, in-review, ready

**Milestones** — M0 Foundation · M1 Core Todo CRUD · M2 Persistence · M3 UX · M4 Quality and Release

## When a hook blocks you

Blocked commits and edits mean a process step was skipped, not that the tooling is in the way. Read the message, go back, do the missing step. Do not work around a guard.
