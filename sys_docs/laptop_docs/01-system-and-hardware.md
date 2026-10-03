# 01 — System & Hardware

## OS

- **Ubuntu 26.04.1 LTS** ("Resolute Raccoon"), ID `ubuntu`, ID_LIKE `debian`.
- Kernel **7.0.0-38-generic** (`#38-Ubuntu SMP PREEMPT_DYNAMIC`, x86_64) — the
  HWE 7.0 kernel, now the same series the desktop runs (upgraded from the
  24.04 GA 6.8 kernel 2026-10-03).
- Hostname: `jacob-82jw`. Machine ID `b5b6f10bdee745c5b4d46d0e657c9224`.
- User: `jpfeiff`.

## Laptop / firmware

- **Lenovo Legion 5 15ACH6** (product `82JW`), board `LNVNB161216`.
- BIOS **HHCN24WW** (2021-11-24).
- UEFI boot (`/boot/efi`, vfat, 300 M).

## CPU

- AMD **Ryzen 7 5800H with Radeon Graphics**, 8 cores / 16 threads, Zen 3,
  1 socket.

## Memory

- **32 GB** (reports 31 GiB) DDR4.

## GPU

- NVIDIA **GeForce RTX 3050 Ti Laptop GPU** (GA107BM), **4 GB** VRAM.
- Driver: proprietary **NVIDIA 580.178.04** — modules `nvidia`, `nvidia_drm`,
  `nvidia_modeset`, `nvidia_uvm`.
- The 5800H also has an integrated Radeon (iGPU), but `amdgpu` is **not**
  loaded — the display runs on the NVIDIA dGPU (hybrid laptop with the iGPU
  effectively inactive).

## Storage

```
nvme0n1p1  vfat    300M   on /boot/efi
nvme0n1p2  ext4    931G   on /                        (label kubuntu_2404 — stale)
nvme1n1p1  ext4    1.8T   on /run/media/jpfeiff/MassStorge
```

- Swap: **512 MiB** (`/swapfile`).
- `/tmp` is `tmpfs` (a new `/etc/fstab` line added by the upgrade).
- Two NVMe drives only — no SATA/external bulk drives attached (the desktop has
  five; this laptop has the OS drive plus `MassStorge`).
- The 26.04 upgrade **swapped the NVMe numbering**: the OS drive is now
  `nvme0n1`, `MassStorge` is `nvme1n1`. `MassStorge` also moved mount points —
  from `/media/jpfeiff/MassStorge` to `/run/media/jpfeiff/MassStorge` (newer
  udisks2 mount policy; `/media/jpfeiff/MassStorge` no longer exists). The root
  fs still carries the `kubuntu_2404` label — it was not renamed.

## Network

- Ethernet: Realtek **RTL8111/8168/8211/8411 Gigabit** (`eno1`, currently DOWN).
- Wi-Fi: Realtek **RTL8852AE 802.11ax** (`wlp4s0`, UP — DHCP, currently
  `10.46.86.5/24` plus IPv6 SLAAC addresses).

## Audio

- NVIDIA HDMI/DP audio, plus the AMD **ACP/ACP3X audio coprocessor** and
  **Family 17h/19h HD Audio** controller. PipeWire/WirePlumber stack.

## Battery

- `BAT0`, 99% (fully-charged), design capacity **87.5%** (some degradation).

## Desktop environment

- **KDE Plasma 6.6.6**, Qt 6.10.2, KDE Frameworks 6.24.0 — via
  `kubuntu-desktop`.
- Session: **Wayland** (`XDG_SESSION_TYPE=wayland`), compositor
  **kwin_wayland** (the X11 `kwin_x11` binary is no longer installed).
- Single built-in panel **1920×1080 @ 165 Hz** (`eDP-1`); the external
  DisplayPort/HDMI outputs are present but disconnected.
