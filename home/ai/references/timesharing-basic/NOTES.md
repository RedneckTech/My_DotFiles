# TIMESHARING BASIC/3270BBS — Notes, Gotchas, and Version Differences

Findings from live testing against the dev server (v3.0.0). The bundled
`basic_manual.md` documents v2.9.2; several things have changed or behave
differently. Everything below was verified by actually running it.

## Version

The dev server runs **TIMESHARING BASIC/3270BBS V3.0.0**. The manual in the
repo (and on the host, and at the tinyurl link) is still v2.9.2. Treat the
manual as mostly-correct but verify against the live interpreter.

## Top gotchas (the ones that will bite you)

- **`+` is string concatenation when either operand is a string.**
  `"5" + 3` = `"53"` (not `8`), `A$ + 1` = `"hello1"`. No type error.
- **`INT()` floors, not truncates.** `INT(-3.7)` = `-4`.
- **`DEF FN` parameter shadows a global of the same name.** `DEF FND(X) =
  SQR(X^2 + Y^2)` with `X=3: Y=4` gives `FND(0)` = `4`, not the manual's `5`.
- **Division by zero is `?DIVISION BY ZERO`** (terminates the program); same
  for `x MOD 0`.
- **`RND` argument is a range, not a seed.** `RND(0)` = random float
  `[0,1)`; `RND(n)` = random integer `[1,n]`; `RND(1)` = `1` (always).
  See MATH_REFERENCE.md.
- **`PRINT #n` uses the same comma(tab)/semicolon(concat) rules as screen
  `PRINT`** — no special padding.
- **File handles are `#1`-`#8`, not `#1`-`#4`** (manual and error text are
  both wrong). `INPUT #` reads one line per variable and cannot target an
  array element. Writes are buffered until `CLOSE`/normal end. See
  FILE_IO_REFERENCE.md.
- **`VARS` lists simple variables only, not arrays.**
- **The 8-char label limit is NOT enforced** — 24-char labels run fine.
- **`$UserInfo` `country` returned the username** (`"admin"`) on this box.
- **`STR$` differs between literal and variable args** — `STR$(5)`→`"5"` but
  `STR$(H)`→`" 5"` (optimizer precomputes the literal without the space).
  Wrap in `TRIM$`. See STRING_REFERENCE.md.
- **Strings cap at 2048 bytes** (`?STRING TOO LONG`); `SPACE$` caps at 255.
- **String comparison is case-sensitive, ASCII order.**
- **`FN`-prefixed variable names are unusable** — `FNA = 100` stores, but
  `PRINT FNA` prints blank (parsed as a function reference). See
  DEF_FN_REFERENCE.md.
- **ISAM `PUT`/`GET` do NOT clear the record array** — fields from the
  previous operation leak into the next record. Re-`DIM arr{}` before each
  PUT/GET. See ISAM_REFERENCE.md.

Full details in LANGUAGE_REFERENCE.md.

## Label mode: LOAD works, interactive entry does not

- `LOAD "prog.bas"` of a label-based file works and reports
  `LOADED prog.bas (N LINES) (LABEL MODE)`.
- Typing a label program interactively at the `>` prompt FAILS:
  - `START:` alone → `?SYNTAX ERROR`
  - `START: PRINT 1` → `?SYNTAX ERROR`
- Root cause: the `:` is parsed as a statement separator, so a bare label
  is not a valid statement. Label detection happens when the whole program
  is parsed (LOAD/RUN), not line-by-line.
- Practical consequence: write label-based programs to a `.bas` file and
  `LOAD` them, or enter them through the ISPF editor (`EDIT`). The
  `uploader.py` workflow (type into ISPF editor → save → load) is the
  supported path for label programs.

## CHECK warnings: only loop-without-SLEEP is active

The v2.9.2 manual lists four warning categories. In v3.0.0:

| Manual warning | v3.0.0 status |
|----------------|---------------|
| Loop without SLEEP | ACTIVE (verified) |
| Overly complex lines (3+ statements) | NOT triggered (4-statement line passed clean) |
| Very long lines (>120 chars) | not tested |
| Insufficient comments (<1 REM/10 lines) | NOT triggered (13-line, 0-comment program passed clean) |

