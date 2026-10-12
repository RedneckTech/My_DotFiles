# TIMESHARING BASIC/3270BBS — Code Quality Guide

A practical style guide for writing clean, maintainable BASIC on the
3270BBS system. Every rule here was verified against the live interpreter
(v3.0.0) on the dev server, not just copied from the manual.

## 1. Pick a program style and stick to it

The interpreter supports two program forms, detected from the FIRST
non-empty, non-comment line:

| First line starts with | Mode | Entry point |
|------------------------|------|-------------|
| a digit                | line-numbered | first line number |
| anything else          | label-based   | `START:` label |

**Line-numbered** (traditional):

```basic
10 REM Print a greeting
20 LET NAME$ = "World"
30 PRINT "Hello, "; NAME$
40 END
```

**Label-based** (modern, recommended for new code):

```basic
START:
    REM Print a greeting
    NAME$ = "World"
    PRINT "Hello, "; NAME$
    END
```

Rules:
- Use increments of 10 (10, 20, 30) so you can insert lines later.
- Label-based programs MUST begin with a `START:` label.
- Labels are case-insensitive, start with a letter/underscore. The manual
  claims an 8-character limit, but v3.0.0 does NOT enforce it (a 24-char
  label runs fine).
- Do NOT mix line numbers and labels in the same `ON...GOTO`/`ON...GOSUB`.

**Important gotcha:** you cannot type a label-based program interactively at
the `>` prompt — a bare `START:` line is rejected with `?SYNTAX ERROR`
because the `:` is parsed as a statement separator. Label programs must be
entered via the ISPF editor (`EDIT`) or written to a `.bas` file and
`LOAD`ed. See NOTES.md.

## 2. Comment deliberately

Two comment forms, both verified:

```basic
10 REM Full-line comment
20 ' Apostrophe also starts a full-line comment
30 X = 10 ' Inline comment after a statement
```

- `REM` and `'` are equivalent for full-line comments.
- `'` can also start an inline comment after any statement.
- The v2.9.2 manual claims CHECK warns on "insufficient comments"
  (< 1 REM per 10 lines). **This warning is NOT active in v3.0.0** — a
  13-line program with zero comments passed CHECK with no warnings. Do not
  rely on CHECK to enforce comment density; enforce it yourself.

## 3. Use CHECK as your quality gate

`CHECK` is the single most valuable tool for code quality. It compiles the
program in memory WITHOUT running it and writes a `.list` file containing:

- Source listing with statement numbers and nesting level (`NT` column)
- Errors, warnings, and informational messages
- Variable cross-reference (where each variable is defined vs referenced)
- Function reference (built-in and user-defined)
- Data dictionary (all variables and arrays)
- Optimizer report (constant folding / function precomputation)
- Load-module statistics (lines, statements, size, arrays)

Run it after every meaningful edit:

```
SAVE "myprog"
CHECK
```

Then read the listing:

```
VIEW myprog.list        ' view without clearing the program in memory
```

The cross-reference table is the fastest way to spot dead variables — a
variable that is DEFINED but never REFERENCED is a candidate for removal.

## 4. Avoid the warnings CHECK does emit

The one warning that is active in v3.0.0 is the **loop-without-SLEEP**
warning:

```
20 FOR I = 1 TO 1000000
   ----  WARNING: FOR loop with 1000000 iterations without SLEEP
                  may trigger loop detector
```

Any tight loop (FOR/NEXT, WHILE/WEND, or a backward GOTO) that runs many
iterations without yielding can trip the execution-time/iteration limiter
(55M iterations / 15s wall clock). Insert a `SLEEP` to yield:

```basic
FOR I = 1 TO 1000000
    X = X + 1
    IF I MOD 1000 = 0 THEN X = SLEEP(0.1)   ' yield every 1000 iterations
NEXT I
```

`SLEEP(n)` (0.1–255s) is a non-busy wait that also credits back execution
time, so it is the correct way to make long-running programs well-behaved.

## 5. Write for the optimizer

The compiler folds constant expressions and precomputes constant function
calls at compile time. You can see exactly what it did in the OPTIMIZER
REPORT section of the listing:

```
  LINE   TYPE              ORIGINAL                 OPTIMIZED
    10   CONSTANT_FOLD     3 * 4                    12
    10   CONSTANT_FOLD     2 + 12                   14
    30   FUNC_PRECOMPUTE   LEN("Hello")             5
```

Implications for style:
- Prefer named constants over magic numbers, but do NOT hand-fold
  arithmetic to "help" the compiler — it already does this. Write the
  readable form (`60 * 60 * 24`) and let the optimizer fold it.
- The optimizer never folds division/MOD by zero, never precomputes
  side-effecting functions (`RND`, `TIMER()`, `INKEY$`), and never folds
  expressions containing variables. So `X = 2 + 3 * 4` folds, but
  `X = A + 3 * 4` does not.

## 6. Name variables clearly

- Numeric variables: no suffix (`COUNT`, `TOTAL`).
- String variables: `$` suffix (`NAME$`, `TITLE$`).
- Names start with a letter, contain letters/digits, are case-insensitive.
- Reserved keywords cannot be variable names. `FN` is technically usable
  as a variable in v3.0.0 but is strongly discouraged (conflicts with
  `DEF FN` user functions).
- Arrays are **0-indexed**: `DIM A(3)` gives elements `A(0)`..`A(3)`.
  `DIM N$(2)` gives `N$(0)`..`N$(2)`.

## 7. Structure subroutines and functions

- `GOSUB`/`RETURN` for reusable blocks; keep subroutines at the end of the
  program after the main `END`.
- `DEF FNname(param) = expression` for single-expression helpers. The name
  must start with `FN` + a letter (`FNSQ`, `FNC`). One parameter only.
- `SELECT CASE` is preferred over long `IF/ELSEIF` chains when testing one
  value against many options — it evaluates the test expression once and
  has no fall-through.

## 8. File I/O hygiene

- Always `CLOSE` files when done (auto-closed at program end, but explicit
  is clearer).
- File numbers are `#1`–`#4` (max 4 open at once).
- Data filenames must end in `.dat` or `.idx`; no path separators.
- Use `WHILE NOT EOF(1)` to read to end of file rather than a fixed count.

```basic
OPEN "scores.dat" FOR INPUT AS #1
WHILE NOT EOF(1)
    INPUT #1, LINE$
    PRINT LINE$
WEND
CLOSE #1
```

## 9. Keep lines simple

- Max line length is 255 characters; the editor's data area is 71 columns,
  so keep source lines under ~71 chars for the ISPF editor.
- The v2.9.2 manual claims CHECK flags lines with 3+ colon-separated
  statements as "complex". **This warning is NOT active in v3.0.0** — a
  line with 4 statements passed CHECK clean. Still, prefer one statement
  per line for readability.

## 10. Quick reference

```
CHECK / VIEW name.list     quality gate + listing
SAVE "name" / LOAD "name"  persist / restore
FILES / FLIST              list files
RENUM                      renumber (line-numbered programs only)
VARS                       list variables in memory
```

See NOTES.md for version differences and gotchas, and examples/ for
verified, runnable programs.
