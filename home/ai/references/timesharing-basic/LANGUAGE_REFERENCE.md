# TIMESHARING BASIC/3270BBS — Language Reference (v3.0.0)

Every entry below was verified by running it on the live dev server
(v3.0.0), not copied from the manual. Where the manual (v2.9.2) disagrees
with observed behavior, the observed behavior is what's documented here.

## Program structure

Two modes, auto-detected from the FIRST non-empty, non-comment line:

- **Line-numbered**: first line starts with a digit. Entry point = lowest
  line number. Lines execute in numeric order.
- **Label-based**: first line starts with anything else. Entry point = the
  `START:` label (required).

Label rules (verified):
- Labels are `Name:` at the start of a line, case-insensitive.
- The manual claims an 8-character label limit; **this is NOT enforced in
  v3.0.0** — a 24-character label (`ThisIsAVeryLongLabelName`) loads and
  runs fine. (The "Label exceeds 8 characters" string exists in the binary
  but is not triggered.)
- `GOTO`/`GOSUB`/`ON...GOTO`/`ON...GOSUB` take label names in label mode.
- You CANNOT type a label program interactively at the `>` prompt — a bare
  `START:` is `?SYNTAX ERROR` (the `:` parses as a statement separator).
  Label programs must be `LOAD`ed from a `.bas` file or entered via the
  ISPF editor.

## Variables and types

- Numeric: no suffix (`X`, `COUNT`). String: `$` suffix (`NAME$`).
- Case-insensitive: `COUNT` and `count` are the same variable.
- Undefined variables default to `0` (numeric) or `""` (string) — no error.
- Arrays are **0-indexed**: `DIM A(3)` gives `A(0)`..`A(3)` (4 elements).
- Associative arrays use `{}`: `DIM PH${}`, then `PH${"Alice"} = "555"`.
  Whole-array assignment: `U{} = $UserInfo`.
- Reserved words (PRINT, IF, FOR, ...) must not be used as variable names;
  doing so parses but behaves unpredictably.

## Operators

- Arithmetic: `+ - * / ^` (power) and `MOD`.
- `INT()` **floors**, not truncates: `INT(-3.7)` = `-4`.
- `MOD` sign follows the dividend: `-7 MOD 3` = `-1`.
- Comparison: `= <> < > <= >=`.
- **`+` is string concatenation when either operand is a string**:
  `"5" + 3` = `"53"` (not `8`), `"x" + "y"` = `"xy"`, `A$ + 1` = `"hello1"`.
  This is the single most common source of type surprises.

## PRINT

- `;` = no separator (concatenated). `,` = tab to next print zone (~14
  columns).
- `PRINT expr [; expr ...] [COLOR name [modifier]]` — COLOR must be last.
  Colors: WHITE RED YELLOW PINK GREEN BLUE TURQUOISE. Modifiers: BLINK,
  REVERSEVIDEO.
- `TAB(n)` moves to column n (1-255).
- `PRINT #n, ...` writes to a file. Same comma(tab)/semicolon(concat) rules
  as screen PRINT — no special padding.

## Control flow

- `IF cond THEN stmt [ELSE stmt]` (single line) and block `IF/ELSEIF/ELSE/
  END IF` (END IF or ENDIF required).
- `FOR I = a TO b [STEP s]` / `NEXT I`. `WHILE cond` / `WEND`.
- `SELECT CASE expr` / `CASE v1, v2` / `CASE ELSE` / `END SELECT`. No
  fall-through; first match wins.
- `GOTO line|label`, `GOSUB line|label` / `RETURN`.
- `ON expr GOTO l1,l2,...` / `ON expr GOSUB l1,l2,...` — 1-based. Out of
  range (expr < 1 or > count) falls through to the next line.
- GOSUB recursion works (verified 5 levels deep; no small stack limit).

## DEF FN (user functions)

Full detail in DEF_FN_REFERENCE.md. Key facts:

- `DEF FNname(param) = expression`. Name is `FN` + any char (letter, digit,
  underscore); exactly ONE parameter (zero/two are errors).
- **Runtime-defined**: the function exists only after the `DEF FN` line
  executes. Use before definition → `?UNDEFINED FUNCTION`. Cleared by NEW,
  survives CHAIN, redefinable.
- **The parameter shadows a global of the same name.** Verified:
  `DEF FND(X) = SQR(X^2 + Y^2)` with `X=3: Y=4` gives `FND(0)` = `4`
  (param X=0 shadows global X=3), NOT the manual's claimed `5`.
- Globals in the body are read at call time, not definition time.
- Body is a single expression (no statements, no recursion — self-call is
  `?RECURSION TOO DEEP`). Nested calls to other functions work.
- Return type is set by the expression, not the `$` suffix: a numeric-named
  function can return a string and vice versa.
- Numeric param rejects string args (`?TYPE MISMATCH`); string param coerces
  numeric args.
- `FN`-prefixed names are unusable as variables (evaluate to blank).

