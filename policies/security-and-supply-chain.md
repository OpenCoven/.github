# Security and software-supply-chain policy

## Threat model

The governance plane is a high-impact target because compromised policy, workflows, manifests, or generated compatibility data can misroute reviewers, weaken checks, or induce downstream repositories to trust the wrong artifact. It remains metadata unless backed by enforcement, but metadata compromise can still create substantial operational harm.

Threats include:

- compromised maintainer or organization-owner accounts;
- malicious or vulnerable third-party Actions;
- untrusted pull-request code reaching secrets or privileged runners;
- workflow modification followed by self-approval;
- mutable dependency/action references;
- forged ownership, conformance, release, or evidence records;
- stale registry state and confused-deputy automation;
- log/artifact disclosure of private or sensitive data;
- supply-chain substitution between source, generated code, package, and release artifact.

## Baseline controls

- Require protected pull-request review and CODEOWNER approval for R4 paths.
- Pin third-party Actions to full commit SHAs.
- Keep workflow permissions explicit and read-only by default.
- Separate build/test from privileged publish/reconcile jobs and environments.
- Use dependency review, secret scanning, lockfiles, reproducible generation, SBOMs, checksums, provenance/attestations, and signing where the owning repository's release model supports them.
- Verify immutable producer artifacts before consumer canaries.
- Run negative vectors for malformed, downgraded, moved, stale, replayed, and unauthorized inputs.
- Treat SLSA, OpenSSF Scorecard, SPDX/CycloneDX, and Sigstore as useful control frameworks and tooling—not automatic proof of product security or certification.

## Release boundary

This repository may describe release-train policy but does not approve or publish releases. Release jobs must bind approval to exact source, lockfile, generated output, artifact digest, environment, and conformance evidence. A main-branch unit test is not a substitute for packaged-artifact verification.
