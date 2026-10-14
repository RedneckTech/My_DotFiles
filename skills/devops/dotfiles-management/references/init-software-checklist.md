# Regenerating init-software.txt

`init-software.txt` sits at the repo root (git-tracked, NOT stowed — like
`skills/` and `sys_docs/`). It is the reinstall checklist for software
installed outside the default Kubuntu 24.04 install, in five sections:
manually-downloaded binaries, Homebrew, Flatpak, Snap, and Apt. When asked to
"update" or "regenerate" it, re-derive each section from the live system rather
than editing the old list by hand.

## Procedure (run these, then rewrite the file)

1. **Manual binaries** — list `~/.local/bin/`, `~/.local/opt/`, `/usr/local/bin/`,
   and `~/bin/`. `~/.local/bin/` mixes real binaries with symlinks into package
   managers; annotate the symlink targets so a reinstall knows the source:
   - npm globals → `~/.local/lib/node_modules/<pkg>`
   - uv tools → `~/.local/share/uv/tools/<tool>`
   - Hermes/agent tooling → `~/.hermes/...`, `~/.cua-driver`, `~/.hermes/node`
   Also check `~/Documents/System_Setup_Docs/User_Packages/` for AppImages and
   `.deb` files (not just AppImages).

2. **Homebrew** — use `brew leaves`, NOT `brew list --formula`. The latter dumps
   every transitive dependency (hundreds of `lib*`/`qt*` entries); `leaves`
   returns only top-level formulas. `brew list --cask` for casks.

3. **Flatpak** — `flatpak list --app` (omit runtimes).

4. **Snap** — `snap list`, then drop the runtime/base rows (`bare`, `core*`,
   `gnome-*`, `gtk-common-themes`, `mesa-*`, `snapd`, `firmware-updater` is a
   user app — keep it). Keep only the user-facing apps.

5. **Apt** — `apt-mark showmanual`, then filter hard. This list is noisy with
   base-system packages that happen to be marked manual (`base-files`, `bash`,
   `bsdutils`, `grub-*`, `lvm2`, `btrfs-progs`, `xfsprogs`, `reiserfsprogs`,
   `jfsutils`, `kpartx`, `dmraid`, `efibootmgr`, `mokutil`, `shim-signed`,
   `hyphen-*`, `language-pack-*`, `wamerican`/`wbritish`, `openoffice.org-hyphenation`,
   `kubuntu-desktop`, `ubuntu-minimal`/`ubuntu-standard`, `linux-*`). List only
   the genuinely user-installed apps and dev tools (editors, CLIs, compilers,
   virtualization, GPU/ROCm, language servers).

## Pitfalls

- **`apt-mark showmanual` is not a clean app list.** It includes every base
  package the installer marked manual, so copying it verbatim turns the
  checklist into a system-package dump. Filter to user-installed apps; the
  header already says "system packages omitted" — honor it.
- **`brew list --formula` is a dependency dump.** Use `brew leaves` for the
  top-level set; group the intentional apps separately from toolchains/libs
  (`go`, `rust`, `openjdk`, `qt`, `glew`, `glfw`, `sdl2_*`) that are also leaves.
- **`snap list` mixes runtimes with apps.** The `core*`/`gnome-*`/`gtk-*`/`mesa-*`
  rows are bases, not user installs — omit them or the list is unreadable.
- **A package can be installed two ways at once** (e.g. `nvtop` in apt AND a
  newer manual binary in `~/.local/bin/`). Note the version difference in the
  manual-binary section rather than silently dropping one.
- **A CLI tool's `--update` can fail with a decompression error when its
  upstream download URL is deprecated.** "Could not find central directory
  end" / "invalid Zip archive" means the client downloaded HTML (a redirect
  page) instead of the archive — not a local unzip problem. Check the URL with
  `curl -sIL`; if it 301s to an HTML page, the asset moved. Replace the client
  with a newer upstream release binary rather than debugging unzip. Concrete
  case: `tldr.sh/assets/tldr.zip` is deprecated, so the apt `tldr` (Haskell)
  and `tealdeer` < 1.8.0 both fail `--update`; install `tealdeer` ≥ 1.8.0 from
  GitHub releases (prebuilt `tealdeer-linux-x86_64-musl`, verify sha256) to
  `~/.local/bin/` and symlink `tldr` → `tealdeer`.
