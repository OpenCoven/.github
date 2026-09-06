# ADR-0002: Governance metadata is coordination and evidence, not protected authority

- **Status:** Proposed; becomes Accepted when merged
- **Date:** 2026-09-03

## Decision

No organization registry, initiative, ADR, issue, Project field, task text, prompt, model response, agent manifest, CI output, or caller-supplied field may grant itself protected OpenCoven authority.

Protected changes continue to require the operation-specific canonical authority and atomic enforcement owned by Familiar Contract, Coven Threads, Psyche, Coven, release systems, or repository administration as applicable.

Governance records may identify required approvers, evidence, and intended state. They become effective write gates only where a separately authenticated enforcement mechanism binds the exact reviewed record to the operation and fails closed on moved or revoked state.

## Consequences

- Pending proposals cannot appear as committed state.
- “Approved” metadata without authenticated, operation-specific enforcement is descriptive only.
- Agents must degrade unverified protected requests to proposals rather than execute them.
- CI success does not prove runtime security, privacy, continuity, legal compliance, or human authorization.
