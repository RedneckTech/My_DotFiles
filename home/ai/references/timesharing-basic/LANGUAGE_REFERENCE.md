# TIMESHARING BASIC/3270BBS — Language Reference (v3.0.1)

Every entry below was verified by running it on the live dev server
(v3.0.1), not copied from the manual. The manual is now v3.0.1 and matches;
where it disagrees, the observed behavior is what's documented here.

## Program structure

Two modes, auto-detected from the FIRST non-empty, non-comment line:

- **Line-numbered**: first line starts with a digit. Entry point = lowest
  line number. Lines execute in numeric order.
- **Label-based**: first line starts with anything else. Entry point = the
  `START:` label (required).

Label rules (verified):
- Labels are `Name:` at the start of a line, case-insensitive.
- There is no label length limit — a 24-character label
  (`ThisIsAVeryLongLabelName`) loads and runs fine. (The manual dropped its
  8-character claim in v3.0.1.)
- `GOTO`/`GOSUB`/`ON...GOTO`/`ON...GOSUB` take label names in label mode.
- You CANNOT type a label program interactively at the `>` prompt — a bare
  `START:` is `?SYNTAX ERROR` (the `:` parses as a statement separator).
  Label programs must be `LOAD`ed from a `.bas` file or entered via the
  ISPF editor.
- Label name charset: letters, underscore, and non-leading digits (`SUB_A:`,
  `SUB1:`); **no `$`** (unresolvable), no reserved words, no leading digit.
  Duplicate labels → `?DUPLICATE LABEL AT LINE n (FIRST AT LINE m): name`
  at LOAD.
- A label program MUST define `START:` (`?MISSING START: LABEL` at LOAD
  otherwise), but `START:` need not be the first label — it is just the
  entry point.
- Labels do NOT stop fall-through: execution flows sequentially through
  them, so an inline subroutine runs twice (once via GOSUB, once by falling
  into its label). Put `END`/`GOTO` before inline subroutines. Full detail:
  GOTO_GOSUB_REFERENCE.md.

## Variables and types

- Numeric: no suffix (`X`, `COUNT`). String: `$` suffix (`NAME$`).
- **Type suffixes make DISTINCT variables**: `X`, `X%`, `X!`, `X#`, `X$` are
  five separate variables. The suffix is part of the name.

  | Suffix | Type | Behavior (verified) |
  |--------|------|---------------------|
  | (none) | double | default |
  | `$` | string | |
  | `%` | integer | scalar assignment truncates toward zero (`X%=3.7` → `3`, `X%=-3.7` → `-3`) |
  | `!` | single | synonym for double (`A!` stores 200.5 exactly) |
  | `#` | double | synonym for double |

  **Gotcha: the suffix does NOT coerce array elements.** `DIM A%(5)` then
  `A%(1) = 3.7` stores `3.7`, not `3` (verified). Only scalar `%`
  assignments truncate. See ARRAYS_REFERENCE.md.
- Case-insensitive: `COUNT` and `count` are the same variable.
- Undefined variables default to `0` (numeric) or `""` (string) — no error.
- Names must start with a letter; letters, digits, underscore after. A name
  may not start with `FN` (that reads as a function call).
- Arrays are **0-indexed by default**: `DIM A(3)` gives `A(0)`..`A(3)`
  (4 elements). `OPTION BASE 1` makes them 1-based. Full detail:
  ARRAYS_REFERENCE.md.
- Associative arrays use `{}`: `DIM PH${}`, then `PH${"Alice"} = "555"`.
  Whole-array assignment: `U{} = $UserInfo`.
- Reserved words (PRINT, IF, FOR, ...) must not be used as variable names;
  `BASE` → `?UNKNOWN STATEMENT: BASE`, and even `KEY$`/`REC$` are refused.
- **Built-in function names are reserved** (v3.0.1): `PI = 3.14159` →
  `?PI IS A BUILT-IN FUNCTION - RENAME VARIABLE`. The full list:
  `ABS ACOS ASC ASIN ATAN BOXCHAR$ CHR$ COS CP310$ DATE$ DAY DEGREES
  DELETED EOF EXP FOUND HOUR INSTR INT LCASE$ LEFT$ LEN LOG LTRIM$ MID$
  MINUTE MONTH PI RADIANS REPLACE$ RIGHT$ RND RTRIM$ SECOND SGN SIN SLEEP
  SPACE$ SQR SQRT STR$ STRING$ TAB TAN TIME$ TIMER TRIM$ UCASE$ VAL YEAR`.
- **Comparing a string to a number is `?TYPE MISMATCH`** (v3.0.0+): `5 =
  "5"` is an error, not true and not a silent no-op. Convert with
  `STR$()`/`VAL()` first. (`+` still coerces — `"5" + 3` = `"53"`.)
- There is **no `INKEY$`** — it is not a built-in, so `K$ = INKEY$` reads as
  an undefined variable and gives `""`.

## No DATA / READ / RESTORE (C64 idiom)

