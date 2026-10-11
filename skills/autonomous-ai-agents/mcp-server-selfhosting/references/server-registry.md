# MCP server registry — free self-hosted replacements

Read each LICENSE before adopting; reject "free for personal use" when the
user needs commercial use.

## GitHub API → github/github-mcp-server (official, self-hosted)

- Replaces the archived `@modelcontextprotocol/server-github`.
- Install without Docker/Go: download
  `github-mcp-server_Linux_<arch>.tar.gz` from the repo's latest release,
  extract, `install -m 755 github-mcp-server ~/.local/bin/`.
- Run `github-mcp-server stdio` with env `GITHUB_PERSONAL_ACCESS_TOKEN`
  (a fine-grained PAT). Flags: `--read-only`, `--lockdown-mode`,
  `--toolsets all|default,actions,gists`, `--gh-host <host>`.
- Verify: `GET https://api.github.com/user` with `Authorization: Bearer`
  header → HTTP 200 + the authenticated login.
- The hosted remote (OAuth, api.githubcopilot.com/mcp/) is NOT self-hosted.
- Fine-grained PATs start `github_pat_` and expose no `x-oauth-scopes`
  header; classic PATs start `ghp_`.

## Filesystem → mark3labs/mcp-filesystem-server (MIT)

- Augments/replaces `@modelcontextprotocol/server-filesystem` (still active
  but bare; mark3labs adds symlink-traversal protection, MIME detection,
  path validation, image/binary read).
- Install: `mcp-filesystem-server_Linux_<arch>.tar.gz` from
  mark3labs/mcp-filesystem-server releases → `~/.local/bin`.
- Run `mcp-filesystem-server <allowed-dir> [<more…>]` — allowlist dirs are
  positional args. Validates every dir at STARTUP.

## Code retrieval — jcodemunch → CodeGraph (colbymchenry/codegraph, MIT)

- jcodemunch (pip/uvx) is freemium — free for personal use, not fully open.
- CodeGraph: `npm i -g @colbymchenry/codegraph` → `codegraph` binary. MCP
  server is `codegraph serve --mcp` (get the exact snippet with
  `codegraph install --print-config opencode`).
- Requires `codegraph init` per project to build `.codegraph/` before tools
  return anything; auto-syncs on file changes after.
- PATH-independent config command:
  `["/home/USER/.local/bin/node", "/home/USER/.local/lib/node_modules/@colbymchenry/codegraph/npm-shim.js", "serve", "--mcp"]`
  (the `codegraph` shim is `#!/usr/bin/env node`, so it needs `node` on PATH).
- Lighter alternative: wrale/mcp-server-tree-sitter (MIT, `pip install`)
  — `get_symbols`/`get_ast`/`find_text`/`get_dependencies`/`analyze_complexity`.

## Context7 (up-to-date library docs) → no true self-host drop-in

- Hosted by Upstash at `mcp.context7.com/mcp`; the MCP client is MIT but the
  maintained doc index and parsing engine are server-side and closed — there
  is no self-hosted equivalent (community "context7-local" forks still call
  the hosted backend).
- Self-host answer: LLMDoc (below) — build your own index of whichever docs
  you actually need.

## Library docs (self-built) → LLMDoc

- llmdoc is a self-hosted docs-indexing MCP server: it ingests docs pages,
  converts them to markdown, chunks them, stores them in a **DuckDB**
  database, and exposes BM25 search to the client. It is the working
  self-host replacement for Context7's closed backend.
- Install via `uv tool install llmdoc` → `~/.local/bin/llmdoc`; wire as a
  `type: "local"` OpenCode MCP server running `llmdoc` (stdio).
- Configure sources as `name:URL` pairs in the `LLMDOC_SOURCES` env var and
  the database path in `LLMDOC_DB_PATH`. A URL may be a `.llms.txt` index
  file or a single docs-page URL.
