# Verification and adherence model

## Layers

1. **Schema/structure** — records parse and contain required fields.
2. **Semantic invariants** — canonical domains are unique; lifecycles, successors, dependencies, and authority boundaries agree.
3. **Derived-state integrity** — generated views match authoritative inputs exactly.
4. **Repository adoption** — local agent manifests, checks, protected paths, and contract pins match the public registry.
5. **Live GitHub reconciliation** — public repository metadata and required manifests match declared state.
6. **Administrative application** — rulesets, permissions, environments, Apps, and break-glass controls are applied.
7. **Control effectiveness** — positive/negative tests and recurring evidence show controls continue working.
8. **Product/protocol conformance** — owning repositories prove structural, runtime, continuity, privacy, interoperability, and release behavior against exact artifacts.

No lower layer implies a higher one.

## Current automated evidence

`./scripts/agent-check fast` provides layers 1–3 for this repository and includes negative regression tests. The reusable workflow provides part of layer 4. The scheduled drift observer provides part of layer 5. Issue #6 tracks layer 6. Advanced cross-repository conformance remains under issue #2 and owning repositories.

## Golden tasks for agent readiness

Each active repository should eventually prove at least:

- a clean-clone documentation change;
- a focused pure-code fix;
- a protected-path proposal that correctly stops for approval;
- a malformed manifest/contract rejection;
- an unsupported-platform result that is reported without being hidden or misclassified;
- a generated-file drift failure;
- a secret/private-data fixture that is rejected without logging sensitive content;
- a cross-repository contract update using an immutable producer artifact.

Measure clarification count, human interventions, check duration, false failures, escaped drift, and rollback success. Do not optimize velocity by weakening protected boundaries.
