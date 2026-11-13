# OpenCoven

**A home for your AI familiars.**

OpenCoven builds local-first tools for working with AI agents that have a name, a purpose, memory, and clear boundaries. Our goal is continuity: keeping the familiar and the work yours as models, tools, and sessions change.

[Website](https://opencoven.ai) · [Documentation](https://docs.opencoven.ai) · [Discord](https://discord.gg/opencoven) · [X](https://x.com/OpenCvn)

## Find your starting point

| If you want to… | Start here |
|---|---|
| Run coding agents from your terminal | **[Coven](https://github.com/OpenCoven/coven)** · A Rust runtime for project-scoped sessions with Codex, Claude Code, and GitHub Copilot CLI. |
| Manage familiar conversations, tasks, and agent work | **[Coven Cave](https://github.com/OpenCoven/coven-cave)** · The desktop control room, with a native iOS companion. |
| Just chat with your familiars | **[Coven Chat](https://github.com/OpenCoven/chat)** · A focused desktop app connected to the Coven CLI on your computer. |
| Bring notes, tasks, tools, and terminals into one workspace | **[Open Sesame](https://github.com/OpenCoven/open-sesame)** · A local widget workspace with a macOS companion and PTY/SSH bridge. |

> [!NOTE]
> OpenCoven is in active development. Platform support, installation requirements, and readiness differ by project. Follow each repository's current README and release notes; a preview or source build is not a promise of a finished integration.

## Start with Coven

Install the CLI and check your environment:

```bash
npm install -g @opencoven/cli
coven doctor
```

Then launch a coding session inside your project:

```bash
cd my-project
coven setup codex
coven daemon start
coven run codex "fix the failing tests"
coven sessions
```

The CLI supports macOS, glibc-based Linux x64, and Windows x64. Provider login and harness setup are separate from installing Coven. See the [installation guide](https://docs.opencoven.ai/docs/guide/install).

Prefer an app? Follow the installation instructions for [Cave](https://github.com/OpenCoven/coven-cave#install), [Chat](https://github.com/OpenCoven/chat), or [Open Sesame](https://github.com/OpenCoven/open-sesame). Open Sesame's native host is currently macOS; its browser preview does not provide local machine access.

## What holds it together

- **Identity with continuity.** The [Familiar Contract](https://github.com/OpenCoven/familiar-contract) is a draft open specification for named identity, defined purpose, bounded authority, persistent memory, and a protected relationship with a person.
- **Authority outside the agent.** Coven's local daemon owns session boundaries. [Threads](https://github.com/OpenCoven/coven-threads) supplies protected-authority validation contracts; full conformance remains subject to its documented limits.
- **Visible work.** Project-scoped sessions, durable records, and inspectable activity make agent work easier to follow and steer.
- **Choice of harness.** Coven provides shared session infrastructure rather than replacing every coding tool with a single provider.

Explore the [documentation](https://docs.opencoven.ai), [brand system](https://github.com/OpenCoven/brand), or [full repository collection](https://github.com/orgs/OpenCoven/repositories).

## Build with us

Start with the repository you use. Read its contribution instructions, pick a focused issue, and tell us what you tested.

- [Find good first issues](https://github.com/search?q=org%3AOpenCoven+label%3A%22good+first+issue%22+state%3Aopen&type=issues)
- Read the [contribution guide](https://github.com/OpenCoven/.github/blob/main/CONTRIBUTING.md), including DCO sign-off
- [Join the Discord](https://discord.gg/opencoven) to discuss ideas and share your work
- Report vulnerabilities **privately** through the [security policy](https://github.com/OpenCoven/.github/blob/main/SECURITY.md), not a public issue

Our [code of conduct](https://github.com/OpenCoven/.github/blob/main/CODE_OF_CONDUCT.md) applies across OpenCoven spaces. For help, see [support](https://github.com/OpenCoven/.github/blob/main/SUPPORT.md).
