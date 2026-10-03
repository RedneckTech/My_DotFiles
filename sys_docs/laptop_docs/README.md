# Laptop — Master Index

Documentation for **jacob-82jw**, the Lenovo Legion 5 15ACH6 laptop. Describes
the OS, hardware, software, configs/dotfiles, systemd services, desktop
settings, and the MCP server setup. Grounded in live
`ls`/`systemctl`/`lspci`/package-manager output as of 2026-10-03
(post-upgrade to Ubuntu 26.04.1).

| Doc | Covers |
|-----|--------|
| [01 — System & hardware](./01-system-and-hardware.md) | OS, kernel, CPU, GPU, RAM, storage, network, battery, desktop env |
| [02 — Installed software](./02-installed-software.md) | Package managers + software/toolchain inventory |
| [03 — Configs & dotfiles](./03-configs-and-dotfiles.md) | dotfiles repo, shell, git/ssh, terminals, editor, input method |
| [04 — systemd & services](./04-systemd-and-services.md) | User + system units, timers, sockets |
| [05 — Desktop settings](./05-desktop-settings.md) | KDE Plasma, panel, keybindings, launchers, power |
| [06 — MCP servers](./06-mcp-servers.md) | OpenCode MCP servers — installation, paths, verification |

## Quick facts

- **OS**: Ubuntu 26.04.1 LTS, kernel 7.0.0-38-generic
- **Desktop**: KDE Plasma 6.6.6 on **Wayland**, single 1920×1080@165 panel
- **Hardware**: Lenovo Legion 5 15ACH6 · AMD Ryzen 7 5800H (8C/16T) · 32 GB
  RAM · NVIDIA RTX 3050 Ti Mobile (4 GB)
- **Shell**: bash · **Editor**: micro · **Terminals**: ghostty / yakuake /
  konsole · **Launcher**: rofi (+ krunner)
- **Package managers**: apt, Homebrew (starship only), snap, plus uv / npm
  toolchains. No flatpak, cargo, go, rust, or zig.
- **Dotfiles**: git repo `~/.user_config/` (remote `RedneckTech/My_DotFiles`),
  stowed via GNU Stow — shared `home/` + per-host `host-<hostname>/` packages;
  see [03](./03-configs-and-dotfiles.md).
- **MCP**: 10 OpenCode MCP servers installed + verified 2026-09-26 (see
  [06](./06-mcp-servers.md)).

## Relationship to the other docs

`../workstation_docs/` documents the **desktop** (`jacob-x570aorusultra`), a
different machine. This directory documents the **laptop**. The two share the
same dotfiles repo and AI stack; hardware and software differ.
`../AI_DOCs/` documents the AI/LLM layer (OpenCode, Hermes, Claude Code, Codex,
LLMDoc) that runs on top of this laptop — the MCP-server setup in
[06](./06-mcp-servers.md) is the laptop-specific record of how that layer was
instantiated here.

## Conventions

- Re-probe before editing these docs; versions/hardware drift over time.
- Never record a secret here. Reference keys by name (e.g.
  `GITHUB_PERSONAL_ACCESS_TOKEN`) only.
- Drive labels reflect the mount points exactly as created (`MassStorge` is the
  literal label on the 1.8 T drive).
