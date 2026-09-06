# GitHub administration, automation, and recovery

## Separation of roles

Use separate identities and scopes:

- **drift observer**: repository metadata/content read plus issue write only in `.github` for one deduplicated report;
- **administrative reconciler**: no standing personal token; a narrowly scoped GitHub App token minted only in a protected environment after reviewed approval;
- **human administrators**: accountable organization owners with hardware-backed MFA and documented break-glass custody.

The observer must never change repository settings. The reconciler must run plan-first, bind application to the reviewed immutable plan and current settings snapshot, and stop on moved state.

## Least privilege

- Default Actions permissions to read-only.
- Grant write permissions per job only when required.
- Prefer GitHub Apps and OIDC over classic PATs or long-lived secrets.
- Restrict repository creation, transfer, visibility, archive, deletion, rulesets, Apps, and environment administration.
- Keep secrets and privileged runners unavailable to untrusted fork pull requests.
- Pin third-party Actions by full commit SHA and review updates.
- Protect workflow, schema, registry, decision, security, release, and migration paths with CODEOWNERS and rulesets.

## Administrative evidence

Policy files do not prove settings are applied. Close an administrative control only with exported settings or API snapshots, exact ruleset/environment identifiers, app scope inventory, and positive/negative test evidence.

## Break-glass

- Maintain at least two custodians when staffing permits.
- Store recovery material outside GitHub using an approved secure process.
- Limit bypass to named emergencies and record every use.
- Require post-event review, credential rotation where relevant, and expiry of temporary access.
- Test organization ownership recovery, App revocation, repository export, ruleset reconstruction, and critical release-channel recovery.

## Backup and portability

Regularly export the `.github` Git repository, accepted ADRs, schemas, registry, ruleset snapshots, app inventory, and Projects/issue mappings. Do not treat generated views as the only backup. Recovery must reconstruct authoritative inputs first and regenerate derived state.
