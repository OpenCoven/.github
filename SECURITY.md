# OpenCoven Security Policy

OpenCoven is an early-stage, identity-preserving familiar infrastructure project. Its repositories include protocol specifications, local runtime authority, orchestration, memory clients, desktop and terminal products, GitHub delivery, documentation, and public web surfaces. Security claims must remain scoped to the repository, release, contract, and verification family that actually supports them.

## Policy precedence

1. A repository-specific `SECURITY.md` is the normative policy for that repository.
2. This organization policy applies when a repository has no more specific policy and to findings that span multiple OpenCoven repositories.
3. Public landing pages and documentation may summarize security posture, but they do not create guarantees beyond the applicable source-adjacent policy and shipped evidence.

## Reporting a vulnerability

**Do not open a public GitHub issue or discussion for a security vulnerability. Do not send exploit details through a public Discord channel or depend on a maintainer's personal account as the reporting path.**

Use the following private path:

1. Open a **GitHub Security Advisory** in the repository most directly affected.
2. If the finding spans repositories, name every known affected repository and contract in that advisory.
3. If the correct repository is unclear, use the private advisory intake in [`OpenCoven/coven`](https://github.com/OpenCoven/coven/security/advisories/new) and state that the report is organization-wide so it can be routed without publishing the details.

Include, where safe and applicable:

- affected repository, release, commit, package, artifact, or protocol revision;
- the security boundary or property believed to be affected;
- reproduction steps using synthetic data;
- expected versus observed behavior;
- impact and required preconditions;
- suggested mitigations or rollback information;
- whether disclosure coordination or researcher credit is requested.

Never include real prompts, memories, credentials, tokens, session identifiers, private repository paths, or user data in a report. Use synthetic placeholders and attach sensitive evidence only through the private advisory.

## Response commitments

OpenCoven currently publishes **no guaranteed acknowledgment or remediation deadline**. Maintainers triage private advisories through repository maintenance and release processes. A response-time target becomes public only after an accountable process can measure and reliably meet it.

Researchers who responsibly disclose may request credit in a release note, with their permission. Embargo and disclosure timing are coordinated case by case through the private advisory.

## Findings in scope

Security reports are welcome for flaws affecting, among other things:

- familiar identity integrity, principal binding, authorization, revision, or recovery;
- protected-surface decisions, mutation gates, replay protection, or downgrade behavior;
- daemon, local IPC, project, path, session, or harness authority boundaries;
- memory/session confidentiality, redaction, retention, encryption, or cross-context isolation;
- task, lease, approval, receipt, recovery, delegation, or publication boundaries;
- GitHub App, webhook, worker, Check Run, pull-request, credential, or deployment behavior;
- release artifacts, update channels, signatures, checksums, attestations, or dependency integrity;
- cross-device, transport, remote-access, synchronization, replica, or revocation behavior when that surface is shipped and supported;
- any integration behavior that turns an upstream dependency or provider flaw into an OpenCoven compromise.

## Third-party and unsupported surfaces

A vulnerability that exists solely in an upstream dependency or model-provider API should normally be reported to that maintainer. Also report it privately to OpenCoven when a bundled version, integration default, credential boundary, compatibility layer, or documented workflow materially exposes OpenCoven users.

Experimental, incubating, archived, disabled-by-default, or design-only surfaces are not automatically security-supported. Their repository status and documentation define whether they are accepted as current release behavior. A finding against a design goal is still useful, but it must not be described as a broken shipped guarantee unless an applicable release and executable control establish that guarantee.

## Guarantees versus design goals

OpenCoven separates three kinds of statements:

- **Enforced property:** tied to a named source-adjacent contract, shipped release, and executable verification family.
- **Residual risk or safe-configuration requirement:** a known limitation users and operators must account for.
- **Protocol or product direction:** an intended property that is not yet a current guarantee.

Examples such as universal session isolation, familiar continuity across every model or device, complete sandboxing, immutable-yet-erasable history, full protocol conformance, and enterprise certification are not organization-wide guarantees merely because they are architectural goals. Report suspected violations privately, but identify whether the affected statement is enforced today or remains a design target.

## Public claim boundaries

Unless supported by current evidence for the named surface, OpenCoven does not claim:

- SOC 2, ISO 27001, independent audit, penetration-test, or other certification status;
- absolute containment, safety, privacy, security, or data-sovereignty guarantees;
- universal model, provider, device, transport, or cloud independence;
- complete structural, runtime-authority, continuity, privacy, interoperability, or full conformance;
- guaranteed response times, service levels, hosted availability, or remediation deadlines.

## Policy maintenance

- Update this file when organization-wide reporting, ownership, or claim rules change.
- Repository policies should link here only for cross-repository routing and should remain more precise about their own enforced properties and residual risks.
- Public security pages should link to the applicable policy and avoid copying mutable promises into marketing content.
- Security-policy drift between the organization and canonical repositories should fail review rather than be silently reconciled in downstream copy.

*Last updated: 2026-08-31*
