# AI Setup — Master Index

Jacob Pfeiff's AI/LLM tooling, documented as of 2026-09-18.

This directory describes every AI agent, MCP server, config, and pipeline on the
machine — where it lives, what it does, and how the pieces connect.

## Tools at a glance

| Tool | Role | Config location | Doc |
|------|------|-----------------|-----|
| OpenCode | Main coding agent (12 agents, 11 MCP servers) | `~/.user_config/home/.config/opencode/` | [opencode](./02-opencode.md) |
| LLMDoc | Self-hosted docs indexing/RAG pipeline (BM25 over DuckDB) | `~/.local/share/llmdoc/` | [llmdoc](./03-llmdoc-pipeline.md) |
| Hermes Agent | Nous Research personal agent (this one) | `~/.hermes/` (symlinked) | [hermes](./04-hermes-agent.md) |
| Claude Code | Coding agent (skills only) | `~/.claude/` | [claude](./05-claude-code.md) |
| OpenAI Codex | Coding agent | `~/.codex/` | [codex](./06-codex.md) |
| Dotfiles repo | Source of truth for all the above | `~/.user_config/` (git) | [dotfiles](./01-dotfiles-config-management.md) |

## The one thing to understand first

Almost every config you touch is actually a symlink into a git repo at
`~/.user_config/` (remote: `git@github.com:RedneckTech/My_DotFiles.git`). Edit the
file in `.user_config`, not the symlink target, or your change won't survive a
sync. See [01-dotfiles-config-management.md](./01-dotfiles-config-management.md).

## Quick reference

- OpenCode config + agents: `~/.user_config/home/.config/opencode/` (symlinked to
  `~/.config/opencode/`)
- OpenCode secrets: `~/.user_config/home/.config/opencode/.env` (sourced by
  `~/.bashrc`, kept out of git via `.gitignore`)
- LLMDoc docs sources served at `http://127.0.0.1:8099/` by a systemd user unit
- LLMDoc search index: `~/.local/share/llmdoc/index.db` (DuckDB, ~285 MB)
- Hermes model: `opencode-go/deepseek-v4-pro` via OpenRouter
