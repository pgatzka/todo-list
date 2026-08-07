---
name: issue-authoring
description: How to write a good issue for this project — titles, scope, Definition of Done, the full label taxonomy, when to split versus link, and how to structure epics. Use when creating or rewriting GitHub issues, or when grooming the backlog.
---

# Issue authoring

An issue is a contract. It says what will exist afterwards that does not exist now, and how anyone can check.

## Title

Name the **outcome**, not the activity.

| Poor            | Better                                        |
| --------------- | --------------------------------------------- |
| Work on storage | Todos persist across reloads                  |
| Fix bug         | Completing a todo no longer clears the filter |
| Improve UI      | Todo list is keyboard-navigable end to end    |
| Add tests       | Todo reducer has coverage for every action    |

No prefixes like `[FEATURE]` — that is what `type/*` labels are for.

## Body

```markdown
## Context

Why this matters now. Skip if self-evident.

## Scope

What is in. Just as importantly, what is deliberately out.

## Definition of Done

- [ ] A verifiable outcome
- [ ] Another verifiable outcome
```

The Definition of Done is the part that matters. Each line must be checkable by someone who did not write the code.

- Bad: `Storage works properly`
- Good: `Reloading the page restores the exact todo list, including completed state`
- Bad: `Good test coverage`
- Good: `Every reducer action has a test, including the empty-list and duplicate-title cases`

For bugs, add reproduction steps, actual behaviour, and expected behaviour. A bug issue without repro steps is a rumour.

## Labels

Every issue needs at least one `type/*` and one `area/*`.

**`type/`** — what kind of change
`feature` new user-facing capability · `bug` something broken · `chore` maintenance, tooling, dependencies · `docs` documentation only · `test` tests and test infrastructure · `refactor` internal change with no behaviour change

**`area/`** — where it lands
`ui` React components and styling · `state` application state and data model · `build` Vite, TypeScript, bundling · `ci` GitHub Actions and automation · `workflow` Claude Code setup, agents, hooks, process · `docs` README, ADRs, guides · `testing` Vitest and coverage · `a11y` accessibility

**`priority/`** — `p0` blocks everything · `p1` next up · `p2` normal · `p3` nice to have

**`size/`** — `xs` under 1h · `s` 1–3h · `m` half a day · `l` 1–2 days · `xl` should probably be split

**`status/`** — `blocked` · `needs-decision` awaiting the customer · `in-review` PR open · `ready` groomed and startable

## Milestones

Every issue gets exactly one.

| Milestone              | Holds                                                               |
| ---------------------- | ------------------------------------------------------------------- |
| M0 Foundation          | Governance, workflow, scaffold, CI — everything before feature work |
| M1 Core Todo CRUD      | Create, read, update, delete, complete. The minimum usable product  |
| M2 Persistence         | Todos survive a reload                                              |
| M3 UX                  | Filtering, sorting, keyboard support, accessibility, polish         |
| M4 Quality and Release | Coverage, e2e, build hardening, first tagged release                |

If an issue does not fit any milestone, either it is premature or the milestone set is wrong. Raise it rather than forcing a fit.

## Split or link

**Split** when the issue has more than one independently shippable outcome, is `size/xl`, or spans several `area/*` labels. Three issues of `size/s` beat one of `size/l` — they review better and land sooner.

**Do not split** to the point where a piece has no standalone value. An issue that produces nothing observable is a task, not an issue; keep it as a step in the body.

**Epics.** When work naturally groups, create a parent issue titled `Epic: <theme>`, labelled `size/xl`, whose body states what "done" means for the whole group. Attach children as real sub-issues via the API — never as a checklist of `#nr` in the body, which nothing can query.

**Dependencies.** If A must land before B, record it structurally with `dependencies/blocked_by`. Prose like "after #3 lands" is invisible to every tool and to the next person reading the board.

Exact commands for both live in the `github-workflow` skill.

## Common failures

- A Definition of Done nobody can verify
- Missing milestone or missing labels — violates the prime rule
- An epic whose children are markdown checkboxes instead of sub-issues
- Dependencies described in prose and never recorded
- Two issues quietly covering the same work because nobody searched closed issues
- `size/xl` issues that sat unsplit until they became unreviewable
