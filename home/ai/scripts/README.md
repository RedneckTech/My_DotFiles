# ai/scripts/ — reusable AI helper scripts

Small scripts that come up again and again across sessions and projects.
Stowed at `~/ai/scripts/`; run them by path (not on `$PATH`):

```bash
python3 ~/ai/scripts/<tool>/<script>.py [args]
```

| Script | What it does |
|--------|--------------|
| `x3270/drive.py` | Drive a persistent `x3270 -script` session through its fifo: send a batch of actions, wait, print the current screen. |
| `bbs/uploader.py` | Type a local BASIC/assembler source file into the 3270BBS ISPF editor over x3270, then `SAVE` + `CHECK`. |
| `bbs/fetch.py` | Pull BBS program/data files (`*.bas *.asm *.list *.idx *.dat`) back into a repo, one commit per program. |

## x3270/drive.py — the fifo driver

Generic 3270 automation helper. It assumes a session already running as:

```bash
mkfifo /tmp/x3270.fifo
setsid x3270 -script -model 3279-2 <host>:3270 > /tmp/x3270.out 2>&1 < /tmp/x3270.fifo &
setsid sh -c 'sleep 86400 > /tmp/x3270.fifo' &   # keeps the fifo open
```

Then:

```bash
python3 drive.py --raw                              # dump the current screen
python3 drive.py --wait 5 'String("RUN")' Enter     # send actions, print screen
```

`FIFO=/tmp/x3270.fifo`, `OUT=/tmp/x3270.out` are hardcoded — edit for a
different session. Escaping: inside `String("...")` escape `"` as `\"`.

## bbs/uploader.py + bbs/fetch.py — the BBS round trip

Both drive an **already-logged-in** x3270 session at the BASIC `READY`
prompt (neither logs in). Prerequisites for `uploader.py`: BBS filename =
basename with no `_`, ASCII only, lines ≤ 71 chars.

```bash
python3 uploader.py FILE.bas --verify      # type it in, SAVE, CHECK
python3 fetch.py                            # pull files into <repo>/bbs (no commit)
python3 fetch.py --commit                   # pull + one commit per program
python3 fetch.py --dry-run                  # list remote files only
```

`fetch.py` resolves the target repo from `git rev-parse --show-toplevel` of
the cwd, so `cd` into the project and run it — no `--dest` needed. It only
adds/updates; it never deletes.

## Canonical copy

These are **copies** of scripts that live with their projects:

| Here | Canonical working copy |
|------|------------------------|
| `x3270/drive.py` | `/media/jpfeiff/BlackBox/3270BBS/basic-learning/drive.py` |
| `bbs/uploader.py` | `/media/jpfeiff/BlackBox/3270BBS/bbs-server/uploader.py` |
| `bbs/fetch.py` | `/media/jpfeiff/BlackBox/3270BBS/bbs-server/fetch.py` |

Improve the project copy first, then re-copy it here so every machine gets
the update. If a script becomes broadly useful, consider replacing this copy
with a thin shim that `exec`s the project copy, so there is only one body to
maintain.
