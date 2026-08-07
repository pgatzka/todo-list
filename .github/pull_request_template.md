<!--
Title must be: #<issue-nr> <issue title>

The `Closes #<nr>` line below is mandatory. CI fails this PR without it, and the
issue will not close on merge. Replace <nr> with the real issue number.
-->

Closes #<nr>

## What changed

<!-- What this does, and why it was done this way. Not a restatement of the diff. -->

## Definition of Done

<!-- Copy every line from the issue's Definition of Done and check each one.
     An unchecked line means this PR is not ready. -->

- [ ]
- [ ]

## Verification

<!-- Paste the actual output. Do not write "all tests pass" without evidence —
     a PR that claims green on a red branch is worse than a red branch. -->

```
npm run lint && npm run typecheck && npm test && npm run build
```

## Checklist

- [ ] Branch is named `<issue-nr>-<kebab-title>`
- [ ] Every commit subject starts with `#<issue-nr> `
- [ ] No file in this diff is unrelated to the issue
- [ ] New behaviour has tests; fixed bugs have a regression test
- [ ] Documentation touched by this change is updated
- [ ] Architectural decisions are recorded as an ADR under `docs/adr/`

## Follow-up

<!-- Anything found while working that is out of scope for this issue.
     Do not fix it here — list it so it becomes its own issue. -->

- None
