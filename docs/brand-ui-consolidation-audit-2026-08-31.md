# OpenCoven Brand, UI, and Brand-Kit Consolidation Audit

**Status:** Decision and execution plan  
**Snapshot:** 2026-08-31  
**Scope:** `OpenCoven/brand`, `OpenCoven/ui`, `OpenCoven/coven-design-system`, private `OpenCoven/coven-design`, and the principal consumers in `coven-landing`, `coven-cave`, `coven-docs`, `psyche-build`, and related product repositories.

## Executive decision

OpenCoven should converge on **two permanent public upstream repositories** and one clear product boundary:

1. **`OpenCoven/brand` is the sole canonical source for identity, visual language, voice, brand assets, semantic brand profiles, and the generated brand kit.**
2. **`OpenCoven/ui` is the sole reusable interaction and component implementation layer.** It consumes a pinned Brand profile, owns framework-neutral interaction contracts and test vectors, and publishes React/shadcn implementations without acquiring runtime or product authority.
3. **Product repositories own production composition and behavior.** `coven-cave` remains authoritative for Cave’s shipped component behavior and optional product themes; `coven-landing` owns static route composition; neither should become a second brand or design-system authority.

The remaining repositories should be handled as follows:

- **Extract and retire `OpenCoven/coven-design-system`.** Preserve its useful component inventory, coverage harness, and selected CSS patterns, but do not preserve its claim to canonical token ownership.
- **Rename private `OpenCoven/coven-design` to `OpenCoven/coven-evals` or `OpenCoven/design-evals`.** It is clean-room/double-blind evaluation tooling, not a brand or component repository.
- **Use `coven-landing` as the reference consumer contract.** Its immutable Brand/UI pins and verification script are the best current model for every downstream surface.
- **Do not merge `OpenCoven/brand#4` unchanged.** It introduces a second canonical `1.0.0` web profile with a different schema, token namespace, typography, palette values, and asset pointer after `web/profile.css`, `web/profile.json`, and `web/assets/mark.svg` were already ratified on `main`.

This consolidation should reduce the active design/brand surface from four ambiguously named repositories to two upstream authorities plus explicit product consumers.

## Why this is urgent

The problem is no longer a lack of design work. OpenCoven has several substantial systems. The risk is **simultaneous canonicality**:

- `brand` now declares a stable `--oc-*` public-web profile and current crown/lotus mark.
- `ui` declares its own reusable component library, registry, semantic tokens, and interaction contracts.
- `coven-design-system` still calls its `--cv-*` tokens and CSS primitives canonical.
- Cave maintains a large production token and theme system and describes its code as authoritative for shipped behavior.
- An open Brand PR proposes another canonical web profile under new filenames and a new token namespace.
- Private `coven-design` is unrelated evaluation tooling but occupies the most obvious design-system repository name.

A familiar protocol cannot credibly insist on one authority for identity and mutation while its public identity system has multiple competing sources of truth. The same portfolio discipline applies here: **one canonical owner per semantic domain, explicit projections, immutable consumer pins, and no silent parallel ledgers.**

## Evidence snapshot

