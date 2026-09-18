# 03 — Configs & Dotfiles

## Dotfiles repo (source of truth)

All user-managed config lives in the git repo `~/.user_config/`, remote
`git@github.com:RedneckTech/My_DotFiles.git` (branch `master`). Live files are
**symlinks** into that repo — edit the repo copy, not the symlink target, or
the change won't survive a sync. Committed via `git` in-prefix.

Live symlinks (probed):

```
~/.bashrc                    -> .user_config/home/.bashrc
~/.xbindkeysrc               -> .user_config/home/.xbindkeysrc
~/.config/starship.toml      -> ../.user_config/home/.config/starship.toml
~/.config/opencode/*         -> .user_config/home/.config/opencode/*
~/.hermes/config.yaml        -> ../.user_config/home/.hermes/config.yaml
~/.hermes/SOUL.md            -> ../.user_config/home/.hermes/SOUL.md
~/.claude/skills             -> ../.user_config/home/.claude/skills
```

`.gitignore` excludes only `home/.config/micro/{backups,buffers}/` and
`home/.config/opencode/node_modules/`. Secrets are **not** in the repo — they
live in `.env` files (see below).

## Shell

- Default shell `/bin/bash`; `~/.bashrc` (symlinked) sources the secret files
  (the OpenCode `.env` and Hermes `.env`, keyed by variable NAME only).
- `~/.profile` (807 B) — login-shell PATH/session bootstrap.
- Prompt: **starship** (`~/.config/starship.toml`, symlinked).

## Git

- Identity: `Jacob Pfeiff <pfeiff33@gmail.com>`.
- GitHub account `RedneckTech`; dotfiles remote over SSH.

## SSH

`~/.ssh/config` defines one host alias:

```
Host 3270BBS
    HostName 192.168.122.150
    User dev
```

(Used by the 3270DEV agent to reach the TN3270 BBS host.)

## Terminals

- **ghostty** — snap (the `Mod1+g` quick terminal).
- **alacritty** — apt (`Mod1+a`), config at `~/.config/alacritty/`.
- **yakuake** — apt drop-down terminal (KDE).
- **konsole** — KDE default (`konsolerc`, `konsolesshconfig`).

## Editor

- **micro** — apt, config at `~/.config/micro/` (the user's everyday editor;
  `.gitignore` trims its backup/buffer dirs).
- **kate** — KDE editor (`katerc`, `kateschemarc`, …) for occasional GUI edits.

## Other notable `~/.config` entries

`alacritty/ ghostty/ fcitx5/ lazygit/ micro/ opencode/ rclone/ rofi/
starship.toml superfile/ htop/` plus the KDE `*rc` files (see desktop doc),
`matplotlib/` (Python), `libreoffice`, `vlcrc`, `qBittorrent`, emulator configs
(`PCSX2`, `rpcs3`, `RetroArch` via flatpak).

## Input method

- **fcitx5** with Chinese add-ons (`fcitx5-chinese-addons`,
  `fcitx5-frontend-all`, `fcitx5-material-color`); configured via
  `~/.config/fcitx5/{conf,profile}` and `kde-config-fcitx5`.
- Current profile: default group `keyboard-us` (US layout).
- Env wired: `GTK_IM_MODULE=fcitx`, `QT_IM_MODULE=fcitx`,
  `XMODIFIERS=@im=fcitx`.

## Fonts

`~/.config/fontconfig/` present; no obviously custom font dirs beyond system
defaults (probe `fc-match` if needed).
