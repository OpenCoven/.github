# Standards and assurance mapping

This mapping helps OpenCoven design future assurance evidence. It does **not** claim certification, attestation, legal compliance, or complete control coverage.

| OpenCoven governance concern | Useful external reference families | Current evidence in this plane | Important gap |
|---|---|---|---|
| Governance, accountability, risk ownership | NIST CSF 2.0 Govern; ISO/IEC 27001/27002 organizational controls; SOC 2 common criteria | Registry, owners/DRIs, lifecycle, controls, ADRs | Independent scope, control ownership separation, operating evidence |
| Secure development | NIST SSDF; OpenSSF Best Practices/Scorecard | Agent policy, risk classes, deterministic checks, dependency/action pinning | Uniform adoption and effectiveness across repositories |
| Supply-chain provenance | SLSA; SPDX; CycloneDX; Sigstore | Contract index, immutable-pin policy, evidence schema | Per-release SBOM/provenance/signing in owning repositories |
| Access and least privilege | NIST CSF Protect; CIS Controls; GitHub security guidance | Administration baseline and issue #6 | Applied org settings, access review, MFA/App evidence |
| Change management and auditability | ISO/IEC 27001 change/configuration controls; SOC 2 change-management criteria | Git history, PR templates, ADRs, exception expiry, generated-view checks | Protected merge/settings evidence and recurring effectiveness tests |
| Incident and vulnerability handling | NIST CSF Respond/Recover; ISO/IEC 27035 concepts | Organization `SECURITY.md`, private-advisory route, recovery policy | Measured response process and tabletop/incident evidence |
| Privacy and data minimization | GDPR/CCPA principles; ISO/IEC 27018 where cloud PII applies | Public/private minimization policy | Processing inventory, legal bases, data-subject procedures, deployment-specific controls |
| AI risk and transparency | NIST AI RMF | Honest claim boundaries and agent authority separation | Deployment-specific measurement, human factors, model/provider controls |
| Cloud security | ISO/IEC 27017 and provider-specific guidance where hosted services exist | Least-privilege/OIDC direction | Cloud-specific shared-responsibility, tenant isolation, logging, key management evidence |

## Interpretation rules

- Standards provide control objectives and vocabulary; they do not prove the implementation satisfies them.
- A public repository check cannot establish SOC 2 or ISO certification.
- Privacy obligations depend on actual processing, roles, jurisdictions, contracts, and deployment behavior.
- AI risk controls supplement rather than replace identity, authorization, software-security, and privacy controls.
- Each assurance claim must name scope, exact release/artifact, environment, evidence period, exceptions, and independent reviewer where applicable.

## Open-source governance and provenance

OpenCoven currently uses MIT licensing, DCO sign-off, patent non-assertion language, and contribution provenance guidance. Before enterprise or foundation transition, obtain qualified legal review of:

- license consistency and third-party notices;
- DCO versus CLA tradeoffs for the intended governance model;
- patent policy and contributor authority;
- trademark/certification-mark rules for conformance claims;
- AI-assisted contribution disclosure and provenance;
- retention of public contribution metadata and security records.
