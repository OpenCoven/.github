# Contributing to OpenCoven

Thank you for your interest in contributing. OpenCoven is MIT licensed and community-driven. We want contributing to be easy, open, and safe for everyone.

## Developer Certificate of Origin (DCO)

OpenCoven uses the **Developer Certificate of Origin (DCO) v1.1** for all contributions. This is a lightweight mechanism — not a CLA — that asks you to certify that you have the right to submit what you're submitting.

By making a contribution to this project, you certify that:

> (a) The contribution was created in whole or in part by you and you have the right to submit it under the open source license indicated in the file; or
>
> (b) The contribution is based upon previous work that, to the best of your knowledge, is covered under an appropriate open source license and you have the right under that license to submit that work with modifications, whether created in whole or in part by you, under the same open source license (unless you are permitted to submit under a different license), as indicated in the file; or
>
> (c) The contribution was provided directly to you by some other person who certified (a), (b) or (c) and you have not modified it.
>
> (d) You understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information you submit with it, including your sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.

### How to Sign Off

Add a `Signed-off-by` line to your commit message:

```
git commit -s -m "Your commit message"
```

This produces:

```
Your commit message

Signed-off-by: Your Name <your.email@example.com>
```

### Patent Non-Assertion

By contributing, you additionally agree not to assert any patent claims — now held or later acquired — against this project or its users that arise from your contribution. See [PATENTS](./PATENTS) for the full non-assertion pledge.

## What we're looking for

- Bug fixes and reliability improvements
- Documentation and example improvements
- New skills, tools, and integrations
- Performance improvements
- Community-requested features

## What we're not

OpenCoven is not a contribution vehicle for proprietary forks. If you are building a closed-source derivative of OpenCoven's architecture, please do not use contribution as a means to learn implementation details that are not yet public. We welcome genuine collaborators.

## Getting started

1. **Read the repository's own guide.** A repository's `CONTRIBUTING.md`, `AGENTS.md`, and PR template take precedence over this default.
2. **Start from an issue for larger changes.** Small fixes can go straight to a PR; for new features or behavior changes, open or comment on an issue first so maintainers can confirm the direction.
3. **Fork and branch:** `git checkout -b fix/short-description`.
4. **Make focused, signed-off commits:** `git commit -s`. One concern per PR.
5. **Verify.** Run the repository's documented build, lint, and test commands, and list the exact commands and results in the PR.
6. **Open a pull request** with a clear description, linked issue, and screenshots for UI changes.

## Agent-assisted contributions

OpenCoven is built for working with agents, and agent-assisted contributions are welcome. You remain the author:

- review and understand every line you submit, and sign off only on work you can certify under the DCO;
- say in the PR when an agent wrote a substantial part of the change;
- do not submit bulk or automated PRs, issues, or comments without a maintainer's agreement;
- never paste real credentials, prompts, memories, or private session data into fixtures, logs, or screenshots.

## Community standards

Participation in OpenCoven spaces is covered by the [Code of Conduct](./CODE_OF_CONDUCT.md). Report security vulnerabilities privately as described in [SECURITY.md](./SECURITY.md), never in a public issue.

## Questions?

See [SUPPORT.md](./SUPPORT.md), or join the Discord: https://discord.gg/opencoven
