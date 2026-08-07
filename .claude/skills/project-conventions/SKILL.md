---
name: project-conventions
description: Branch naming, commit format, code standards, ADR format and the Definition of Done for this project. Use before committing, before opening a PR, when writing TypeScript or React code, and when recording an architectural decision.
---

# Project conventions

## Branches

```
<issue-nr>-<kebab-case-title>
```

`14-todos-persist-across-reloads`, `2-claude-code-workflow-agents-commands-hooks-skills`.

Always cut from an up-to-date `main` with a clean tree. `main` itself is never worked on — the only commit ever made directly to it was the initial empty README, and that will not recur.

## Commits

```
#<issue-nr> Imperative subject under 72 characters
```

- The prefix is mandatory and hook-enforced; the number must match the branch.
- Imperative mood: "Add", "Fix", "Remove" — not "Added", "Fixes".
- One logical change per commit. Commit at each meaningful step, not once at the end.
- Body optional; use it for *why*, never for restating the diff.
- No `Co-Authored-By`, no tool advertising.

```
#14 Add localStorage adapter for the todo list
#14 Fall back to an empty list when stored JSON is corrupt
#14 Add tests for the corrupt-storage path
```

## TypeScript

- `strict: true`. **No `any`** — use `unknown` and narrow, or model the type properly.
- No `@ts-ignore` without a comment explaining why and a linked issue.
- Prefer `type` for unions and object shapes; `interface` when declaration merging is genuinely needed.
- Derive types rather than restating them: `type Todo = ReturnType<typeof createTodo>` beats a hand-maintained duplicate.
- Make illegal states unrepresentable. A discriminated union beats a bag of optional booleans.

## React

- Function components with hooks. No class components.
- One component per file, named the same as the file.
- Co-locate the test as `Component.test.tsx` beside it.
- Keep state as local as it can be. Lift only when genuinely shared.
- Extract a custom hook when logic is reused *or* when it makes a component readable — not speculatively.
- Semantic HTML first. A real `<button>` before a `<div onClick>`. Always.

## Comments

Explain **why**, never **what**. The code already says what.

```ts
// Reads are debounced because the storage write blocks paint on large lists.
```

not

```ts
// Set the todos state
```

Match the comment density of surrounding code. Delete commented-out code rather than shipping it.

## Tests

- Name the behaviour: `it('keeps focus in the input after adding a todo')`.
- One behaviour per test. Arrange–Act–Assert, visibly.
- Query by role, label and text. Reach for `data-testid` only when no accessible query exists.
- No conditionals in tests. No sleeps — use `findBy*` and `waitFor`.
- Deterministic and order-independent.
- Every fixed bug gets a regression test that fails against the old behaviour.

## ADRs

`docs/adr/ADR-NNNN-short-slug.md`, sequential and zero-padded.

Sections: **Context** (the forces, so a reader sees why this was a question) · **Decision** (active voice) · **Consequences** (what it makes easy *and* hard — the downsides are the point) · **Alternatives considered** (each with the specific reason it lost).

Status is `Proposed` until the customer approves, then `Accepted`. Superseded records are never deleted — mark `Superseded by ADR-NNNN` and keep the history.

Write one when the decision is expensive to reverse, constrains future work, or the customer would want a say. Do not write one for naming or file placement.

## Definition of Done

- [ ] The issue's own Definition of Done is satisfied, line by line
- [ ] `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` all pass
- [ ] New behaviour has tests; fixed bugs have regression tests
- [ ] Documentation touched by the change is updated
- [ ] Architectural decisions recorded as an ADR
- [ ] Every commit prefixed `#<nr>`
- [ ] PR body contains `Closes #<nr>`
- [ ] CI green

## Scope discipline

Something broken but unrelated found mid-issue does **not** get fixed in that branch. Note it, finish the issue, report it so it gets its own. Unrelated changes destroy reviewability and traceability.

If an issue turns out materially bigger than described, stop and propose a split. Silently doing three issues' work under one number is not diligence.

## Reporting

Report what actually happened. Failing tests get reported with their output. Skipped steps get named. Never call an issue done on red.
