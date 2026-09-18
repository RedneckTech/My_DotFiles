# Dotfiles & Config Management

## Core idea

All AI (and general dotfile) config lives in a version-controlled repo, then is
symlinked into live locations. The repo is the source of truth.

- Repo: `~/.user_config/`
- Remote: `git@github.com:RedneckTech/My_DotFiles.git`
- Branch: `master`

## Layout

```
~/.user_config/
  .git/                         # the repo itself
  home/
    .bashrc
    .xbindkeysrc
    .claude/skills/             # Claude Code skills (4)
    .config/
      alacritty/
      ghostty/
      micro/
      opencode/                 # opencode.jsonc, agents/, .env, package.json
      rofi/
      starship.toml
    .hermes/
      config.yaml               # Hermes agent config
      SOUL.md                   # Hermes personality
```

## Symlink map (repo -> live path)

These are individual symlinks (hand-managed, not GNU Stow):

| Live path | -> Target |
|-----------|-----------|
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

Note: `~/.config/opencode/` is a real directory that also holds the `node_modules`
and `bin` needed to actually run OpenCode; only the *user-edited* files
(`opencode.jsonc`, `agents/`, `package.json`) are symlinked into the repo.

## `.bashrc` integration

Two lines matter for the AI stack:

```
export PATH=/home/jpfeiff/.opencode/bin:$PATH
[ -f "$HOME/.user_config/home/.config/opencode/.env" ] && . "$HOME/.user_config/home/.config/opencode/.env"
```

- Adds the OpenCode CLI to PATH.
- Sources the OpenCode secrets file so `{env:GITHUB_PERSONAL_ACCESS_TOKEN}`
  placeholders in `opencode.jsonc` resolve.

## Secrets handling

Secrets are **not** committed. The `.env` files are gitignored and chmod 600:

- `~/.user_config/home/.config/opencode/.env`
- `~/.hermes/.env` (also holds active Hermes keys)

Never commit a secret: keep using gitignore + `.env`, and never paste real values
into chat, logs, or commits.

## Editing discipline

Always edit the file inside `~/.user_config/`, never through the symlink's own
path (they resolve to the same file, but conceptually the repo copy is the
source of truth and must be committed). After changing anything, commit:

```
cd ~/.user_config && git add -A && git commit -m "describe the change"
```

Recent commits (2026-09-13) show the pattern:
- `Update opencode agents; add ScriptDev/debug/review, drop bash-scripts; trim hermes config`
- `Add Hermes agent configs to stow; update opencode agents`
- `add ispf-editor subagent (uploader.py based); document x3270 Reset key lockup recovery`
