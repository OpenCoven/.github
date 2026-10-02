# Exceptions and temporary waivers

Exceptions are a controlled escape hatch, not a parallel policy system.

Every exception must be recorded in `governance/exceptions.json` and include:

- unique identifier and affected control;
- narrow scope and exact repositories/paths where public;
- owner and approving authority;
- rationale and risk assessment;
- compensating controls;
- creation and expiry dates;
- required remediation and verification;
- status: `proposed`, `active`, `expired`, `closed`, or `revoked`.

Rules:

1. No exception may grant familiar identity, protected mutation, runtime, release, publication, or organization-administration authority.
2. R4 exceptions require protected-owner review and an explicit, operation-specific authorization path.
3. An active exception must expire within 90 days unless a stricter control applies.
4. Expired active exceptions fail CI.
5. An exception cannot suppress evidence of drift; it may only explain a reviewed and bounded deviation.
6. Closing an exception requires evidence that the control is restored or the policy was superseded through an ADR.