- It fetches sources over its OWN HTTP layer, NOT stdio — so `.llms.txt`
  index files must be reachable over HTTP. Serve them from a local static
  server (`python3 -m http.server 8099 --bind 127.0.0.1 --directory <dir>`,
  ideally as a systemd user unit) and point `LLMDOC_SOURCES` at
  `http://127.0.0.1:8099/<name>.llms.txt`.
- Pitfalls:
  - The index is DuckDB, not SQLite — open/inspect it with `duckdb`, never
    `sqlite3` (which reports "file is not a database").
  - Some docs sites (e.g. Zig's language reference) are ONE server-rendered
    page with no crawlable per-page URLs; a sitemap crawl yields nothing.
    Point LLMDoc at the page URL directly — it indexes the whole thing as a
    single (properly chunked) document and stays searchable.
  - The stdio MCP refresh path can hang/fail; rebuild the index directly with
    the tool's venv Python (`…/uv/tools/llmdoc/bin/python` calling its refresh
    entry point) rather than round-tripping through the MCP client.

## Still-active reference servers (npm, no Docker)

The `modelcontextprotocol/servers` repo keeps these active: fetch, filesystem,
git, memory, sequential-thinking, time (everything else moved to
servers-archived). Install via `npm i -g @modelcontextprotocol/server-<x>`.
Their bins are `#!/usr/bin/env node` shims — wire them as explicit
`["/home/USER/.local/bin/node", "/home/USER/.local/lib/node_modules/@modelcontextprotocol/server-<x>/dist/index.js"]`
instead of relying on PATH, matching the codegraph convention.

- **memory** writes `memory.jsonl` to its OWN package dir by default — pin it
  with env `MEMORY_FILE_PATH` (e.g. `~/.local/share/opencode-memory/memory.jsonl`)
  or every project dir gets littered. Verify it starts: `server running on stdio`.
- **sequential-thinking** is stateless — no path/env config needed.

## Browser automation → @playwright/mcp (Microsoft, Apache-2.0)

- `npm i -g @playwright/mcp` → bin `playwright-mcp` (shim → `cli.js`).
- Needs a browser: `cd ~/.local/lib/node_modules/@playwright/mcp && npx playwright install chromium`
  (~190 MB Chromium + ~115 MB headless shell into `~/.cache/ms-playwright`).
  Smoke-test system deps with a one-liner `chromium.launch({headless:true})`
  + `page.goto('https://example.com')` before declaring it ready.
- Run headed BY DEFAULT; pass `--headless` and `--isolated` (don't persist the
  profile) for a coding-agent install.

## Document→Markdown → markitdown-mcp (Microsoft, MIT)

- `uv tool install markitdown-mcp` → `~/.local/bin/markitdown-mcp`. Stdio by
  default; `--http`/`--sse` for network transports. Converts PDF/DOCX/PPTX/
  XLSX/images/audio to Markdown for the model. Good pairing for a docs agent.

## TUI automation → terminal-driver-mcp (funkyfunc, MIT)

The "Playwright for TUIs": PTY-backed (node-pty) + headless xterm, so an agent
gets a clean 2D text screen, sends keystrokes, waits/asserts on state, holds
persistent sessions, and records to asciinema `.cast` replayable as regression
tests.

- `npm i -g --allow-scripts=terminal-driver-mcp,node-pty terminal-driver-mcp`.
  The `--allow-scripts` flag is REQUIRED: node-pty has no Linux prebuild, so
  its install script must run `node-gyp rebuild` to compile `build/Release/pty.node`
  (needs a C++ toolchain). Without it the server starts but PTY spawn fails.
- Verify native pty actually works (not just "server started"):
  `node -e "const p=require('node-pty').spawn('bash',['-c','echo ok'],{});p.onData(d=>console.log(d))"`
  from the package dir. Then confirm the tool surface via stdio
  `initialize` + `tools/list` (session_create/read/write/wait/assert/click/screenshot).
- Wire as `["/home/USER/.local/bin/node", "…/terminal-driver-mcp/dist/index.js"]`.
- Session state is in-memory: survives tool calls, dies on server restart.
