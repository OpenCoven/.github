# OpenCoven/.github

Organization profile, community health files, and shared GitHub defaults for [OpenCoven](https://github.com/OpenCoven).

The public organization page is rendered from [`profile/README.md`](profile/README.md). The other files here are **defaults**: GitHub uses them in any OpenCoven repository that does not ship its own copy.

## What lives here

| File | Purpose | Overridden by a repository's own |
|---|---|---|
| [`profile/README.md`](profile/README.md) | Organization landing page and project directory | — |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | DCO sign-off, patent non-assertion, and PR expectations | `CONTRIBUTING.md` |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Community standards and enforcement | `CODE_OF_CONDUCT.md` |
| [`SECURITY.md`](SECURITY.md) | Private vulnerability reporting and claim boundaries | `SECURITY.md` |
| [`SUPPORT.md`](SUPPORT.md) | Where to ask for help | `SUPPORT.md` |
| [`ISSUE_TEMPLATE/`](ISSUE_TEMPLATE) | Bug report and feature request forms | `.github/ISSUE_TEMPLATE/` (replaces the whole set) |
| [`PULL_REQUEST_TEMPLATE.md`](PULL_REQUEST_TEMPLATE.md) | Default pull request checklist | Any PR template |
| [`.github/FUNDING.yml`](.github/FUNDING.yml) | Sponsor button linking [OpenCoven](https://github.com/sponsors/OpenCoven) and [BunsDev](https://github.com/sponsors/BunsDev) on GitHub Sponsors | `.github/FUNDING.yml` |
| [`PATENTS`](PATENTS) · [`PROVENANCE.md`](PROVENANCE.md) | Patent non-assertion pledge and origin record | — |
| [`AGENTS.md`](AGENTS.md) · [`llms.txt`](llms.txt) | Instructions and navigation for coding agents | — |
| [`docs/`](docs) | Organization-level audits and decision records | — |

## Editing

- Keep the profile's project directory in sync with public, non-archived repositories. Take descriptions from each repository's About text and README rather than writing new claims.
- Commands in the profile must match the owning repository's README (for example, `coven` install steps come from [`OpenCoven/coven`](https://github.com/OpenCoven/coven)).
- Security wording follows [`SECURITY.md`](SECURITY.md). Do not add response-time, certification, or guarantee language that the policy does not support.
- Preview Markdown and check every link before merging. Issue forms must be valid YAML; GitHub silently drops an invalid form.

There is nothing to build or install in this repository.
