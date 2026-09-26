# 03 — Configs & Dotfiles

## Dotfiles repo (source of truth)

All user-managed config lives in the git repo `~/.user_config/`, remote
`git@github.com:RedneckTech/My_DotFiles.git` (branch `master`). Live files are
**symlinks** into that repo — edit the repo copy, not the symlink target, or
the change won't survive a sync.

### Live symlinks actually present on this laptop (probed)

```
~/.bashrc                    -> .user_config/home/.bashrc
~/.xbindkeysrc               -> .user_config/home/.xbindkeysrc
~/.config/starship.toml      -> ../.user_config/home/.config/starship.toml
~/.config/opencode/opencode.jsonc -> ../../.user_config/home/.config/opencode/opencode.jsonc
```

### Stow layout — per-host split (2026-09-26)

The repo was restructured from a single `home` package into a shared package
plus per-host packages, so a machine-specific edit on one box can't clobber the
other:

- `home/` — shared baseline, stowed by both machines (bashrc, xbindkeysrc,
  editor/terminal/prompt configs, `.claude/skills/`, `.config/opencode/` with
  agents + skills, `starship.toml`, `.hermes/SOUL.md`).
- `host-jacob-x570aorusultra/` — desktop-only (currently `.hermes/config.yaml`).
- `host-jacob-82jw/` — laptop-only (doesn't exist yet; create it when this
  laptop needs a machine-specific file).

`update_dotfiles.sh` now stows `home` plus `host-$(hostname)` when that package
exists — on this laptop that resolves to just `home`. Stow uses `--no-folding`
(individual files, so `~/.config/opencode/` stays a real dir that can also hold
`node_modules/`).

Symlink reconciliation from this split:

- `~/.config/opencode/skills/` is symlinked in (full skill set from the repo).
- `~/.config/opencode/agents/*.md` (12 agents) are symlinked in.
- `~/.config/opencode/.env` is symlinked to `home/.config/opencode/.env`.
- The stale `bash-scripts.md` agent symlink was removed (the file was dropped
  from the repo).

### `~/.hermes/` handling

- `~/.hermes/SOUL.md` is symlinked to `home/.hermes/SOUL.md` (persona text,
  identical on both machines).
- `~/.hermes/config.yaml` is **not** symlinked on this laptop: it's
  Hermes-managed live state (seeds `_config_version`, writes migrations, updates
  fields at runtime — it grew 107535 → 107586 bytes in one session). It lives
  in the desktop host package, not the shared `home/` package, so the laptop
  keeps its own Hermes-managed copy as a regular file. Pre-split backups are
  under `~/.local/state/dotfiles-stow/backups/`.

### `.gitignore`

Excludes `home/.config/micro/{backups,buffers}/`,
`home/.config/opencode/node_modules/`, and `home/.config/opencode/.env`
(added 2026-09-26 for the GitHub token). Secrets are **not** in the repo — they
live in `.env` files sourced by `~/.bashrc`.

## Shell

- Default shell `/bin/bash`; `~/.bashrc` (symlinked) sources the secret files —
  the OpenCode `.env` and the Hermes `.env` (keyed by variable NAME only).
- `~/.profile` (868 B) — login-shell PATH/session bootstrap.
- Prompt: **starship** (`~/.config/starship.toml`, symlinked; the only Homebrew
  formula on this laptop).

## Git

- Identity: `Jacob Pfeiff <pfeiff33@gmail.com>`.
- GitHub account `RedneckTech`; dotfiles remote over SSH.

## SSH

- **No `~/.ssh/config`** on this laptop. The desktop had a `3270BBS` host
  alias (`192.168.122.150`, user `dev`) — that alias does not exist here.

## Terminals

- **ghostty** — installed (`/usr/bin/ghostty`), the `Mod1+g` quick terminal.
- **yakuake** — KDE drop-down terminal.
- **konsole** — KDE default.
- **alacritty** — **not installed**, though `~/.xbindkeysrc` still binds
  `Mod1+a` to it (that binding is a no-op here).

## Editor

- **micro** — `/usr/bin/micro`, config at `~/.config/micro/` (settings.json,
  bindings.json, syntax/).
- **kate** — KDE editor for occasional GUI edits.

## Other notable `~/.config` entries

`alacritty/ ghostty/ fcitx/ fcitx5/ gtk-2.0/ gtk-3.0/ gtk-4.0/ ibus/ kate/
libreoffice/ matplotlib/ micro/ opencode/ rofi/ uv/` plus the KDE `*rc` files
(see desktop doc), `starship.toml`, `user-dirs.dirs`.

## Input method

- **fcitx5** with Chinese add-ons; configured via `~/.config/fcitx5/` and
  `kde-config-fcitx5`. Env wired: `GTK_IM_MODULE=fcitx`,
  `QT_IM_MODULE=fcitx`, `XMODIFIERS=@im=fcitx`.

## Fonts

- `~/.config/fontconfig/` present; no obviously custom font dirs beyond system
  defaults (probe `fc-match` if needed).
