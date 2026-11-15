# TIMESHARING BASIC/3270BBS — Manual Errata & Discrepancy Report

**For:** the BASIC/3270BBS developer (moshix)
**From:** testing against the live dev server
**Status:** RESOLVED in v3.0.1. The shipped manual is now **v3.0.1** and
matches the running interpreter **v3.0.1** (BBS build 4.4.2.1). Every item
below was re-verified on the live server before being closed out — no item
was closed on the changelog's word alone.

## Version status

| Thing        | Was    | Now      |
|--------------|--------|----------|
| `basic_manual.md` | v2.9.2 | **v3.0.1** |
| interpreter  | v3.0.0 | **v3.0.1** |
| BBS build    | 4.3.0  | **4.4.2.1** |

## A. Manual statements that were wrong — resolved

| # | Old finding | Fix in 3.0.1 | Verified |
|---|---|---|---|
| A1 | DEF FN "Distance" example said `FND(0)` = 5 | example corrected; behavior unchanged (param still shadows the global → `4`) | manual text; behavior re-confirmed |
| A2 | `DEF FNR(N)=INT(RND(1)*N+1)` never random | `RND(1)` now returns a random float in [0,1); example corrected | live ✅ |
| A3 | `RND` described as "random 0-1" | `RND(1)` is random 0-1 again | live ✅ |
| A4 | 8-char label limit claimed but not enforced | claim removed from the manual | manual text |
| A5 | file handles "1-4" | manual + error text now `1-8` | changelog |
| A6 | `.idx` documented but rejected | `OPEN` now accepts `.idx` | live ✅ |
| A7 | strings "no fixed maximum" | manual now states the 2048-byte cap | manual text |
| A8 | three CHECK warnings missing | complex/long/comment warnings all implemented | live ✅ |
| A9 | `INPUT #` one-line-per-variable undocumented | manual now documents it (incl. array-element targets) | manual text |
| A10 | `STRING$` referenced but absent | `STRING$(n, c$)` added | live ✅ |
| A11 | `?ARRAY NOT DEFINED` vs real message | error table corrected (two distinct messages) | manual text |

## B. Interpreter bugs — resolved

| # | Old bug | Fix in 3.0.1 | Verified |
|---|---|---|---|
| B1 | `STR$` literal vs variable (optimizer) | constant folding matches runtime: `STR$(5)` → `" 5"` | live ✅ |
| B2 | ISAM `PUT`/`GET` don't clear the array | successful `PUT` empties the array; `GET`-finds-nothing leaves it | live ✅ (PUT) |
| B3 | `DELETED(n)` reported the wrong record | fixed — reports the record `GET` returned | changelog |
| B4 | `INPUT #` ignored array-element target | array elements stored correctly | live ✅ |
| B6 | ISAM sequential scan was insertion order | `GET ... NEXT` now returns **key order** | live ✅ |
| B7 | CHAIN into label-mode callee failed silently | label callee runs; caller resumes after CHAIN | live ✅ |

## C. Still open

1. **`$UserInfo{"country"}` still returns the username** — verified live on
   3.0.1: `country=[admin]`. Missing keys now correctly read `""` (verified:
   `nosuch=[]`), but the `country` key itself still resolves to the username.
   Treat `country` as unreliable. (Old B5, not fixed.)

## D. New / changed behavior in 3.0.1 (intentional — older programs may break)

- **Reserved names:** built-in function names can no longer be variables.
  `PI = 3.14159` → `?PI IS A BUILT-IN FUNCTION - RENAME VARIABLE` (live ✅).
  Same for `LEN`, `DAY`, `TIMER`, `HOUR`, `MINUTE`, `SECOND`, `YEAR`, `MONTH`,
  and others (full list under "Reserved names" in the manual). Rename such
  variables.
- **`RND(1)`** (arg in [1,2)) returns a random float in [0,1) again.
- **`STR$`** now always prefixes a space to non-negative numbers, literal or
  variable. Pad with `RIGHT$("0" + TRIM$(STR$(n)), 2)` as before.
- **`STRING$(n, c$)`** added (n copies of c$'s first character).
- **`.idx`** filenames accepted alongside `.dat`.
- **`INPUT` / `INPUT #`** store into array elements (`A(I)`) and associative
  elements (`C{K}`).
- **ISAM:** successful `PUT` empties the array; `GET ... NEXT` is key order;
  `DELETED(n)` reports the record `GET` returned.
- **CHAIN:** label-mode callees work; CHAIN depth limited to 256.
- **CHECK** now warns on complex lines (3+ statements), long lines (>120
  chars), and too few comments — all three verified firing live.
- **Stricter syntax:** trailing text after a statement, a trailing comma
  (`NEXT I,`), `!=`, `\`, `&HFF`, and malformed numbers (`1E`, `12AB`) are
  now `?SYNTAX ERROR` instead of being silently misread.
- **SELECT CASE:** QBasic-style ranges — `CASE 1 TO 9`, `CASE IS > 9`,
  mixed with values.
- **`ON n GOTO/GOSUB`** with n = 0 or past the list continues with the next
  statement (was `?ILLEGAL FUNCTION CALL`).
- **Memory:** a program may hold at most 10 MB (`?OUT OF MEMORY (MAX 10 MB)`).
- **`MID$(...) = ...`** (GW-BASIC MID$ statement) → `?MID$ STATEMENT NOT
  SUPPORTED`.

## Behavior that is UNCHANGED (still true in 3.0.1 — the reference docs stand)

- `+` is string concatenation when either operand is a string.
- `INT()` floors, it does not truncate.
- Comparisons return -1 (true) / 0 (false).
- Division by zero (`x/0`, `x MOD 0`) terminates the program.
- Arrays are 0-indexed.
- No `ROUND`/`CEIL`/`FLOOR`/`MIN`/`MAX` — use `INT`.
- `DEF FN` parameter shadows a global of the same name.
- `FN`-prefixed variable names evaluate to blank in expressions.
- `VARS` lists simple variables only, not arrays.
- Strings cap at 2048 bytes; `SPACE$` caps at 255.

---

*Re-verified on the live dev server (BASIC/3270BBS v3.0.1, BBS build
4.4.2.1). Detailed write-ups live in the sibling reference docs:
LANGUAGE_REFERENCE.md, DEF_FN_REFERENCE.md, STRING_REFERENCE.md,
MATH_REFERENCE.md, TIME_REFERENCE.md, FILE_IO_REFERENCE.md,
ISAM_REFERENCE.md, CHAIN_REFERENCE.md, BOXCHAR_CP310_REFERENCE.md,
UI_PANELS.md, NOTES.md.*
