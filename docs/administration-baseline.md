# GitHub administration baseline

This document is an implementation checklist for organization settings. Repository content cannot enforce these controls by itself. `OpenCoven/.github#6` is the authoritative activation gate until exact settings evidence is recorded.

## `.github/main` ruleset

Required:

- pull request before merge;
- at least one approval and CODEOWNER review for protected paths;
- stale approval dismissal after new commits;
- resolved review conversations;
- required `Governance CI / validate` check;
- blocked force push and branch deletion;
- no routine administrator bypass;
- signed commits or equivalent verified provenance where operationally supportable;
- exported ruleset ID/configuration retained as evidence.

## Organization permissions

Review and minimize:

- base member repository permission;
- repository creation and visibility-change rights;
- archive, transfer, deletion, ruleset, webhook, App, secret, environment, and runner administration;
- outside collaborators and dormant administrators;
- OAuth Apps, GitHub Apps, deploy keys, classic PATs, and machine users;
- branch/ruleset bypass lists.

Require organization-member MFA. Prefer hardware-backed MFA for owners and break-glass custodians.

## Actions

- Default `GITHUB_TOKEN` to read-only.
- Allow only required Actions and reusable workflows.
- Pin third-party Actions to full commit SHAs and review automated updates.
- Disable or constrain workflows from forks that could access secrets or privileged runners.
- Use protected environments for publication and administrative reconciliation.
- Prefer OIDC and short-lived GitHub App installation tokens over long-lived secrets.
- Separate untrusted build/test from privileged signing, publication, or settings application.

## Settings reconciliation

A future administrative reconciler must have two modes:

1. **plan**: read settings, compare against reviewed desired state, and emit a deterministic immutable plan;
2. **apply**: require protected-environment approval, verify the plan digest and live-state preconditions, apply only listed changes, and emit before/after receipts.

The apply identity must not accept arbitrary repository, permission, or operation fields from pull-request code. It must stop on moved, stale, revoked, or contradictory state.

## Recovery exercise

At least periodically prove:

- repository and accepted-policy export;
- ruleset reconstruction;
- App/token revocation;
- organization-owner recovery;
- release channel and package ownership recovery;
- break-glass access followed by log review and credential rotation.
