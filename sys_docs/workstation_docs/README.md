# Workstation — Master Index

Documentation for **jacob-x570aorusultra**, Jacob's primary desktop. Describes
the OS, hardware, user-installed software, configs/dotfiles, settings, and
systemd services. Grounded in live `ls`/`systemctl`/`glxinfo`/package-manager
output as of 2026-09-18.

| Doc | Covers |
|-----|--------|
| [01 — System & hardware](./01-system-and-hardware.md) | OS, kernel, CPU, GPU, RAM, storage, network, desktop environment |
| [02 — Installed software](./02-installed-software.md) | Package managers + full software/toolchain inventory |
| [03 — Configs & dotfiles](./03-configs-and-dotfiles.md) | dotfiles repo, shell, git/ssh, terminals, editor, input method |
| [04 — systemd & services](./04-systemd-and-services.md) | User + system units, timers, sockets |
| [05 — Desktop settings](./05-desktop-settings.md) | KDE Plasma, monitors, keybindings, launchers, autostart |

## Quick facts

- **OS**: Ubuntu 24.04.5 LTS (Noble Numbat), kernel 7.0.0-31-generic (HWE)
- **Desktop**: KDE Plasma 5.27.12 (Kubuntu) on **X11**, kwin WM, 3× 2560×1440
- **Hardware**: Gigabyte X570 AORUS ULTRA · AMD Ryzen 9 3900X (12C/24T) ·
  32 GB RAM · AMD Radeon RX 9070 XT (16 GB, RDNA4)
- **Shell**: bash · **Editor**: micro · **Terminals**: ghostty / alacritty /
  yakuake / konsole · **Launcher**: rofi (+ krunner)
- **Package managers**: apt, Homebrew (`/home/linuxbrew/.linuxbrew`), snap,
  flatpak (RetroArch only), plus uv / cargo / npm / go toolchains
- **VMs**: libvirt + virt-manager / qemu (host's `virtlockd`/`virtlogd` running)
- **Dotfiles**: git repo `~/.user_config/` (remote `RedneckTech/My_DotFiles`),
  symlinked into `~`; secrets live in `.env` files sourced by `~/.bashrc`

## Relationship to the AI docs

`../AI_DOCs/` documents the AI/LLM stack (OpenCode, Hermes, Claude Code, Codex,
LLMDoc) that runs *on top of* this workstation. This directory documents the
host itself — the two are complementary. The LLMDoc pipeline (`llmdoc-serve`)
is the one service that bridges them; see
[04-systemd-and-services](./04-systemd-and-services.md) and
`../AI_DOCs/03-llmdoc-pipeline.md`.

## Conventions

- Re-probe before editing these docs; versions/hardware drift over time.
- Never record a secret here. Reference keys by name (e.g.
  `GITHUB_PERSONAL_ACCESS_TOKEN`) only.
- Drive labels reflect the mount points exactly as created (e.g.
  `/media/jpfeiff/MassStorge` is the literal label).
