# 05 — Desktop Settings

## Environment

- **KDE Plasma 5.27.12** (Kubuntu `kubuntu-desktop`), Qt 5.15.13, KF 5.115.0.
- **X11** session (not Wayland), WM **kwin**.
- Single built-in panel **1920×1080 @ 165 Hz** (`DP-4`); external DisplayPort /
  HDMI outputs present but disconnected.

## Keybindings

Two layers, be careful not to collide them:

**xbindkeys** (`~/.xbindkeysrc`, symlinked; autostarted via the
`app-xbindkeys@autostart` systemd user unit):

```
Mod1 + w        rofi -show window
Mod1 + r        rofi -show run
Mod1 + g        open ghostty
Mod1 + a        open alacritty   (alacritty NOT installed on this laptop — no-op)
control+shift+q xbindkeys_show (the help overlay)
```

**KDE global shortcuts** (`~/.config/kglobalshortcutsrc`) — notable defaults:

- `Meta+D` peek desktop · `Meta+W` overview · `Meta+F8` desktop grid ·
  `Meta+T` tile editor · `Meta+L` lock · `Meta+P` display switch ·
  `Ctrl+Alt+Del` logout · `Meta+Ctrl+A` attention · `Meta+Ctrl+Esc` kill window
  · `Meta+Ctrl+Arrows` switch desktops · `Meta+Alt+K` switch keyboard layout.

## Launcher / apps

- **rofi** (custom keybinds above) + KDE **krunner** as the two launchers.
  rofi config at `~/.config/rofi/config.rasi`.
- Default apps: Firefox (browser) + Thunderbird (mail) via snap. Konsole is
  the KDE default terminal; ghostty/yakuake are the extra ones.

## Power

- **power-profiles-daemon** active (laptop CPU power profiles).
- Battery: `BAT0`, 99% fully-charged, ~87.5% design capacity — KDE
  `powerdevilrc` holds the suspend/power settings.

## Appearance / themes

- GTK configs (`gtkrc`, `gtk-2.0/`, `gtk-3.0/`, `gtk-4.0/`) and `kdeglobals`
  present; screenshot/theme specifics live in the KDE `*rc` files — re-read
  them if you need exact colors.

## Input

- fcitx5 (US + Chinese add-ons) — see [03-configs-and-dotfiles.md](./03-configs-and-dotfiles.md).
- Laptop keyboard + touchpad (KDE `kcminputrc` / `kxkbrc` hold layout/input
  details).

## Screenshots / accessibility / misc

- `spectacle` (KDE screenshot tool, `spectaclerc`).
- `kscreenlockerrc` / `ksmserverrc` for lock/session behavior.
- `kwinrulesrc` holds any per-window rules.

## Files/dirs worth knowing (user-level)

- `~/.config/user-dirs.dirs` standard XDG dirs.
- `~/.local/share/` — runtime data for opencode-memory (per-agent knowledge
  graphs), uv tools, and the MCP servers set up 2026-09-26 (see
  [06-mcp-servers.md](./06-mcp-servers.md)).
- `~/.cache/ms-playwright/` — Playwright Chromium used by the `playwright` MCP
  server.
- `/media/jpfeiff/MassStorge` is the single secondary data drive (1.8 T).
