# Repository automation

Everything in this directory enforces the process described in
[`../CLAUDE.md`](../CLAUDE.md). The rules are meant to be mechanical: a
convention that only lives in prose is one that gets skipped under pressure.

## Workflows

| Workflow                                         | Runs on                                   | Enforces                                                                                 |
| ------------------------------------------------ | ----------------------------------------- | ---------------------------------------------------------------------------------------- |
| [`ci.yml`](workflows/ci.yml)                     | PRs to `main`, pushes to `main`           | Format, lint, typecheck, test with coverage, build                                       |
| [`traceability.yml`](workflows/traceability.yml) | PR opened, edited, synchronized, reopened | Branch naming, `Closes #<nr>` in the body, `#<nr>` title prefix, `#<nr>` on every commit |

`traceability.yml` listens for `edited` as well as `synchronize`, because the
closing keyword lives in the PR body — a body edit would otherwise never be
re-checked.

Both workflows declare `permissions: contents: read`. Neither writes to the
repository. PR-controlled text reaches the shell through `env:` rather than
`${{ }}` interpolation, which would be a script-injection vector.

## Issue forms

Blank issues are disabled. Each form applies its `type/*` label automatically and
requires an `area/*` and a milestone, so an issue cannot be opened in a state that
violates the prime rule.

- [`feature.yml`](ISSUE_TEMPLATE/feature.yml) — requires Scope, Definition of Done, Area, Milestone
- [`bug.yml`](ISSUE_TEMPLATE/bug.yml) — requires repro steps, actual, expected, DoD, Area, Milestone, Priority
- [`chore.yml`](ISSUE_TEMPLATE/chore.yml) — requires a "why now" rationale alongside the rest

## Branch protection

[`branch-protection.json`](branch-protection.json) is the applied configuration,
kept in version control so it is reviewable and reproducible rather than living
only in the GitHub UI.

| Setting                                                         | Value        | Why                                                                                                            |
| --------------------------------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------------------- |
| `required_status_checks.strict`                                 | `true`       | A branch must be up to date with `main` before merging, so checks run against what will actually land          |
| `required_status_checks.contexts`                               | both CI jobs | Neither quality nor traceability can be skipped                                                                |
| `required_pull_request_reviews.required_approving_review_count` | `0`          | Forces a pull request without deadlocking a single-maintainer repository — GitHub does not allow self-approval |
| `required_linear_history`                                       | `true`       | Squash merges only, so `main` keeps one commit per issue                                                       |
| `allow_force_pushes` / `allow_deletions`                        | `false`      | History on `main` is not rewritable                                                                            |
| `required_conversation_resolution`                              | `true`       | Review findings get resolved, not merged past                                                                  |
| `enforce_admins`                                                | `true`       | The rule applies to the repository owner too — see below                                                       |

### On `enforce_admins`

Set to `true` deliberately. With it `false`, the owner could still push straight to
`main`, which would leave "no work on main" true only for everyone who lacked the
permission to break it. The rule is worth having precisely because it also
constrains the person who could opt out.

Verified rather than assumed. A direct push to `main` by the repository owner is
rejected:

```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: - Changes must be made through a pull request.
remote: - 2 of 2 required status checks are expected.
 ! [remote rejected] HEAD -> main (protected branch hook declined)
```

The cost is real: if CI itself breaks badly enough that no PR can go green, the fix
cannot be merged through the normal path. The escape hatch is to lift enforcement,
merge the repair, and immediately restore it:

```bash
gh api --method DELETE repos/{owner}/{repo}/branches/main/protection/enforce_admins
# ... merge the fix ...
gh api --method POST repos/{owner}/{repo}/branches/main/protection/enforce_admins
```

Reach for that only to repair the pipeline. Using it to skip a failing check
defeats the entire arrangement.

## Reapplying protection

```bash
gh api --method PUT repos/{owner}/{repo}/branches/main/protection \
  --input .github/branch-protection.json
```

Verify it took effect rather than assuming — an unverified rule is an assumption:

```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  --jq '{checks: .required_status_checks.contexts, pr: .required_pull_request_reviews != null, force: .allow_force_pushes.enabled}'
```
