# Repository lifecycle and creation policy

## Lifecycle states

The machine-readable state machine is in `governance/lifecycle.json`.

- **incubating**: experimental, time-bounded, and not a canonical public dependency;
- **active**: actively developed with an accountable owner and verification path;
- **maintenance**: supported with limited change and an explicit review cadence;
- **deprecated**: successor or retirement plan exists; no new canonical surface;
- **archived**: read-only historical record;
- **tombstone**: minimal successor/provenance pointer after an approved retirement.

Canonicality is separate from lifecycle. An active repository may be supporting or specimen-only; an archived repository is historical and cannot retain a current canonical claim.

## New repository gate

Before a repository is created or made public, record a proposal that answers:

1. Which existing canonical component was evaluated, and why can it not own this work?
2. What unique domain, product, distribution, or experiment boundary justifies a repository?
3. Who is the owner, technical DRI, and successor if the owner becomes unavailable?
4. What lifecycle, risk class, visibility, license, security support, and data classification apply?
5. What bootstrap, fast verification, release, archival, and rollback procedures exist?
6. Which contracts are produced and consumed, and how are they versioned and pinned?
7. What is the 30- or 90-day graduation/retirement criterion?

Repository creation metadata cannot authorize the runtime or protected behavior implemented inside it.

## Public graduation gate

An incubating repository may become active public only when:

- its canonicality and non-goals are reviewed;
- no canonical public domain conflicts exist;
- a root agent guide or equivalent route exists;
- deterministic bootstrap and fast verification work from a clean clone;
- security policy, license, contribution provenance, and release status are truthful;
- R3/R4 paths have protected ownership and evidence requirements;
- downstream consumers use immutable contract or artifact references where applicable;
- the governance registry and live GitHub metadata agree.

## Review and succession

Every active public repository has one owner and one technical DRI. During the bootstrap-single-owner phase, `BunsDev` may hold both roles, but the registry must not imply healthy separation of duties. Each R3/R4 repository should add a qualified backup reviewer before claiming mature governance.

Ownership changes require a reviewed registry change recording the effective date, outgoing and incoming accountable identities, unresolved risk, and transition evidence. Git history provides provenance; do not erase prior ownership records.
