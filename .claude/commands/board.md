---
description: Milestone and issue status overview
allowed-tools: Bash(gh:*), Bash(git:*)
---

## Milestones

!`gh api repos/{owner}/{repo}/milestones --state all --jq '.[] | "\(.title) [\(.state)] — \(.open_issues) open, \(.closed_issues) closed"' 2>/dev/null || echo "none"`

## Open issues

!`gh issue list --state open --limit 60 --json number,title,milestone,labels,assignees --jq '.[] | "#\(.number) \(.title)\n    milestone: \(.milestone.title // "NONE")  labels: \(if (.labels|length)>0 then ([.labels[].name]|join(", ")) else "NONE" end)"' 2>/dev/null || echo "none"`

## Open pull requests

!`gh pr list --state open --json number,title,headRefName,isDraft --jq '.[] | "#\(.number) \(.title) [\(.headRefName)]\(if .isDraft then " (draft)" else "" end)"' 2>/dev/null || echo "none"`

## Local

Branch: !`git branch --show-current`
Uncommitted: !`git status --porcelain | wc -l | tr -d ' '` file(s)
Branches: !`git branch --format='%(refname:short)' | tr '\n' ' '`

## Task

Summarise the state of the project for the decision driver. Be concise and factual.

- Which milestone is active, and how far through it the work is
- What is in flight right now, and whether anything is stalled
- Anything **blocked** — check dependencies for open issues:
  `gh api repos/{owner}/{repo}/issues/<nr>/dependencies/blocked_by`
- Any issue violating the rules: no milestone, no labels, `size/xl` needing a split
- Any local branch with no open PR, or unpushed work

Close with a recommended next action — the single most useful thing to do next, and why.
