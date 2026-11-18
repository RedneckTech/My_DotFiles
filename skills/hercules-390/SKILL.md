---
name: hercules-390
description: "Build & deploy the Hercules Hyperion mainframe emulator."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hercules, mainframe, s390, mvs, emulation, autotools, build]
    related_skills: [x3270-scripting]
---

# Hercules (Hyperion) — build & deploy

## When to Use

- Building Hercules Hyperion from source on this workstation (new version, fresh checkout, reinstall).
- Deploying a relocatable, self-contained copy of the build into a guest dir (MVS_38, S_390) or elsewhere.
- Making an autotools-built binary set run from a directory other than its build tree (the $ORIGIN rpath technique generalizes beyond Hercules).
- Choosing/configuring a guest OS (NUMCPU, MAINSIZE, ARCHMODE) — per-OS CPU/storage limits and licensing rules live in references/guest-os-limits.md.

Source lives at ~/MainFrames/hyperion (git master). Guest dirs MVS_38/ and S_390/ hold one self-contained copy each for MVS 3.8 and S/390 guests. Build in-tree, then copy the real binaries out.

## Build (this workstation, Ubuntu + linuxbrew)

1. Missing -dev headers come from linuxbrew, not system apt: zlib, bzip2, and ltdl all live under /home/linuxbrew/.linuxbrew (the libtool formula ships ltdl.h and libltdl.so). Pass them explicitly:

       CPPFLAGS="-I/home/linuxbrew/.linuxbrew/include" \
       LDFLAGS="-L/home/linuxbrew/.linuxbrew/lib -Wl,-rpath,/home/linuxbrew/.linuxbrew/lib" \
       ./configure

2. Do NOT pass --with-ltdl-lib=/home/linuxbrew/.linuxbrew/lib — it requires a libltdl.la, which linuxbrew does not install, and configure aborts with "invalid ltdl library directory". The CPPFLAGS/LDFLAGS alone satisfy the lt_dlopen check.

3. util/bldlvlck is noisy: it flags autoconf/automake/flex/gawk as missing, but none are needed — configure and Makefile.in are pre-generated in the git tree, and the build uses mawk, not gawk. The only hard dep is libltdl, covered by linuxbrew above.

4. make -j16 (24-core box). The top-level executables are libtool wrapper scripts; the REAL ELF binaries are in .libs/. Always copy from .libs/, never the wrappers.

## Install for use from anywhere (make install)

For a normal "start it from anywhere" install (per-user, no sudo): configure with `--prefix="$HOME/.local"` (already first on this box's PATH), `make -j16`, `make install`. Installs hercules + ~40 utilities to ~/.local/bin, libherc*.so to ~/.local/lib, and the 17 device modules + dyncrypt/dyngui to ~/.local/lib/hercules — MODULESDIR resolves correctly, no HHC01536W warning. libtool relinks at install with an rpath to ~/.local/lib, so libherc*.so resolve without touching ld.so.conf (the "add LIBDIR to /etc/ld.so.conf" warning is cosmetic here). System-wide (/usr/local) needs sudo, which the agent can't supply — have the user re-configure with the default prefix and run `sudo make install` themselves.

PITFALL: `-DMODULESDIR="$(modexecdir)"` (and PKGDATADIR/HERC_LOCALEDIR) are passed via CPPFLAGS and baked into .o files at compile time. Re-running configure with a different --prefix does NOT recompile them — make reports "Nothing to be done" and the OLD paths stay baked in. After any --prefix change, run `make clean && make -j16` before `make install`. Verify with `strings .libs/hercules | grep /local/lib/hercules`.

## Deploy a relocatable, self-contained copy

The build output is: hercules + ~40 utilities (dasdinit, dasdconv, cckdcdsk, hetget, tapecopy, vmfplc2, …) + 5 shared libs (libherc.so, libhercd.so, libhercs.so, libherct.so, libhercu.so) + 19 device modules (hdt*.so, dyngui.so, dyncrypt.so). Binaries link against libherc*.so, so a naive copy won't run.

1. Copy all real ELF binaries + libherc*.so + hdt*.so + dyngui.so + dyncrypt.so + a sample hercules.cnf into the target dir. Skip libhdt3420_not_mod.so (build artifact, not loadable).

2. Set $ORIGIN rpath on EVERY ELF file in the dir so each resolves its deps from its own directory — this makes the copy portable:

       patchelf --set-rpath '$ORIGIN' <file>    # brew install patchelf if missing

3. Device modules are dlopen'd at runtime. hercules's own RUNPATH=$ORIGIN lets dlopen find hdt*.so in the executable's dir, even though the compile-time MODULESDIR is wrong (see below).

4. Startup warning "HHC01536W '/usr/local/lib/hercules' is not a valid directory" is cosmetic: MODULESDIR is hardcoded to $(libdir)/hercules and cannot be made relative, but modules load anyway via the $ORIGIN dlopen fallback (proven: dyncrypt/hdteq preload + device modules all open from the executable's dir). Silence it with HERCULES_LIB="$PWD" ./hercules or -p "$PWD".

5. Verify the copy actually runs, don't assume: ./hercules --version and ./dasdinit from inside the dir, then confirm module loading with strace — open a config that attaches a device (e.g. a 3420 tape) and check the .so opens resolve to the target dir:

       strace -f -e trace=openat -o /tmp/trace.log timeout 4 ./hercules -f cfg.cnf
       grep '\.so' /tmp/trace.log

## Notes

- System libz.so.1 and libbz2.so.1.0 exist under /lib/x86_64-linux-gnu, so they resolve from system paths even with a pure $ORIGIN rpath — no need to bundle them.
- In-tree build leaves .libs/ and .o artifacts in the source tree; that is normal.
- Each deployed dir is ~75 MB / 66 files. Identical file sets across guest dirs are expected (same build).
