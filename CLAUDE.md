# todo-list

A todo application built with TypeScript, React and Vite. **Every line of this project is implemented by Claude Code.** The user is the customer and the decision driver: they decide _what_ and _why_, Claude decides _how_ and does the work.

---

## The Prime Rule

> **No work without an issue.** Every change traces to a GitHub issue that has a milestone and at least one label.

When the user asks for anything that touches the repository:

1. **Search first.** `gh issue list --search "<keywords>" --state all` — does an issue already cover this?
2. **If yes**, work that issue.
3. **If no**, create one _before_ touching a file. Assign a milestone, apply labels, link it to related issues.
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

An issue is not done until every line of the checklist in the `project-conventions` skill holds — the issue's own Definition of Done, the four local checks, tests, docs, ADRs, commit prefixes, `Closes #<nr>`, and green CI. The same list is enforced by the pull request template, the `code-reviewer` agent and `traceability.yml`.

---

## Stack

The stack is `package.json`; the reasoning is [ADR-0001](docs/adr/ADR-0001-typescript-react-vite.md). End-to-end tests use Playwright, which is not in the manifest yet.

Conventions:

- No `any`. Use `unknown` and narrow, or model the type properly.
- Function components with hooks. No class components.
- Co-locate a component's test beside it as `Component.test.tsx`.
- Prefer composition over configuration flags.

---

## Agents and commands

Delegate to the specialist rather than doing everything inline. The nine agents in `.claude/agents/` and the seven commands in `.claude/commands/` are already listed with their descriptions at the start of every session — read those, not a copy of them here.

---

## Guardrails

Hooks in `.claude/settings.json` block commits and edits that break the rules above.

A blocked action is not a bug to work around. It means the process was skipped — go back and do the missing step.

---

## Working With the Customer

The user drives decisions. Claude:

- **Presents options with a recommendation** rather than a survey, and asks when a choice materially changes the work.
- **Records decisions as ADRs** so they are reviewable, not buried in a chat log.
- **Never expands scope silently.** If an issue turns out to be bigger than stated, say so and propose a split.
- **Reports honestly.** Failing tests get reported with their output. Skipped steps get named.
