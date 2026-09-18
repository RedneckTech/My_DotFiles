# OpenCode

OpenCode is the primary everyday coding agent. It has twelve agents (five
primary, seven subagents) and eleven defined MCP servers (one — `llmdoc` — is
currently disabled; see note below).

## Install & paths

- CLI: `~/.opencode/bin/opencode` (on PATH via `~/.bashrc`)
- Config: `~/.user_config/home/.config/opencode/opencode.jsonc`
  (symlinked to `~/.config/opencode/opencode.jsonc`)
- Agents: `~/.user_config/home/.config/opencode/agents/*.md`
  (symlinked to `~/.config/opencode/agents/`)
- Secrets: `~/.user_config/home/.config/opencode/.env`
  (holds `GITHUB_PERSONAL_ACCESS_TOKEN`, sourced by `~/.bashrc`)
- Skills: `~/.user_config/home/.config/opencode/skills/` (symlinked to
  `~/.config/opencode/skills/`)
- Plugin: `superpowers` (see Skills section)

## MCP servers (from `opencode.jsonc`)

All are `type: "local"` (spawned as child processes).

| Name | Command | Purpose |
|------|---------|---------|
| `filesystem-mcp` | `~/.local/bin/mcp-filesystem-server` with roots `/home/jpfeiff`, `/tmp`, `/media/jpfeiff` | Sandboxed file access |
| `llmdoc` | `~/.local/bin/llmdoc` (env: `LLMDOC_SOURCES`, `LLMDOC_DB_PATH`) | BM25 search over indexed docs — see [LLMDoc](./03-llmdoc-pipeline.md). **Disabled** (`enabled: false`, 2026-09-13) |
| `codegraph` | `node ~/.local/lib/node_modules/@colbymchenry/codegraph/npm-shim.js serve --mcp` | Codebase graph/index |
| `github-mcp` | `~/.local/bin/github-mcp-server stdio` (env: `GITHUB_PERSONAL_ACCESS_TOKEN`) | GitHub PR/issues/repo ops |
| `playwright` | `node ~/.local/lib/node_modules/@playwright/mcp/cli.js --headless --isolated` | Browser automation (headless Chromium) — web testing/scraping |
| `markitdown` | `~/.local/bin/markitdown-mcp` | Converts PDF/DOCX/PPTX/XLSX/images to Markdown |
| `sequential-thinking` | `node ~/.local/lib/node_modules/@modelcontextprotocol/server-sequential-thinking/dist/index.js` | Structured step-by-step reasoning |
| `memory-docs` / `memory-3270dev` / `memory-gendev` | `node ~/.local/lib/node_modules/@modelcontextprotocol/server-memory/dist/index.js` (env: `MEMORY_FILE_PATH`) | Per-agent knowledge-graph memory — one file each under `~/.local/share/opencode-memory/` (`docs.jsonl`, `3270dev.jsonl`, `gendev.jsonl`), scoped to docs/3270DEV/GenDev |
| `terminal-driver` | `node ~/.local/lib/node_modules/terminal-driver-mcp/dist/index.js` | PTY-backed terminal control — drive/test TUIs (vim, htop, gdb, REPLs) via screen snapshot + keystrokes + assert |

### LLMDoc source list (`LLMDOC_SOURCES`)

```
fastapi:http://127.0.0.1:8099/fastapi.llms.txt
python:http://127.0.0.1:8099/python.llms.txt
flask:http://127.0.0.1:8099/flask.llms.txt
bash:http://127.0.0.1:8099/bash.llms.txt
zig:https://ziglang.org/documentation/master/
```

The first four are served locally by `llmdoc-serve.service`; zig is fetched
directly as one server-rendered page.

## Agents

