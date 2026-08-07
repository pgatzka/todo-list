# ADR-0001: Build the todo application with TypeScript, React and Vite

- **Status:** Superseded by [ADR-0002](ADR-0002-client-server-postgres.md)
- **Date:** 2026-08-07
- **Decided by:** Project owner (decision driver)

## Supersession

The supersession is partial. ADR-0002 replaces the client-only architecture and
the browser-storage persistence described below; the TypeScript, React, Vite,
Vitest, Playwright and tooling choices carry forward unchanged. The record is
left as written, including the milestone plan that has since been reorganised.

## Context

`todo-list` is a new project with no existing code. Every line is implemented by
Claude Code, with the project owner acting as customer and decision driver. The
stack choice had to be made before any scaffold existed, because it determines the
lint and format hooks, the CI pipeline, the `area/*` label taxonomy and which
specialist agents are worth having.

The forces that mattered:

- **The product is small and interaction-heavy.** A todo list has little business
  logic and a lot of interface. Whatever we pick is judged mostly on how well it
  handles UI state and rendering.
- **Milestones span client-only through persistence.** M1 is in-memory CRUD, M2
  adds persistence. The stack must not force a backend before M2, but must not
  make one painful later either.
- **Every change is machine-authored and machine-reviewed.** Static types are not
  a style preference here — they are the primary automated check that a change is
  coherent before a human reads it.
- **Feedback speed gates everything.** The delivery loop runs lint, typecheck,
  test and build on every issue. A slow toolchain multiplies across every issue in
  the project.

## Decision

We will build the application as a client-side single-page app using
**TypeScript** (strict), **React** and **Vite**, tested with **Vitest** and
**React Testing Library**, with **Playwright** for end-to-end tests and
**ESLint + Prettier** for lint and format. Node 24 is the runtime.

## Consequences

What this makes easy:

- Type errors catch a large class of machine-authored mistakes before review,
  which matters more here than on a human-written codebase.
- Vite's dev server and build are fast enough that the four-check verification
  loop stays cheap to run on every commit.
- Vitest shares Vite's config and transform pipeline, so there is one build
  configuration rather than two.
- React Testing Library pushes tests toward accessible queries, which means the
  a11y commitments in M3 get partial enforcement from the test suite itself.
- The ecosystem is large and well documented, so the agents are working with
  patterns that are heavily represented rather than exotic ones.

What this makes hard:

- **No server, so M2 persistence is browser storage.** Todos will live in
  `localStorage` or IndexedDB. There is no sync across devices and no shared
  state between users. If that is ever wanted, it is a new decision and a new ADR,
  not an extension of this one.
- **React ships a runtime.** For an application this small the framework is a
  meaningful share of the bundle. We accept that; bundle size is not a stated goal.
- **Client-side rendering only.** No SSR, no SEO story, a blank first paint until
  JavaScript loads. Acceptable for a personal todo tool, not for a public site.
- **Strict TypeScript costs upfront effort.** Modelling state properly takes
  longer than reaching for `any`. That cost is deliberate and is enforced by
  convention in `CLAUDE.md`.

## Alternatives considered

### Next.js with SQLite and Prisma

A genuinely full-stack option that would have made M2 persistence real — a
database, server-side rendering, and a path to multi-user.

It lost because it front-loads a large amount of infrastructure — a server, a
database, migrations, an ORM — for a product whose M1 is a list of strings in
memory. The complexity would have arrived four milestones before the requirement
justifying it. Should the project ever need shared or cross-device state, this
becomes the obvious successor and should be reconsidered then.

### Python with FastAPI and SQLite

An API-first design with `pytest`, `ruff` and `mypy`.

It lost because the product is overwhelmingly interface, not API. This would have
made the interesting part of the work — interaction and accessibility — either a
second stack to maintain alongside the first, or absent entirely.

### A terminal CLI in TypeScript

The smallest possible scope, keeping attention on the delivery process rather than
on the product.

It lost because the process is meant to serve a real product, not substitute for
one. A CLI would also have made the `ux-designer` agent and the M3 UX milestone
close to meaningless.

### Plain JavaScript instead of TypeScript

Rejected without much debate. On a codebase where every change is machine-authored,
the type checker is the cheapest and most reliable reviewer available. Removing it
to save configuration effort would be a poor trade.
