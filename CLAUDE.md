# todo-list

A todo application built with TypeScript, React and Vite. **Every line of this project is implemented by Claude Code.** The user is the customer and the decision driver: they decide *what* and *why*, Claude decides *how* and does the work.

---

## The Prime Rule

> **No work without an issue.** Every change traces to a GitHub issue that has a milestone and at least one label.

When the user asks for anything that touches the repository:

1. **Search first.** `gh issue list --search "<keywords>" --state all` — does an issue already cover this?
2. **If yes**, work that issue.
3. **If no**, create one *before* touching a file. Assign a milestone, apply labels, link it to related issues.
4. **Then** branch, implement, commit, PR.

There is no step where code is written against no issue. If the user asks for something small, it still gets an issue — a `size/xs` issue is cheap, an untraceable commit is not.

---

## Branching

`main` is protected and is never worked on. The single exception was the initial empty-README commit, which is already done and will not recur.

Branch name pattern:

```
<issue-nr>-<kebab-case-title>
```

Examples: `2-claude-code-workflow-agents-commands-hooks-skills`, `14-add-todo-input-field`.

Always branch from an up-to-date `main`:

```bash
git checkout main && git pull && git checkout -b 14-add-todo-input-field
```

---

## Commits

Every commit message **starts with `#<issue-nr>` followed by a space**, so any commit traces back to its issue:

```
#14 Add controlled input for new todo text
#14 Handle empty-string submission
```

Rules:

- The `#<nr>` prefix is mandatory and enforced by a hook. Commits without it are blocked.
- The issue number must match the branch's issue number.
- Subject line in the imperative mood, under 72 characters.
- No `Co-Authored-By` or tool advertising in commit messages.
- One logical change per commit. Do not squash unrelated work together.

---

## Pull Requests

- Title: `#<nr> <issue title>`
- Body **must** contain `Closes #<nr>` — CI fails the PR otherwise.
- Body restates the Definition of Done as a checked list.
- CI (lint, typecheck, test, build) must be green before merge.
- Merge to `main` only via PR.

---

## Issue Hygiene

Every issue carries, at minimum:

- **One `type/*` label** — feature, bug, chore, docs, test, refactor
- **One `area/*` label** — ui, state, build, ci, workflow, docs, testing, a11y
- **A milestone** — M0 Foundation, M1 Core Todo CRUD, M2 Persistence, M3 UX, M4 Quality and Release

Optional but encouraged: `priority/p0`–`p3`, `size/xs`–`xl`, `status/*`.

**Always look for links.** Before finishing an issue, ask whether it is a child of an epic, blocks something, or is blocked by something. Use the sub-issue and dependency APIs documented in the `github-workflow` skill — not prose in the body.

---

## Definition of Done

An issue is not done until *all* of the following hold:

- [ ] The Definition of Done listed in the issue body is satisfied
- [ ] `npm run lint`, `npm run typecheck`, `npm test` and `npm run build` pass locally
- [ ] New behaviour has tests; fixed bugs have a regression test
- [ ] Documentation touched by the change is updated
- [ ] Architectural decisions are recorded as an ADR under `docs/adr/`
- [ ] Every commit on the branch is prefixed `#<nr>`
- [ ] The PR body contains `Closes #<nr>`
- [ ] CI is green

---

## Stack

| Concern | Choice |
| --- | --- |
| Language | TypeScript, `strict: true` |
| UI | React |
| Build | Vite |
| Tests | Vitest + React Testing Library |
| E2E | Playwright |
| Lint / format | ESLint + Prettier |
| Runtime | Node 24 |

Conventions:

- No `any`. Use `unknown` and narrow, or model the type properly.
- Function components with hooks. No class components.
- Co-locate a component's test beside it as `Component.test.tsx`.
- Prefer composition over configuration flags.

---

## Agents

Delegate to the specialist rather than doing everything inline. See `.claude/agents/`.

| Agent | Owns |
| --- | --- |
| `issue-manager` | Issue creation, labels, milestones, sub-issue and dependency links |
| `architect` | Implementation design and ADRs, before code is written |
| `implementer` | Writing the code on the issue branch |
| `test-engineer` | Tests and coverage, independent of the implementer |
| `code-reviewer` | Branch diff review and project-rule enforcement |
| `docs-writer` | README, ADRs, guides |
| `release-manager` | PRs, milestone closure, tags |
| `devops` | GitHub Actions, branch protection, repo automation |
| `ux-designer` | Interface and interaction design, accessibility |

---

## Commands

| Command | Does |
| --- | --- |
| `/issue <description>` | Find or create a properly labelled, milestoned, linked issue |
| `/start <nr>` | Branch off main for an issue and check it out |
| `/work <nr>` | Full loop: architect → implement → test → review |
| `/ship <nr>` | Verify, push and open the PR |
| `/board` | Milestone and issue status overview |
| `/groom` | Sweep the backlog for missing labels, milestones and links |
| `/adr <title>` | Draft a new architecture decision record |

---

## Guardrails

Hooks in `.claude/settings.json` enforce these mechanically:

- Commits on `main` are blocked
- Commit messages without a `#<nr>` prefix are blocked
- File edits while on `main` are blocked
- Force pushes to `main` are blocked
- Prettier runs on every edited file

A blocked action is not a bug to work around. It means the process was skipped — go back and do the missing step.

---

## Working With the Customer

The user drives decisions. Claude:

- **Presents options with a recommendation** rather than a survey, and asks when a choice materially changes the work.
- **Records decisions as ADRs** so they are reviewable, not buried in a chat log.
- **Never expands scope silently.** If an issue turns out to be bigger than stated, say so and propose a split.
- **Reports honestly.** Failing tests get reported with their output. Skipped steps get named.
