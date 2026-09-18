# 01 — System & Hardware

## OS

- **Ubuntu 24.04.5 LTS** ("Noble Numbat"), ID `ubuntu`, ID_LIKE `debian`.
- Kernel **7.0.0-31-generic** (`#31~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC`,
  x86_64) — the Ubuntu HWE kernel; `PREEMPT_DYNAMIC` (desktop-lowlatency
  preemption available via `preempt=full`).
- Hostname: `jacob-x570aorusultra`. Machine ID `7553d15a…`.
- User: `jpfeiff` (UID 1000), in groups `sudo`, `adm`, `libvirt`, `plugdev`,
  `sambashare`, `dip`, `cdrom`, `lpadmin`.

## Motherboard / firmware

- Gigabyte **X570 AORUS ULTRA** (AM4). BIOS **F22** (2020-08-20).
- UEFI boot (`/boot/efi`, vfat, 301 MB, grub-efi-amd64-signed).

## CPU

- AMD **Ryzen 9 3900X**, 12 cores / 24 threads, Zen 2, 1 socket.

## Memory

- **32 GB** (reports 31 GiB) DDR4.

## GPU

- AMD **Radeon RX 9070 XT** (RDNA4, `gfx1201`), ASUS board, **16 GB** VRAM.
- Driver: open-source Mesa **radeonsi** + kernel `amdgpu`; LLVM 20.1.2;
  DRM 3.64. Works over X11 (Plasma x11 session).
- Also present: `mesa-vulkan-drivers` (apt) and Homebrew `mesa` — two Mesa
  installs coexist; the rendering stack resolves to the one on the lib path.
- Monitoring tools installed: `nvtop`, `radeontop`, `glances`.

## Storage

```
/dev/nvme0n1p2  ext4    916G   on /                      (root)
/dev/nvme0n1p1  vfat    301M   on /boot/efi
/dev/nvme1n1p1  ext4    1.8T   on /media/jpfeiff/MassStorge
/dev/sda1       ext4    452G   on /media/jpfeiff/BlackBox   (3270BBS project lives here)
/dev/sdb1       exfat   11T    on /media/jpfeiff/DataCore
/dev/sdc1       ext4    9.1T   on /media/jpfeiff/NeonDrive
```

- `/dev/sda1` (BlackBox, 452 G) is where the 3270 BBS server project is
  checked out (`/media/jpfeiff/BlackBox/3270BBS`).
- `MassStorge` is the literal (typo'd) volume label on the 1.8 T drive.

## Network

- Ethernet: Intel **I211 Gigabit** (rev 03).
- Wi-Fi: Intel **Wi-Fi 6 AX200** (rev 1a).

## Audio

- Two AMD HD audio devices (the RX 9070 XT's HDMI/DP audio `ab40`, plus the
  X570 board's Starship/Matisse HDA). PipeWire/WirePlumber sound stack
  (see systemd doc).

## Desktop environment

- **KDE Plasma 5.27.12**, Qt 5.15.13, KDE Frameworks 5.115.0 — installed via
  the `kubuntu-desktop` meta-package.
- Session: **X11** (`XDG_SESSION_TYPE=x11`), window manager **kwin**.
- 3 monitors, all 2560×1440: `DisplayPort-1`, `DisplayPort-2` (primary),
  `HDMI-A-0`.
