---
description: Sweep the backlog for missing labels, milestones, links and oversized issues
argument-hint: [milestone]
allowed-tools: Bash(gh:*), Read, Task
---

## Backlog

!`gh issue list --state open --limit 100 --json number,title,milestone,labels,body --jq '.[] | "#\(.number) \(.title)\n    milestone: \(.milestone.title // "NONE")  labels: \(if (.labels|length)>0 then ([.labels[].name]|join(", ")) else "NONE" end)"' 2>/dev/null || echo "none"`

## Milestones

!`gh api repos/{owner}/{repo}/milestones --jq '.[] | "\(.title) — \(.open_issues) open, \(.closed_issues) closed"' 2>/dev/null || echo "none"`

## Scope

$ARGUMENTS

## Task

Delegate to `issue-manager`. Audit the backlog and report findings **before** changing anything.

Check every open issue for:

1. **Missing milestone** — violates the prime rule, must be fixed
2. **Missing `type/*` or `area/*` label** — same
3. **No Definition of Done** in the body, or a DoD too vague to verify
4. **`size/xl`** — propose a concrete split into sub-issues
5. **Unrecorded relationships** — the single most commonly skipped step:
   - Issues that clearly belong under an existing epic but are not sub-issues
   - Ordering dependencies stated in prose but never recorded via the API
   - Issues blocked by something already closed, where the block should be released
6. **Duplicates or overlaps** between open issues
7. **Stale state labels** — `status/in-review` with no open PR, `status/blocked` whose blocker is closed
8. **Milestone drift** — an issue whose content clearly belongs in a different milestone

Verify relationships against the API rather than trusting the body text:

```bash
gh api repos/{owner}/{repo}/issues/<nr>/sub_issues
gh api repos/{owner}/{repo}/issues/<nr>/dependencies/blocked_by
```

## Output

A table of findings: issue, problem, proposed fix. Then ask which to apply. Apply only what is approved — grooming that silently rewrites the backlog is worse than none.
