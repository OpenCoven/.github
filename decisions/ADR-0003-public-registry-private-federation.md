# ADR-0003: Keep the central registry public and federate private overlays

- **Status:** Proposed; becomes Accepted when merged
- **Date:** 2026-09-03

## Decision

`governance/repositories.json` inventories public repositories only. Private repositories publish the same repository-manifest contract locally and participate through access-controlled Projects, issues, evidence, or a future approved private projection.

The public plane may refer to an opaque private overlay by capability identifier, but it must not disclose private repository names, incident details, credentials, user data, prompts, memories, private paths, or confidential plans.

Aggregation must preserve provenance and access controls. A private projection may consume the public registry; the public registry must never infer or mirror private data back into public output.

## Consequences

The public portfolio is transparent and independently verifiable without turning `.github` into a confidentiality hazard. Organization-wide views spanning private work require an authenticated projection and cannot be reconstructed from public files alone.
