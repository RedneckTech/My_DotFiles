# 01 — System & Hardware

## OS

- **Ubuntu 24.04.5 LTS** ("Noble Numbat"), ID `ubuntu`, ID_LIKE `debian`.
- Kernel **6.8.0-142-generic** (`#142-Ubuntu SMP PREEMPT_DYNAMIC`, x86_64) — the
  GA 6.8 kernel, **not** the HWE 7.0 kernel the desktop runs.
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
nvme1n1p1  vfat    300M   on /boot/efi
nvme1n1p2  ext4    931G   on /                        (label kubuntu_2404)
nvme0n1p1  ext4    1.8T   on /media/jpfeiff/MassStorge
```

- Swap: **511 MiB**.
- Two NVMe drives only — no SATA/external bulk drives attached (the desktop has
  five; this laptop has the OS drive plus `MassStorge`).

## Network

- Ethernet: Realtek **RTL8111/8168/8411 Gigabit** (`eno1`, currently DOWN).
- Wi-Fi: Realtek **RTL8852AE 802.11ax** (`wlp4s0`, UP — `10.86.127.5/24`).

## Audio

- NVIDIA HDMI/DP audio, plus the AMD **ACP/ACP3X audio coprocessor** and
  **Family 17h/19h HD Audio** controller. PipeWire/WirePlumber stack.

## Battery

- `BAT0`, 99% (fully-charged), design capacity **87.5%** (some degradation).

## Desktop environment

- **KDE Plasma 5.27.12**, Qt 5.15.13, KDE Frameworks 5.115.0 — via
  `kubuntu-desktop`.
- Session: **X11** (`XDG_SESSION_TYPE=x11`), window manager **kwin**.
- Single built-in panel **1920×1080 @ 165 Hz** (`DP-4`); the external
  DisplayPort/HDMI outputs are present but disconnected.
