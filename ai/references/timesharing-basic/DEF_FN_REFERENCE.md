# DEF FN — User-Defined Functions in TIMESHARING BASIC (v3.0.0)

Everything below was verified by running it on the live dev server. The
manual's DEF FN section is thin and contains at least one wrong example;
this is the authoritative reference.

## Syntax

```
DEF FNname(param) = expression
```

- `FNname` — the function name, `FN` + at least one more character.
- `param` — exactly ONE parameter (required).
- `expression` — a single expression (the body).

## Naming rules (verified)

| Name | Result |
|------|--------|
| `FNA`, `FNSQ` | works |
| `FN1` (FN + digit) | works |
| `FN_` (FN + underscore) | works |
| `FNVERYLONGFUNC` (15 chars) | works |
| `FNSIN` (FN + built-in name) | works |
| `FNA$` (string function) | works |
| `FN` alone | `?EXPECTED FUNCTION NAME AFTER FN` |

So the name is `FN` + any single character (letter, digit, underscore), and
can be arbitrarily long. The manual's "FN followed by a letter" is too
narrow.

## Parameters: exactly one, typed by the `$` suffix

- `DEF FNA(X) = ...` — parameter `X` is numeric.
- `DEF FNA$(X$) = ...` — parameter `X$` is string.

Zero parameters → `?EXPECTED PARAMETER NAME`. Two parameters →
`?EXPECTED ) AFTER PARAMETER`. There is no way to define a multi-parameter
or zero-parameter function.

**Type checking is asymmetric:**

- Numeric parameter + string argument → `?TYPE MISMATCH` (hard error).
  `FNA("5")` fails.
- String parameter + numeric argument → coerced to string, works.
  `FNA$(5)` = `"5"`.

## Return type is determined by the expression, NOT the `$` suffix

The `$` on the function name does not constrain the return value:

- `DEF FNA(X) = X + "abc"` → `FNA(5)` = `"5abc"` (numeric-named function
  returns a string).
- `DEF FNA$(X$) = VAL(X$) * 2` → `FNA$("21")` = `42` (string-named function
  returns a number).

The `$` suffix is effectively cosmetic on the return side; the expression
decides. (It does matter on the parameter side — see above.)

## The body is a single expression

- No colon-separated statements: `DEF FNA(X) = X + 1: X + 2` →
  `?SYNTAX ERROR`.
- No IF/loops/assignment inside the body — it is one expression only.

The body may contain:
- Built-in functions: `SIN`, `COS`, `LEN`, `UCASE$`, `VAL`, etc.
- Other user functions: `DEF FNB(X) = FNA(X) * 2` works.
- Global variables (read at call time — see below).
- Arrays: `DEF FNA(X) = A(X) * 2` works.
- Associative arrays: `DEF FNA$(N$) = P${N$}` works.
- The parameter, any number of times: `X + X + X + X + X`.

## Recursion is NOT allowed

`DEF FNF(X) = X * FNF(X - 1)` → `?RECURSION TOO DEEP`. Since the body is a
single expression there is no way to write a base case, so self-recursion
is effectively impossible. Mutual recursion (A calls B calls A) would hit
the same limit.

Nested calls to *different* functions work fine (verified a 5-deep chain
`FNE → FND → FNC → FNB → FNA`).

## DEF FN is a RUNTIME statement, not a compile-time declaration

This is the most important behavioral fact:

- The function is only available AFTER the `DEF FN` line has executed.
- Using it before the definition → `?UNDEFINED FUNCTION: FNA IN LINE n`.
- `GOTO` jumping over the `DEF FN` line → the function is never defined,
  and any later use fails.

Consequence: put `DEF FN` statements at the TOP of the program, before any
code path that calls them. A `DEF FN` inside a `GOSUB` subroutine works and
the function survives the `RETURN` (verified).

## Scope and lifetime

- **Global within the program**: callable from `GOSUB` subroutines.
- **Persists across `CHAIN`**: a function defined in the main program is
  usable in the chained program (verified).
- **Cleared by `NEW`**: after `NEW`, the function is gone
  (`?UNDEFINED FUNCTION`).
- **Redefinition allowed**: a later `DEF FNA` replaces the earlier one
  (latest wins).

## Parameter shadowing and globals

- The parameter shadows a global variable of the same name, and the global
  is NOT modified by the call. Verified: `X = 100` then
  `DEF FNA(X) = X + 1` → `FNA(5)` = `6`, and `X` is still `100` afterward.
- Global variables referenced in the body are read at CALL time, not
  definition time. Verified: `DEF FNA(X) = X + Y` with `Y=10` gives 15,
  then `Y=100` gives 105.

This is why the manual's own example is wrong:

```basic
DEF FND(X) = SQR(X^2 + Y^2)
X = 3: Y = 4
PRINT FND(0)      ' manual says 5, actual is 4
```

`FND(0)` uses the parameter `X=0` (which shadows global `X=3`), so it
computes `SQR(0^2 + 4^2)` = `4`, not `5`.

## Variable-name collision: `FN` prefix is reserved

