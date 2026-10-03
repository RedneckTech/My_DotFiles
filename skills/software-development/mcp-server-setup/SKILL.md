---
name: mcp-server-setup
description: Use when installing, wiring, or verifying MCP servers.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mcp, opencode, claude-code, codex, tooling, stdio]
    related_skills: [opencode, claude-code, codex]
---

# MCP Server Setup & Verification

## When to Use

- A config (`opencode.jsonc`, `claude_desktop_config.json`, `.mcp.json`) lists
  MCP servers whose binaries/packages are not yet on the machine.
- A previously installed MCP server stopped launching and needs a stdio check.
- You need to confirm "installed" actually means "starts and lists tools".

Turn an MCP server config (e.g. the `mcp` block in `opencode.jsonc`) into
working servers on a machine, then verify each one actually launches.

## 1. Extract hard requirements from the config

Read the config's `mcp` block. For each server, note the exact `command` array
(absolute binary paths + args) and any `environment` block. Every absolute path
in the config is a hard requirement: setup is done only when each path resolves
on disk. Run a path-resolution check over every config path before declaring
success.

## 2. Confirm package/bin names before installing

- npm: `npm view <pkg> name version bin` — confirms the package exists and the
  `bin` name it ships, which may differ from the name used in the config.
- PyPI: `uv tool install <pkg>` then check which binary lands in `~/.local/bin`;
  or `curl -s https://pypi.org/pypi/<pkg>/json` for entry points.
- Go/compiled servers (github-mcp-server): get version + Linux tarball from
  GitHub releases.

## 3. Install into the location the config hardcodes

- npm: `npm install -g --prefix ~/.local <pkg...>`. Pitfall: plain
  `npm install -g` installs into the active node's own global prefix (here
  Hermes-managed `~/.hermes/tools/node-*/...`), NOT `~/.local`. Always pass
  `--prefix` to match the config's `~/.local/lib/node_modules` paths.
- Python: `uv tool install <pkg>` → binary in `~/.local/bin`.
- Go: download the release tarball, `install -m 0755 <bin> ~/.local/bin/`.

## 4. Bridge name/path mismatches with symlinks

- Config names the binary differently than the package ships (e.g. config
  `mcp-filesystem-server` vs npm bin `mcp-server-filesystem`) →
  `ln -s <real> ~/.local/bin/<config-name>`.
- Config hardcodes a runtime path that does not exist (e.g. `~/.local/bin/node`
  when node lives in a versioned Hermes tools dir) → create a shim symlink to
  the real binary.

## 5. Verify every server over stdio — "installed" is not "working"

MCP stdio transport is newline-delimited JSON. Send `initialize` then
`tools/list` and read the JSON-RPC responses. Run
`scripts/mcp_probe.py -- CMD [ARG...]` (keeps stdin open, reads incrementally).

Pitfalls:
- Go-compiled servers (github-mcp-server) start slowly. A probe that writes the
  requests and immediately closes stdin reports a false FAIL
  ("server is closing: EOF"). Keep stdin open and read with a timeout.
- `npm install -g` may warn install scripts were blocked (`allow-scripts`). For
  native deps (node-pty) verify the actual `.node` binary loads AND spawns
  before concluding it is broken — Linux builds usually ship a prebuilt
  `build/Release/*.node` that needs no install script.
- Playwright MCP starts fine without a browser but its tools fail at call time.
  Install the browser separately:
  `node <pkg>/node_modules/playwright/cli.js install chromium`
  → `~/.cache/ms-playwright`.

## 6. Secrets are a manual step — never fabricate

Configs reference env vars (e.g. `{env:GITHUB_PERSONAL_ACCESS_TOKEN}`) sourced
from a `.env` that does not travel with the repo. The server installs and starts
without it; only auth'd calls fail. Create the `.env` only with a value the user
provides, otherwise record it as a remaining manual step.

When the user does provide the value, three pitfalls:

- **`export` is required when the `.env` is `source`d.** If the shell sources the
  file with plain `.` (common: a `[ -f ... ] && . ...` line in `.bashrc`), a bare
  `KEY=value` line is a shell-local variable that child processes — the agent AND
  the MCP servers it spawns — do NOT inherit. Write `export KEY=value`. Verify
  with a round-trip through a child process (`bash -c '. <file> && python3 -c
  "import os;print(os.environ.get("KEY"))"'`), not just `echo $KEY`, which only
  proves the shell-local copy exists.

- **"gitignored" is verified, not assumed.** Before writing the secret, run
  `git check-ignore -v <path>` — a fresh dotfiles repo often does NOT ignore
  `.env`. If it is missing, add it to the repo's `.gitignore`, `chmod 600` the
  file, then confirm `git ls-files <path>` is empty (never tracked) and
  `git status` does not list it.

- **GitHub token scopes.** `github-mcp-server` needs at minimum `repo` (classic
  PAT) or Contents/PRs/Issues write + Metadata read (fine-grained). `read:org`
  is for org/team tools, `read:packages` only for pulling the Docker image. A
  fine-grained PAT returns no `X-OAuth-Scopes` header — its absence (not the
  token shape) is how you tell the two apart.

## 7. Document the result in the user's sys_docs

Machine-specific setup goes in `sys_docs/laptop_docs/` as numbered
`<NN>-<topic>.md` files plus a `README.md` index, matching the existing markdown
style (tables for paths/versions). Record actual versions, install channel,
symlinks created, probe results, and remaining manual steps — the machine's
real state, not the reference state described in the general
`workstation_docs`/`AI_DOCs`.