There is **no `DATA`, `READ`, or `RESTORE` statement** — each parses as
`?SYNTAX ERROR`. The C64/GW-BASIC pattern of embedding a constant list in
the program and reading it is replaced by (verified live, see
`examples/datademo.bas`):

- **Numbers**: a `DIM` array — `OPTION BASE 1` first for 1-based indices —
  with inline element assignment.
- **Strings**: one delimited string (`"a,b,c"`) walked in a loop with
  `INSTR`/`LEFT$`/`MID$`.
- **Numbers as text**: parse with `VAL`. Re-assign the source string to the
  loop variable to re-read from the top — that is the `RESTORE` equivalent.
- **Key → value tables**: associative arrays (`DIM T{}`).

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
- `TAB(n)` is a string function returning spaces to reach column n
  (1-based; never moves backward; truncates non-integers; a string arg is a
  no-op). Max usable column is 79 — the 80th character of a line is
  dropped. **It counts UTF-8 bytes**, so after a 3-byte box character it
  lands 2 columns early; use `SPACE$` for panel rows. See `UI_PANELS.md`.
- `PRINT #n, ...` writes to a file. Same comma(tab)/semicolon(concat) rules
  as screen PRINT — `TAB` works the same way (and is byte-counted).

## Simple statements

- `LET` is optional: `LET X = 10` and `X = 10` are the same.
- `CLS` clears the screen.
- `END` ends the program (in a CHAINed program, returns to the caller).
  `STOP` always ends the WHOLE run, abandoning every pending CHAIN level.
- `INPUT "prompt"; var` reads one value (or more: `INPUT A, B`). The input
  field starts right after the prompt and is at least 20 columns; a prompt
  longer than 57 chars wraps. The time spent waiting does NOT count toward
  the 15-second limit. `INPUT` and `INPUT #` store into array elements
  (`INPUT N(2)`, `INPUT I, A(I)` — `A(I)` uses the `I` just read).
- Comments: `REM ...` and `' ...` (apostrophe) start a comment; `'` works
  inline after code too.

## Control flow

- `IF cond THEN stmt [ELSE stmt]` (single line) and block `IF/ELSEIF/ELSE/
  END IF` (END IF or ENDIF required).
- `FOR I = a TO b [STEP s]` / `NEXT I`. `WHILE cond` / `WEND`.
  - `STEP 0` → `?STEP CANNOT BE ZERO`. `NEXT J, I` closes two loops at once.
  - `NEXT I` must match the innermost `FOR`'s variable (`NEXT J` over a
    `FOR I` → `?NEXT WITHOUT FOR`).
  - `FOR I = 5 TO 1` (start already past end, no negative step) skips the
    body; a `WHILE` false the first time skips to its `WEND` the same way.
- `SELECT CASE expr` / `CASE ...` / `CASE ELSE` / `END SELECT`. No
  fall-through; first match wins. `CASE` supports exact lists
  (`CASE 1, 2`), inclusive ranges (`CASE 1 TO 5`), comparisons
  (`CASE IS > 5` — `IS` required), and any mix of the three
  (`CASE 1, 3 TO 5, IS > 10`). Numeric and string selectors don't mix;
  string matching is case-sensitive. Full detail:
  SELECT_CASE_REFERENCE.md.
- `GOTO line|label`, `GOSUB line|label` / `RETURN`.
- `ON expr GOTO l1,l2,...` / `ON expr GOSUB l1,l2,...` — 1-based; index is
  truncated toward zero. 1..N selects the target, `0` or `> N` falls
  through to the next line, a NEGATIVE index → `?ILLEGAL FUNCTION CALL`,
  a string index → `?TYPE MISMATCH`.
- GOSUB recursion is bounded at **1024 levels** (deeper → `?OUT OF STACK`).
- Full detail on all of the above: GOTO_GOSUB_REFERENCE.md.

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

`LEN LEFT$ RIGHT$ MID$ CHR$ ASC STR$ VAL SPACE$ STRING$ UCASE$ LCASE$ TRIM$
LTRIM$ RTRIM$ INSTR REPLACE$ BOXCHAR$`

- `INSTR(s$, find$)` is 1-based; returns 0 if not found; empty find → 1.
- `TRIM$` removes both ends, `LTRIM$`/`RTRIM$` one end.
- `SPACE$(n)` caps at 255 chars; `SPACE$(0)` → `""`.
- **Strings cap at 2048 bytes** — over that → `?STRING TOO LONG (MAX 2048
  BYTES)` (the manual's "no fixed maximum length" is wrong).
- **`STR$` prefixes a space to non-negative numbers** (literal and variable
  alike — the 3.0.0 literal/variable optimizer bug is fixed). Pad with
  `RIGHT$("0" + TRIM$(STR$(n)), 2)`. Full detail in STRING_REFERENCE.md.
- String comparison is **case-sensitive, ASCII order** (`"abc"`≠`"ABC"`,
  `"a"<"A"` is false). `MID$(s$,0,n)` → `?ILLEGAL QUANTITY ERROR`.
- `STRING$(n, c$)` exists (v3.0.1) — n copies of c$'s first character.
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
  `[0,1)`; `RND(n)` = random integer `[1,n]`; `RND(1)` (arg in [1,2)) = a
  random float in `[0,1)` (v3.0.1). `RND(0.5)` → ILLEGAL QUANTITY ERROR.
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
  manual and error text now agree), and the handle must be a literal, not a
  variable.
