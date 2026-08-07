# Architecture decision records

Every decision that is expensive to reverse, constrains future work, or that the
customer would want a say in gets a numbered record here. The record captures the
reasoning at the time it was made, so a later reader can tell whether the reasons
still hold.

## Index

| ADR | Title | Status | Date |
| --- | --- | --- | --- |
| [0001](ADR-0001-typescript-react-vite.md) | Build the todo application with TypeScript, React and Vite | Accepted | 2026-08-07 |

## Writing one

Copy [`template.md`](template.md) to `ADR-NNNN-short-slug.md`, using the next
sequential number, zero-padded to four digits. Or run `/adr <decision title>`.

Four sections, all of them required:

- **Context** — the forces at play, so a reader understands why this was a question
- **Decision** — what is chosen, active voice, one decision per record
- **Consequences** — what it makes easy *and* what it makes hard
- **Alternatives considered** — each with the specific reason it lost

## Rules

- **Status starts at `Proposed`.** The project owner is the decision driver. A
  record stays `Proposed` until they approve it, and no code implements a proposed
  decision.
- **One decision per record.** If a record needs the word "also", it is two ADRs.
- **Never delete a record.** When a decision is replaced, mark the old one
  `Superseded by ADR-NNNN` and leave it in place. The history is the point.
- **Update this index** whenever a record is added or its status changes.

## What does not need an ADR

Naming, file placement, extracting a helper, choosing a test location. If the
decision can be reversed in an afternoon by one person, write the code instead.
