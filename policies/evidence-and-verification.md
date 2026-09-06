# Evidence and verification policy

## Evidence hierarchy

Strong evidence is source-adjacent, exact, reproducible, and bound to the state being evaluated. Prefer:

1. accepted schemas and normative artifacts;
2. immutable source and dependency revisions;
3. deterministic tests and negative vectors;
4. packed artifact, signed release, or real-daemon results where the boundary requires them;
5. GitHub settings/ruleset/API snapshots for administrative controls;
6. machine-readable receipts with command, environment, result, and provenance.

Narrative summaries, badges, dashboards, and model conclusions are derived evidence and must link to the underlying result.

## Required distinctions

Report independently:

- structural validity;
- repository verification;
- runtime authority behavior;
- continuity behavior;
- privacy behavior;
- interoperability behavior;
- packaged/release artifact verification;
- administrative-control application;
- operational control effectiveness.

Never collapse partial results into a generic “compliant” or “secure” label.

## Control-effectiveness testing

A declared control is effective only when:

- the enforcing mechanism is identified;
- the intended and negative paths are tested;
- bypass and administrator behavior are known;
- the evidence names exact revisions and settings;
- drift is detected on a defined cadence;
- stale, degraded, or unavailable evidence is represented explicitly.

## Evidence packets

Use `schemas/evidence-packet.schema.json`. Evidence packets are append-only review artifacts for a named change. Corrections create a new revision or superseding packet rather than erasing prior evidence.

Do not place secrets, personal data, private prompts, private memories, raw terminal history, or embargoed findings in public evidence.
