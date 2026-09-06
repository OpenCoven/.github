# Repository consolidation, archival, and retirement

Repository removal is an externally consequential and often irreversible operation. A registry disposition is a plan, not authorization to archive, transfer, privatize, or delete.

## Required sequence

1. **Inventory references** across source, docs, workflows, package manifests, submodules, badges, domains, webhooks, GitHub Apps, release scripts, update feeds, and installation instructions.
2. **Inventory distribution** across npm, crates.io, PyPI, Maven, SwiftPM, Homebrew, containers, downloadable artifacts, checksums, attestations, and evergreen URLs.
3. **Preserve provenance**: tags, releases, issues, discussions, advisories, licenses, notices, contributor history, and any legally required records.
4. **Select destination** and migrate only non-duplicative value with traceable commits or documented extraction receipts.
5. **Publish a successor notice** that distinguishes current canonical behavior from historical material.
6. **Archive first** for an observation period unless a documented legal or security exception requires another path.
7. **Monitor breakage**: failed downloads, inbound links, package use, installer/update requests, and new issues.
8. **Apply the final action** only with explicit authorization, an immutable reviewed plan, current-state revalidation, and rollback evidence.

## Retirement evidence packet

Must include:

- repository and exact head revision;
- proposed destination or tombstone;
- reference and package searches performed;
- release/download/update-channel findings;
- legal/license/provenance preservation;
- user migration and communications plan;
- observation start/end and monitoring results;
- rollback archive and recovery procedure;
- authorized administrator and exact action receipt.

Deletion is not the default. Prefer consolidation plus archive/tombstone when historical links, releases, citations, or provenance remain valuable.
