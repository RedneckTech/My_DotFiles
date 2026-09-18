# 02 — Installed Software

Software is installed through **five** paths. Know which one a tool came from
before upgrading it, or you'll break a symlink / leave an orphan.

| Manager | Prefix / scope | Notes |
|---------|---------------|-------|
| **apt** (`dpkg`) | system | 112 manually-installed packages (the base + user apps) |
| **Homebrew** | `/home/linuxbrew/.linuxbrew` | 261 formulae (~20 top-level; the Qt6/mesa/ffmpeg stack lives here) |
| **snap** | `/snap` | 6 user apps + bases |
| **flatpak** | system | 1 app (RetroArch) |
| **uv / npm / cargo / go** | `~/.local`, `~/.hermes`, `~/.cargo`, `~/go` | language toolchains + agent-managed tools |

## Toolchain versions (probe, don't trust these over time)

- C/C++: gcc/g++ 13.3 (`/usr/bin`); `make`, `pkg-config`, `clangd` (apt).
- Rust 1.98.1 — via Homebrew (`/home/linuxbrew/.linuxbrew/bin/{rustc,cargo}`).
- Go 1.27.1 — via Homebrew (`/home/linuxbrew/.../go/1.27.1`); `GOPATH=~/go`
  currently empty.
- Java — OpenJDK via Homebrew (`openjdk`).
- Python 3.14 — Homebrew `python@3.14` (system `python3` is 3.14.7, PEP 668
  externally-managed → use a venv/uv, never bare `pip install`).
- Node v26.8.2 / npm 11.19.1 — **Hermes-managed** (`~/.local/bin/node`,
  symlinked to `~/.hermes/node`). Global npm packages install into
  `~/.local/lib/node_modules`.
- Zig — `~/.local/bin/zig` with language server `~/.local/bin/zls`.

## Homebrew — top-level (`brew leaves`)

`berkeley-db@5 fastfetch glances glew glfw go gum lazygit libxpm openjdk qt
ripgrep rust sdl2_image sdl2_ttf shellcheck starship superfile unzip zlib`

Highlights: the full **Qt6 stack** (`qt`, ~20 `qt*` formulae — used by the gui
agent), **mesa/ffmpeg/llvm** (transitive for the graphics stack), plus CLI
tools `ripgrep`, `shellcheck`, `fastfetch`, `glances`, `gum`, `lazygit`,
`superfile`. One cask: **codex** (OpenAI Codex CLI).

## User-local binaries (`~/.local/bin`)

`codegraph cua-driver fbc gen-llms-txt.py github-mcp-server hermes hermes-acp
hermes-agent inv invoke llmdoc lua-language-server markitdown-mcp
mcp-filesystem-server mcp-server-memory mcp-server-sequential-thinking node
npm npx playwright-mcp terminal-driver-mcp zig zls`

This is the agent/toolchain layer (Hermes, its MCP servers, uv-installed
tools, language servers). `uv` itself lives at `~/.hermes/bin/uv`. See
`../AI_DOCs/02-opencode.md` for how the MCP servers wire into OpenCode.

## uv tools (`uv tool list`)

- `browser-use` v0.13.10 (→ `browser`, `browser-use`, `browseruse`, …)
- `llmdoc` v0.3.1
- `markitdown-mcp` v0.0.1a7

## snap

User apps: `discord`, `firefox`, `ghostty` (terminal), `marktext` (markdown
editor), `thunderbird`, `bash-language-server`. Plus snap bases/runtimes
(`core20/22/24`, `mesa-2404`, `gnome-*-2204/2404`, `gtk-common-themes`,
`snapd`, `firmware-updater`).

## flatpak

- `org.libretro.RetroArch` (game emulator frontend).

## apt — notable manually-installed packages

Grouped (full manual list is 112 packages):

- **Desktop env**: `kubuntu-desktop`, `kubuntu-wallpapers`, `kde-config-fcitx5`.
- **Terminals/editors/launchers**: `alacritty`, `yakuake`, `micro`, `rofi`.
- **Dev tooling**: `shellcheck`, `shfmt`, `python3-pylsp`, `clangd`, `stow`,
  `eza`, `zoxide`, `fzf`, `tldr`, `nala`.
- **BBS/3270**: `x3270`, `c3270`.
- **Media/gaming**: `vlc`, `steam:i386`, `qpittorrent`, emulators via flatpak
  (RetroArch) — PCSX2/RPCS3 config dirs exist under `~/.config`.
- **GPU/monitoring**: `nvtop`, `radeontop`, `lm_sensors`, `mesa-utils`,
  `mesa-vulkan-drivers`, `xserver-xorg-video-amdgpu`.
- **Virtualization**: `qemu-system-x86`, `virt-manager`, `ovmf`.
- **Storage/filesystems**: `btrfs-progs`, `lvm2`, `xfsprogs`, `jfsutils`,
  `reiserfsprogs`, `exfatprogs`, `dmraid`, `dmeventd`, `kpartx`,
  `thin-provisioning-tools`.
- **Cloud/transfer**: `rclone`, `p7zip-full`, `unrar`.
- **Input**: `fcitx5-chinese-addons`, `fcitx5-frontend-all`,
  `fcitx5-material-color`.
- **Security/util**: `clamav`, `mokutil`, `htop`, `tree`.
- **CLI niceties** (also some via brew): `fzf`, `ripgrep`, `eza`, `zoxide`,
  `tldr`, `gum`, `lazygit`, `superfile`.

## Language servers (LSP) present

`bash-language-server` (snap) · `python3-pylsp` (apt) · `clangd` (apt) ·
`lua-language-server` (`~/.local/bin`) · `zls` (zig, `~/.local/bin`).