| Surface | Inspected revision/state | Material finding |
|---|---|---|
| [`OpenCoven/brand`](https://github.com/OpenCoven/brand) | `4127be6d402089d15953e76988bbeab2db37df54` on `main` | Stable Brand web profile v1 landed; old authoritative docs and legacy-looking assets remain beside it; `main` is unprotected. |
| [`OpenCoven/ui`](https://github.com/OpenCoven/ui) | `fa61e9449cf2f5973532d45486b8fafbdf616425` on `main` | Strong monorepo, package, registry, contracts, accessibility and visual receipts; release/adoption and branch governance are incomplete. |
| [`OpenCoven/coven-design-system`](https://github.com/OpenCoven/coven-design-system) | `6032f9f407982379e39ed1a40eec7a2e8b24e5c6` | Useful 62-family/224-class CSS inventory, but stale, private-package distribution, no GitHub release, no workflow surfaced, and duplicate canonical claim. |
| [`OpenCoven/coven-design`](https://github.com/OpenCoven/coven-design) | private, current `main` | Double-blind evaluation/capture tooling; naming collides with design-system and brand work. |
| [`OpenCoven/coven-landing`](https://github.com/OpenCoven/coven-landing) | current `main` | Pins Brand and UI revisions, vendors exact artifacts, and verifies canonical bytes and interaction hooks. |
| [`OpenCoven/coven-cave`](https://github.com/OpenCoven/coven-cave) | current `main` | Mature production design language and drift tests, but its UI-boundary documentation is already stale relative to the live UI repository. |
| Open pull requests | [OpenCoven/brand#4](https://github.com/OpenCoven/brand/pull/4); [OpenCoven/ui#2](https://github.com/OpenCoven/ui/pull/2), [OpenCoven/ui#3](https://github.com/OpenCoven/ui/pull/3), [OpenCoven/ui#6](https://github.com/OpenCoven/ui/pull/6) | [OpenCoven/brand#4](https://github.com/OpenCoven/brand/pull/4) duplicates a ratified profile; [OpenCoven/ui#2](https://github.com/OpenCoven/ui/pull/2) and [OpenCoven/ui#3](https://github.com/OpenCoven/ui/pull/3) are stacked against moving bases; [OpenCoven/ui#6](https://github.com/OpenCoven/ui/pull/6) is a draft named `noop`. |

## Current-state audit

### 1. `OpenCoven/brand`: correct destination, internally split

#### What is strong

`brand` now has the right canonical proposition:

- `web/profile.css` and `web/profile.json` define a framework-neutral, versioned public-web contract.
- `web/assets/mark.svg` is the current flat monochrome crown/lotus mark.
- validation checks profile/package version agreement, contrast pairs, mark flatness, responsive specimens, reduced motion, forced colors, and voice rules;
- `coven-landing` pins the exact Brand revision and canonical asset blob;
- the README explicitly assigns visual identity to Brand, interaction semantics to UI, and production behavior to product repositories.

This is the foundation to keep.

#### What is broken or ambiguous

1. **The root documentation still contains a retired design era.**  
   `DESIGN.md` describes the older trident-flame/hood/crescent identity, older violet values, legacy product names, and motion/glow guidance that conflicts with the current flat no-glow mark. `docs/BRAND-USAGE.md` still points consumers at obsolete paths and says hover states should glow. `docs/DESIGN.md` points to `../../DESIGN.md`, which is not the correct repository-root relative path.

2. **Legacy and current assets are mixed under authoritative-looking names.**  
   The current canonical mark is the compact `web/assets/mark.svg`. The `logo/` directory also contains several very large SVGs under names such as `opencoven-logo.svg`, `opencoven-white.svg`, `opencoven-black.svg`, and `opencoven-mark.svg`, plus `icons/trident.svg`. Even if retained for provenance, those files should not remain indistinguishable from current assets.

3. **The Brand package is marked private and has no GitHub release.**  
   The repository instructs consumers to pin an immutable commit or release, but the inspected package cannot be published as configured and the repository exposes no releases. Git vendoring works, but the distribution contract is unfinished.

4. **Licensing is too vague for a mixed code/assets repository.**  
   The README reserves the brand assets while saying tokens and documentation follow “OpenCoven ecosystem” terms. The repository metadata reports `NOASSERTION`. Before moving MIT-licensed CSS from `coven-design-system`, Brand needs an explicit split between code/token licensing and trademark/asset usage.

5. **The canonical branch is not protected.**  
   `main` currently has no branch protection or required checks. A canonical identity asset and semantic profile should not be directly mutable without review and green contract checks.

6. **The validator only protects the new web profile.**  
   It does not currently fail on stale authoritative docs, retired geometry outside the canonical SVG, duplicate “canonical” profiles, obsolete paths, oversized legacy assets, or inconsistent social-kit derivatives.

#### Immediate verdict

**Keep and harden.** `brand` should become the only public Brand/brand-kit repository, but it needs a repository-wide reconciliation before it can honestly function as the sole source of truth.

---

### 2. `OpenCoven/ui`: correct implementation layer, not yet a settled release surface

#### What is strong

`ui` has evolved beyond a specimen scratchpad:

- one TypeScript source powers the package, shadcn registry, and specimen app;
- framework-neutral interaction contracts and test vectors are explicit;
- package boundaries keep the UI presentation-only and separate from runtime authority;
- strict type, unit, interaction, accessibility, architecture, registry, build, generated-artifact, clean-consumer, and visual receipt checks are unusually strong;
- current CI pins GitHub Actions by immutable revisions;
- the repository has a clear route to reusable operational components and agent-specific blocks.

This repository should survive consolidation and receive the reusable implementation work extracted from `coven-design-system`.

#### What remains unresolved

1. **Brand consumption is conceptual rather than mechanically pinned.**  
   UI currently declares its own default values, including `#9386d0` presence, rather than consuming a generated adapter from an immutable Brand profile. That is acceptable for a distinct product profile only after the profile relationship is explicit; today it is another implicit design decision.

2. **Distribution is described, not yet proven as a stable release channel.**  
   `@opencoven/ui` and `ui.opencoven.ai` are documented, but no GitHub releases surfaced. The package metadata has no license field, and the inspected workflows do not include a release/publish lane.

3. **There is no production package adoption evidence in the searched product manifests.**  
   Landing consumes the framework-neutral contract rather than the React package, which is appropriate. Cave deliberately re-expresses patterns. The package still needs at least one controlled consumer canary before it is treated as a stable shared dependency.

4. **Open PR topology is carrying unnecessary risk.**  
   PR #2 is open and currently reported non-mergeable against an old `main`; PR #3 is stacked on #2 rather than `main`; PR #6 is a draft `noop` using the same visual-review head. This obscures the actual integration sequence.

5. **Cave’s documentation is stale about UI.**  
   Cave still says UI is not a packaged npm library, while UI now explicitly documents `@opencoven/ui`, registry installation, package builds, and clean-consumer tests.

6. **The canonical branch is not protected.**  
   As with Brand, `main` should require the exact CI and visual-review contracts that define the repository’s value.

#### Immediate verdict

**Keep, formalize, and release.** UI should become the only reusable implementation repository, but it must consume Brand explicitly, complete its release contract, clean its PR stack, and prove one downstream integration.

---

### 3. `OpenCoven/coven-design-system`: technically useful, strategically redundant

#### What is worth preserving

The repository is not empty or careless. It contains:

- 224 `.cv-*` classes;
- 21 package exports;
- a coverage harness requiring 62 component families;
- controls, feedback, data, application, agent, and marketing blocks;
- framework-neutral CSS;
- compatibility and embed experiments;
- provenance documenting a double-blind synthesis process.

That work should be mined, not discarded blindly.

#### Why the repository should still retire

1. **It claims the same semantic territory as Brand and UI.**  
   Its README and package description call its tokens, foundations, primitives, and guidance canonical. That is now incompatible with Brand’s canonical profile and UI’s canonical interaction/component role.

2. **Its token system is a third vocabulary.**  
   `--cv-*` includes different neutral, violet, cyan, type, radius, elevation, and motion scales. It cannot be wholesale aliased to current Brand without reintroducing drift.

3. **Its default brand direction is dated.**  
   The “familiar glow cyan” secondary accent and older violet system are not part of the current restrained monochrome/violet Brand profile.

4. **Its distribution story is internally inconsistent.**  
   README says immutable Git tags and status `v0.1.0`; package metadata is private `0.2.0`; no GitHub releases surfaced.

5. **Coverage checks presence, not product-grade behavior.**  
   The harness proves classes and gallery references exist. It does not replace keyboard, focus, semantics, reduced-motion completeness, screen-reader behavior, clean-consumer packaging, or product-level verification.

6. **No direct package consumer was found.**  
   Search found `--cv-*` remnants and compatibility references in products, but no verified product dependency on `@opencoven/coven-design-system`. This lowers retirement risk, subject to the normal organization-wide reference gate.

7. **Its human-facing name collides with a different private repository.**

#### Immediate verdict

**Feature-freeze, extract, archive, then delete after the retirement window.** Do not spend another cycle making it independently release-ready.

---

### 4. Private `OpenCoven/coven-design`: useful repository, wrong name and boundary

The repository describes clean-room design specs and double-blind evaluation tooling. Its recent work centers on blinding envelopes, arm/session tokens, locked reveal, tamper-evident capture, and evaluation receipts.

That is potentially valuable infrastructure, but it is not:

- the Brand source of truth;
- a component library;
- a brand kit;
- a public design-system repository.

#### Immediate verdict

**Retain private, rename, and narrow.**

Preferred names:

1. `OpenCoven/coven-evals`
2. `OpenCoven/design-evals`
3. `OpenCoven/evidence-lab`

Move generic visual-review orchestration into `.github` or UI only when it becomes a reusable organization control-plane capability. Keep blinded evaluation data and evaluator-specific semantics in the renamed private repository.

---

### 5. `coven-landing`: the reference consumer

Landing already models the architecture OpenCoven should standardize:

- immutable Brand and UI revisions;
- profile and contract versions;
- canonical asset blob identity;
- vendored paths with provenance;
- explicit ownership declarations;
- a verification script that rejects raw-value drift, wrong mark bytes, missing interaction hooks, non-static navigation regressions, missing theme states, and stale homepage assertions.

#### Immediate verdict

**Promote the pattern, not the implementation.** Extract the manifest schema and verification conventions into an organization-wide consumer contract that Docs, Cave-hosted public views, Psyche Build, and future sites can adopt.

---

### 6. `coven-cave`: production authority with an upstream reconciliation gap

Cave’s production design system is substantial and should not be replaced wholesale by a generic package. It has:

- product-specific semantic tokens;
- 12 themes × light/dark modes;
- production components and route behavior;
- CI drift ratchets;
- accessibility and product-specific idioms;
- explicit authority over shipped behavior.

The correct consolidation is **not** “replace Cave CSS with UI.” It is:

- Brand owns the invariant OpenCoven identity and default product-profile semantics;
- UI owns reusable interaction/component contracts and optional implementations;
- Cave maps those contracts into its production architecture and owns all behavior;
- Cave’s optional themes remain Cave-owned product customization;
- the default Coven theme and canonical mark must remain pinned to Brand;
- Cave updates its UI boundary documentation and runs upstream contract canaries.

#### Immediate verdict

**Keep product authority; remove canonical brand ambiguity.**

## Target architecture

```text
OpenCoven/.github
  portfolio registry · ownership ADRs · reusable drift / release policy
                                  │
                                  ▼
OpenCoven/brand
  canonical mark · identity assets · voice · semantic Brand profiles
  asset manifest · generated brand kit · migration guides · checksums
          │ immutable profile + asset pins
          ├───────────────────────────────┐
          ▼                               ▼
OpenCoven/ui                      framework-neutral consumers
  interaction contracts          coven-landing · coven-docs
  test vectors                    static Cave web views
  React package
  shadcn registry
          │ bounded view models / optional implementation adoption
          ▼
Product repositories
  coven-cave · psyche-build · chat · coven-code · other products
  production composition · data · state · behavior · optional local themes

Retirement path:
  coven-design-system ──extract──▶ brand / ui / product migration fixtures
                       └─archive─▶ delete after observation gate

Namespace repair:
  private coven-design ──rename──▶ coven-evals
```

## Canonical ownership contract

### `OpenCoven/brand` owns

- current mark and approved identity assets;
- retired-asset registry and deprecation status;
- wordmark/lockup rules;
- core palette and identity invariants;
- named semantic Brand profiles;
- voice, messaging, imagery, social, diagram, and motion principles;
- brand/trademark usage terms;
- generated brand-kit release artifacts;
- machine-readable asset and profile manifests.

### `OpenCoven/ui` owns

- framework-neutral interaction semantics;
- state names and stable interaction hooks;
- keyboard, focus, reduced-motion, and accessibility test vectors;
- React primitives, composed components, and operational blocks;
- shadcn registry output;
- specimen and visual-receipt surfaces;
- mapping a pinned Brand profile into component defaults;
- package/registry release compatibility.

### Product repositories own

- routes, data, state, persistence, networking, and authority;
- production composition and local behavior;
- product-specific view-model adapters;
- optional product themes and density choices;
- product-specific accessibility and browser validation;
- deliberate, documented local aliases that do not redefine Brand semantics.

### No repository may own

- a second “canonical” mark;
- a copied palette presented as a new source of truth;
- identity/status semantics inferred privately from colors;
- production authority inside a reusable UI component;
- framework behavior inside Brand;
- generic reusable component semantics duplicated inside each product without a declared reason.

## Profile model: avoid one giant token layer

A single universal token file would simply move the ambiguity into one repository. Use four explicit layers:

### Layer 0 — Brand invariants

Owned by Brand:

- mark geometry and asset identity;
- core violet family and neutral posture;
- identity/presence/action distinction;
- status semantics;
- voice and imagery constraints;
- typography roles, not bundled font binaries.

### Layer 1 — Named Brand profiles

Owned by Brand and versioned separately:

- `public-web/v1` — current `web/profile.css` and `web/profile.json`;
- `product-default/v1` — default OpenCoven application identity semantics;
- later profiles only when a real consumer requires them.

A profile is not “canonical everywhere.” It is canonical **for its declared surface class**.

### Layer 2 — UI component tokens

Owned by UI:

- component and density variables;
- generated aliases to a pinned Brand profile;
- tool-class and agent-surface presentation semantics;
- no copied raw Brand literals in hand-authored component files.

### Layer 3 — Product tokens

Owned by products:

- route/layout/shell/elevation details;
- optional themes;
- local aliases;
- explicit mappings back to Brand/UI roles;
- no promotion of local values into organization-wide Brand without a reviewed profile change.

## Required consumer lock

Generalize Landing’s existing contract into `opencoven.design-consumer/v1`:

```json
{
  "schemaVersion": "opencoven.design-consumer/v1",
  "brand": {
    "repository": "OpenCoven/brand",
    "revision": "<40-char SHA>",
    "profile": "public-web",
    "profileVersion": "1.0.0",
    "assets": {
      "mark": {
        "source": "web/assets/mark.svg",
        "gitBlob": "<40-char blob SHA>",
        "vendoredPath": "public/assets/opencoven-mark.svg"
      }
    }
  },
  "ui": {
    "repository": "OpenCoven/ui",
    "revision": "<40-char SHA>",
    "contractVersion": "1.0.0",
    "packageVersion": "0.1.0"
  },
  "local": {
    "profile": "landing",
    "aliases": "docs/design/aliases.json",
    "productionOwner": "OpenCoven/coven-landing"
  }
}
```

Every consumer should verify:

- immutable SHAs, not branch heads;
- exact canonical asset bytes;
- profile/schema compatibility;
- allowed aliases;
- no retired-mark references;
- required interaction hooks;
- accessibility and product-level scenarios;
- generated/vendored artifacts are clean after verification.

## Brand repository consolidation plan

### A. Ratify a repository-wide source-of-truth hierarchy

Add `docs/ADR-0001-brand-ui-ownership.md`:

1. `web/profile.*` is canonical for public web v1.
2. `web/assets/mark.svg` is the only current mark source for that profile.
3. Root docs may explain history but may not contradict a stable profile.
4. `logo/legacy/**` contains non-current assets and is never a default import.
5. UI owns interaction/components; products own production behavior.
6. New profile names require a concrete consumer and major/minor version review.
7. Two artifacts may not both claim the same profile name/version.

### B. Reconcile or retire stale documentation

- Replace root `DESIGN.md` with a short current architecture and historical index, or move the existing file to `docs/history/2026-05-trident-era.md`.
- Rewrite `docs/BRAND-USAGE.md` against `web/profile.*` and the current mark.
- Fix `docs/DESIGN.md` to point to the correct current document.
- Add a CI grep/semantic check for retired hood/trident language outside `docs/history` and `assets/legacy`.
- Remove stale OpenClaw/OpenMeow/Cast-era product references from normative material.
- Keep historical rationale only when clearly labeled non-normative.

### C. Quarantine legacy assets

Preserve provenance without accidental reuse:

```text
logo/
  README.md
  legacy/
    hood-trident-v1/
      manifest.json
      opencoven-logo.svg
      opencoven-white.svg
      opencoven-black.svg
      ...
web/assets/
  mark.svg                  # current public-web canonical source
assets/
  manifest.json             # all current + legacy status, hashes, dimensions
```

Do not move existing paths until the reference scan is complete. First add the manifest and deprecation notices; then migrate paths in a major/minor release with compatibility aliases where needed.

The two supplied hood/trident images should be treated as retired reference material only, never as current logo inputs.

### D. Add an asset manifest and deterministic kit builder

`assets/manifest.json` should record:

- stable asset ID;
- status: `canonical`, `approved-variant`, `generated`, `legacy`, `retired`;
- source path;
- source commit/blob and SHA-256;
- viewBox/dimensions;
- foreground/background constraints;
- minimum size and clear space;
- allowed use cases;
- prohibited modifications;
- generator and source asset for derivatives;
- licensing/trademark terms;
- replacement/successor.

Add deterministic scripts:

- `scripts/build-brand-kit.mjs`
- `scripts/verify-brand-kit.mjs`
- `scripts/scan-retired-assets.mjs`
- `scripts/verify-consumer-locks.mjs`
- `scripts/check-svg-safety.mjs`

### E. Resolve licensing before migration

Adopt an explicit split, subject to legal review:

- **code, schemas, validators, token exports:** one named open-source license;
- **logos, marks, social assets, brand templates:** OpenCoven brand/trademark usage terms;
- **third-party font references:** names and links only; never bundle unlicensed binaries;
- **migrated `coven-design-system` code:** retain required MIT notices and provenance.

Do not leave “OpenCoven ecosystem terms” as the operative license for reusable code.

### F. Complete distribution

Choose and document one primary contract:

- GitHub Releases containing `opencoven-brand-kit-vX.Y.Z.zip`, `SHA256SUMS`, profile files, manifest, and changelog;
- optionally publish `@opencoven/brand` after removing `private: true`;
- consumers may continue immutable Git vendoring, but released artifacts should exist.

A release should be built from a clean tag and include provenance, not manually assembled local files.

## UI repository consolidation plan

### A. Add a pinned Brand adapter

Add a machine-readable Brand lock and generated adapter:

```text
contracts/brand-lock.json
packages/ui/src/styles/brand.generated.css
scripts/sync-brand-profile.mjs
scripts/verify-brand-profile.mjs
```

Rules:

- generated adapter carries Brand revision/profile/version;
- hand-authored UI CSS never duplicates raw Brand values;
- UI component tokens can be more specific but must alias semantic Brand roles;
- UI can expose neutral override hooks for product consumers;
- changing the Brand lock requires visual receipts and a migration note.

### B. Define the product-default profile relationship

The current UI/Cave presence value and the public-web value need not be identical. The relationship must be explicit:

- Brand creates `product-default/v1` only after comparing UI and Cave;
- UI specimens consume it;
- Cave’s default `coven` theme maps to it;
- Cave’s other 11 themes remain Cave-owned;
- public web remains on `public-web/v1`.

This avoids forcing a marketing palette into dense product UI while retaining one owner for OpenCoven identity semantics.

### C. Complete the release contract

- add explicit code license;
- add changesets or an equivalent deterministic version workflow;
- publish GitHub releases;
- decide whether npm publication is supported now or whether registry/source installation is the only stable path;
- if npm is supported, add provenance/attestation and packed-package consumer tests;
- publish compatibility table: Brand profile, UI contract, React, registry schema;
- protect `main` and require CI plus visual review for relevant paths.

### D. Clean the current PR topology

- **Close [OpenCoven/ui#6](https://github.com/OpenCoven/ui/pull/6)** unless it has a documented purpose; a `noop` draft should not be part of the release graph.
- **Rebase or recreate [OpenCoven/ui#2](https://github.com/OpenCoven/ui/pull/2) directly on current `main`.** Preserve the visual-receipt work but eliminate its stale base and 76-commit ambiguity.
- **Restack [OpenCoven/ui#3](https://github.com/OpenCoven/ui/pull/3) on the cleaned #2 or split it into reviewable PRs:** contracts/adapters, components, specimen route, registry output.
- update every PR body from claimed historical mergeability to current evidence;
- avoid stacking long-lived branches on feature branches once shared foundation work has landed.

### E. Import only the useful parts of `coven-design-system`

Every migrated component must satisfy UI’s stronger contract:

- semantic/native structure;
- keyboard and focus behavior;
- visible state names;
- reduced-motion completeness;
- high contrast/forced colors;
- 320–430 px and 200% zoom/reflow;
- unit/accessibility tests;
- registry/package output;
- visual receipts;
- presentation-only authority boundary.

## `coven-design-system` extraction matrix

| Existing material | Destination | Decision |
|---|---|---|
| Raw `--cv-*` palette, type, radius, elevation, motion scales | Brand comparison document only | **Do not copy wholesale.** Reconcile useful values against current profiles, then delete the old authority. |
| Semantic `--cv-*` themes | Brand profile migration analysis | Use only as evidence while defining `product-default/v1`; no permanent alias layer. |
| Core CSS reset/base | UI or product-specific baseline | Port only if it improves the existing baseline and passes clean-consumer tests. |
| Controls | UI primitives | Compare against Base UI/native implementations; port missing behavior, not CSS names. |
| Feedback and data components | UI package/registry | Port selectively with semantics and accessibility tests. |
| Agent components (`turn`, `tool`, `approval`, `work-group`, `compaction`, etc.) | UI agent-surface components | Highest-value extraction candidates; compare against current UI inventory first. |
| Application shell/navigation/panes | UI blocks or product repos | UI only when truly reusable; product-specific shells stay in products. |
| Marketing blocks (`navbar`, features, pricing, testimonial, footer) | Brand specimens + owning web product | Do not make React implementations canonical without a real React consumer. |
| `compat/*` shims | Owning product migration folders | Move only when an active consumer exists; otherwise delete. |
| Embed/host-frame experiments | UI optional adapter | Retain only with an explicit embed consumer and threat/accessibility model. |
| Preview/gallery | UI migration evidence | Capture final receipts, then archive as historical evidence. |
| Coverage harness | UI migration script | Reuse the inventory concept, but extend it to behavior, exports, tests, and rendered receipts. |
| Provenance | UI/Brand migration archive | Preserve attribution and method history. |

### Retirement sequence

1. Freeze feature work.
2. Create `MIGRATION.md`, `DEPRECATION.md`, and final inventory.
3. Tag the exact final state if no trustworthy tag exists.
4. Open extraction issues in Brand/UI/product repositories.
5. Remove or migrate all organization references.
6. Replace README with a successor map.
7. Archive for 30 days.
8. Monitor references, downloads, issues, and build failures.
9. Delete only after a rollback archive and final reference scan.

## Brand-kit v1.1 specification

The generated Brand kit should contain source-of-truth assets and deterministic derivatives, not a loose folder of manually edited files.

```text
opencoven-brand-kit-v1.1.0/
  README.md
  MANIFEST.json
  SHA256SUMS
  LICENSE-CODE
  BRAND-USAGE.md
  CHANGELOG.md

  identity/
    mark.svg
    mark-black.svg
    mark-white.svg
    mark-16.png
    mark-32.png
    mark-64.png
    mark-128.png
    mark-256.png
    mark-512.png
    mark-1024.png
    favicon.svg
    favicon.ico
    apple-touch-icon.png
    pwa-192.png
    pwa-512.png

  profiles/
    public-web/
      profile.css
      profile.json
      specimen.html
    product-default/
      profile.css
      profile.json
      specimen.html

  social/
    og-1200x630.svg
    og-1200x630.png
    github-social-preview.png
    x-avatar.png
    x-banner.png
    discord-banner.png
    youtube-thumbnail-template.svg
    linkedin-banner.png
    metadata.json

  templates/
    architecture-diagram.svg
    announcement-card.svg
    quote-card.svg
    repository-og.svg

  guidance/
    identity.md
    voice.md
    imagery.md
    accessibility.md
    product-status.md
    migration.md

  legacy/
    README.md
    manifest.json
```

### Brand-kit quality gates

- canonical SVG uses `currentColor`, has no external resources, script, raster embed, filter, gradient, or unsafe metadata;
- mark is legible at 16/24/32 px;
- generated variants are byte-reproducible;
- social safe areas are machine-readable and tested;
- every PNG records its source asset and generator version;
- light/dark and monochrome specimens exist;
- no retired geometry appears outside `legacy`;
- alt-text guidance accompanies social templates;
- no font files are included;
- checksums and release provenance are published.

## Immediate pull-request triage

### `OpenCoven/brand#4`

**Decision: request replacement, not merge.**

Why:

- `main` already has canonical `web/profile.css`, `web/profile.json`, and `web/assets/mark.svg` at version `1.0.0`;
- #4 adds `web/tokens.css` and `web/tokens.json`, also labeled canonical `1.0.0`;
- it uses a different schema and token prefix (`--oc-web-*`);
- it changes typography from the ratified profile;
- it changes action/presence values;
- it points consumers at the ambiguous `logo/` directory instead of the canonical asset path;
- merging would create two canonical public-web profiles with the same version.

Salvage the strongest explanatory material from `web/README.md` into `docs/WEB-SURFACE-PROFILE.md` and create a narrowly scoped follow-up PR against the ratified artifacts.

### `OpenCoven/ui#2`

Rebase/recreate on current `main`; preserve visual-review functionality and receipts. Update the body with current head/base/check evidence.

### `OpenCoven/ui#3`

After #2 is clean, either restack or split. The developer-surface work is strategically aligned because it remains presentation-only, but 90+ stacked commits are too broad for a stable release boundary.

### `OpenCoven/ui#6`

Close as abandoned/duplicate unless its purpose is documented immediately.

## Repository governance

### Branch rulesets for `brand` and `ui`

Require:

- pull request;
- no force pushes or branch deletion;
- required CI;
- required visual review when profile/component/asset paths change;
- one owner approval;
- resolved review conversations;
- stale approval dismissal after material changes;
- CODEOWNERS on canonical assets, profiles, contracts, release workflows, and licensing;
- signed release tags;
- least-privilege workflow permissions;
- immutable action revisions.

### Change classes

| Class | Example | Required evidence |
|---|---|---|
| Patch | typo, clarification, additive specimen | checks; no consumer migration |
| Minor | additive token/component/asset | checks, visual receipts, consumer canary |
| Major | semantic token change, mark/path/schema removal | ADR, migration guide, downstream canaries, owner approval, release note |
| Protected identity | canonical mark, voice/legal semantics, retired/current status | Brand-owner approval and exact asset/provenance receipt |
| Release | package/kit publication | clean tag, checksums, provenance, rollback plan |

### Agent entrypoints

Add root `AGENTS.md` to Brand and UI containing:

- canonical ownership and non-ownership;
- current profile/package versions;
- protected and generated paths;
- bootstrap and fast/full checks;
- no-font-binary rule;
- asset-generation provenance;
- consumer lock update procedure;
- completion/evidence requirements;
- retirement restrictions.

## Execution plan

### Phase 0 — containment, 0–48 hours

- [ ] Mark [OpenCoven/brand#4](https://github.com/OpenCoven/brand/pull/4) as superseded/rework-required; prevent duplicate profile merge.
- [ ] Close [OpenCoven/ui#6](https://github.com/OpenCoven/ui/pull/6).
- [ ] Freeze `coven-design-system` feature work.
- [ ] Ratify the Brand/UI/product ownership ADR.
- [ ] Protect `brand/main` and `ui/main`.
- [ ] Add a cross-repository consolidation epic.
- [ ] Capture current repo, asset, token, package, tag, release, and reference inventories.
- [ ] Declare `web/profile.*` + `web/assets/mark.svg` the current public-web v1 source.

**Exit:** no new canonical token, mark, or component authority can land outside Brand/UI.

### Phase 1 — Brand reconciliation, days 2–7

- [ ] Move retired normative text into history.
- [ ] Rewrite Brand usage guidance and fix paths.
- [ ] Add asset manifest and legacy statuses.
- [ ] Add retired-asset scan and duplicate-profile guard.
- [ ] Ratify code/assets licensing split.
- [ ] Add CODEOWNERS, AGENTS.md, and release policy.
- [ ] Produce reproducible Brand kit v1.1 release candidate.
- [ ] Add organization consumer-lock schema based on Landing.

**Exit:** a new contributor cannot accidentally select the old mark, old profile, or obsolete token source.

### Phase 2 — UI integration and design-system extraction, days 7–14

- [ ] Add Brand lock and generated adapter to UI.
- [ ] Decide/ratify `product-default/v1`.
- [ ] Inventory all 62 design-system families against current UI.
- [ ] Port only missing, high-value components.
- [ ] Preserve behavior/a11y tests and migration provenance.
- [ ] Restack [OpenCoven/ui#2](https://github.com/OpenCoven/ui/pull/2) and [OpenCoven/ui#3](https://github.com/OpenCoven/ui/pull/3) into a clean sequence.
- [ ] Add release/version/license workflow.
- [ ] Publish a release candidate and registry canary.

**Exit:** UI has no hand-copied Brand literals and every imported design-system feature passes UI’s full contract.

### Phase 3 — consumer migration, days 14–30

- [ ] Keep Landing green as the reference canary.
- [ ] Add design-consumer locks to Docs and relevant public web surfaces.
- [ ] Add Brand/default-profile lock and UI contract lock to Cave.
- [ ] Update Cave’s stale UI boundary documentation.
- [ ] Add canaries to Psyche Build and Chat where they consume shared assets/components.
- [ ] Replace old mark copies and raw Brand values.
- [ ] Ensure default product theme mapping is explicit while optional Cave themes remain local.

**Exit:** every active public-facing consumer identifies exact Brand/UI versions and contains no accidental second canonical source.

### Phase 4 — retirement and stabilization, days 30–45

- [ ] Tombstone and archive `coven-design-system`.
- [ ] Rename private `coven-design`.
- [ ] Monitor for 30 days before deletion.
- [ ] Publish Brand kit v1.1 and UI v0.2/1.0 according to the chosen maturity policy.
- [ ] Remove obsolete compatibility entrypoints after all pins update.
- [ ] Add scheduled organization-wide drift scans.
- [ ] Run a clean-room consumer exercise from docs only.

**Exit:** two upstream repositories, zero ambiguous canonical ownerships, zero retired-mark references, and reproducible releases.

## Proposed GitHub issue decomposition

### Organization / `.github`

1. **[P0] Ratify Brand → UI → product ownership ADR**
2. **[P0] Add organization-wide design consumer-lock schema and drift workflow**
3. **[P0] Protect canonical Brand/UI branches and paths**
4. **[P1] Track OpenCoven brand/UI consolidation and repository retirement**

### `brand`

1. **[P0] Reconcile root Brand docs with public-web profile v1**
2. **[P0] Quarantine retired hood/trident assets and add asset manifest**
3. **[P0] Prevent duplicate canonical profiles and retired-asset use**
4. **[P1] Define product-default Brand profile with UI and Cave**
5. **[P1] Ratify code versus brand-asset licensing**
6. **[P1] Build and release reproducible OpenCoven Brand Kit v1.1**
7. **[P1] Add AGENTS.md, CODEOWNERS, and protected change policy**

### `ui`

1. **[P0] Consume pinned Brand profile through generated adapter**
2. **[P0] Repair visual-review/developer-surface PR stack**
3. **[P1] Inventory and import approved coven-design-system components**
4. **[P1] Publish package/registry release and compatibility contract**
5. **[P1] Add a real downstream package or registry consumer canary**
6. **[P1] Add AGENTS.md, CODEOWNERS, and branch/path rules**

### `coven-design-system`

1. **[P0] Freeze, inventory, and publish migration map**
2. **[P1] Extract approved assets/components with provenance**
3. **[P1] Tombstone and archive after organization reference scan**

### `coven-cave`

1. **[P1] Pin Brand default-profile and UI interaction contracts**
2. **[P1] Reconcile Cave design-language docs with live UI**
3. **[P1] Map default Coven theme to Brand while preserving local optional themes**

### `coven-landing` / `coven-docs` / other consumers

1. **[P1] Graduate Landing’s upstream contract into shared consumer schema**
2. **[P1] Adopt immutable Brand/UI pins and retired-asset scan**
3. **[P1] Add source revision and date to screenshots and diagrams**

## Success metrics

| Metric | Target |
|---|---:|
| Repositories claiming canonical Brand/token ownership | 1 |
| Repositories claiming reusable component/interaction ownership | 1 |
| Active consumers with immutable Brand lock | 100% |
| Active applicable consumers with immutable UI contract lock | 100% |
| Retired hood/trident references outside legacy/history | 0 |
| Hand-copied raw Brand values in UI/product code | 0, except documented generated artifacts |
| Canonical asset variants with manifest + checksum + provenance | 100% |
| Brand/UI protected branches and protected canonical paths | 100% |
| Brand/UI releases with checksums and compatibility metadata | 100% |
| Design-system components migrated without full UI evidence | 0 |
| Stale duplicate profile namespaces for the same surface/version | 0 |
| Broken consumers caused by design-system retirement | 0 |
| Root AGENTS.md in Brand/UI | 100% |
| Clean-room Brand-kit and UI consumer bootstrap | Pass |
| Ambiguous repository names in the design/brand namespace | 0 |

## Risks and mitigations

### Risk: consolidating tokens breaks Cave’s rich theme system

**Mitigation:** Brand owns only identity invariants and the default product profile. Cave retains optional themes and production behavior. Mapping is explicit, not replacement-by-package.

### Risk: useful CSS is lost during design-system retirement

**Mitigation:** create a complete 62-family inventory, final receipts, and migration decision per family. Archive before deletion.

### Risk: Brand becomes a monorepo for every UI detail

**Mitigation:** Brand owns values, assets, voice, and profiles. UI owns reusable implementation. Products own behavior and composition. Enforce with architecture tests.

### Risk: npm/package publication creates premature compatibility promises

**Mitigation:** declare maturity honestly. GitHub release + immutable registry can precede stable npm. Publish compatibility ranges and use pre-1.0 versions until the contract is ready.

### Risk: legacy assets are still used from unknown release paths

**Mitigation:** organization code search, workflow/package scan, web/social metadata scan, 30-day archive window, and rollback bundle before deletion or path removal.

### Risk: PR cleanup discards good work

**Mitigation:** capture branch SHAs, generate diffs and receipts, then recreate narrow PRs. Close only after replacement branches are linked.

## Final recommendation

Treat this as a **canonical-authority repair**, not a cosmetic reorganization.

The durable end state is:

- `brand` tells every familiar and human **what OpenCoven is allowed to look and sound like**;
- `ui` provides **reusable, tested ways to express those semantics**;
- Cave and other products decide **how those expressions behave in production**;
- every consumer pins and verifies the exact upstream identity it embodied;
- legacy work remains traceable without being mistaken for the current self.

That is the brand-system equivalent of OpenCoven’s identity architecture: one protected source, explicit revisions, constrained projections, verifiable embodiments, and no accidental forks.
