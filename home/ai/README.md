# ai/ — shared AI assets

A home in the dotfiles repo for things the AI assistants (Hermes, OpenCode
agents, etc.) need on **every** machine:

- `scripts/` — small reusable helper scripts that come up again and again.
- `references/` — verified, authoritative reference documents (the ones the
  AI should trust over any vendor/manual prose).

The tree lives in the shared `home/` stow package, so **stow links it at
`~/ai/`** — use that path (`~/ai/scripts/...`, `~/ai/references/...`). Edit
the files in the repo (`home/ai/...`); `~/ai/` is just the symlink view.

```
~/ai/                        (stowed from home/ai/)
  scripts/
    x3270/    drive.py          drive a persistent x3270 -script session (fifo)
    bbs/      uploader.py       type a local BASIC/assembler file into the BBS ISPF editor
              fetch.py          pull BBS program files back into a repo
  references/
    timesharing-basic/          TIMESHARING BASIC/3270BBS v3.0.0 (verified live)
```

## Conventions

- **Scripts are copied in, not moved.** The working copy stays in its project
  repo; this is the portable, cross-machine copy. When you improve one,
  re-copy it here (or, better, replace it with a thin shim that calls the
  project copy — see "Canonical copy" in `scripts/README.md`).
- **References are copies of a project's verified doc set.** Each subject
  gets its own subdirectory with its own `README.md` index.
- One subject per subdirectory; keep filenames stable so agent prompts that
  point at them don't break.

## Adding things

- New script → put it under the matching `scripts/<tool>/` dir, `chmod +x`,
  add a row to `scripts/README.md`.
- New reference set → `references/<subject>/` with a `README.md` index, and
  add it to the list in `references/README.md`.