## String functions (all verified)

`LEN LEFT$ RIGHT$ MID$ CHR$ ASC STR$ VAL SPACE$ UCASE$ LCASE$ TRIM$
LTRIM$ RTRIM$ INSTR REPLACE$ BOXCHAR$`

- `INSTR(s$, find$)` is 1-based; returns 0 if not found; empty find → 1.
- `TRIM$` removes both ends, `LTRIM$`/`RTRIM$` one end.
- `SPACE$(n)` caps at 255 chars; `SPACE$(0)` → `""`.
- **Strings cap at 2048 bytes** — over that → `?STRING TOO LONG (MAX 2048
  BYTES)` (the manual's "no fixed maximum length" is wrong).
- **`STR$` is inconsistent**: a literal arg is optimizer-precomputed WITHOUT
  the leading space (`STR$(5)`→`"5"`), but at runtime `STR$` prepends a
  space to non-negative numbers (`STR$(H)`→`" 5"`). Wrap in `TRIM$` for
  padding. Full detail in STRING_REFERENCE.md.
- String comparison is **case-sensitive, ASCII order** (`"abc"`≠`"ABC"`,
  `"a"<"A"` is false). `MID$(s$,0,n)` → `?ILLEGAL QUANTITY ERROR`.
- `STRING$` does NOT exist (parsed as an array).
- `BOXCHAR$(1-6)` = ┌ ┐ └ ┘ ─ │ (single-line box).
- `CP310$(1-50)` = extended graphics (double-line box 7-12, blocks 21-28,
  arrows 29-32, shapes 33-36). Double-line box chars may not render in all
  emulators (x3270 shows them as ■).

## Math functions (all verified)

`ABS INT SGN SQRT SQR SIN COS TAN ATAN ASIN ACOS LOG EXP RND PI RADIANS
DEGREES`

Full detail in MATH_REFERENCE.md. Key facts:

- Trig is in radians. `PI()` = 3.14159..., `RADIANS(deg)`, `DEGREES(rad)`.
- `INT` floors (see above). `SGN` = -1/0/1.
- **`RND` argument is a RANGE, not a seed**: `RND(0)` = random float
  `[0,1)`; `RND(n)` = random integer `[1,n]`; `RND(1)` = `1` (always).
  `RND(0.5)` → ILLEGAL QUANTITY ERROR.
- **No `ROUND`/`CEIL`/`FLOOR`/`MIN`/`MAX`** (parsed as arrays). Use `INT`:
  `FLOOR=INT(x)`, `CEIL=-INT(-x)`, `ROUND=INT(x+0.5)`.
- Precedence: `^` (right-assoc) > unary `-` > `*` `/` `MOD` > `+` `-`. `/` is
  floating-point. `MOD` sign follows the dividend (`-7 MOD 3` = `-1`).
- `0^0` = 1. `SQRT(-1)`/`LOG(0)`/`ASIN(2)`/`(-8)^(1/3)` → ILLEGAL QUANTITY
  ERROR. `x/0` and `x MOD 0` → DIVISION BY ZERO.
- Doubles: `0.1+0.2` ≠ `0.3`; `2^53+1` = `2^53`.

## Time functions (all verified)

`TIME$() DATE$() TIMER() HOUR() MINUTE() SECOND() YEAR() MONTH() DAY()
SLEEP(n)`

Full detail in TIME_REFERENCE.md. Key facts:

- `DATE$()` = `YYYY-MM-DD`, `TIME$()` = `HH:MM:SS` (both zero-padded
  strings). The component functions return plain numbers.
- `TIMER()` = seconds since midnight (float, sub-second precision).
- `SLEEP(n)` pauses n seconds (0.1-255), returns 0, is non-busy, and grants
  ~15% execution-time credit. Out-of-range (0, <0.1, >255) →
  `?SLEEP VALUE OUT OF RANGE (0.1-255)`.
- Time is the host's local time (UTC on the dev VM).
- No day-of-week / day-of-year functions; undefined function calls return
  empty rather than erroring.
- `STR$` prepends a space, so pad with `RIGHT$("0" + TRIM$(STR$(n)), 2)`.
- Over-running the 15s limit → `?EXECUTION TIME LIMIT REACHED`.

## EVAL

`EVAL(expr$)` evaluates a string as a BASIC expression at runtime. Works
with numeric expressions and string functions **when they reference
variables**: `EVAL("A + B")`, `EVAL("LEFT$(N$, 5)")`, `EVAL("LEN(N$)")`.
String literals with nested quotes inside EVAL are unreliable.

## File I/O (sequential)

Full detail in FILE_IO_REFERENCE.md. Key facts:

- `OPEN "f.dat" FOR INPUT|OUTPUT|APPEND AS #n`. **Handles are 1-8** (the
  manual and the error text both say 1-4 — wrong), and the handle must be a
  literal, not a variable.
- Filenames must end `.dat`; `.idx`/`.txt` → `?ILLEGAL FILE NAME`.
- `PRINT #n, ...` uses the same comma(tab)/semicolon(concat) rules as screen
  PRINT — **no special padding**.
- **`INPUT #n, var` reads one LINE per variable.** `INPUT #1, A, B, C`
  reads three lines, not three comma-separated values.
- **`INPUT #` cannot target an array element** — `INPUT #1, N(2)` stores
  into the scalar `N`, not `N(2)`. Read into a scalar, then assign.
- Numeric parse stops at the first non-numeric char; non-numeric → `0`.
- **Writes are buffered**: data lands at `CLOSE` or normal program end. A
  runtime error loses the buffer (the file may not be created at all).
- No error handling (`ON ERROR GOTO` unsupported).

## Indexed files (ISAM)

Full detail in ISAM_REFERENCE.md. Key facts:

- `OPEN "f.dat" FOR INDEXED AS #n KEY = "field"`.
- `PUT #n, arr{}` (upsert), `GET #n, arr{}, KEY=expr|REC=n|NEXT`,
  `DELETE #n, KEY=expr|REC=n`, `RESET #n`. Status: `FOUND(n)`, `EOF(n)`,
  `DELETED(n)`.
- **PUT and GET do NOT clear the array** — fields from the previous
  operation persist. Re-`DIM arr{}` before each PUT/GET to avoid stale
  fields (this is the #1 ISAM gotcha).
- Records are schemaless; missing fields read back as `0`.
- Record numbers are 1-based; sequential order is INSERTION order (not
  key-sorted); PUT is a true upsert; DELETE is a soft delete (0x7F marker);
  GET NEXT skips deleted records.
- `DELETED(n)` is unreliable — don't trust it.

## Program chaining

- `COMMON var1, var2$` declares variables that persist across `CHAIN`.
- `CHAIN "prog"` loads and runs another program; on its END, control
  returns to the line after CHAIN. COMMON values flow both directions
  (verified: sub set RESULT, main read it back).

## BBS data access (associative arrays)

- `$UserInfo` → `username`, `country`. (Observed: `country` returned the
  username `"admin"` on this box — treat as unreliable.)
- `$TermInfo` → `model` (`Mod2`/`Mod3`/`Mod4`), `codepage` (`310`/`037`).
- `$Mail(n)`, `$ChatMessage(n)`, `$Topic(n)`, `$Post(topic_id, n)` — return
  empty strings when no data. Keys per the manual.

## Commands

- Program: `RUN LIST [range] NEW RENUM [(s,i)] DELETE range`.
  `RENUM 100,5` renumbers to 100,105,110... (verified).
- Files: `SAVE "name" LOAD "name" RENAME a.bas b.bas EDIT [name] BROWSE
  ERASE [pattern] FILES [pattern] [/W] [/C] [/U user] FLIST [pattern]`.
- Syntax: `CHECK` (compile + listing), `VIEW name.list`, `EMAIL name.list`.
- Other: `HELP VARS CLEAR BYE/EXIT/QUIT`.
- `VARS` lists simple variables only, NOT arrays.

## CHECK listing

`CHECK` produces a `.list` file with: source listing (STMT + NT nesting
column), errors/warnings/informational, variable cross-reference, function
reference, data dictionary, optimizer report, load-module statistics.

Warnings actually emitted in v3.0.0:
- **Loop without SLEEP** (verified: `FOR I = 1 TO 1000000` triggers it).

Warnings in the manual that are NOT emitted in v3.0.0:
- "Insufficient comments" (13-line 0-comment program passed clean).
- "Overly complex lines" (4-statement line passed clean).

Optimizer (verified): constant folding (`2 + 3 * 4` → `14`) and function
precomputation (`LEN("Hello")` → `5`, `ASC("A")` → `65`). Never folds
division/MOD by zero, side-effecting functions, or variable expressions.

## Error messages (verified)

- `?SUBSCRIPT OUT OF RANGE IN LINE n` — array index out of bounds.
- `?UNDEFINED LINE n IN LINE m` — GOTO/GOSUB to nonexistent line.
- `?SYNTAX ERROR` — parse error (also shown for bare `START:`).
- `?FILE NAME TOO LONG (MAX 10 CHARACTERS)` — filename > 10 chars.
- Division by zero: `?DIVISION BY ZERO` (terminates the program). Same for
  `x MOD 0`.
- Type mismatch: no error — `+` coerces to string concatenation.

## Limits (from manual + verified where noted)

- Line length 255 chars; program size 256 KB.
- Array dimension 10,000; 2D total 100,000,000 elements.
- Execution: 55M iterations / 15s wall clock (SLEEP credits back).
- Open files: 4 (#1-#4). Data file size 256 KB. Output buffer 1000 lines.
- Filename: **10 chars max** (verified). Label: no enforced 8-char limit
  (verified 24 chars works).
- `SPACE$`/`STRING$` cap at 255; concatenation uncapped.