A variable whose name starts with `FN` cannot be used as a normal variable
in an expression. `FNA = 100` stores fine (VARS shows it), but
`PRINT FNA`, `PRINT FNA + 0`, `PRINT FNA * 1` all print blank — the parser
treats `FNA` as a function reference, and with no function defined it
evaluates to empty. Do not use `FN`-prefixed names for variables.

## How many, and how big

- At least 10 functions in one program work (no small limit found).
- The body is subject to the 255-character line limit (a 337-char `DEF FN`
  line is skipped with `?WARNING: LINE TOO LONG (MAX 255)`). So the body is
  at most ~240 chars after the `10 DEF FNA(X) = ` prefix.

## Where functions can be used

Anywhere an expression is allowed:
- `PRINT FNA(5)`
- `IF FNA(3) > 5 THEN ...`
- `FOR I = 1 TO FNA(2)`
- String concatenation: `"val=" + FNA(5)` → `"val=10"`
- Array index, nested inside other functions, etc.

## Works in label mode too

`DEF FN` works identically in label-based programs (verified with the
manual's own examples loaded as `.bas` files). The `START:` label form is
fine; the only label-mode caveat is that you must `LOAD` the program (you
can't type it interactively — see NOTES.md).

## The manual's RND example is broken

The manual's "Random number in range" example:

```basic
DEF FNR(N) = INT(RND(1) * N + 1)
```

does NOT produce random numbers. Because `RND(1)` returns `1`
(deterministic — see LANGUAGE_REFERENCE.md), `FNR(10)` always returns
`11`. Verified: five calls all printed `Random 1-10: 11`.

The correct form uses `RND(0)` (a random float):

```basic
DEF FNR(N) = INT(RND(0) * N + 1)
```

which produces random integers in `1..N` (verified: `6 1 9 10 8`).

## Usage patterns (all verified)

DEF FN is a single-expression function, but it composes into a wide range
of idioms. Every pattern below was run on the live interpreter.

### Math helpers
```basic
DEF FNSQ(X) = X * X
DEF FNCUBE(X) = X * X * X
PRINT FNSQ(5)          ' 25
```

### Predicate / boolean functions
Comparisons return **-1 for true, 0 for false** (not 1). `AND`, `OR`,
`NOT` work in the body.
```basic
DEF FNISPOS(X) = X > 0
DEF FNISEVEN(X) = X MOD 2 = 0
DEF FNVALID(X) = X >= 1 AND X <= 10
PRINT FNISEVEN(4)      ' -1 (true)
```

### String helpers
```basic
DEF FNPAD$(S$) = "[" + S$ + "]"
DEF FNGREET$(N$) = "Hello, " + N$ + "!"
PRINT FNGREET$("World")   ' Hello, World!
```

### Lookup tables (array and associative array)
```basic
DIM TBL(3): TBL(1)=10: TBL(2)=20: TBL(3)=30
DEF FNLOOK(X) = TBL(X)          ' array lookup
DIM PH${}: PH${"Bob"} = "555-2"
DEF FNPH$(N$) = PH${N$}         ' associative lookup
```

### Type conversion
```basic
DEF FNNUM$(X) = STR$(X)         ' number -> string
DEF FNSTR(X$) = VAL(X$)         ' string -> number
```

### Composition (function of function)
```basic
DEF FNDBL(X) = X * 2
DEF FNQUAD(X) = FNDBL(FNDBL(X))
PRINT FNQUAD(5)         ' 20
```

### In control flow
```basic
IF FNISPOS(N) THEN ...                    ' IF
FOR I = 1 TO FNDBL(2) ... NEXT I          ' FOR bound
WHILE FNLIM(I) ... WEND                   ' WHILE condition
SELECT CASE FNCAT(I) ... END SELECT       ' SELECT CASE
ON FNSEL(2) GOTO 100, 200, 300            ' ON...GOTO
```

### As an array index
```basic
DEF FNIDX(X) = X + 1
PRINT A(FNIDX(2))       ' A(3)
```

### In file I/O
```basic
PRINT #1, FNDBL(7)      ' writes 14
```

### Formatting helpers
```basic
DEF FNBAR$(N) = SPACE$(N) + "*"          ' indent
DEF FNPCT(X) = X * 100                    ' percent
```

### Date/time (dummy arg required — one param is mandatory)
```basic
DEF FNDATE$(X) = DATE$()
PRINT FNDATE$(0)        ' 2026-10-12
```

### INPUT validation
```basic
DEF FNVALID(X) = X >= 1 AND X <= 10
INPUT "Enter 1-10: ", N
IF FNVALID(N) THEN PRINT "valid" ELSE PRINT "invalid"
```

### String comparison
```basic
DEF FNU$(X$) = UCASE$(X$)
IF FNU$("yes") = "YES" THEN PRINT "match"
```

## Quick reference

```
DEF FNname(param) = expression     define (param: X numeric, X$ string)
FNname(arg)                        call
```

- Exactly one parameter; zero/two are errors.
- Body is one expression; no statements, no recursion.
- Runtime-defined: must execute before first use; cleared by NEW; survives
  CHAIN; redefinable.
- Parameter shadows globals; globals read at call time.
- `$` on the name is cosmetic for the return type; the expression decides.
- Numeric param rejects strings; string param coerces numbers.
- `FN`-prefixed variable names are unusable as variables.
