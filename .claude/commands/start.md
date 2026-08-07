---
description: Branch off main for an issue and check it out
argument-hint: <issue-nr>
allowed-tools: Bash(gh:*), Bash(git:*), Read
---

## Issue

!`gh issue view $1 --json number,title,state,milestone,labels,body --jq '"#\(.number) [\(.state)] \(.title)\nMilestone: \(.milestone.title // "NONE")\nLabels: \(if (.labels|length)>0 then ([.labels[].name]|join(", ")) else "NONE" end)\n\n\(.body)"' 2>/dev/null || echo "Issue $1 not found."`

Blocked by: !`gh api repos/{owner}/{repo}/issues/$1/dependencies/blocked_by --jq 'if length==0 then "nothing" else (.[] | "#\(.number) [\(.state)] \(.title)") end' 2>/dev/null || echo "unknown"`

Current state: !`git branch --show-current` — !`git status --porcelain | wc -l | tr -d ' '` uncommitted change(s)

## Task

Start work on issue #$1.

1. **Verify the issue is workable.** Stop and report if any of these fail:
   - It exists and is open
   - It has a milestone
   - It has at least one label
   - Nothing that blocks it is still open — if something is, say what and stop

   If the milestone or labels are missing, fix them via `issue-manager` before branching.

2. **Make sure the tree is clean.** Uncommitted changes belong to whatever came before; do not drag them onto a new branch.

3. **Branch from an up-to-date main:**

   ```bash
   git checkout main && git pull
   git checkout -b $1-<kebab-case-title>
   ```

   The slug comes from the issue title: lowercase, hyphens, no punctuation, trimmed to something readable.

4. **Report** the branch name, the Definition of Done to be satisfied, and the reminder that commits on this branch start with `#$1 `.

Suggest `/work $1` next.
