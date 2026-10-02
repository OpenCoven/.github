# OpenCoven

> Open-source, local-first infrastructure for AI familiars: named agents with their own lanes, memory, and authority boundaries, working beside you on real projects.

[Website](https://opencoven.ai) · [Docs](https://docs.opencoven.ai) · [Discord](https://discord.gg/opencoven) · [X](https://x.com/OpenCvn) · [Feedback](https://feedback.opencoven.ai)

---

**Your agents, tools, and context are scattered across chats, repos, terminals, and browsers.**

OpenCoven gives them one local-first, hackable home. Coding harnesses run inside explicit project boundaries, every session is visible and durable, and familiars keep their identity and memory across the work.

Less duct-taped scripts. More living workspace.

## Get started

### Run agent sessions from your terminal

Install the [Coven CLI](https://www.npmjs.com/package/@opencoven/cli) (macOS, Linux x64, Windows x64):

```bash
npm install -g @opencoven/cli
coven doctor            # detects harnesses and prints fix hints
```

Launch work inside a project:

```bash
cd my-project
coven setup codex       # provider-owned login
coven daemon start
coven run codex "fix the failing tests"
coven sessions          # browse and inspect sessions
```

Bare `coven` opens the interactive UI. Claude Code, GitHub Copilot CLI, and other harnesses plug into the same daemon. See the [getting started guide](https://docs.opencoven.ai/docs/guide/getting-started).

### Install the desktop apps (macOS)

```bash
brew install --cask opencoven/tap/coven-cave   # Coven Cave control room
brew install --cask opencoven/tap/wand         # Wand
```

Coven Cave builds for macOS, Windows, and Linux are on its [releases page](https://github.com/OpenCoven/coven-cave/releases/latest).

## Projects

> [!NOTE]
> OpenCoven is early. Each repository's README states its own status, platform support, and limits. Experimental and legacy projects are labeled below.

**Runtime and protocol**

| Repository | What it is |
|---|---|
| [coven](https://github.com/OpenCoven/coven) | Local-first Rust runtime for project-scoped coding-agent sessions: durable state, authority boundaries, and multi-harness support. Ships the `coven` CLI. |
| [familiar-contract](https://github.com/OpenCoven/familiar-contract) | Open specification for portable agent identity, authority, memory, and self-governance boundaries. |
| [coven-threads](https://github.com/OpenCoven/coven-threads) | Authority and governance layer for protected familiar identity, memory, and write surfaces. |
| [psyche](https://github.com/OpenCoven/psyche) | Familiar runtime and orchestration protocol for persistent AI identities. |
| [coven-runtimes](https://github.com/OpenCoven/coven-runtimes) | Runtime SDK, conformance toolkit, and registry for integrating agent runtimes. |
| [sdk](https://github.com/OpenCoven/sdk) | Experimental TypeScript SDK and CLI for clients, transports, and shared protocol types. |

**Apps**

| Repository | What it is |
|---|---|
| [coven-cave](https://github.com/OpenCoven/coven-cave) | Desktop control room for familiars, agent sessions, memory, workflows, and GitHub triage. |
| [psyche-build](https://github.com/OpenCoven/psyche-build) | Desktop cockpit for running parallel coding agents in visible, isolated workspaces. |
| [coven-code](https://github.com/OpenCoven/coven-code) | Multi-provider AI coding-agent TUI in Rust. |
| [chat](https://github.com/OpenCoven/chat) | Early desktop scaffold for OpenCoven Chat with least-privilege Tauri boundaries. |
| [cauldron](https://github.com/OpenCoven/cauldron) | Clean-room kernel for Covenstead, the desktop where you watch your familiars work. |
| [coven-memory](https://github.com/OpenCoven/coven-memory) | Browser and iOS client for inspecting familiar memory through Coven's read APIs. |
| [coven-pocket](https://github.com/OpenCoven/coven-pocket) | Local-first iOS coding agent powered by Coven Code. |
| [wand-releases](https://github.com/OpenCoven/wand-releases) | Signed, notarized macOS builds of Wand. |

**Tools and integrations**

| Repository | What it is |
|---|---|
| [coven-reach](https://github.com/OpenCoven/coven-reach) · [coven-scout](https://github.com/OpenCoven/coven-scout) | Rust MCP servers for filesystem and web operations. |
| [desktop-use](https://github.com/OpenCoven/desktop-use) | Computer-use adapter for agents and desktop automation. |
| [coven-github-webhook](https://github.com/OpenCoven/coven-github-webhook) | Hosted webhook service for the OpenCoven GitHub App. |
| [homebrew-tap](https://github.com/OpenCoven/homebrew-tap) | Homebrew casks for OpenCoven desktop apps. |

**Docs, brand, and design**

| Repository | What it is |
|---|---|
| [coven-docs](https://github.com/OpenCoven/coven-docs) | Source for [docs.opencoven.ai](https://docs.opencoven.ai). |
| [coven-landing](https://github.com/OpenCoven/coven-landing) | Source for [opencoven.ai](https://opencoven.ai). |
| [brand](https://github.com/OpenCoven/brand) | Canonical visual identity, voice, and public-web brand profile. |
| [ui](https://github.com/OpenCoven/ui) | Reference interface components and UI explorations. |

**Research, experiments, and legacy:** [open-fable](https://github.com/OpenCoven/open-fable) (recurrent-depth transformer research) · [coven-codeflow](https://github.com/OpenCoven/coven-codeflow) (experimental workflow CLI) · [demo-workspace](https://github.com/OpenCoven/demo-workspace) (synthetic demo data) · [claude-code-cast](https://github.com/OpenCoven/claude-code-cast) (legacy) · [coven-design-system](https://github.com/OpenCoven/coven-design-system) (being folded into `brand` and `ui`)

## Why builders use it

- 🧠 **Familiar-native**: named agents with lanes, memory, and boundaries, not interchangeable task runners
- 🔒 **Explicit authority**: the local daemon owns project boundaries; clients are convenience layers
- 💻 **Local-first**: your workspace stays close, inspectable, and yours
- 🧩 **Any harness**: Codex, Claude Code, Copilot CLI, and future adapters share one substrate
- 🌐 **Multi-surface**: terminal, desktop, mobile, chat, and GitHub

## Contribute

OpenCoven is early, open, and moving fast. This is the best time to shape it.

- 🐛 Open an issue in the repository you're using. Not sure which one? Start with [coven](https://github.com/OpenCoven/coven/issues).
- 🔀 Send a PR. Look for [good first issues](https://github.com/search?q=org%3AOpenCoven+label%3A%22good+first+issue%22+state%3Aopen&type=issues), and read the [contribution guide](https://github.com/OpenCoven/.github/blob/main/CONTRIBUTING.md) first (commits need a DCO sign-off).
- 💬 [Join the Discord](https://discord.gg/opencoven) to plan features and share what you're building.
- 🔐 Found a vulnerability? Report it privately as described in the [security policy](https://github.com/OpenCoven/.github/blob/main/SECURITY.md), not in a public issue.

Everyone in OpenCoven spaces follows the [code of conduct](https://github.com/OpenCoven/.github/blob/main/CODE_OF_CONDUCT.md). For help, see [support](https://github.com/OpenCoven/.github/blob/main/SUPPORT.md).

## Community

For builders, tinkerers, researchers, and weird little agent enjoyers.

**Join the Coven** 🌙 · [Website](https://opencoven.ai) · [Discord](https://discord.gg/opencoven) · [X](https://x.com/OpenCvn)
