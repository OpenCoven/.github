# Governance-plane rollout

The rollout is intentionally reversible. It does not itself archive, transfer, privatize, delete, release, publish, or change organization settings.

## Initial slice — this change

- establish ADRs and source-of-truth boundaries;
- inventory the current public GitHub surface;
- encode lifecycle, canonicality, ownership, risk, disposition, controls, and exceptions;
- add cross-repository initiatives and public dependency/contract indexes;
- add dependency-free validation, generation, negative tests, issue forms, and evidence templates;
- add read-only CI, reusable readiness/evidence workflows, and scheduled public drift observation;
- create separate repository and administrative activation issues.

Exit: clean local fast gate and green PR CI.

## Days 0–30

1. Establish an eligible independent reviewer and backup CODEOWNER through the
   separately authorized issue #6 administration path.
2. Apply and evidence the `.github/main` ruleset and organization/Actions
   baseline from issue #6 without a routine administrator bypass.
3. Prove that direct pushes are rejected and that the governance-plane PR can
   satisfy the required review, CODEOWNER, conversation-resolution, and
   `Governance CI / validate` gates.
4. Review and merge the governance-plane PR through that protected path.
5. Pilot repository-local `agent/manifest.json` and the reusable readiness workflow in at least two canonical repositories at an immutable `.github` commit.
6. Reconcile the live public inventory and correct default-branch/archive/manifest drift.
7. Convert current portfolio recommendations into scoped repository-local migration issues.
8. Add backup reviewers for the highest-risk R4 repositories or explicitly track the bus-factor exception.

Exit:

- repository and administrative activation gates are closed;
- two pilot consumers are green;
- no unowned or duplicate public canonical domains;
- drift observer maintains at most one issue.

## Days 31–60

1. Extend manifests and fast/full interfaces to all retained active public repositories.
2. Add immutable producer/consumer canaries for the trust stack.
3. Generate the public compatibility page in Coven Docs from exact artifacts.
4. Migrate non-duplicative value from deprecated repositories with provenance.
5. Archive time-bounded historical repositories only after the retirement gate and explicit authorization.
6. Add SBOM/provenance/signing evidence to release-owning repositories where appropriate.

Exit:

- every retained public repository has owner, lifecycle, manifest, clean bootstrap, and required checks;
- every canonical producer has at least one immutable downstream canary;
- no deprecated repository introduces a new canonical surface.

## Days 61–90

1. Complete approved consolidation, private-incubation, transfer, archival, or tombstone actions.
2. Validate package/update/download/domain/webhook continuity after each retirement observation window.
3. Run standardized golden-task evaluations and control-effectiveness tests.
4. Add access-controlled aggregation for private repository manifests without copying private context into public files.
5. Decide whether scale justifies a Backstage/service-catalog projection; keep files as authority unless a new ADR proves otherwise.
6. Publish an evidence-backed portfolio review with exact residual risks and no certification overclaims.

Exit:

- public inventory matches the reviewed target for that date;
- zero ambiguous canonical ownership;
- zero expired exceptions or stale generated views;
- zero broken references caused by approved retirement;
- administrative and release controls have recurring effectiveness evidence.

## Revisit criteria

Reconsider the architecture if confidentiality, scale, bottlenecks, availability, or blast radius remain unacceptable for two review cycles despite the mitigations in ADR-0001.
