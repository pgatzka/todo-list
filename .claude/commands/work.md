---
description: Run the full delivery loop for an issue — design, implement, test, review
argument-hint: <issue-nr>
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task, TodoWrite
---

## Issue

!`gh issue view $1 --json number,title,state,milestone,labels,body --jq '"#\(.number) [\(.state)] \(.title)\nMilestone: \(.milestone.title // "NONE")\nLabels: \(if (.labels|length)>0 then ([.labels[].name]|join(", ")) else "NONE" end)\n\n\(.body)"' 2>/dev/null || echo "Issue $1 not found."`

Branch: !`git branch --show-current`

## Task

Deliver issue #$1 end to end.

**Precondition.** The checked-out branch must be `$1-<something>`. If it is `main` or another issue's branch, stop and run `/start $1` first. Hooks will block you otherwise.

Then run the loop, delegating to the specialists rather than doing everything inline:

1. **Design** — `ux-designer` first if this is user-facing, then `architect` for anything `size/m` or larger, that adds a dependency, or that changes the data model. Skip for genuinely trivial issues and say why. If the design involves a decision the customer should own, draft the ADR and get approval before implementing.

2. **Implement** — `implementer` writes the code on the branch, committing at each meaningful step with `#$1 ` prefixes.

3. **Test** — `test-engineer` writes tests against the issue's Definition of Done, independently of how the implementer built it.

4. **Review** — `code-reviewer` checks traceability, scope, DoD and conventions, and dispatches deep review to the `pr-review-toolkit` specialists.

5. **Document** — `docs-writer` if behaviour, setup or architecture changed.

6. **Fix what review found**, then re-review. Do not carry known blocking findings into a PR.

## Scope discipline

Anything you find that is outside this issue's scope does **not** get fixed here. Note it, finish #$1, and report it at the end so it becomes its own issue. If #$1 turns out to be materially bigger than described, stop and propose a split.

## Report

Finish with the real output of `npm run lint && npm run typecheck && npm test && npm run build`, the DoD walked line by line, and anything found for follow-up. If checks fail, say so with the output — do not report done on red.

Suggest `/ship $1` when it is genuinely ready.
