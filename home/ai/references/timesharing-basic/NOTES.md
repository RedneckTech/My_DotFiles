# TIMESHARING BASIC/3270BBS — Notes, Gotchas, and Version Differences

Findings from live testing against the dev server (v3.0.1). The bundled
`basic_manual.md` is now v3.0.1 and matches the interpreter. Everything
below was verified by actually running it.

## Version

The dev server runs **TIMESHARING BASIC/3270BBS V3.0.1** (BBS build
4.4.2.1). The manual in the repo (and on the host) is **v3.0.1** and is
now accurate. The previous mismatch (manual v2.9.2 vs interpreter v3.0.0)
is closed — see MANUAL_ERRATA_FOR_DEV.md for the item-by-item resolution.

## Top gotchas (still true in 3.0.1 — these WILL bite you)

- **`+` is string concatenation when either operand is a string.**
  `"5" + 3` = `"53"` (not `8`), `A$ + 1` = `"hello1"`. No type error.
- **`INT()` floors, not truncates.** `INT(-3.7)` = `-4`.
- **`DEF FN` parameter shadows a global of the same name.** `DEF FND(X) =
  SQR(X^2 + Y^2)` with `X=3: Y=4` gives `FND(0)` = `4` (the manual now says
  this correctly).
- **Division by zero is `?DIVISION BY ZERO`** (terminates the program); same
  for `x MOD 0`.
- **Comparisons return -1 (true) / 0 (false).** `X = (A = B) * 10` gives
  `-10`, not `10`.
- **Built-in function names can no longer be variables.** `PI = 3.14159` →
  `?PI IS A BUILT-IN FUNCTION - RENAME VARIABLE`. Same for `LEN`, `DAY`,
  `TIMER`, `HOUR`, `MINUTE`, `SECOND`, `YEAR`, `MONTH`. Rename them (e.g.
  `MYPI`).
- **`PRINT #n` uses the same comma(tab)/semicolon(concat) rules as screen
  `PRINT`** — no special padding.
- **File handles are `#1`-`#8`** (manual and error text now say 1-8).
  `INPUT #` reads one line per variable and DOES store into array elements.
  Writes are buffered until `CLOSE`/normal end. See FILE_IO_REFERENCE.md.
- **`VARS` lists simple variables only, not arrays.**
- **`$UserInfo` `country` still returns the username** (`"admin"`) on this
  box — treat as unreliable (missing keys now correctly read `""`).
- **Strings cap at 2048 bytes** (`?STRING TOO LONG`); `SPACE$` caps at 255.
- **String comparison is case-sensitive, ASCII order.**
- **`FN`-prefixed variable names are unusable** — `FNA = 100` stores, but
  `PRINT FNA` prints blank (parsed as a function reference).
- **ISAM:** a successful `PUT` empties the record array; `GET ... NEXT`
  returns key order. Still re-`DIM` before each GET to be safe (a
  GET-finds-nothing leaves the array as it was). See ISAM_REFERENCE.md.

Full details in LANGUAGE_REFERENCE.md.

## What changed in 3.0.1 (was different in 3.0.0)

- `RND(1)` is now a random float in [0,1) (it was always 1). `RND(0)` =
  float [0,1); `RND(n)` = integer [1,n].
- `STR$` now prefixes a space to non-negative numbers for BOTH literals and
  variables (the literal/variable optimizer bug is fixed).
- `STRING$(n, c$)` now exists.
- `.idx` filenames are now accepted.
- `INPUT`/`INPUT #` now store into array elements.
- ISAM: `PUT` clears the array; `GET ... NEXT` is key order; `DELETED(n)`
  fixed.
- CHAIN into a label-mode callee now works.
- CHECK now warns on complex lines (3+ statements), long lines (>120), and
  too few comments.
- Stricter syntax: trailing text after a statement, `!=`, `\`, `&HFF`, and
  malformed numbers are now `?SYNTAX ERROR`.
- SELECT CASE gains `CASE 1 TO 9` / `CASE IS > 9`.
- `ON n GOTO/GOSUB` with n=0 or past the list continues (was an error).
- 10 MB program memory cap.

## Label mode: LOAD works, interactive entry does not

- `LOAD "prog.bas"` of a label-based file works and reports
  `LOADED prog.bas (N LINES) (LABEL MODE)`.
- Typing a label program interactively at the `>` prompt FAILS:
  `START:` alone → `?SYNTAX ERROR`.
- Root cause: the `:` is parsed as a statement separator. Label detection
  happens when the whole program is parsed (LOAD/RUN), not line-by-line.
- Practical consequence: write label programs to a `.bas` file and `LOAD`
  them, or enter them through the ISPF editor (`EDIT`).

## CHECK warnings (all active in 3.0.1)

| Warning | Trigger |
|---|---|
| Loop without SLEEP | a tight FOR/WHILE loop with no `SLEEP` |
| Complex line | 3+ statements on one line |
| Long line | >120 characters |
| Too few comments | fewer than 1 comment per N lines |

Verified live: a 4-statement line, a 170-char line, and a 0-comment
13-line program all fire their warnings in 3.0.1.

## Arrays are 0-indexed

`DIM A(3)` creates `A(0)`..`A(3)` (4 elements). Consistent across the
language.

## The optimizer is real and visible

`CHECK`'s OPTIMIZER REPORT shows constant folding and function
precomputation. Constant folding now uses the same routines as runtime, so
`STR$(5)` folds to `" 5"` (with the space) — the old literal/variable
mismatch is gone.

## BBS data access works from BASIC

- `$UserInfo` → `{"username": "admin", ...}` (`country` unreliable, see
  above).
- `$TermInfo` → `{"model": "Mod2", "codepage": "310"}`.
- `$ChatMessage(n)`, `$Mail(n)`, `$Topic(n)`, `$Post(id, n)` available.

## Filename limit: 10 characters

`?FILE NAME TOO LONG (MAX 10 CHARACTERS)`. Keep `.bas` names to 10 chars or
fewer. (The 8-char label limit is NOT enforced and no longer claimed.)

## Screen output scrolls; capture it deliberately

The BASIC output buffer is 1000 lines but the 3270 screen shows only 24
rows. When testing:
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
