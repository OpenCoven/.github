# Cross-repository initiatives

An initiative is the canonical organization-level record for **why coordinated work exists, who is accountable, which repositories own the implementation, what it depends on, and how completion is proven**.

It is not a duplicate task database. Implementation issues, pull requests, tests, migrations, and release evidence remain in their owning repositories. GitHub Projects may render these records and linked issues, but the Project is a view rather than an independent authority.

## Lifecycle

`proposed → active → verifying → completed`

Alternative terminal states are `superseded` and `cancelled`. A completed initiative must have evidence for every exit criterion. A status change cannot authorize a protected OpenCoven mutation or release.

## Required fields

Each `*.json` record must name:

- one decision owner;
- one technical DRI;
- one outcome and explicit non-goals;
- participating repository workstreams;
- cross-initiative dependencies;
- exit criteria and evidence state;
- accepted or proposed organization ADRs;
- a review date.

Use `schemas/initiative.schema.json` and validate with `./scripts/agent-check fast`.
