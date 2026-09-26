# OpenCode MCP Servers — This Laptop

Actual install state and verification, 2026-09-26. This is the machine-specific
record of how the MCP servers defined in
`~/.user_config/home/.config/opencode/opencode.jsonc` were set up on this
laptop. The general reference (agents, permissions, per-agent grants) lives in
[`../AI_DOCs/02-opencode.md`](../AI_DOCs/02-opencode.md).

## Summary

All **10 enabled** MCP servers from `opencode.jsonc` are installed and verified
launching. `llmdoc` is the 11th and remains **disabled** (not installed — see
below). Each server was probed over the MCP stdio protocol (`initialize` +
`tools/list`) and returned a valid result.

| Server | Install channel | Version | Probe result |
|--------|-----------------|---------|--------------|
| `filesystem-mcp` | npm | 2026.8.31 | OK, 14 tools |
| `codegraph` | npm | 1.6.0 | OK, 1 tool |
| `github-mcp` | Go binary | 1.12.2 | OK |
| `playwright` | npm | 0.0.82 (playwright 1.64.0-alpha) | OK, 25 tools |
| `markitdown` | uv tool | 0.0.1a7 | OK, 1 tool |
| `sequential-thinking` | npm | 2026.8.31 | OK, 1 tool |
| `memory-docs` / `memory-3270dev` / `memory-gendev` | npm (one package) | 2026.8.31 | OK, 9 tools |
| `terminal-driver` | npm | 1.5.0 | OK, 18 tools |
| `llmdoc` | — (disabled) | — | not installed |

## Runtime prerequisite: Node

The five Node-based servers are invoked in the config as
`/home/jpfeiff/.local/bin/node <path>`. Node on this machine is **Hermes-managed**
and lives at `~/.hermes/tools/node-26.7.0-linux-x64/bin/` (v26.7.0, npm 11.19.0),
not `~/.hermes/node` as older docs claimed. To satisfy the config's hardcoded
path, shims were created:

```sh
ln -s ~/.hermes/tools/node-26.7.0-linux-x64/bin/{node,npm,npx} ~/.local/bin/
```

`~/.local/bin/node` → the Hermes node binary (same for `npm`, `npx`).

## Install layout

### npm packages → `~/.local/lib/node_modules` + bins in `~/.local/bin`

```sh
npm install -g --prefix ~/.local \
  @modelcontextprotocol/server-filesystem \
  @modelcontextprotocol/server-memory \
  @modelcontextprotocol/server-sequential-thinking \
  @colbymchenry/codegraph \
  terminal-driver-mcp \
  @playwright/mcp
```

This puts packages under `~/.local/lib/node_modules/` (matching the config
paths exactly) and bin shims in `~/.local/bin/`.

### `github-mcp-server` (Go binary)

Downloaded the `Linux_x86_64` tarball from the `github/github-mcp-server`
releases (v1.12.2) and installed the binary to `~/.local/bin/github-mcp-server`.

### `markitdown-mcp` (Python, uv tool)

```sh
uv tool install markitdown-mcp
```

→ `~/.local/bin/markitdown-mcp` (symlink into `~/.local/share/uv/tools/`).

## Symlinks created (bridging name/path mismatches)

| Link | Target | Why |
|------|--------|-----|
| `~/.local/bin/mcp-filesystem-server` | `mcp-server-filesystem` | config uses the short name; npm bin is `mcp-server-filesystem` |
| `~/.local/bin/node` | Hermes node | config hardcodes `~/.local/bin/node` |
| `~/.local/bin/npm` / `npx` | Hermes npm/npx | convenience / parity |

## Memory data files

The three `memory-*` servers are the same `@modelcontextprotocol/server-memory`
package pointed at different `MEMORY_FILE_PATH`s. Created empty:

```sh
~/.local/share/opencode-memory/docs.jsonl
~/.local/share/opencode-memory/3270dev.jsonl
~/.local/share/opencode-memory/gendev.jsonl
```

## Playwright browser

`@playwright/mcp` launches Chromium, so the browser was installed:

```sh
node ~/.local/lib/node_modules/@playwright/mcp/node_modules/playwright/cli.js install chromium
```

→ `~/.cache/ms-playwright/` (`chromium-1246`, `chromium_headless_shell-1246`,
`ffmpeg-1011`). The config runs `--headless --isolated`, so the headless shell
is what gets used.

## Verification

- Probe script sent `initialize` + `tools/list` over stdio to each server and
  read the JSON-RPC responses (see table above). 8/8 distinct binaries OK.
- `terminal-driver-mcp`'s native dep `node-pty@1.1.0` was verified end-to-end
  (loaded + spawned a PTY that returned `hello-from-pty`, exit 0). The npm
  `allow-scripts` warning for `node-pty` is benign: the Linux build uses the
  prebuilt `build/Release/pty.node` shipped in the tarball, not `spawn-helper`.
- `github-mcp-server --version` → `1.12.2`.
- All 10 config paths resolve on disk (only `llmdoc` is absent, by design).

## GitHub auth token — done

`GITHUB_PERSONAL_ACCESS_TOKEN` is set up (2026-09-26) and verified:

- Lives in `~/.user_config/home/.config/opencode/.env` (mode `600`).
- Uses `export GITHUB_PERSONAL_ACCESS_TOKEN=…` — the `export` is required:
  `~/.bashrc:265` sources the file with plain `.`, and a bare `KEY=value` line
  is a shell-local variable that child processes (opencode + its MCP servers)
  do **not** inherit.
- Kept out of git by the root `.gitignore`
  (`home/.config/opencode/.env`); confirmed untracked via `git ls-files` /
  `git check-ignore`.
- Verified end-to-end: `github-mcp-server` `get_me` returns the authenticated
  user (`RedneckTech`). The token is a **fine-grained** PAT (no
  `X-OAuth-Scopes` header), so scopes are per-repository permissions rather
  than classic OAuth scopes.

## Still disabled

- **`llmdoc`** remains `enabled: false` (and is not installed) — history of
  23 GB RSS / OOM-kills during indexing (see
  [`../AI_DOCs/03-llmdoc-pipeline.md`](../AI_DOCs/03-llmdoc-pipeline.md)).
  Re-enabling requires installing it (`uv tool install llmdoc`), adding the
  `llmdoc-serve` systemd unit + `gen-llms-txt.py` sources, flipping `enabled`
  to true, and restoring the per-agent `llmdoc_*` grants.

## Notes / gotchas

- Node's global prefix is Hermes-managed
  (`~/.hermes/tools/node-26.7.0-linux-x64`), so plain `npm install -g` would
  land modules there, not in `~/.local/lib/node_modules`. Always pass
  `--prefix ~/.local` (or keep the shims + prefix consistent).
- The `@playwright/mcp` dependency is an alpha (`playwright 1.64.0-alpha`); the
  browser build it downloads tracks that alpha. A future `@playwright/mcp`
  upgrade may re-download a different Chromium.
