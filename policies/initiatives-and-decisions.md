# Initiative and decision procedure

## Cross-repository initiatives

Create an initiative when one outcome requires work in more than one canonical repository or requires an organization-level ownership, lifecycle, compatibility, or sequencing decision.

Each initiative has one decision owner, one technical DRI, explicit workstream owners, dependencies, non-goals, review date, and evidence-backed exit criteria. Avoid percent-complete fields. Derive operational status from linked issues and immutable evidence where possible.

Implementation tasks remain in their owning repositories. The central initiative links them and defines the shared outcome; it does not copy their mutable task descriptions.

## Status changes

- `proposed`: scope and ownership under review;
- `active`: accepted outcome with work in progress;
- `verifying`: implementation is present and exit evidence is being assembled;
- `completed`: every criterion has exact evidence and no unresolved blocking risk;
- `superseded`: another initiative owns the outcome;
- `cancelled`: intentionally stopped with rationale and residual-risk disposition.

A status change requires a pull request. `completed` without evidence must fail validation.

## ADR placement

Place an ADR here only when it changes organization-spanning ownership, compatibility, lifecycle, sequencing, public/private boundary, or governance invariants. Keep component design and implementation ADRs in the owning repository.

Accepted ADRs are immutable historical records. Amend by a new ADR that supersedes or narrows the prior decision; do not silently rewrite the old rationale.

## Conflict resolution

1. Stop any protected or irreversible action affected by the conflict.
2. Identify the canonical owner using the registry and current implementation evidence.
3. Gather exact repository revisions, contracts, tests, and settings snapshots.
4. Let the relevant decision owner resolve scope; require canonical protected authority for any protected operation.
5. Record the decision and migrate or deprecate conflicting surfaces.
6. Add a regression check where the conflict could recur mechanically.
