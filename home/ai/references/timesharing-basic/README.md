# TIMESHARING BASIC/3270BBS — Learning & Testing

A scratch area for learning the TIMESHARING BASIC language on the 3270BBS
dev server and for documenting how to write quality code on it.

## What's here

- `MANUAL_ERRATA_FOR_DEV.md` — **report for the BASIC/3270BBS developer**:
  every place the shipped manual (v2.9.2) disagrees with the running
  interpreter (v3.0.0), plus interpreter bugs found in testing.
- `LANGUAGE_REFERENCE.md` — the full language reference: every statement,
  function, command, error, and limit, all verified live against v3.0.0.
  This is the authoritative doc.
- `DEF_FN_REFERENCE.md` — deep dive on user-defined functions (`DEF FN`):
  naming, parameters, return types, scope, recursion, and gotchas.
- `BOXCHAR_CP310_REFERENCE.md` — the box-drawing and graphics character
  functions: full character tables, argument handling, and the x3270
  rendering caveat.
- `UI_PANELS.md` — a cookbook for building terminal UIs and panels with
  BOXCHAR$/CP310$: boxes, grids, progress bars, centering, and reusable
  subroutines.
- `CHAIN_REFERENCE.md` — program chaining (`COMMON`/`CHAIN`): how variables
  cross program boundaries, what persists, nesting, and recursion.
- `ISAM_REFERENCE.md` — indexed files: the four operations, status
  functions, the schemaless record model, the `PUT`/`GET` array-reuse
  gotcha, and the on-disk format.
- `FILE_IO_REFERENCE.md` — sequential file I/O: OPEN modes, the 1-8 handle
  range, PRINT #/INPUT # semantics, error messages, and the buffered-write
  behavior.
- `TIME_REFERENCE.md` — date/time functions: formats, SLEEP range, the
  STR$/TRIM$ padding gotcha, and the execution-time limit / SLEEP credit.
- `STRING_REFERENCE.md` — string functions: every function with edge cases,
  the 2048-byte string limit, the STR$ compile-time/runtime bug, and
  case-sensitive comparison.
- `MATH_REFERENCE.md` — math functions and operators: RND's real semantics,
  operator precedence, error cases, and the missing ROUND/CEIL/FLOOR/MIN/MAX.
- `STYLE_GUIDE.md` — how to write clean, maintainable BASIC (the code
  quality guide).
- `NOTES.md` — gotchas, version differences (v3.0.0 vs the v2.9.2 manual),
  and automation notes.
- `examples/` — runnable `.bas` programs with verified output.
- `drive.py` — minimal helper to drive the persistent `x3270 -script`
  session (see below).

## Environment

- Dev server: `ssh 3270BBS` (libvirt VM `virtserv`, user `dev`), BBS binary
  `tsu` at `~/3270BBS`, TN3270 on `192.168.122.151:3270` (DHCP — IP drifts).
- BASIC is reached from the main menu via `M;B` (Extended Menu → BASIC).
- Login `admin` / `admin`; skip the first-login profile screen with PF(3).
- Programs are flat files: `basic/<user>/*.bas` (source), `*.list` (CHECK
  listings), `*.dat`/`*.idx` (data). Pull them back with
  `bbs-server/fetch.py`.

## Quick start (drive the live session)

The session is a persistent `x3270 -script` process reading actions from
`/tmp/x3270.fifo` and writing to `/tmp/x3270.out`. `drive.py` sends a batch
of actions and prints the current screen:

```bash
# dump the current screen
python3 drive.py --raw

# enter and run a program
python3 drive.py --wait 5 \
  'String("NEW")' Enter \
  'String("10 PRINT \"Hello\"")' Enter \
  'String("RUN")' Enter
```

Escaping rule: inside `String("...")`, escape `"` as `\"`. When passing
actions as shell args, use single quotes with SINGLE backslashes.

## Verified language surface

Tested live and confirmed working: line-numbered and label-based programs
(via LOAD), `PRINT` (incl. `COLOR`), `LET`/implicit assignment, `INPUT`,
`IF/THEN/ELSE` (single-line and block), `FOR/NEXT`, `WHILE/WEND`,
`SELECT CASE`, `GOSUB/RETURN`, `DEF FN`, `DIM` (numeric, string, and
associative `{}` arrays), string functions (`LEN`, `LEFT$`, `RIGHT$`,
`MID$`, `REPLACE$`, `INSTR`, `STR$`, `VAL`, `CHR$`, `ASC`, `UCASE$`,
`LCASE$`), math functions (`ABS`, `INT`, `SGN`, `SQRT`/`SQR`, `SIN`, `COS`,
`LOG`, `EXP`, `PI`, `RADIANS`, `DEGREES`), time functions (`DATE$`,
`TIME$`, `YEAR`, `MONTH`, `DAY`, `HOUR`, `MINUTE`, `SECOND`, `TIMER`),
file I/O (`OPEN`/`PRINT #`/`INPUT #`/`CLOSE`/`EOF`), `SAVE`/`LOAD`/`FILES`,
`CHECK`/`VIEW`, and BBS data access (`$UserInfo`, `$TermInfo`).

See STYLE_GUIDE.md and NOTES.md for the details and the gotchas.
