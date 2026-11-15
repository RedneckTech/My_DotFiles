# TIMESHARING BASIC/3270BBS — Learning & Testing

A scratch area for learning the TIMESHARING BASIC language on the 3270BBS
dev server and for documenting how to write quality code on it.

## What's here

- `MANUAL_ERRATA_FOR_DEV.md` — **report for the BASIC/3270BBS developer**:
  the item-by-item resolution of the old manual-vs-interpreter mismatches
  (all fixed in v3.0.1), the one remaining open item, and the 3.0.1
  behavior changes.
- `LANGUAGE_REFERENCE.md` — the full language reference: every statement,
  function, command, error, and limit, all verified live against v3.0.1.
  This is the authoritative doc.
- `ARRAYS_REFERENCE.md` — `DIM`/`OPTION BASE`, numeric/string/associative
  arrays, type-suffixed arrays, records, and the array limits (dimension
  10,000; 65,535 total elements).
- `DEF_FN_REFERENCE.md` — deep dive on user-defined functions (`DEF FN`):
  naming, parameters, return types, scope, recursion, and gotchas.
- `BOXCHAR_CP310_REFERENCE.md` — the box-drawing and graphics character
  functions: full character tables, argument handling, and the x3270
  rendering caveat.
- `UI_PANELS.md` — a cookbook for building terminal UIs and panels:
  BOXCHAR$/CP310$ rendering table (x3270 and c3270), the TAB function
  (absolute, byte-counted — use SPACE$ after box chars), boxes, panels,
  tables, progress bars, centering, and gotchas.
- `CHAIN_REFERENCE.md` — program chaining (`COMMON`/`CHAIN`): how variables
  cross program boundaries, what persists, nesting, and recursion.
- `GOTO_GOSUB_REFERENCE.md` — jumps and subroutines: `GOTO`, `GOSUB`/
  `RETURN`, and `ON…GOTO`/`ON…GOSUB`, including target-mode rules, the
  exact index semantics, error messages, and the 1024-level recursion limit.
- `SELECT_CASE_REFERENCE.md` — the `SELECT CASE` block: exact lists, `TO`
  ranges, `IS` comparisons, mixing all three, `CASE ELSE`, first-match-wins,
  and string vs numeric matching (identical in both modes).
- `ISAM_REFERENCE.md` — indexed files: the four operations, status
  functions, the schemaless record model, the PUT-clears-array semantics,
  and the on-disk format.
- `FILE_IO_REFERENCE.md` — sequential file I/O: OPEN modes, the 1-8 handle
  range, PRINT #/INPUT # semantics, error messages, and the buffered-write
  behavior.
- `TIME_REFERENCE.md` — date/time functions: formats, SLEEP range, the
  STR$/TRIM$ padding gotcha, and the execution-time limit / SLEEP credit.
- `STRING_REFERENCE.md` — string functions: every function with edge cases,
  the 2048-byte string limit, the STR$ leading-space behavior, and
  case-sensitive comparison.
- `MATH_REFERENCE.md` — math functions and operators: RND's real semantics,
  operator precedence, error cases, and the missing ROUND/CEIL/FLOOR/MIN/MAX.
- `STYLE_GUIDE.md` — how to write clean, maintainable BASIC (the code
  quality guide).
- `STACK_REFERENCE.md` — how to build a LIFO stack (array + top pointer +
  GOSUB subroutines): numeric and string stacks, multiple stacks, a queue,
  overflow/underflow, capacity, and gotchas.
- `BBS_DATA_REFERENCE.md` — the live BBS data sources: `$UserInfo`,
  `$TermInfo`, `$Mail`, `$ChatMessage`, `$Topic`, `$Post` — every key and
  the shared record rules.
- `MODERN_PATTERNS_REFERENCE.md` — modern coding concepts in this BASIC:
  recursion (frame stacks), memoization, sorting, searching, linked lists,
  binary trees, objects, and the no-short-circuit gotcha — all verified.
- `NOTES.md` — gotchas and version differences (v3.0.1), and automation
  notes.
- `examples/` — runnable `.bas` programs with verified output.
- `drive.py` — minimal helper to drive the persistent `x3270 -script`
  session (see below).
- `drive_c3270.py` — same helper for a `c3270 -scriptport` session (TCP
  instead of the FIFO; see "c3270 instead of x3270" below).

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

Escaping rule: inside `String("...")`, escape `\"` as `\\\"`. When passing
actions as shell args, use single quotes with SINGLE backslashes.

## c3270 instead of x3270

`c3270` is the curses (terminal) member of the same x3270 suite — same
version here (4.1ga10), same actions and status line, but no X11. Use it
when working over SSH or on a headless box.

Differences that matter:

- **No `-script`.** c3270 rejects it. It exposes the s3270 protocol on a
  TCP port with `-scriptport <port>` (or a UNIX socket with `-socket`).
- **Needs a tty.** It is curses-based. From a non-interactive shell, run it
  under a pty: `script -qec /path/to/launch.sh /tmp/c3270.typescript`.
- **Same protocol.** Actions (`String`, `Tab`, `Enter`, `PF(n)`, `Ascii`,
  `Query(...)`) behave identically; `drive_c3270.py` speaks it.

Launch (pty + script port):

```bash
cat > /tmp/start_c3270.sh <<'EOF'
#!/bin/sh
exec c3270 -model 3279-2 -scriptport 12352 192.168.122.151:3270
EOF
chmod +x /tmp/start_c3270.sh
script -qec /tmp/start_c3270.sh /tmp/c3270.typescript &
```

Drive it exactly like `drive.py`, but against the port:

```bash
python3 drive_c3270.py --port 12352 --raw
python3 drive_c3270.py --port 12352 --wait 5 \
  'String("admin")' Tab 'String("admin")' Enter
```

### Models and screen sizes (tested)

c3270 supports `-model 3278|3279-[2-5]` and `-oversize <cols>x<rows>`, and
locally reports the larger size (`Model 3279-5-E, 43 rows x 132 cols`).
**But this BBS stays at 24x80:**

- Models 3/4/5 have a *default* 24x80 screen; the larger size is the
  *alternate* screen, entered only when the host sends Erase/Write
  Alternate. `tsu` never does.
- `-oversize` makes c3270 send `IBM-DYNAMIC`; the server ignores it and
  falls back to model 2.
- The status line and `Query(Model)` both report `IBM-3279-2-E` / `2 24 80`
  regardless of `-model` or `-oversize`.

So the model/oversize options are real c3270 features, but they buy
nothing on this host. The win over x3270 is headless operation, not a
bigger screen.

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
