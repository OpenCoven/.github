# OpenCoven cross-repository operating model

## Purpose

The governance plane centralizes **organization-level context** without centralizing implementation authority. It provides one public ownership map, one initiative definition per cross-repository outcome, one accepted decision trail, and deterministic aggregate views.

## Responsibility model

| Role | Accountable for | Not sufficient for |
|---|---|---|
| Decision owner | Outcome, scope, priority, conflict resolution, and acceptance of organization-level tradeoffs | Protected runtime authorization or GitHub administration |
| Technical DRI | Coordinated technical delivery, dependency sequencing, evidence completeness, and handoff | Unreviewed merge, release, publication, or destructive action |
| Repository owner | Repository purpose, lifecycle, maintainership, and successor planning | Another repository's canonical implementation |
| Canonical-domain owner | Normative artifacts and invariant enforcement for the named domain | Self-expansion into adjacent domains without review |
| Workstream driver | Implementation issue/PR and repository-local verification | Changing the central outcome alone |
| Protected owner/approver | Review at an R3/R4 boundary | Authority outside the exact operation and system |
| GitHub administrator | Organization/repository settings under authenticated access | Familiar, Threads, Psyche, Coven, release, or publication authority |

RACI tables may be generated for presentations, but the machine-readable records use one accountable decision owner and one technical DRI to avoid diffuse responsibility. Contributors and consulted parties stay in repository issues/Projects rather than a static central list.

## Source-of-truth split

```text
Organization outcome and ownership
        └── .github initiative / ADR / public registry
                ├── owning-repository issue and PR
                ├── immutable contract/artifact revision
                ├── exact CI, real-daemon, or packaged evidence
                └── generated Project/dashboard view
```

- Central files answer **why**, **who**, **which owner**, **which dependency**, and **which exit evidence**.
- Owning repositories answer **how**, **what code**, **what test**, **what migration**, and **what release**.
- GitHub settings evidence answers **whether administrative controls are actually applied**.
- Projects answer **what needs attention now** and remain replaceable views.

## Review cadence

- P0 initiatives: review at least weekly while active.
- P1 initiatives: review at least biweekly.
- Active public repositories: lifecycle review at least quarterly.
- Incubating, maintenance, and deprecated repositories: review on the shorter cadence encoded in `governance/lifecycle.json`.
- R3/R4 administrative and compatibility controls: scheduled drift plus periodic effectiveness testing.

The `review_by` field is a fail-closed prompt for reassessment, not an automatic state transition.

## Cross-repository change protocol

1. Identify the canonical producer and all affected consumers.
2. Open or update the organization initiative only when the shared outcome or ownership changes.
3. Make implementation changes in owning repositories.
4. Version the canonical schema/contract and publish immutable vectors/artifacts where applicable.
5. Update consumers to exact revisions and run consumer-specific canaries.
6. Record migration, rollback, unsupported platforms, degraded profiles, and residual risk.
7. Update the central dependency/contract index only after source-adjacent evidence exists.
8. Complete an initiative only when every exit criterion points to exact evidence.

## Conflict and escalation

When two repositories claim the same domain, validation fails. Work may continue as proposals, but no new canonical release or protected mutation should rely on the conflict.

Escalation order:

1. repository owners gather current implementation evidence;
2. canonical-domain owner identifies the governing invariant;
3. technical DRI proposes the smallest migration or containment;
4. decision owner resolves organization scope;
5. protected owner/administrator authorizes the exact protected operation;
6. a regression guard prevents the ambiguity from recurring.

## Bus factor and succession

The current registry truthfully marks `bootstrap-single-owner`. This is accepted bootstrap risk, not a mature control state.

R3/R4 maturity requires:

- at least one qualified backup reviewer or delegated team;
- documented ownership transfer procedure;
- protected credentials and break-glass custody not bound to one personal account;
- periodic access review;
- provenance-preserving ownership history.
