# ADR-0001: Use `OpenCoven/.github` as the public organization governance plane

- **Status:** Proposed; becomes Accepted when merged through the protected review path
- **Date:** 2026-09-03
- **Decision owner:** BunsDev
- **Technical DRI:** BunsDev
- **Scope:** Public organization governance, portfolio coordination, and shared verification

## Context

OpenCoven spans identity, protected authorization, orchestration, daemon/runtime authority, clients, products, delivery, documentation, and brand repositories. Cross-repository plans and responsibility can drift when maintained independently in issues, documents, chats, dashboards, or repository-local roadmaps.

The organization needs one durable answer for public repository purpose, lifecycle, canonical domain ownership, cross-repository initiatives, shared policy, compatibility relationships, and generated portfolio views. It must not create another runtime control plane or duplicate repository-local implementation truth.

`OpenCoven/.github` already has organization-wide GitHub semantics for community files and reusable workflows. It is public, discoverable, versioned, reviewable, and portable as ordinary Git data. It is also high impact and therefore requires stronger administrative protection than its current unprotected `main` branch.

## Decision

Use `OpenCoven/.github` as the canonical **public organization-governance and portfolio-coordination plane**.

It owns:

- the public repository registry, lifecycle, public canonical-domain map, and disposition plan;
- cross-repository initiatives, organization ADRs, dependency/contract indexes, and shared policy;
- schemas, deterministic validation, reusable read-only verification workflows, drift reconciliation, and generated public views;
- coordination evidence for GitHub administration, without claiming the settings are applied until independently verified.

It does not own:

- component implementation, component ADRs, migrations, tests, releases, or repository-local evidence;
- private repository inventory or confidential operational context;
- familiar identity, protected authorization, orchestration, runtime persistence/execution, release approval, or publication approval;
- a manually maintained duplicate of Issues, Pull Requests, Projects, or runtime state.

Private repositories remain federated through repository-local manifests and access-controlled operational views. Public records may use opaque private-overlay identifiers without revealing private inventory.

GitHub Projects is the preferred operational presentation for cross-repository work, but its fields are derived coordination views. Files in Git remain authoritative for organization policy, ownership, lifecycle, initiative definition, and accepted decisions; repository issues and artifacts remain authoritative for implementation and evidence.

## Alternatives considered

### New dedicated governance repository

Rejected for now. It would add another repository and discovery surface without materially improving separation. Revisit only if `.github` special-repository coupling, scale, confidentiality, or availability becomes a measured constraint that cannot be mitigated.

### Documentation repository as the control plane

Rejected. Documentation should present generated compatibility and policy information, not become the write authority for repository administration and portfolio ownership.

### GitHub Projects or Issues as the sole authority

Rejected. They are useful operational views but weaker for schema validation, immutable review, portable history, deterministic generation, and offline inspection. They also encourage manually duplicated status.

### Backstage or another service catalog as primary authority

Deferred. A catalog may consume the registry when the organization has enough scale to justify operating it. It must remain a projection unless separately ratified.

### Monorepo consolidation

Rejected as a governance solution. Some code may consolidate for technical reasons, but a monorepo does not resolve protected authority, ownership, release, or cross-product lifecycle boundaries and would create a large migration/blast radius.

### Pure repository-local federation

Rejected as insufficient. Repository-local truth remains necessary, but without a central ownership and initiative index it cannot reliably detect duplicate canonical claims, unowned repositories, or portfolio drift.

## Consequences

Positive:

- one discoverable public ownership and portfolio source;
- reviewable, machine-readable policy and history;
- generated rather than manually recopied portfolio views;
- explicit canonical/derived and public/private boundaries;
- reusable agent and CI contracts without adding another service.

Costs and risks:

- `.github` becomes a high-impact supply-chain and governance target;
- central changes can create organization-wide noise or bottlenecks;
- the public repository cannot contain private operational detail;
- declarative records can diverge from actual GitHub settings;
- schemas can ossify if evolution and exceptions are not governed.

Mitigations:

- protect `main`, workflows, schemas, decisions, and registry paths through rulesets and CODEOWNERS;
- default workflows to read-only and pin third-party Actions by commit;
- separate read-only drift observation from privileged plan-bound reconciliation;
- reconcile declared state against GitHub APIs and owning-repository evidence;
- use expiring exceptions and versioned schemas;
- retain implementation and protected authority in canonical repositories.

## Activation criteria

This decision is active only after:

1. repository validation and generated-view checks pass;
2. the governance-plane PR is reviewed and merged;
3. `.github/main` is protected by required review and `Governance CI / validate`;
4. organization Actions/app/environment/break-glass controls are evidenced;
5. at least two canonical repositories consume the reusable readiness workflow at an immutable revision.

Before criteria 3–4, records are reviewed coordination truth but not independently verified GitHub-administration enforcement.

## Revisit triggers

Re-evaluate the repository choice when any of these persist for two review cycles:

- public/private separation prevents necessary coordination;
- registry or initiative review regularly blocks unrelated delivery;
- generated artifacts or Git history become operationally unmanageable;
- `.github` outages or special semantics materially impair governance availability;
- more than 100 active repositories or multiple autonomous governance domains require delegated catalogs;
- a service catalog provides measured value that outweighs its operational and duplicate-truth risk;
- ruleset, workflow, or app blast radius cannot be reduced to the accepted risk tolerance.
