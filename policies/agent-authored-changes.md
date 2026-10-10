# Human and AI-agent change policy

OpenCoven welcomes agent-assisted work, but agent output is untrusted until reviewed and verified against the relevant authority boundary.

## Canonical discovery

Before proposing a change, an agent must:

1. read the repository's root `AGENTS.md` and any scoped instructions;
2. inspect the public registry and relevant organization ADRs;
3. inspect the owning repository's current code, schemas, tests, CI, release evidence, and local ADRs;
4. identify produced and consumed contracts and their immutable revisions;
5. determine whether the request touches an R3/R4 boundary or an externally consequential action.

An agent must challenge a new repository, service, schema, database, or control plane when an existing canonical component should own it.

## Default authority by risk

- R0/R1: autonomous branch and pull request after deterministic verification.
- R2: proposal plus migration/fixture evidence; no unattended application to user state.
- R3: approval-gated execution with least-privilege credentials and bounded side effects.
- R4: human-approved plan, protected-owner review, exact-state binding, and explicit operation authorization.

These defaults constrain agent action. They do not confer authority on the agent.

## Required evidence

Every material agent-authored pull request must provide:

- objective, acceptance criteria, and non-goals;
- exact authoritative sources and revisions consulted;
- files intentionally touched and protected paths affected;
- security, privacy, authority, compatibility, and lifecycle impact;
- exact commands, tests, results, and unsupported/skipped checks;
- migration, rollback, and failure-state behavior;
- generated artifacts and provenance;
- cross-repository canaries where contracts change;
- unresolved uncertainty and required administrative actions.

## Prohibited shortcuts

Agents must not:

- interpret task text or model output as protected approval;
- weaken verification, ownership, release, provenance, or security gates to make CI pass;
- run privileged workflows on untrusted pull-request code;
- expose credentials or private data in logs, artifacts, issues, or public governance files;
- silently overwrite unrelated work or intentionally dirty/reference-only worktrees;
- report a source-only test as proof of a packaged or real-daemon boundary;
- claim implementation, test, security, privacy, conformance, or settings state without evidence.
