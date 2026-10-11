---
name: mcp-server-selfhosting
description: Self-host, replace, and wire MCP servers; verify them.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MCP, self-hosted, opencode, servers, config, secrets]
    related_skills: [opencode, github]
---

# Self-hosting MCP servers

Trigger: replacing a hosted/archived/freemium MCP server with a free
self-hosted one, wiring one into a client config (OpenCode), or verifying an
installed server actually works. See `references/server-registry.md` for the
known-good per-server recipes (GitHub, filesystem, CodeGraph, Context7,
LLMDoc).

## Core facts

- The `modelcontextprotocol/servers` reference repo archived 13 of its 20
  servers (GitHub, GitLab, Postgres, Puppeteer, Redis, Brave Search, etc.) to
  `servers-archived`. Most `npx @modelcontextprotocol/server-<x>` snippets in
  the wild are dead. Filesystem, git, memory, fetch, everything,
  sequential-thinking, and time remain active.
- Prefer a prebuilt release binary over Docker/Go when neither runtime is
  installed: fetch the `*_linux_<arch>.tar.gz` asset from the repo's latest
  release, `tar xzf`, then `install -m 755 <bin> ~/.local/bin/<bin>`.
- Confirm arch first (`uname -m`) and read the REAL latest tag from the
  GitHub API (`curl -s …/releases/latest`), never a stale search result.

## Procedure

1. Identify what the current server does and why it needs replacing
   (archived? hosted SaaS? freemium license? a `command` that was never
   filled in).
2. Find a free/open replacement — read the LICENSE. Prefer MIT; a "free for
   personal use" license fails if the user needs commercial use.
3. Install (prebuilt binary > Docker > `go install` > npx/uvx), pinned to
   `~/.local/bin`.
4. Wire it into the client config (OpenCode schema below).
5. Verify it launches and — where auth matters — that the credential works,
   without ever printing the secret.

## OpenCode MCP config (local and remote)

```jsonc
"name": {
  "type": "local",
  "command": ["/home/USER/.local/bin/<bin>", "<subcommand>"],
  "environment": { "TOKEN_VAR": "{env:TOKEN_VAR}" },   // optional
  "enabled": true
}
```
Remote uses `"type": "remote", "url": "…", "headers": {…}`.

- `{env:VAR}` is resolved from the process env at launch; an unset var
  becomes an empty string.
- OpenCode does NOT auto-load `.env` files. Source it from the shell rc
  (`[ -f ~/.config/…/.env ] && . "$…"` appended to `~/.bashrc`) or install a
  dotenv plugin. Put the secret in a `chmod 600` file — never in chat, logs,
  or version control.
- Renaming an MCP entry means updating its permission globs everywhere
  (config `permission` block AND each agent's frontmatter `x_*: allow`).

## Verification

- `timeout 3 <bin> <args>` with no stdin: clean start (exit 0/124, no error
  line) = good; an immediate "failed to access …/no such" = config bug.
- Go MCP servers write JSON-RPC responses to STDERR, not stdout — capture
  stderr when peeking at `initialize`/`tools/list`.
- A stdio MCP server exits on stdin EOF; an `EOF`/`server is closing` error
  after piping handshake messages is a test artifact, not a fault. For auth
  verification, hit the underlying API directly instead.
- Validate a credential without exposing it: report only length and prefix
  (`printf` `${#VAR}` and `${VAR:0:N}`), then a direct REST probe — e.g.
  `curl -H "Authorization: Bearer $TOKEN" https://api.github.com/user` — and
  report the HTTP code + login, never the token.

## Pitfalls

- Don't trust old `@modelcontextprotocol/server-<x>` references; check the
  repo's archived status before installing.
- The unscoped npm package `github-mcp-server` is NOT GitHub's — it is an
  unrelated community repo (jungchihoon). GitHub's own is
  `github/github-mcp-server` (release binaries).
- Filesystem MCP servers that validate the allowlist at startup refuse to
  boot when an allowlisted path is absent (e.g. an unmounted external drive).
- SSH-key git auth does NOT transfer to an API-token MCP server; the PAT must
  be created and stored separately even when `git push` already works.
- An MCP server that needs a per-project index (e.g. `codegraph init`) serves
  empty results until that index is built — the server launching is not the
  same as it being useful.