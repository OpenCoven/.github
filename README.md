# OpenCoven organization governance plane

`OpenCoven/.github` is the canonical **public organization-governance and portfolio-coordination plane** for OpenCoven.

It answers four organization-level questions:

1. Which public repositories exist, why do they exist, and what lifecycle are they in?
2. Which repository owns each canonical public domain?
3. Which cross-repository outcomes, decisions, dependencies, and evidence are currently in force?
4. Which shared policies and verification contracts apply across the organization?

It does **not** replace implementation repositories or OpenCoven's protected authority systems.

> Organization metadata coordinates work and records evidence. It never grants familiar identity authority, protected mutation authority, orchestration authority, daemon authority, release authority, or publication authority merely because a file, issue, project field, task, prompt, or model output says so.

## Authority model

| Concern | Canonical source |
|---|---|
| Public repository purpose, lifecycle, ownership, and disposition | `governance/repositories.json` |
| Cross-repository outcome, DRI, workstreams, dependencies, and exit criteria | `initiatives/*.json` |
| Organization-spanning decisions | `decisions/` |
| Public contract/dependency index | `compatibility/` |
| Shared policy and control intent | `policies/` and `governance/controls.json` |
| Repository implementation, tests, migrations, release evidence, and component ADRs | The owning repository |
| Runtime identity, authorization, orchestration, persistence, and commit decisions | Familiar Contract, Coven Threads, Psyche, Coven, and their canonical artifacts |
| Operational portfolio views | GitHub Issues/Projects and generated files; never an independent authority |

The governance plane is intentionally federated at implementation boundaries: central records define organization-level ownership and coordination, while repository-local manifests and evidence prove what is actually implemented.

## Public/private boundary

This repository is public. Its registry therefore inventories **public repositories only**. Private repository names, incidents, credentials, user data, prompts, memories, unpublished security findings, and confidential plans must remain in private repository-local manifests or access-controlled operational views.

A public record may state that a responsibility is resolved by a private overlay without naming or copying that overlay. See [`policies/public-private-data.md`](policies/public-private-data.md).

## Deterministic verification

The fast path has no third-party Python dependencies and performs no network access:

```bash
./scripts/agent-bootstrap
./scripts/agent-check fast
```

It validates:

- repository-registry structure and unique canonical ownership;
- lifecycle, successor, DRI, risk, and manifest-adoption invariants;
- initiative, decision, dependency, control, exception, and evidence schemas;
- generated portfolio outputs;
- workflow permission and immutable-action-pin policy;
- public/private and secret-like-data safeguards;
- this repository's own agent manifest;
- negative regression fixtures through unit tests.

The scheduled drift workflow separately compares the declared public inventory with GitHub's public repository metadata and maintains one deduplicated drift issue.

### Reusable workflow validation

The public reusable workflows are intentionally narrow. Callers must invoke
`OpenCoven/.github/.github/workflows/reusable-agent-readiness.yml@<40-hex-sha>`
or `OpenCoven/.github/.github/workflows/reusable-evidence-packet.yml@<40-hex-sha>`
directly from a workflow file that is a direct child of `.github/workflows/`.
The caller job's literal `with.policy_ref` must equal the exact SHA used in
`uses`, the literal checked path input must match the runtime input (or the
documented `manifest_path` default), and the runtime `policy_ref` input must
match both before the governance-policy checkout is used. The bootstrap guard
accepts only a narrow literal caller profile for policy-sensitive fields:
plain or unescaped quoted ASCII event identifiers in scalar, block-mapping,
block-sequence, or flow-sequence `on` events under a plain top-level `on`
key; direct block-mapping `jobs` under a plain top-level `jobs` key; plain
job identifiers; plain direct job-level `uses` keys whose values are canonical
literal reusable-workflow references; and plain direct block-mapping `with`
inputs on the one relevant reusable caller job. Mutable branches, tags,
malformed refs, nested reusable callers, expressions in the checked inputs,
YAML block scalars, multiline scalar continuations, flow mappings, YAML tags,
quoted policy-sensitive keys, quoted job-level `uses`/`with` values, escaped
event scalars, anchors, aliases, merge keys, duplicate/ambiguous caller jobs
or event keys, and `secrets: inherit` are rejected closed rather than
interpreted. Any unsupported direct job-level `uses` syntax is rejected before
the guard filters for the expected OpenCoven reusable target, so a malformed
actual caller cannot be hidden behind a later decoy job.

Repository-provided paths are always treated as data. The reusable workflows
pass `manifest_path` and `evidence_path` through environment variables and
quoted shell variables, then `scripts/governance.py` resolves them against the
trusted checkout root as repository-relative files. Absolute paths,
traversal, control characters, symlink components/files, directories, missing
files, and special files are rejected; evidence packets must be JSON files
below `evidence/`.

Local manifest validation can still be run without a GitHub caller context by
using the explicit local safe mode:

```bash
python3 scripts/governance.py validate-manifest \
  --target-root . \
  --local-self-declared-repository \
  agent/manifest.json
```

That mode keeps the same trusted path checks and registry comparison, but is
forbidden inside GitHub Actions. Reusable workflows must pass
`--caller-repository "$GITHUB_REPOSITORY"` so the registry entry is selected
from GitHub's caller identity, never from the manifest's self-declared name.

## Repository map

```text
agent/             This repository's machine-readable agent contract
governance/        Public portfolio registry, controls, lifecycle, exceptions
initiatives/       Cross-repository outcomes and responsibility assignments
decisions/         Organization-spanning ADRs and decision index
compatibility/     Public dependency, contract, and release-train indexes
policies/          Normative organization-governance procedures
docs/              Operating model, administration, mappings, and rollout
generated/         Deterministic views; never edit by hand
schemas/           JSON Schemas for exchanged governance records
scripts/           Dependency-free validation, generation, and reconciliation
tests/             Red-to-green governance invariant tests
.github/            Review templates, issue forms, and least-privilege workflows
```

## Change procedure

1. Identify the canonical owner before proposing a new repository, schema, service, database, or control plane.
2. Change the smallest authoritative record; do not duplicate repository-local truth here.
3. Include an evidence packet describing objective, non-goals, authority impact, tests, migration, rollback, and uncertainty.
4. Regenerate derived views with `python3 scripts/governance.py generate`.
5. Run `./scripts/agent-check fast`.
6. Merge only through the protected review path once the administrative hardening gate is complete.

Temporary exceptions must be typed, owner-approved, narrowly scoped, and expiring. See [`policies/exceptions.md`](policies/exceptions.md).

## Current activation state

The files in this repository can establish **specified and verified repository-level policy**. They do not prove that GitHub organization settings match the policy. Activation therefore has two gates:

- **Repository gate:** schema, validation, generated views, and CI are merged and green.
- **Administrative gate:** branch/ruleset, Actions, app, environment, and break-glass settings are applied and independently evidenced.

Until both gates close, the governance plane is authoritative for reviewed public portfolio records but is not an independently verified GitHub-administration enforcement boundary.

## Related work

- Governance-plane activation: `OpenCoven/.github#5`
- Administrative hardening: `OpenCoven/.github#6`
- Advanced reusable automation conformance: `OpenCoven/.github#2`
