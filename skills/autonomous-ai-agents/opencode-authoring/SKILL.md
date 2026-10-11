---
name: opencode-authoring
description: "Author OpenCode agent .md files and MCP server config."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [opencode, agents, mcp, config, self-hosted]
    related_skills: [opencode, hermes-agent-skill-authoring]
---

# OpenCode Authoring (agents + MCP)

Authoring this user's OpenCode agent definition files and MCP server config.
Covers the frontmatter shape, body conventions, subagent handoffs, and which
MCP servers are dead vs. self-hostable.

## Locations (non-standard — do not assume)

- Agents: `~/.user_config/home/.config/opencode/agents/*.md`
- Config: `~/.user_config/home/.config/opencode/opencode.jsonc`

The `.user_config/home/.config/opencode/` prefix is this user's actual
OpenCode home. The standard `~/.config/opencode/` is NOT where these live on
this box — always confirm before writing.

## Agent file shape

YAML frontmatter: `description` (one line), `mode` (`primary` or `subagent`),
optional `temperature` (e.g. `0.2` for deterministic agents), and a
`permission` block.

Permission keys in use: `bash`, `edit`, `read` (each `allow`/`ask`),
`external_directory` (`ask`, or a path-scoped object
`{"*": "ask", "/path/**": "allow"}`), `webfetch`, `websearch`, `task`,
`skill`, and MCP wildcards `github-mcp_*`, `context7_*`, `filesystem-mcp_*`,
`jcodemunch-mcp_*`.

- Primary agents: `mode: primary` and `task: allow` (so they can spawn
  subagents).
- Subagents: `mode: subagent`; `edit` is `allow` when they fix code
  (review/debug) or `ask` when they should not mutate unilaterally.

## Body conventions (this user's standard)

Model the body on the user's own `3270DEV` agent — a dense,
environment-grounded operating manual, never a one-line stub. Standard
section order: Environment facts -> stack/coding rules -> workflow for every
task -> pitfalls -> numbered imperative rules.

- VERIFY environment facts before writing, don't assume: check installed
  tooling and versions with `terminal` (`command -v shellcheck; uv --version;
  node --version`) and label anything installable-but-absent as such. Do not
  ship commands for tools that aren't there.
- Ground tooling to what the box actually has at the time (this box
  historically: shellcheck + shfmt, uv, python 3.14, node 26, dash as
  `/bin/sh`; ruff/pytest/frameworks via uv; no `gh`, no docker, no go).
- Subagent handoffs: add a `## Handoff subagents` section to primary agents
  wiring them to the review/debug (or other) subagents "via task" — the
  house phrase is "spawn the `NAME` subagent (via task)". Scope the handoff
  to what actually applies; review's lint/security gates don't transfer to
  non-shell languages, say so rather than mis-wiring.
- Never hardcode a single repo in a GitHub-facing agent. Derive `OWNER/REPO`
  from `git remote get-url origin` and stop-and-ask when there is no
  `origin`.
- Keep new agents language/stack-agnostic where a class exists (review,
  debug) so shell, Python, and other primaries can all spawn them.

## MCP config

Local: `{"type": "local", "command": ["..."], "environment": {...},
"enabled": true}`. Remote: `{"type": "remote", "url": "...", "headers":
{...}}`. Secret interpolation is `"{env:VAR_NAME}"` inside values. The
local env-var key is `environment` (object), NOT `env`.

See `references/mcp-self-hosted.md` for which reference servers are dead and
the free self-hosted replacements.

## Pitfalls

- `@modelcontextprotocol/server-*` packages for archived reference servers
  are dead — 13 of them (GitHub, GitLab, Postgres, Puppeteer, Brave Search,
  Slack, Redis, Sentry, etc.) were archived into `servers-archived` and their
  npm packages marked "no longer supported". Verify a server is still
  maintained before writing an npx command for it.
- The unscoped npm package `github-mcp-server` is an UNRELATED community
  repo (jungchihoon), not GitHub's official server. The official one is
  `github/github-mcp-server`, which publishes prebuilt binaries (no
  Docker/Go/dependency build) — download the release tarball and run
  `github-mcp-server stdio` with `GITHUB_PERSONAL_ACCESS_TOKEN` set.
