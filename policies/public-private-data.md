# Public and private governance data

`OpenCoven/.github` is public. Public transparency is useful only when it does not disclose private inventory, security material, personal data, or operational secrets.

## Public data allowed here

- public repository names and observed public GitHub metadata;
- public canonical-domain ownership, lifecycle, risk class, and disposition;
- public cross-repository initiatives and non-sensitive dependency relationships;
- organization policies, schemas, reusable read-only workflows, and generated views;
- public GitHub identities serving as owners or DRIs;
- links to public issues, pull requests, releases, and evidence.

## Data prohibited here

- private repository names or confidential product codenames unless separately approved for publication;
- credentials, tokens, secret values, recovery material, private endpoints, or internal network detail;
- non-public vulnerability reports, exploit detail, embargo status, or incident evidence;
- prompts, memories, conversation transcripts, terminal logs, private file paths, session identifiers, or user data;
- private contractual, commercial, employment, legal, partnership, or financial records;
- unnecessary personal information, contact data, behavioral profiles, or contributor metadata.

## Private federation

Private repositories should carry repository-local `agent/manifest.json` records conforming to the public schema. Access-controlled Projects or a future approved private projection may aggregate those manifests.

A public initiative may use an opaque reference such as `private-overlay: github-delivery` to acknowledge a private workstream. It must not reveal the backing repository, members, incidents, or implementation details.

## Privacy principles

- Minimize collected data and fields.
- Use stable public GitHub identities only where accountability requires them.
- Avoid copying issue or commit personal data into derived governance records.
- Retain accepted decisions and contribution history as public open-source records, but expire temporary exceptions and operational details.
- Never claim GDPR, CCPA, ISO, SOC 2, or another compliance status based solely on this policy.
