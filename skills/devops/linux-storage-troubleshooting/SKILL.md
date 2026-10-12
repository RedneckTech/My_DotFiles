---
name: linux-storage-troubleshooting
description: Use when diagnosing a missing or undetected drive on Linux.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [linux, storage, disk, sata, hardware, troubleshooting]
    related_skills: []
---

# Linux Storage Troubleshooting

## When to Use

- A drive is missing, unmounted, or not showing up in the file manager.
- A fstab mount fails at boot or a mount point is unexpectedly empty.
- A drive is plugged in and powered but not detected.

Diagnose why a drive is missing, unmounted, or not showing up. Work the ladder top-down: config → block device → hardware link. Each step narrows whether the problem is a mount config issue, a filesystem/UUID mismatch, or a physical/data-cable failure.

## Procedure

1. **Read the expected mount config.**
   `grep -iE 'media|uuid|ext4|ntfs|exfat' /etc/fstab`
   Note the UUID and mount point of the drive in question.

2. **List what is actually connected and mounted.**
   `lsblk -o NAME,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINTS`
   `sudo blkid`  (authoritative filesystem/UUID info)
   Match each fstab UUID against the connected devices. A fstab UUID that matches no connected device means the drive is not detected — not a mount error.

3. **If the UUID is absent, check the hardware link.**
   `sudo journalctl -b | grep -iE 'ata[0-9]+:|ahci|link down|link is'`
   Look for the SATA controller init and per-port link status.

4. **Confirm per-port link state from sysfs.**
   `find /sys/devices -name sata_spd -exec sh -c 'echo "{}: $(cat {})"' \;`
   `<unknown>` on every port = no device negotiating on any SATA port.

## Interpreting the result

- **`SATA link down (SStatus 0 SControl 300)`** = the SATA PHY sees no device signal at all. This is a physical/data-cable problem, NOT a filesystem or UUID problem. Power may be connected while the data link is dead. Causes, in order: SATA data cable loose/disconnected, bad dock/enclosure data connection, drive controller failure (spins but won't negotiate), SATA port disabled in BIOS.
- **Drive present in `lsblk` but not mounted** = mount config or UUID mismatch; fix fstab, don't chase hardware.
- **Drive present but wrong UUID** = filesystem was reformatted or cloned; update fstab to the new UUID.

## Pitfalls

- `lsblk -f` can show empty FSTYPE/LABEL/UUID columns for mounted drives (the fs info read fails silently). Use `sudo blkid` for authoritative filesystem/UUID data — never conclude a drive is unformatted from `lsblk -f` alone.
- `dmesg` may be restricted (`kernel.dmesg_restrict`) or its ring buffer cleared, returning nothing for disk events. Use `sudo journalctl -b` for boot-time hardware detection instead.
- A USB device visible in `lsusb` but absent from `lsblk`/`blkid` is not enumerating as storage (dead card, reader with no media, or USB enumeration failure) — it is not the drive you are looking for unless the user says so.
- The mount point directory persisting (empty, root-owned) after a drive disappears is normal — it does not mean the drive is still there. Check the device, not the directory.
- `SStatus 0` specifically means no signal at the PHY layer. Do not waste time on filesystem repair (`fsck`) or remount attempts when the link is down — the drive is not reachable at all.
