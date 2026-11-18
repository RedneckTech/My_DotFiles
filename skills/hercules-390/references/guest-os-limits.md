# Guest OS limits & licensing (what can run on the deployed copy)

Use this when choosing/configuring a guest (NUMCPU, MAINSIZE, ARCHMODE) or when a user asks about running a specific IBM OS.

## Architecture modes in this Hyperion build

S/370, ESA/390, z/Arch. There is NO S/380 mode in standard Hyperion (verified: no S/380 anywhere in the source tree) — see MVS/380 below.

## CPU count: hardware ceiling vs OS limit

"Max CPU Engines" printed at startup is the HARDWARE emulation ceiling (this build: 128) — how many processors the emulated z/Arch machine can be configured with. It is not a recommendation. NUMCPU is a per-guest choice, and the guest OS's own software limit governs how many CPUs it actually drives. MVS 3.8 using 2 CPUs while the hardware allows 128 is not a contradiction.

## Per-OS limits

- MVS 3.8 (MVS/370, the free 3.8j): ARCHMODE S/370, 24-bit. Max 2 CPUs (symmetric, tightly-coupled MP). Max 16 MB — the "16 MB line" is architectural (2^24), applies to BOTH real and virtual storage, and is unaffected by CPU count: two CPUs share one 16 MB real store, not 16 each. Config: `MAINSIZE 16`, `NUMCPU 2` (1 is more common in practice).
- VM/370 (Release 6, free): ARCHMODE S/370, 24-bit. Max 2 CPUs but ASYMMETRIC — one main CPU plus an "attached processor" (APU) that has no I/O capability; VM/370 does I/O on the main CPU only. 16 MB. Usually run `NUMCPU 1`.
- MVS/380: MVS 3.8j patched for AMODE 31 (31-bit apps), still 2 CPUs / 16 MB base. Does NOT run on standard Hyperion — it requires the S/380 architecture in the Hercules/380 fork (based on old Hercules 3.07). "380" = 370 + 31-bit, nothing to do with CPU count.
- OS/390 V1R2: ESA/390, 31-bit. Licensed only — see below.
- z/OS (ADCD): z/Arch, 64-bit. Licensed only — see below.

## Licensing (governs "install OS/390 / z/OS" requests)

- Freely distributable IBM mainframe OSes: MVS 3.8j and VM/370 R6 only. These are the zero-license options and the realistic hobbyist route (MVS 3.8j / TK4- turnkey, or VM/370 SixPack).
- OS/390 and z/OS are IBM-proprietary and NOT freely obtainable. IBM no longer sells or distributes OS/390 (out of support for decades); the current equivalent is z/OS via a license.
- ADCD / DemoPkg (pre-built DASD for OS/390 or z/OS): time-limited (hard-coded expiration date checked against the TOD clock at IPL/runtime), licensed to ONE machine by type/model/serial, non-transferable, IBM employees / qualified Business Partners only, development use only. License terms expressly prohibit running it on Hercules or any non-approved emulator (FLEX-ES was the sanctioned one).
- Do NOT help run ADCD/DemoPkg on Hercules, and do NOT help circumvent the expiration date. Redirect to MVS 3.8j / TK4- / VM/370 instead.
