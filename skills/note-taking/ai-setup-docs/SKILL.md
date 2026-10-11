---
name: ai-setup-docs
description: Use when updating AI setup docs in ~/.user_config/sys_docs/AI_DOCs/.
version: 1.0.0
author: Jacob Pfeiff (RedneckTech)
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Documentation, Dotfiles, OpenCode, LLMDoc, Hermes, AI Setup]
    related_skills: []
---

# AI Setup Documentation

The user's entire AI/LLM tooling stack is documented as markdown in
`~/.user_config/sys_docs/AI_DOCs/` (live in the git repo `~/.user_config/`,
NOT under `~/.user_config/home/`). After ANY change to the AI setup (configs, agents,
skills, MCP servers, pipelines, cron), update the relevant doc before finishing
the task. The convention is recorded in persistent memory.

## Doc files

- `README.md` — master index (tool table + "symlink into git repo" primer)
- `01-dotfiles-config-management.md` — `.user_config` repo, symlink map, .bashrc wiring, secrets rules
- `02-opencode.md` — MCP servers, agents, permission model, references
- `03-llmdoc-pipeline.md` — gen-llms-txt.py -> systemd serve -> MCP -> DuckDB index
- `04-hermes-agent.md` — config.yaml, model, skills catalog, active secrets
- `05-claude-code.md` — skills (now symlinked into the repo)
- `06-codex.md` — config.toml, trusted projects

## Architecture facts (get these right)

- Source of truth is the git repo `~/.user_config/` (remote
  `git@github.com:RedneckTech/My_DotFiles.git`, branch `master`).
- Live configs are SYMLINKS into that repo (not copies): `~/.bashrc`,
  `~/.config/starship.toml`, `~/.hermes/config.yaml`, `~/.hermes/SOUL.md`,
  `~/.config/opencode/{opencode.jsonc,package.json,agents/*.md}`,
  `~/.claude/skills`.
- OpenCode secrets: `~/.user_config/home/.config/opencode/.env` (sourced by
  `~/.bashrc` line ~265). Hermes secrets: `~/.hermes/.env`.
- LLMDoc active index is DuckDB at `~/.local/share/llmdoc/index.db` (NOT
  sqlite3; there is no `~/.llmdoc` anymore — it was stale and removed).
- LLMDoc `.llms.txt` sources served by systemd user unit `llmdoc-serve.service`
  at `127.0.0.1:8099` from `~/.local/share/llmdoc/sources/`.

## Re-scan when changes happen

Run these to rediscover the live state before editing docs:

```bash
# OpenCode config + agents
cat ~/.user_config/home/.config/opencode/opencode.jsonc
ls ~/.user_config/home/.config/opencode/agents/

# Hermes
cat ~/.user_config/home/.hermes/config.yaml

# Codex / Claude
cat ~/.codex/config.toml
ls ~/.claude/skills

# LLMDoc index stats (DuckDB)
~/.local/share/uv/tools/llmdoc/bin/python -c "
import duckdb
c=duckdb.connect('/home/jpfeiff/.local/share/llmdoc/index.db', read_only=True)
for r in c.execute('''select d.source_name,count(c.id) from documents d left join chunks c on c.doc_id=d.id group by 1 order by 2 desc''').fetchall():
    print(r)"

# symlinks (keep the map current)
find ~ -maxdepth 2 -type l 2>/dev/null | while read l; do t=$(readlink "$l"); case "$t" in *user_config*) echo "$l -> $t";; esac; done
```

## Hard rules

- NEVER copy a secret value into docs. Reference keys by NAME only
  (e.g. `GITHUB_PERSONAL_ACCESS_TOKEN`), redact values with `<redacted>`.
- Ground every claim in actual file reads — do not document from memory
  or guess. Re-read configs after changes.
- Keep the README's tool table and per-tool docs consistent when tools
  are added/removed.
