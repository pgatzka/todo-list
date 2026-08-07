# ADR-0002: Make the application client/server with Fastify, PostgreSQL and Drizzle

- **Status:** Accepted
- **Date:** 2026-08-07
- **Decided by:** Project owner (decision driver)

## Context

[ADR-0001](ADR-0001-typescript-react-vite.md) chose a browser-only single-page
app. It said, in the alternative it rejected, that if the project ever needed
shared or cross-device state then that would be a new decision and a new ADR
rather than an extension of that one. This is that record.

Two things changed after ADR-0001 was written. The product requirement changed:
the list has to be usable from a phone and from a desktop and show the same
todos, and the todos themselves grow from strings into records with notes, a due
date and time, a priority and tags, which are then filtered, sorted and searched
(#53, #57, #58, #59). The milestone plan changed with it: M2 is now delivery and
operations — a container image, a host, a deployed database (#21) — where it had
previously meant browser storage. ADR-0001's Context describes the older plan and
should be read as a record of what was true then.

The forces that matter now:

- **State has to outlive the browser profile.** `localStorage` and IndexedDB are
  scoped to one browser on one device. There is no arrangement of client-side
  code that makes the same list appear on a second device. This is the
  requirement that forces a server; nothing else here would on its own.
- **The M3 work is query work.** Filtering by status and by tag together, sorting
  by due date, priority and creation time, and finding todos by text are
  operations a relational engine performs against indexes. In the browser they
  are array scans over whatever happens to have been loaded, and the correctness
  of the answer depends on all of the data being present.
- **The richer todo wants constraints the store can enforce.** Priorities from a
  fixed set, timestamps stored unambiguously, tags related to todos in a defined
  way. A store that enforces types, nullability, defaults and referential
  integrity removes a class of data bugs from the application code. The shape of
  that schema is not decided here — see the scope note below.
- **Every change is machine-authored and machine-reviewed.** This was true for
  ADR-0001 and it constrains the answer more now, because a second deployable
  doubles the surface. The interface between the two halves has to be typed and
  small enough that the type checker still catches an incoherent change before a
  human reads it.
- **The application has to run unattended.** M2 puts it on a host, redeployed on
  every merge, with migrations as a gated deploy step and a backup and restore
  procedure (#47, #50, #51). Whatever is chosen has to be operable by one person
  reading a runbook.
- **Feedback speed still gates everything.** Carried forward unchanged from
  ADR-0001. The four checks run on every issue, and a database in that loop is a
  cost paid on every one of them.

## Decision

> We will run the application as a Fastify server on Node backed by PostgreSQL
> through Drizzle ORM, laid out as a single-repository npm workspace, with the
> browser talking to the server over a REST API whose request and response types
> live in a shared TypeScript package.

This extends ADR-0001 rather than replacing it wholesale. TypeScript in strict
mode, React, Vite, Vitest, React Testing Library, Playwright, ESLint and
Prettier, and Node 24 all carry forward as the frontend half of the workspace and
are not reopened here. What this record supersedes is ADR-0001's architectural
claim — that the application is client-side only and that persistence is browser
storage. ADR-0001 is marked `Superseded by ADR-0002` because that is the only
status value the template offers, but the supersession is partial in exactly the
way described above.

Two things are deliberately out of scope for this record. The schema — tables,
columns, identifiers, how tags are represented, how due timestamps are stored —
is ADR-0003 (#27). The container image, the compose topology and the deployment
model are ADR-0004 (#39). This record decides only which engine, which access
layer, which transport and which repository layout.

## Consequences

What this makes easy:

- One list, addressable from any device, which is the requirement that started
  this. The browser holds a view of the data instead of owning it.
- The M3 filtering, sorting and search work becomes SQL against indexes rather
  than client-side array work, and stays correct as the list grows past whatever
  a first page loads.
- Drizzle's schema is ordinary TypeScript, so column types flow into the server's
  types without a code generation step, and `drizzle-kit` emits plain SQL
  migrations that are reviewed as SQL in the pull request that adds them.
- Fastify is small — routing, schema-based validation, serialisation and hooks.
  The documented error contract (#31) is built on its validation hooks rather
  than against a framework's opinion about responses.
- One workspace means a change to the API and a change to its caller land in one
  pull request, and one CI run proves both halves still agree.
- The Postgres in the local compose file, the Postgres in CI and the Postgres on
  the host are the same engine, so integration tests exercise the real thing
  (#30 requires this explicitly).

What this makes hard:

- **Nothing runs without a database.** A developer checkout and a CI job both
  have to start Postgres and apply migrations before a test can run. That is
  slower and has more failure modes than ADR-0001's loop, and it is a direct cost
  against the feedback-speed force above.
- **Migrations become versioned artefacts and a deploy gate.** Once deployed data
  exists, schema changes are forward-only, have to be reviewed as SQL, have to
  run before the new version starts, and a bad one is recovered from backup
  rather than by editing code and redeploying.
- **There is a host to operate.** Patching, secrets, backups, restore drills and
  whatever breaks at three in the morning. None of that exists for a static
  bundle on a CDN.
- **Two build targets in one repository.** Workspace hoisting, TypeScript project
  references, more than one `tsconfig`, and root scripts that fan out across
  packages. Misconfiguration in that layer surfaces as a confusing build error
  rather than a clear one.
- **REST with shared types is a convention, not a guarantee.** A handler and its
  caller agree at compile time only about the type they both import. Nothing
  checks that the URL the client calls is the route the server registered, and
  JSON erases the difference between a `Date` and the string it becomes on the
  wire. That drift is real and only integration tests catch it.
- **PostgreSQL is heavier than this product needs.** A personal todo list will
  never approach what it is built for, and we are running a server process,
  managing connection configuration and maintaining a backup procedure for a
  dataset that would fit in a text file. We accept that weight because the
  lighter option trades it for the constraints described under SQLite below.

## Alternatives considered

### Prisma instead of Drizzle

A schema written in Prisma's own DSL, from which a typed client and the
migrations are generated.

It lost because the generated client has to exist before anything typechecks.
That puts a code generation step into the developer loop, the CI job, the
container build and any clean checkout, and each of those is a place it can be
forgotten or go stale. Drizzle's schema is TypeScript that the compiler already
reads, and its migrations are SQL files a reviewer reads directly, where Prisma's
are produced from a diff of the DSL. For a project whose migration reviewer is a
person reading a pull request, plain SQL is the more reviewable artefact.

### tRPC instead of REST with shared types

Procedure calls whose client-side types are inferred from the server's router, so
there is no hand-written contract to drift at all.

It lost on a requirement, not on ergonomics: the epic (#20) states the API has to
be reachable and documented independently of the UI. tRPC's transport is an
implementation detail rather than an interface — awkward to call with `curl`, and
it does not express itself in the HTTP status codes that the error contract (#31)
is defined in terms of. It would also couple the frontend build to the server's
source tree and to a single TypeScript version across both. The inferred types
are genuinely better than what we are choosing; they were not worth giving up an
independently usable API.

### Next.js instead of Fastify plus the Vite SPA

One framework covering both halves, with route handlers, server rendering and a
build that emits both sides.

It lost because it replaces the ADR-0001 frontend instead of extending it. The
Vite configuration, the Vitest transform pipeline that shares it and the existing
application would all be migrated, and the return is mostly server rendering,
which #33 explicitly puts out of scope. It also makes the framework the
deployment model: the container question (#41) becomes how to self-host Next
rather than how to run a Node process. If SSR or an SEO story ever become
requirements, this is the obvious successor and should be reconsidered then.

### SQLite instead of PostgreSQL

A single file, no server process, no connection configuration, and comfortably
enough capacity for this data volume.

It lost on the deployment model. M2 redeploys a freshly built image on every
merge to `main`, and a SQLite database is a file on the host that the deployment
must never lose — which turns it into a volume with careful lifecycle rules, and
turns backup into copying a file consistently while it is open. Running Postgres
as a separate service in the compose stack keeps the application container
stateless and makes backup and restore an ordinary dump and load (#50, #51).
SQLite's column typing is also by affinity rather than strict, which sits badly
with a project that leans on static types as its primary automated check.

### A separate repository for the backend

Independent history, independent CI and a hard boundary between the two halves.

It lost because the boundary would cost more than it protects. A change to the
wire format becomes two pull requests in two repositories with no single CI run
proving they agree, and the shared types package has to be published to a
registry and version-negotiated to cross the boundary at all. Nothing here wants
independent release cadence or different access control; there is one deployable
and one person. The cost of the single repository is that CI runs every workspace
for a docs-only change until we make it selective, which is a cheaper problem to
have.
