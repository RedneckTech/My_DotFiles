# Live path -> repo target symlink map

| Live path | Target |
|---|---|
| `~/.bashrc` | `.user_config/home/.bashrc` |
| `~/.xbindkeysrc` | `.user_config/home/.xbindkeysrc` |
| `~/.config/starship.toml` | `../.user_config/home/.config/starship.toml` |
| `~/.hermes/config.yaml` | `../.user_config/home/.hermes/config.yaml` |
| `~/.hermes/SOUL.md` | `../.user_config/home/.hermes/SOUL.md` |
| `~/.config/opencode/opencode.jsonc` | `../../.user_config/home/.config/opencode/opencode.jsonc` |
| `~/.config/opencode/package.json` | `../../.user_config/home/.config/opencode/package.json` |
| `~/.config/opencode/package-lock.json` | `../../.user_config/home/.config/opencode/package-lock.json` |
| `~/.config/opencode/agents/*.md` | `../../../.user_config/home/.config/opencode/agents/*.md` |
| `~/.claude/skills` | `../.user_config/home/.claude/skills` |

Only user-edited files are symlinked; runtime dirs (`~/.config/opencode/node_modules`,
`~/.opencode/bin`, `~/.claude` runtime state) stay local.
