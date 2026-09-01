# Brand and UI consolidation resolution addendum

**Date:** 2026-09-01  
**Applies to:** `docs/brand-ui-consolidation-audit-2026-08-31.md`

The August 31 audit is retained as the evidence snapshot that identified the simultaneous-canonicality risk. This addendum records the disposition of the urgent Brand merge hazard so the organization plan does not continue to present it as unresolved.

## Resolved containment

`OpenCoven/brand#4` was rewritten on top of the already-ratified profile and merged as `798e2f5f2f1a69f5d156ccc0a9aafc4f7da55fc8`.

The merged change does **not** introduce the proposed second `1.0.0` profile. Instead it:

- keeps `web/profile.json`, `web/profile.css`, and `web/assets/mark.svg` as the sole normative public-web authority;
- makes Brand validation fail closed when another root-level JSON manifest claims stable or canonical web-profile authority;
- reserves `web/tokens.css` and `web/tokens.json` as invalid parallel-authority aliases;
- documents that a successor profile replaces the current authority through reviewed versioning rather than coexisting beside it.

The exact Brand contract CI for the rewritten head passed before merge. The audit recommendation “do not merge Brand #4 unchanged” is therefore satisfied; references to the earlier competing-profile form are historical findings, not current merge instructions.

## Still open at the organization-setting layer

`brand/main` remains unprotected as of this addendum. Repository-local validation now detects the semantic duplication, but an organization ruleset or branch-protection rule must still require review and the Brand contract CI before changes can enter `main`.

The minimum required setting is:

- target: `OpenCoven/brand` branch `main`;
- require pull requests and at least one approving review;
- require the repository’s Brand contract check;
- dismiss stale approvals after new commits;
- prohibit force pushes and branch deletion;
- do not permit routine administrator bypass.

The connected GitHub write surface used for this execution does not expose branch-protection or organization-ruleset mutation, so this setting remains an explicit administrator action rather than a repository patch.

## Remaining consolidation sequence

The broader audit remains valid after this containment change:

1. reconcile retired Brand docs and legacy-looking assets;
2. mechanically pin UI to the canonical Brand profile;
3. settle UI release and downstream canary evidence;
4. extract useful non-duplicative work from `coven-design-system` and retire its canonical claim;
5. apply required-review and required-check rulesets to Brand and UI;
6. migrate consumers through immutable lock records and evidence-backed updates.
