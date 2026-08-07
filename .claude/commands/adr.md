---
description: Draft a new architecture decision record
argument-hint: <decision title>
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

## Decision

$ARGUMENTS

## Existing records

!`ls -1 docs/adr/*.md 2>/dev/null | grep -v template || echo "none yet"`

Branch: !`git branch --show-current`

## Task

Delegate to `architect` for the reasoning and `docs-writer` for the record.

1. **Confirm it is architectural.** Worth an ADR if it is expensive to reverse, constrains future work, or the customer would want a say — state management, storage, runtime dependencies, the data model. Not worth one if it is a naming or file-placement choice; say so and stop rather than manufacturing ceremony.

2. **Find the next number.** Sequential, zero-padded: `docs/adr/ADR-0004-short-slug.md`.

3. **Write it** from `docs/adr/template.md`:
   - **Context** — the forces at play, stated so a reader understands why this was even a question
   - **Decision** — what is chosen, active voice
   - **Consequences** — what this makes easy _and_ what it makes hard; the downsides are the point
   - **Alternatives considered** — each with the specific reason it lost

4. **Status is `Proposed`.** The user is the decision driver. Present the recommendation and wait for approval before marking it `Accepted` — and before any code implements it.

5. **Update `docs/adr/README.md`** with the new entry.

6. **Commit on the issue branch** with the `#<nr> ` prefix. If no issue covers this decision, create one via `/issue` first — an ADR is work like any other.

Never delete a superseded ADR. Mark it `Superseded by ADR-NNNN` and leave the history intact.
