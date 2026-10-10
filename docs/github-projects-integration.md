# GitHub Issues and Projects integration

## Division of authority

| Data | Authoritative location | Project treatment |
|---|---|---|
| Repository lifecycle, canonicality, public domain ownership, risk | `governance/repositories.json` | Read-only generated fields/labels |
| Initiative outcome, decision owner, technical DRI, dependencies, exit criteria | `initiatives/*.json` | Synced view and filtering |
| Implementation status, code, review, tests | Owning repository issue/PR/CI | Native issue/PR fields |
| Accepted organization decision | `decisions/` | Link only |
| Compatibility/release evidence | Owning repository artifact plus `compatibility/` index | Digest/profile summary only |
| Immediate prioritization and attention | Project | Operational; not copied back as normative truth unless reviewed |

## Recommended Project fields

- Initiative ID
- Canonical domain
- Owning repository
- Workstream driver
- Decision owner
- Technical DRI
- Risk class
- Lifecycle
- Current gate
- Dependency state
- Evidence state
- Target release
- Last verified revision
- Stale/degraded flag

Avoid manually maintained percent-complete fields. Compute status from linked workstream issues, required checks, and explicit exit criteria.

## Synchronization contract

The safe direction is:

```text
Git files + owning-repository evidence → generated Project fields
Project prioritization/assignment → human-reviewed PR when normative records must change
```

A Project automation may propose a registry or initiative update, but must not commit a protected change directly. Duplicate issue creation should be prevented with stable initiative/workstream identifiers.

## Private work

Use an access-controlled Project for private-repository workstreams. The public initiative may contain an opaque private-overlay identifier, but synchronization must not copy private titles, descriptions, assignees, labels, paths, or evidence into the public repository.
