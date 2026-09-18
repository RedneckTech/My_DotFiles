# 04 — systemd & Services

systemd manages the user session (KDE Plasma) and system daemons. Sound is
PipeWire/WirePlumber; virtualization via libvirt.

## User services (enabled/active of note)

| Unit | Purpose |
|------|---------|
| `llmdoc-serve.service` | Serves the LLMDoc `.llms.txt` files at `127.0.0.1:8099` (the AI docs pipeline — see `../AI_DOCs/03-llmdoc-pipeline.md`). Installed but **not auto-enabled**. |
| `pipewire.service` / `pipewire-pulse.service` / `wireplumber.service` | Audio stack (replaces PulseAudio/ALSA brokers). |
| `plasma-kcminit.service` / `plasma-ksmserver.service` / `plasma-plasmashell.service` | KDE Plasma session bring-up. |
| `kde-baloo.service` | KDE file-content indexer (Baloo). |
| `app-xbindkeys@autostart.service` | Launches `xbindkeys` at login (see keybindings). |
| `app-org.kde.kdeconnect.daemon@autostart.service` | KDE Connect daemon. |
| `gcr-ssh-agent.service` / `gnome-keyring-daemon.service` / `gpg-agent*.socket` | Credential/key agents (SSH, GPG, keyring). |
| `drkonqi-coredump-cleanup.service` | KCrash metadata cleanup. |
| `systemd-tmpfiles-setup.service` / `systemd-tmpfiles-clean.timer` | temp/state cleanup. |

Also active at session level: `dbus.service`, `dconf.service`,
`at-spi-dbus-bus` (accessibility), `filter-chain` (PipeWire filter).

## System services (non-default running)

| Unit | Purpose |
|------|---------|
| `smartmontools.service` | SMART disk health monitoring daemon. |
| `virtlockd.service` / `virtlogd.service` | libvirt lock/log daemons — this host runs VMs (virt-manager/qemu). |
| `libvirtd` (via socket) | libvirt management (see `virt-manager`, `qemu-system-x86`). |
| `power-profiles-daemon.service` | CPU power profiles. |
| `switcheroo-control.service` | Multi-GPU switcheroo control (unused here — single dGPU). |
| `rtkit-daemon.service` | Realtime scheduling for audio. |

(The user manager `user@1000.service` and core systemd targets are, of course,
running too.)

## Timers / sockets

- User: `systemd-tmpfiles-clean.timer`, `snap.firmware-updater.firmware-notifier.timer`,
  `launchpadlib-cache-clean.timer`. Plus GPG/SSH/keyring sockets and
  `speech-dispatcher.socket`.

## Notes

- `llmdoc-serve.service` is the one service that crosses into the AI stack;
  there's no cron/launchd equivalent — scheduled work on this box is
  systemd-only.
- No Docker; no snap auto-update override of note.
