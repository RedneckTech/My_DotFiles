# 05 — Desktop Settings

## Environment

- **KDE Plasma 5.27.12** (Kubuntu `kubuntu-desktop`), Qt 5.15.13, KF 5.115.0.
- **X11** session (not Wayland), WM **kwin**.
- 3× 2560×1440 monitors: `DisplayPort-1`, `DisplayPort-2` (primary), `HDMI-A-0`.

## Keybindings

Two layers, be careful not to collide them:

**xbindkeys** (`~/.xbindkeysrc`, symlinked; autostarted via the
`app-xbindkeys@autostart` systemd user unit):

```
Mod1 + w        rofi -show window
Mod1 + r        rofi -show run
Mod1 + g        open ghostty
Mod1 + a        open alacritty
control+shift+q xbindkeys_show (the help overlay)
```

**KDE global shortcuts** (`~/.config/kglobalshortcutsrc`) — notable defaults:

- `Meta+D` peek desktop · `Meta+W` overview · `Ctrl+F9`/`F10`/`F7` present
  windows · `Meta+F8` desktop grid · `Meta+Ctrl+A` attention · `Meta+T`
  tile editor · `Ctrl+Esc` system activity · `Meta+L` lock · `Ctrl+Alt+Del`
  logout · `Meta+P` display switch.

## Launcher / apps

- **rofi** (custom keybinds above) + KDE **krunner** as the two launchers.
- Default apps: Firefox (browser) + Thunderbird (mail) via snap. Konsole is
  the KDE default terminal; ghostty/alacritty/yakuake are the extra ones.

## Power

- `power-profiles-daemon` active; KDE `powerdevilrc` holds the power/suspend
  settings.

## Appearance / themes

- Wallpapers: `kubuntu-wallpapers`. fcitx5 uses `fcitx5-material-color` theme.
- GTK configs (`gtkrc`, `gtk-3.0/`, `gtk-4.0/`) and `kdeglobals` present;
  screenshot/theme specifics live in the KDE `*rc` files — re-read them if you
  need exact colors.

## Input

- fcitx5 (US + Chinese add-ons) — see `03-configs-and-dotfiles.md`.
- Touchpad toggles exist in kglobalshortcutsrc (desktop is a tower; keyboard +
  mouse are primary).

## Screenshots / accessibility / misc

- `spectacle` (KDE screenshot tool, `spectaclerc`).
- `kscreenlockerrc` / `ksmserverrc` for lock/session behavior.
- `kwinrulesrc` holds any per-window rules.

## Files/dirs worth knowing (user-level)

- `~/.config/user-dirs.dirs` standard XDG dirs.
- `~/.local/share/` — runtime data for llmdoc (DuckDB index), opencode-memory
  (per-agent knowledge graphs), awesome-agent-skills clone, etc.
- The five data/mount drives under `/media/jpfeiff/` are the bulk storage
  (see `01-system-and-hardware.md`).