| Agent | Mode | Purpose |
|-------|------|---------|
| `3270DEV` | primary | Drives a live 3270 BBS over x3270 — writes/checks/runs TIMESHARING BASIC and S/360 assembler via ISPF editor, held output, file tools |
| `ispf-editor` | subagent | Uploads local BASIC/assembler source to the BBS and does manual ISPF editor ops (FIND/CHANGE/line commands/save) through a persistent x3270 session |
| `ScriptDev` | primary | Shell script authoring, portability & best practices (temp 0.2) |
| `docs` | primary | Project documentation |
| `web-apps` | primary | Web app dev, modern practices, responsive design |
| `GenDev` | primary | General coding in any language — CLI/TUI/GUI/graphics/web/native; delegates domain-heavy work to `tui`/`gui`/`graphics` |
| `debug` | subagent | Four-phase systematic root-cause debugging |
| `review` | subagent | Code review — correctness/security/quality, structured pass/fail |
| `github` | subagent | GitHub workflows: PRs, issues, repo ops |
| `tui` | subagent | Terminal UIs (ncurses/curses/rich/textual/ratatui) — spawned by GenDev |
| `gui` | subagent | GUIs (tkinter, Qt6, GTK4, web) — spawned by GenDev |
| `graphics` | subagent | Plots/images/2D-3D (matplotlib/Pillow/native GL/GLEW/GLFW/SVG/web) — spawned by GenDev |

### Permission model

- Global: `filesystem-mcp_*`, `llmdoc_*`, `github-mcp_*`, `codegraph_*`,
  `playwright_*`, `markitdown_*`, `sequential-thinking_*`, `memory-docs_*`,
  `memory-3270dev_*`, `memory-gendev_*`, `terminal-driver_*` are all
  **denied** by default — tools opt in per-agent.
- `plan` allows `filesystem-mcp_*` + `codegraph_*`; `build` allows
  `filesystem-mcp_*` + `codegraph_*` + `playwright_*` + `terminal-driver_*`.
- Most agents use `bash: allow`, `edit: allow`, `read: allow`, tool access via
  `webfetch/websearch: allow`, `task: allow`, `skill: allow`.
- `ispf-editor` restricts `external_directory` to `"/media/jpfeiff/BlackBox/3270BBS/**": allow` (everything else asks).
- `docs` uses `bash: ask`.
- Per-agent MCP grants (2026-09-18): `filesystem-mcp_*` → all coding agents
  except `ispf-editor`; `github-mcp_*` → github; `codegraph_*` → GenDev,
  ScriptDev, web-apps, 3270DEV; `playwright_*` → web-apps, gui, GenDev;
  `markitdown_*` → docs, 3270DEV, GenDev; `sequential-thinking_*` → debug,
  review, ScriptDev, 3270DEV, GenDev; `memory-docs_*` → docs,
  `memory-3270dev_*` → 3270DEV, `memory-gendev_*` → GenDev;
  `terminal-driver_*` → tui, GenDev, debug.
- `llmdoc` is parked: `enabled: false` AND its per-agent `llmdoc_*` grants
  were stripped (2026-09-18). Re-enabling it means re-adding the grants.

## Skills

OpenCode auto-discovers `SKILL.md` skills from `~/.config/opencode/skills/`
(also `~/.claude/skills`, `~/.agents/skills`). Installed skill sources:

- **superpowers** (MIT, `obra/superpowers`) — installed as an OpenCode
  *plugin* via the `plugin` array in `opencode.jsonc`; registers 14
  methodology skills (TDD, systematic-debugging, writing-plans,
  requesting/receiving-code-review, git-worktrees, subagent-driven
  development, etc.). Loads on demand via OpenCode's `skill` tool.
- **anthropics/skills** (Apache 2.0) — 15 skills copied into
  `~/.config/opencode/skills/`: mcp-builder, claude-api, brand-guidelines,
  canvas-design, algorithmic-art, web-artifacts-builder, theme-factory,
  slack-gif-creator, internal-comms, academy-guide, discernment-nudge, plus
  docx/pdf/pptx/xlsx (source-available, not OSI-open-source). Four more
  (doc-coauthoring, frontend-design, skill-creator, webapp-testing) live in
  `~/.claude/skills/` only — shared by Claude Code and OpenCode.
- **awesome-agent-skills** (catalog) — cloned to
  `~/.local/share/awesome-agent-skills/` as a *browsable reference*
  (~1500 skills across 70+ team repos), not auto-loaded skills. `git pull`
  to refresh.

## References (pinned docs)

`references.3270manuals` points at the `moshix/3270BBS` repo for:
`basic_manual.md` (TIMESHARING BASIC), `assembler_manual.md` (S/360),
`3270UserGuide.pdf`, `README.md`, `ConfigurationFile_HowTo.md` (tsu.cnf keys).
