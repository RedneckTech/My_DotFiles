---
name: dotfiles-management
description: Use when managing the ~/.user_config dotfiles via stow.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [dotfiles, stow, symlinks, config, setup]
---

# Dotfiles Management (~/.user_config + GNU Stow)

## When to Use

- Reconcile symlinks on a machine ("update stow", "apply the dotfiles").
- Set up a fresh machine from the dotfiles repo.
- A config file is stale or absent in `$HOME` but present in the repo.

The repo `~/.user_config/` (remote `RedneckTech/My_DotFiles`, branch `master`)
is the source of truth. It is split into a shared `home/` package (stowed by
every machine) plus per-host `host-<hostname>/` packages for machine-specific
files; stow links the packages into `~`.

## Agent-created skills (shared `skills/`)

The repo's top-level `skills/` dir is the shared home for Hermes agent-created
(self-improving) skills — the ones NOT in Hermes's bundled catalog. It is
git-tracked but NOT stowed; each host points Hermes at it with BOTH settings:

    hermes config set skills.create_dir '~/.user_config/skills'
    hermes config set skills.external_dirs '["~/.user_config/skills"]'

The two keys do different jobs and BOTH are required:

- `skills.create_dir` — where `skill_manage` writes NEW skills (empty = the
  profile-local `~/.hermes/skills/`). It also feeds the agent's startup skill
  list, but it is NOT scanned by the `skill_view` / `skills_list` tools.
- `skills.external_dirs` — extra read-only dirs the tools DO scan. Without it,
  `skill_view('<name>')` returns "not found" for every shared skill even though
  the files exist and the prompt lists them.

New skills the agent writes land in `create_dir`; edits to existing skills
happen in place. Sync the usual way: commit + push after a session, `git pull`
on the other host.

Caveats: bundled skills stay in `~/.hermes/skills/` (seeded by `hermes update`).
Local `~/.hermes/skills/` takes precedence over the external/create dirs, so a
skill present in both places shadows the shared copy — remove the local
duplicate when a skill moves into `skills/`. Never commit `~/.hermes/skills/`
runtime state (`.curator_ledger.jsonl`, `.usage.json`, `.locks/`,
`.bundled_manifest`).

## Core command

```
# dry run (always first) — home + the current host's package (host pkg optional)
stow -nR --no-folding -d ~/.user_config -t ~ home "host-$(hostname)"
# apply
stow -R  --no-folding -d ~/.user_config -t ~ home "host-$(hostname)"
```

The repo also ships two drivers: `update_dotfiles.sh` (simple: dry-run, confirm,
stow, then commit/push) and `update_dotfiles_safe.sh` (adds `--adopt` conflict
handling with backups to `~/.local/state/dotfiles-stow/backups/<ts>/`). Use the
safe one when a machine has existing-file conflicts.

## Rules

1. **Always pass `--no-folding`.** Without it stow folds whole directories into
   a single symlink, which collides with real dirs that must also hold
   non-managed content — `~/.config/opencode/` must stay a real directory so
   `node_modules/` can live alongside the stowed files.

2. **Host packages hold ALL machine-specific divergence — not just Hermes.**
   The `host-<hostname>/` package is the general home for any file that differs
   between machines: per-host live state, hardware-specific settings, secrets,
   machine-local config, generated/expanded content — anything not identical on
   every box. Rule of thumb: a file belongs in shared `home/` only if every
   machine uses the byte-identical copy; everything else goes in the package of
   the host that owns it.

   Hermes is one instance: `~/.hermes/config.yaml` is live state Hermes rewrites
   at runtime (carries `_config_version`, grows between checks) — put it in
   `host-<hostname>/.hermes/config.yaml` so each machine keeps its own regular
   file. `~/.hermes/SOUL.md` (persona) is read-only and identical everywhere —
   keep it in shared `home/` and let it be symlinked.

   Because the host package IS stowed, the tracked `config.yaml` would otherwise
   be symlinked over the live regular file and abort every stow run. Each host
   package therefore carries a `host-<hostname>/.stow-local-ignore` with
   `^/\.hermes/config\.yaml$` so stow skips it (stow auto-discovers this file;
   no `--ignore` flag or script change needed). The live `~/.hermes/config.yaml`
   is a regular file kept in sync with the host copy via `cp`, never a symlink.

3. **Resolve machine-specific files with a host package, not `--adopt`.**
   `--adopt` MOVES the live file into the repo (overwriting the committed copy)
   then symlinks — it pollutes the repo with the machine's expanded/generated
   content, and a following `-R` restow rolls the whole change back anyway if a
   conflict remains. `--ignore` is a stopgap that leaves the file unmanaged. The
   durable fix is to move the divergent file into `host-<hostname>/` so only the
   owning machine tracks it.

4. **Back up before any destructive stow.** Before `--adopt`, copy both the live
   target AND the repo/package version, plus `git status` / `git diff`
   snapshots. The safe script already does this; reproduce it manually when
   driving stow directly.

5. **Stow is atomic on conflict.** If any target is "neither a link nor a
   directory", the whole operation aborts and nothing is applied. Diagnose with
   the `-n` dry run and read the trailing "would cause conflicts" list — do not
   assume a partial apply happened.

## Secrets convention

Secrets live in gitignored `.env` files under the repo (e.g.
`home/.config/opencode/.env`) and are sourced by `~/.bashrc`. Whenever you touch
one (full treatment in the `mcp-server-setup` skill):

- **`export` the value, don't assign it bare.** `~/.bashrc` sources the file with
  plain `.`, and a bare `KEY=value` is shell-local — child processes don't
  inherit it. Write `export KEY=value`.
- **Gitignore before creating.** A fresh repo's `.gitignore` often doesn't cover
  `.env`; `git check-ignore` it first, add the path if missing, then `chmod 600`.
