# 04 — systemd & Services

systemd manages the user session (KDE Plasma) and system daemons. Sound is
PipeWire/WirePlumber. This is a laptop, so power, Wi-Fi, and Bluetooth services
are present.

## User services (enabled of note)

| Unit | Purpose |
|------|---------|
| `pipewire.service` / `pipewire-pulse.service` / `wireplumber.service` | Audio stack |
| `plasma-kwin_wayland.service` | KWin Wayland compositor |
| `plasma-plasmashell.service` / `plasma-ksmserver.service` / `plasma-kded6.service` | KDE Plasma session bring-up |
| `plasma-powerdevil.service` / `plasma-kaccess.service` / `plasma-gmenudbusmenuproxy.service` / `plasma-xembedsniproxy.service` / `plasma-polkit-agent.service` | Plasma power / tray / a11y / portal helpers |
| `xdg-desktop-portal.service` + `plasma-xdg-desktop-portal-kde.service` / `xdg-desktop-portal-gtk.service` | Wayland portal backends |
| `xdg-document-portal.service` / `xdg-permission-store.service` | Wayland document + permission storage |
| `kde-baloo.service` | KDE file-content indexer |
| `app-xbindkeys@autostart.service` | Launches `xbindkeys` at login |
| `app-org.kde.kdeconnect.daemon@autostart.service` | KDE Connect |
| `gcr-ssh-agent.service` / `gnome-keyring-daemon.service` / `gpg-agent*` / `ssh-agent.service` | Credential/key agents |
| `obex.service` | Bluetooth OBEX push |
| `drkonqi-coredump-cleanup.service` / `drkonqi-sentry-postman.*` | KCrash metadata cleanup |
| `mpris-proxy.service` | MPRIS Bluetooth media proxy |
| `kunifiedpush-distributor.service` | KDE unified-push distributor |
| `filter-chain.service` | PipeWire filter |

No `llmdoc-serve.service` here — LLMDoc is disabled/not installed on this
laptop (see [06-mcp-servers.md](./06-mcp-servers.md) and
`../AI_DOCs/03-llmdoc-pipeline.md`).

## System services (non-default running)

| Unit | Purpose |
|------|---------|
| `sddm.service` | Display manager (KDE login) |
| `NetworkManager.service` + `wpa_supplicant.service` | Networking / Wi-Fi |
| `bluetooth.service` | Bluetooth |
| `power-profiles-daemon.service` | CPU power profiles (laptop) |
| `switcheroo-control.service` | Hybrid-GPU switcheroo control (NVIDIA + iGPU) |
| `nvidia-persistenced.service` / `nvidia-powerd.service` | NVIDIA persistence + power-management daemons |
| `upower.service` | Battery/power device state |
| `ModemManager.service` | Mobile-broadband management |
| `smartmontools.service` | SMART disk monitoring |
| `cups.service` / `cups-browsed.service` | Printing |
| `rtkit-daemon.service` | Realtime scheduling for audio |
| `cron.service` | Standard system cron daemon (note: this is **not** Hermes cron — see `../AI_DOCs/04-hermes-agent.md`) |
| `avahi-daemon.service` | mDNS/DNS-SD |

Plus the usual `accounts-daemon`, `polkit`, `udisks2`, `systemd-{resolved,
timesyncd,hostnamed,journald,logind,udevd}`, `rsyslog`, `dbus`,
`unattended-upgrades`, `snapd`, `kerneloops`, `networkd-dispatcher`,
`user@1000.service`.

## Timers / sockets

- User: `drkonqi-coredump-cleanup.timer`, `launchpadlib-cache-clean.timer`,
  `snap.firmware-updater.firmware-notifier.timer`. Plus GPG/SSH/keyring sockets
  and `speech-dispatcher.socket`.

## Notes

- The 26.04 upgrade moved the session from X11 to **Wayland**, so the Plasma
  session is driven by `plasma-kwin_wayland.service` (+ the new `plasma-kded6`,
  `xdg-desktop-portal`, and `xdg-document-portal` units) instead of the old
  `kwin_x11` / `kded5` units.
- `fwupd.service` is `static` (D-Bus/socket activated) and inactive at idle —
  it is not always-on the way older installs showed it.
- There is no `llmdoc-serve.service` on this laptop — the one service that
  bridged into the AI stack on the desktop is absent here because LLMDoc is
  disabled.
- No libvirt/qemu services (no local VMs on this laptop).
