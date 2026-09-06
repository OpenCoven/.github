# Generated governance control index

> Generated from `governance/controls.json`. A control marked specified or implemented is not necessarily administratively applied or operationally effective.

| Control | Objective | Enforcement | State |
|---|---|---|---|
| `GOV-001` Unique canonical ownership | Every canonical public domain has exactly one owning repository. | scripts/governance.py validate | implemented |
| `GOV-002` Public/private minimization | The public registry contains public repositories and non-sensitive metadata only. | registry scope and secret-like-data validation | implemented |
| `GOV-003` Lifecycle accountability | Every public repository has a lifecycle, owner, DRI, risk class, disposition, and review date. | scripts/governance.py validate | implemented |
| `GOV-004` Derived-view integrity | Generated portfolio views exactly reflect authoritative records. | generate --check | implemented |
| `GOV-005` Least-privilege workflows | Workflows declare permissions and pin third-party Actions to immutable commits. | workflow policy validation | implemented |
| `GOV-006` Protected governance branch | Governance changes enter main only through reviewed, checked pull requests. | GitHub organization ruleset | administrative-gate-open |
| `GOV-007` Exception expiry | Every waiver is scoped, approved, expiring, and visible. | scripts/governance.py validate | implemented |
| `GOV-008` Repository drift detection | Declared public inventory is reconciled against GitHub without becoming a second mutable status store. | scheduled read-only discovery plus one issue | implemented-pending-merge |
| `GOV-009` Protected authority separation | Governance metadata cannot grant OpenCoven runtime or protected mutation authority. | review, schemas, and architecture canaries in owning repositories | specified |
| `GOV-010` Evidence-backed change | Material governance changes include machine-readable, reviewable evidence. | reusable evidence workflow | implemented-pending-adoption |
