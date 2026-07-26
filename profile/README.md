# OpenCoven

> An open-source, AI-native workspace for building with agents.

[Website](https://opencoven.ai) · [Discord](https://discord.gg/OpenCoven) · [X](https://x.com/OpenCvn)

---

**Your agents, tools, and context — scattered across chats, repos, terminals, and browsers.**

OpenCoven pulls it all into one local-first, hackable workspace where AI agents remember context, use real tools, and work alongside you across every surface.

Less duct-taped scripts. More living workspace.

## Get started

Install the [CLI](https://www.npmjs.com/package/@opencoven/cli):

```bash
npm install -g @opencoven/cli
```

Check your setup (detects harnesses, prints fix hints):

```bash
coven doctor
```

Enter your project and launch:

```bash
cd my-project
coven
```

That's it — you're in. There's no init step: the directory you run from *is* your workspace. On first launch, OpenCoven offers to download the engine (version-pinned, checksum-verified), then drops you into an interactive workspace. Give it a task straight from the prompt:

```bash
coven "fix the failing tests"
```

Prefer explicit control? Run the daemon and target a specific agent:

```bash
coven daemon start
coven run codex "fix the failing tests"
coven run claude "polish this UI"
coven sessions          # browse and inspect sessions
```

## Why builders use it

- 🧠 **Agent-native** — build, run, and coordinate agents in one place
- 🔧 **Real tool access** — connect agents to what they need to actually do the work
- 💻 **Local-first** — your workspace stays close, hackable, and yours
- 🧩 **Extensible** — add skills, integrations, agents, and custom workflows
- 🌐 **Multi-surface** — desktop, web, chat, terminal, and beyond

## Contribute

OpenCoven is early, open, and moving fast — the best time to shape it.

- 🐛 [Open an issue](https://github.com/OpenCoven/coven/issues) — bugs, ideas, feature requests
- 🔀 [Send a PR](https://github.com/OpenCoven/coven/pulls) — start with a [good first issue](https://github.com/OpenCoven/coven/labels/good%20first%20issue)
- 💬 [Join the Discord](https://discord.gg/OpenCoven) — plan features and share what you're building
- 🧩 Build a skill or integration and share it with the Coven

We're building in public with the community. Jump in early and help define what the agentic workspace becomes.

## Community

For builders, tinkerers, researchers, and weird little agent enjoyers.

**Join the Coven** 🌙 · [Website](https://opencoven.ai) · [Discord](https://discord.gg/OpenCoven) · [X](https://x.com/OpenCvn)
