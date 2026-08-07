---
description: Find an existing issue for a request, or create a properly labelled, milestoned and linked one
argument-hint: <what needs doing>
allowed-tools: Bash(gh:*), Read, Grep, Glob, Task
---

## Request

$ARGUMENTS

## Existing issues

Open: !`gh issue list --state open --limit 40 --json number,title,milestone,labels --jq '.[] | "#\(.number) \(.title) [\(.milestone.title // "no milestone")] \([.labels[].name] | join(", "))"' 2>/dev/null || echo "none"`

Milestones: !`gh api repos/{owner}/{repo}/milestones --jq '.[] | "\(.title) — \(.open_issues) open, \(.closed_issues) closed"' 2>/dev/null || echo "none"`

## Task

Delegate to the `issue-manager` agent.

1. **Search before creating**, closed issues included, so this does not become a duplicate:
   `gh issue list --search "<keywords>" --state all`
2. If an existing issue covers the request, report it and stop — do not create a second one.
3. If nothing covers it, create an issue with **all** of:
   - A title naming the outcome, not the activity
   - One `type/*` label and one `area/*` label
   - A milestone
   - `priority/*` and `size/*` where they can be judged
   - A body with `## Scope` and an explicit `## Definition of Done` checklist
4. **Then look for links** — this is the step that gets skipped:
   - Is it a child of an existing epic? Attach it as a sub-issue.
   - Does something have to land first? Record a blocked-by dependency.
   - Does it unblock something already open? Record that from the other side.

   Both relationships need the database id, not the issue number:

   ```bash
   CHILD_ID=$(gh api repos/{owner}/{repo}/issues/<child-nr> --jq '.id')
   gh api --method POST repos/{owner}/{repo}/issues/<parent-nr>/sub_issues -F sub_issue_id=$CHILD_ID

   BLOCKER_ID=$(gh api repos/{owner}/{repo}/issues/<blocker-nr> --jq '.id')
   gh api --method POST repos/{owner}/{repo}/issues/<nr>/dependencies/blocked_by -F issue_id=$BLOCKER_ID
   ```

5. If the request is really several pieces of work, propose an epic with sub-issues rather than one oversized issue.

Report the issue number and URL, and state whether to start it now with `/start <nr>`.
