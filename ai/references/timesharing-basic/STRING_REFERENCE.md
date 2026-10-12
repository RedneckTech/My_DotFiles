# String Functions — Complete Reference (v3.0.0)

Everything below was verified by running it on the live interpreter.

## The functions

| Function | Returns | Verified behavior |
|----------|---------|-------------------|
| `LEN(s$)` | length | `LEN("ABCDEF")`=6, `LEN("")`=0 |
| `LEFT$(s$,n)` | left n chars | n=0 → `""`; n>len → whole string |
| `RIGHT$(s$,n)` | right n chars | n=0 → `""`; n>len → whole string |
| `MID$(s$,p,n)` | substring | 1-based; n omitted → to end; p>len → `""` |
| `CHR$(n)` | char from code | `CHR$(65)`="A", `CHR$(97)`="a" |
| `ASC(s$)` | code of 1st char | `ASC("ABC")`=65 |
| `STR$(n)` | number→string | see the bug below |
| `VAL(s$)` | string→number | leading spaces ok; `VAL("abc")`=0 |
| `SPACE$(n)` | n spaces | n=0 → `""`; caps at **255** |
| `UCASE$(s$)` | uppercase | non-letters unchanged |
| `LCASE$(s$)` | lowercase | |
| `TRIM$(s$)` | strip both ends | |
| `LTRIM$(s$)` | strip leading | |
| `RTRIM$(s$)` | strip trailing | |
| `INSTR(s$,find$)` | 1-based position | 0 if not found; empty find → 1 |
| `REPLACE$(s$,old$,new$)` | replace all | no match → unchanged |

`BOXCHAR$` / `CP310$` are covered in BOXCHAR_CP310_REFERENCE.md.

## CRITICAL BUG: STR$ differs between compile-time and runtime

`STR$` prepends a space to **non-negative** numbers at runtime, but the
optimizer's constant-folding omits it. The same expression gives different
results depending on whether the argument is a literal:

```
STR$(5)          ' literal  -> "5"    (FUNC_PRECOMPUTE, no space)
H = 5 : STR$(H)  ' variable -> " 5"   (runtime, leading space)
```

Verified at runtime: `STR$(0)`=`" 0"`, `STR$(1)`=`" 1"`, `STR$(12)`=`" 12"`,
`STR$(100)`=`" 100"`, `STR$(3.5)`=`" 3.5"`, but `STR$(-5)`=`"-5"` (negatives
have no leading space).

The CHECK listing confirms the mechanism:

```
30   FUNC_PRECOMPUTE   STR$(5)     "5"
```

Consequence: code that pads numbers with `RIGHT$("0" + STR$(n), 2)` works
for literals but produces `" 5"` for variables. **Always wrap in `TRIM$`**:

```basic
RIGHT$("0" + TRIM$(STR$(n)), 2)      ' -> "05"  (correct)
```

`LEN`, `ASC`, `CHR$`, and `VAL` were checked and are consistent between
literal and variable — only `STR$` has this discrepancy.

## String length limit: 2048 bytes

The manual says strings are "dynamically sized with no fixed maximum
length". **That is wrong.** The real limit is **2048 bytes**:

```
build a 2048-char string  ->  len=2048    (ok)
build a 2049-char string  ->  ?STRING TOO LONG (MAX 2048 BYTES)
```

`SPACE$` has its own, lower cap of **255** (`LEN(SPACE$(300))` = 255), but
ordinary concatenation can reach 2048.

## String indexing

There is no `s$(1)` subscript. Extract a single character with `MID$`:

```basic
S$ = "HELLO"
MID$(S$, 1, 1)   ' "H"
MID$(S$, 2, 1)   ' "E"
MID$(S$, 5, 1)   ' "O"
```

## Comparison is case-sensitive, ASCII order

Comparisons return **-1 (true)** or **0 (false)**:

```
"abc" = "abc"    -> -1
"abc" = "ABC"    ->  0     (case-sensitive)
"a" < "A"        ->  0     (uppercase sorts before lowercase — ASCII)
"abc" < "abd"    -> -1
"cat" < "dog"    -> -1
```

Operators: `= <> < > <= >=`.

## `+` is string concatenation

If either operand is a string, `+` concatenates (and coerces numbers):

```basic
"val=" + "42"    ' "val=42"
"n=" + STR$(7)   ' "n=7"
"5" + 3          ' "53"   (NOT 8)
```

## Special characters

Use `CHR$` to embed control/escape characters:

```basic
"a" + CHR$(92) + "b"   ' a\b   (backslash)
"tab" + CHR$(9) + "!"  ' tab!
"new" + CHR$(10) + "x" ' embedded newline
```

## Does not exist

- **`STRING$(n, char)`** — the manual mentions it, but it is NOT a function.
  `STRING$(3, "*")` is parsed as an array reference and raises
  `?ARRAY NOT DIMENSIONED: STRING$`.

## Error messages (verified)

| Error | Cause |
|-------|-------|
| `?ILLEGAL QUANTITY ERROR` | `MID$(s$, 0, n)` — position must be ≥ 1 |
| `?STRING TOO LONG (MAX 2048 BYTES)` | string exceeds 2048 bytes |
| `?ARRAY NOT DIMENSIONED: STRING$` | using the non-existent `STRING$` function |

## Quick reference

```basic
LEN LEFT$ RIGHT$ MID$ CHR$ ASC STR$ VAL SPACE$ UCASE$ LCASE$
TRIM$ LTRIM$ RTRIM$ INSTR REPLACE$
```
