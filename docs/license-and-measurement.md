# License clarity and adoption measurement

Maintainer reference. Last checked: 2026-11-13. This page records evidence and a measurement procedure; it does not change licenses or enable analytics.

## Read the license in the repository you use

The organization name is not a license grant. Follow the repository's authoritative license files and any applicable file-level notices. This inventory is not a replacement for those terms.

| Project | Evidence checked | Follow-up |
| --- | --- | --- |
| Coven | [LICENSE](https://github.com/OpenCoven/coven/blob/main/LICENSE): MIT | Keep README/package metadata consistent with the license. |
| Coven Cave | [LICENSE](https://github.com/OpenCoven/coven-cave/blob/main/LICENSE): choice of MIT or AGPL-3.0, with linked license texts | GitHub reports `NOASSERTION`; this is not evidence that the license is absent. Preserve the existing dual-license terms. |
| Coven Chat | [LICENSE](https://github.com/OpenCoven/chat/blob/main/LICENSE): MIT | Keep metadata consistent. |
| Open Sesame | No root license file found in the [repository root](https://github.com/OpenCoven/open-sesame); GitHub's license field is empty | Maintainer decision needed: establish and publish the intended authoritative terms. Do not infer MIT from this organization's contribution guide. |
| Coven Threads | [LICENSE](https://github.com/OpenCoven/coven-threads/blob/main/LICENSE): MIT | Keep metadata consistent. |
| Familiar Contract | [LICENSE](https://github.com/OpenCoven/familiar-contract/blob/main/LICENSE): MIT | Keep metadata consistent. |

Before a release, recheck the license files, README license link, package metadata and bundled notices. Resolve discrepancies with maintainers rather than automatically replacing legal text. No license changes are included in this work.

## Measure useful progress without adding product telemetry

Start with a weekly maintainer review of existing aggregate sources. The goal is to learn whether people can discover a project, choose the right entry point, run it, and contribute. These signals are separate observations, not an identified-user conversion funnel.

| Stage | Metric and source | Interpretation |
| --- | --- | --- |
| Discovery | Repository views and referrers from GitHub Insights → Traffic, where available | Interest, not active users. Record the exact observation window. |
| Evaluation | Popular repository content; documentation page totals only if an already-approved analytics source exists | GitHub traffic does not measure the external docs site. Mark docs visits “not measured” until a source is verified. |
| Acquisition | Weekly change in GitHub release-asset `download_count`, separated by release, OS and artifact type | Downloads are not unique installs. Exclude signatures, checksums, receipts, SBOMs and contract bundles from installer totals. |
| First useful result | Voluntary onboarding reports: attempted/succeeded/blocked, product, version, OS and a redacted blocker category | Report success as successes / voluntary attempts, with sample size. It is a biased sample, not a product-wide activation rate. |
| Contribution | Count merged PRs from first-time repository contributors during the week, with bots excluded | Verify previous merged PR history. Public contributor activity is not evidence of product usage. |
| Support friction | Count onboarding-related issues and recurring blocker categories | Use to fix installation/docs, not to score individuals. |

GitHub documents a 14-day traffic window, so a weekly review can capture daily aggregates before they disappear. Do not sum overlapping rolling windows or add daily unique counts and call them weekly unique people. See [GitHub traffic documentation](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-traffic-to-a-repository) and [release asset API fields](https://docs.github.com/en/rest/releases/assets).

### Weekly record

Keep one row per source, project, metric and non-overlapping window:

```csv
window_start_utc,window_end_utc,project,metric,value,unit,source_url,coverage_notes
```

1. Record collection time and the actual source window. Use “not measured” for unavailable data, never zero.
2. Save aggregate counts, not visitor identifiers, IP addresses, raw referrers with query strings, prompts, memories or session logs.
3. For release assets, retain asset IDs and previous cumulative counts so deltas remain comparable. Treat deleted/replaced assets as a break in the series.
4. Record the README, release or onboarding change made that week. Compare subsequent non-overlapping periods without claiming causation.
5. Choose one bottleneck and one small improvement for the next week.

Do not add analytics scripts, tracking pixels, cross-site identifiers, automatic diagnostic uploads or product events as part of this procedure. Any future instrumentation needs a separate reviewed purpose, consent model, data minimization, retention policy and implementation.

## Initial public snapshot

Observed 2026-11-13 via GitHub repository and release APIs. These are point-in-time counters, not adoption rates:

| Repository | Stars | Forks |
| --- | ---: | ---: |
| Coven | 75 | 26 |
| Coven Cave | 32 | 29 |
| Coven Chat | 3 | 0 |
| Open Sesame | 0 | 0 |
| Coven Threads | 2 | 1 |
| Familiar Contract | 8 | 2 |

For [Coven v0.5.0](https://github.com/OpenCoven/coven/releases/tag/v0.5.0), the four platform archives had cumulative counts of Linux x64: 3, macOS arm64: 2, macOS x64: 2, Windows x64: 2. This is **9 archive downloads**, not nine people or successful installations. Other release assets are excluded.

Traffic, external documentation visits, first-run success, and first-time-contributor baselines have not been collected here. No recurring collection job or telemetry was enabled.
