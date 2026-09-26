# 04 — systemd & Services

systemd manages the user session (KDE Plasma) and system daemons. Sound is
PipeWire/WirePlumber. This is a laptop, so power, Wi-Fi, and Bluetooth services
are present.

## User services (enabled of note)

| Unit | Purpose |
|------|---------|
| `pipewire.service` / `pipewire-pulse.service` / `wireplumber.service` | Audio stack |
| `plasma-kcminit.service` / `plasma-ksmserver.service` / `plasma-plasmashell.service` | KDE Plasma session bring-up |
| `kde-baloo.service` | KDE file-content indexer |
| `app-xbindkeys@autostart.service` | Launches `xbindkeys` at login |
| `app-org.kde.kdeconnect.daemon@autostart.service` | KDE Connect |
| `gcr-ssh-agent.service` / `gnome-keyring-daemon.service` / `gpg-agent*` | Credential/key agents |
| `obex.service` | Bluetooth OBEX push |
| `drkonqi-coredump-cleanup.service` | KCrash metadata cleanup |
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
| `upower.service` | Battery/power device state |
| `fwupd.service` | Firmware updates |
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

- There is no `llmdoc-serve.service` on this laptop — the one service that
  bridged into the AI stack on the desktop is absent here because LLMDoc is
  disabled.
- No libvirt/qemu services (no local VMs on this laptop).