- Filenames must end `.dat` or `.idx`; `.txt` → `?ILLEGAL FILE NAME`.
- `PRINT #n, ...` uses the same comma(tab)/semicolon(concat) rules as screen
  PRINT — **no special padding**.
- **`INPUT #n, var` reads one LINE per variable.** `INPUT #1, A, B, C`
  reads three lines, not three comma-separated values.
- **`INPUT #` stores into array elements** (v3.0.1) — `INPUT #1, N(2)`
  fills `N(2)`, not the scalar. Still reads one line per variable.
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
- **A successful PUT empties the array** (v3.0.1) — no more field leaking.
  A `GET` that finds nothing leaves the array as it was, so still re-`DIM
  arr{}` before each GET to be safe.
- Records are schemaless; missing fields read back as `0` (or `""` in BBS
  data).
- Record numbers are 1-based; **sequential order is KEY order** (v3.0.1, was
  insertion order); PUT is a true upsert; DELETE is a soft delete (0x7F
  marker); GET NEXT skips deleted records.
- `DELETED(n)` now reports the record `GET` returned (v3.0.1 fixed it).

## Program chaining

- `COMMON var1, var2$` declares variables that persist across `CHAIN`.
- `CHAIN "prog"` loads and runs another program; on its END, control
  returns to the line after CHAIN. COMMON values flow both directions
  (verified: sub set RESULT, main read it back).

## BBS data access (associative arrays)

Full detail (every key, indexing, and the shared record rules) in
BBS_DATA_REFERENCE.md. The sources: `$UserInfo` (username/country),
`$TermInfo` (model/codepage), `$Mail(n)`, `$ChatMessage(n)`, `$Topic(n)`,
`$Post(topic_id, n)`. Copy into an array with `U{} = $UserInfo`; the
assignment REPLACES the array, a missing key reads `""`, all values are
strings, and key names ignore case. **Known bug:** `$UserInfo{"country"}`
returns the username (3.0.1) — treat as unreliable.

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

Warnings emitted in v3.0.1 (all verified live):
- **Loop without SLEEP** (`FOR I = 1 TO 1000000`).
- **Complex line** (3+ statements on one line).
- **Long line** (>120 characters).
- **Too few comments** (0 comments for N lines).

Optimizer (verified): constant folding (`2 + 3 * 4` → `14`) and function
precomputation (`LEN("Hello")` → `5`, `ASC("A")` → `65`). Never folds
division/MOD by zero, side-effecting functions, or variable expressions.

## Error messages (verified)

- `?SUBSCRIPT OUT OF RANGE IN LINE n` — array index out of bounds.
- `?UNDEFINED LINE n IN LINE m` — GOTO/GOSUB to nonexistent line.
- `?SYNTAX ERROR` — parse error (also shown for bare `START:`).
- `?FILE NAME TOO LONG (MAX 10 CHARACTERS)` — a PROGRAM name > 10 chars.
- `?TYPE MISMATCH IN LINE n` — comparing a string to a number (`5 = "5"`),
  or a string index to `ON...GOTO/GOSUB`.
- `?STEP CANNOT BE ZERO IN LINE n` — `FOR ... STEP 0`.
- `?NEXT WITHOUT FOR` / `?WEND WITHOUT WHILE` — mismatched loop closer.
- `?ARRAY TOO LARGE (MAX 65535 ELEMENTS)` — array over the element cap.
- `?OPTION BASE MUST PRECEDE ANY DIM` — `OPTION BASE` after a `DIM`.
- Division by zero: `?DIVISION BY ZERO` (terminates the program). Same for
  `x MOD 0`.

## Limits (from manual + verified where noted)

- Line length 255 chars; program memory 10 MB (v3.0.1, incl. variables/arrays/output/open files).
- Array dimension 10,000; **total elements 65,535** (`?ARRAY TOO LARGE`).
- Execution: 55M iterations / 15s wall clock (SLEEP credits back).
- Open files: 8 (#1-#8). Data file size 256 KB. Output buffer 1000 lines.
- **Program name: 10 chars** (not counting `.bas`). **Data file name: up to
  32 chars including the `.dat`/`.idx` extension** (28-char stem verified).
  Label: no length limit.
- Control nesting: GOSUB 1024; CHAIN 256; 256 open each of FOR / WHILE /
  block IF / SELECT CASE.
- `SPACE$`/`STRING$` cap at 255; concatenation capped at 2048 bytes.