Do not rely on CHECK to enforce comment density or line simplicity.

## RND() argument semantics differ from the manual

The manual says `RND(x)` returns a random number 0–1. Observed behavior:

```
RND(1)   -> 1            (deterministic, always 1)
RND(0)   -> 0.264532...  (random float)
RND(100) -> 89           (random integer in range)
```

So the argument is a RANGE, not a seed, and `RND(1)` is a degenerate case
that returns 1. For a random float use `RND(0)`; for a random integer in
`[0, n)` use `RND(n)`. Verify before relying on it.

## Arrays are 0-indexed

`DIM A(3)` creates `A(0)`..`A(3)` (4 elements). `DIM N$(2)` creates
`N$(0)`..`N$(2)`. The manual's examples use both `A(1)` and `N$(0)`, which
is consistent with 0-based indexing.

## The optimizer is real and visible

`CHECK`'s OPTIMIZER REPORT shows constant folding and function
precomputation applied at compile time. Verified:

```
10 X = 2 + 3 * 4        ->  CONSTANT_FOLD 3*4 -> 12, 2+12 -> 14
20 Y = 3.14159 * 10 * 10 ->  CONSTANT_FOLD (two steps) -> 314.159
30 Z = LEN("Hello")      ->  FUNC_PRECOMPUTE -> 5
40 A = ASC("A")          ->  FUNC_PRECOMPUTE -> 65
```

## BBS data access works from BASIC

Verified live:
- `$UserInfo` → `{"username": "admin", "country": ""}`
- `$TermInfo` → `{"model": "Mod2", "codepage": "310"}`
- `$ChatMessage(n)`, `$Mail(n)`, `$Topic(n)`, `$Post(id, n)` are available
  (not all exercised; see the manual for key names).

## uploader.py --verify (FIXED)

`uploader.py --verify` used to type `load "name"` and `check` into the ISPF
editor as DATA LINES instead of running them at READY, because the PF(12)
save transition paints blank for up to 60s and the verify step fired before
the editor closed. Fixed by adding a `wait_for_ready()` poll after PF(12)
that waits for the `SAVED` confirmation (or the `READY` banner) before
proceeding. Verified: `--verify` now runs `load`/`check` at READY and
reports `NO ERRORS OR WARNINGS FOUND`.

## Filename limit: 10 characters

The BBS rejects filenames longer than 10 characters with
`?FILE NAME TOO LONG (MAX 10 CHARACTERS)`. `verifytest` (10) is accepted;
`cleanverify` (11) is not. Keep `.bas` names to 10 chars or fewer. (Labels
have a separate 8-character limit.)

## Screen output scrolls; capture it deliberately

The BASIC output buffer is 1000 lines but the 3270 screen shows only 24
rows. A program that prints more than a screenful scrolls, and an `Ascii`
dump only returns the CURRENT screen. When testing:
- `CLEAR` before `RUN` to free the screen for output.
- Keep test programs' output short, or
- Redirect output to a `.dat` file (`PRINT #1, ...`) and read it back via
  SSH (`ssh 3270BBS 'cat ~/3270BBS/basic/admin/NAME.dat'`).

## Filenames

- User filenames cannot contain `_` (reserved for community files).
- `%` prefix = shared user file; `_` prefix = community file (read-only).
- `SAVE "name"` appends `.bas` automatically; `RENAME` requires both
  extensions explicitly.

## Driving the session (for future automation)

The persistent `x3270 -script` session reads actions from `/tmp/x3270.fifo`
and writes responses to `/tmp/x3270.out`. `drive.py` in this directory is a
minimal helper. Key escaping rule: inside `String("...")`, escape `"` as
`\"` and `\` as `\\`. When passing actions as shell args to `drive.py`,
use single quotes with SINGLE backslashes (not `\\"`), e.g.
`drive.py 'String("LOAD \"prog.bas\"")' Enter`.
