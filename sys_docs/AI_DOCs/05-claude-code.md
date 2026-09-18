# Claude Code

Anthropic's Claude Code agent. On this machine it is configured with **skills
only** — no overridden model, hooks, or settings.

## Paths

- Skills: `~/.claude/skills/` → symlink to `~/.user_config/home/.claude/skills/`
  (source of truth is the dotfiles repo; see `01-dotfiles-config-management.md`)

## Skills (4)

| Skill | Purpose |
|-------|---------|
| `doc-coauthoring` | Structured document authoring workflow |
| `frontend-design` | Frontend design conventions guidance |
| `skill-creator` | Tooling to author/package new skills (has its own scripts, eval harness, references) |
| `webapp-testing` | Drive and test web apps (Playwright/Puppeteer helpers, examples, `with_server.py`) |

These are the standard Anthropic-provided skills. `skill-creator` in particular is
self-contained (agents/, scripts/, references/, eval-viewer/).
