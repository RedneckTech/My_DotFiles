# SELECT CASE (v3.0.1)

Everything below was verified by running it on the live interpreter
(TIMESHARING BASIC v3.0.1 on 3270BBS build 4.4.2), in BOTH line-numbered
and label modes. The syntax and semantics are identical in the two modes.

## Syntax

```basic
SELECT CASE expr
CASE v1, v2, ...          ' exact match against any value in the list
CASE low TO high          ' inclusive range
CASE IS op expr           ' comparison (IS is REQUIRED before an operator)
CASE ELSE                 ' default (catch-all)
END SELECT
```

`SELECT CASE expr` takes any expression — numeric or string — not just a
variable (`SELECT CASE N MOD 3` works). `END SELECT` closes the block.

## CASE forms

Four forms, all verified:

### 1. Exact-value list

```basic
SELECT CASE X
CASE 1
    PRINT "one"
CASE 2, 3, 4
    PRINT "two, three, or four"
END SELECT
```

`CASE 2, 3, 4` matches if `X` equals ANY value in the list. Negative values
are fine (`CASE -1`).

### 2. Inclusive range (TO)

```basic
SELECT CASE X
CASE 1 TO 5
    PRINT "between 1 and 5"
END SELECT
```

Ranges are **inclusive on BOTH bounds** (verified: `X=1` and `X=5` both
match `CASE 1 TO 5`). Negative ranges work (`CASE -5 TO -1`). String ranges
work too (`CASE "ant" TO "dog"` — `"cat"` matches).

### 3. Comparison (IS)

```basic
SELECT CASE X
CASE IS > 5
    PRINT "greater than 5"
CASE IS < 0
    PRINT "negative"
END SELECT
```

The **`IS` keyword is required** before a comparison operator. All six
operators work: `= <> < > <= >=` (verified). String comparisons work
(`CASE IS > "m"` — `"zoo"` matches).

A **bare** `CASE > 5` (without `IS`) is `?SYNTAX ERROR IN LINE n`.

### 4. Mixed list + range + IS in one CASE

All three forms combine in a single `CASE`, comma-separated:

```basic
SELECT CASE X
CASE 1, 3 TO 5, IS > 10
    PRINT "1, or 3..5, or over 10"
END SELECT
```

Verified: `X=4` matches via `3 TO 5`, `X=9` matches exactly, `X=20` matches
via `IS > 10`.

## CASE ELSE

- `CASE ELSE` is the default branch — it matches whatever the other CASEs
  did not.
- It does **NOT** have to be last. A `CASE ELSE` placed before other CASEs
  simply matches first and makes the later CASEs dead code (first-match-wins
  applies to ELSE too).
- **Duplicate `CASE ELSE` is NOT an error** — the first one wins, the rest
  are ignored.
- Omitting `CASE ELSE` is fine: if nothing matches, execution just falls
  through to the statement after `END SELECT` (no error).

## Matching semantics

- **First match wins; no fall-through.** Once a `CASE` matches, its body
  runs and control jumps to after `END SELECT` — later CASEs are NOT
  evaluated (verified with overlapping cases: `CASE 1,2,3` before
  `CASE 3,4,5` with `X=3` ran only the first).
- **No match and no `CASE ELSE`** → falls through to after `END SELECT`,
  silently (no error).
- **Numeric vs string are separate.** `CASE "5"` does NOT match a numeric
  `5` — it is a silent no-match, NOT a type error.
- **String CASE matching is case-sensitive** (ASCII order), matching the
  language's string comparison: `CASE "banana"` does not match `"Banana"`.

## Nesting

`SELECT CASE` nests inside a `CASE` body, and mixes with other control flow
(GOSUB/FOR/etc.). Verified:

```basic
SELECT CASE X
CASE 2
    PRINT "outer 2"
    SELECT CASE Y
    CASE 20
        PRINT "inner 20"
    END SELECT
    PRINT "back in outer 2"
END SELECT
```

A `CASE` body can contain any other control-flow construct, verified in
both line-numbered and label modes:

- **`IF/THEN/ELSE`** — both single-line (`IF x=2 THEN ... ELSE ...`) and
  block (`IF ... THEN` / `ELSE` / `END IF`).
- **`FOR/NEXT`** loops.
- **`WHILE/WEND`** loops.
- **`GOSUB`/`RETURN`**.
- **Nested `SELECT CASE`** (above).

There is no restriction on what statements appear inside a `CASE` body.

## END SELECT

- `END SELECT` (with a space) closes the block. `ENDSELECT` without the
  space is `?SYNTAX ERROR IN LINE n`.
- **Omitting `END SELECT` is NOT a load or runtime error** — the program
  loads and runs, but the block has no proper terminator, so the result is
  undefined/messy. Always close the block.

## Both modes

`SELECT CASE` works identically in line-numbered and label programs. In
label mode the block is just written without line numbers:

```basic
START:
X=2
SELECT CASE X
CASE 1
PRINT "one"
CASE 2
PRINT "two"
END SELECT
END
```

## Errors (verified)

| Situation | Result |
|---|---|
| `CASE > 5` (bare operator, no `IS`) | `?SYNTAX ERROR IN LINE n` (RUN) |
| missing `END SELECT` | no error (undefined block termination) |
| duplicate `CASE ELSE` | no error (first wins) |
| `CASE ELSE` before other CASEs | no error (first-match-wins) |
| `CASE "5"` vs numeric selector | no error, silent no-match |
| no match, no `CASE ELSE` | no error, falls through |

There are no SELECT-CASE-specific runtime error messages — malformed CASE
syntax is a plain `?SYNTAX ERROR`.

## Quick reference

```
SELECT CASE expr          begin a case block on expr (any expression)
CASE a, b, c              exact match against any listed value
CASE a TO b               inclusive range (both bounds; strings too)
CASE IS op expr           comparison; IS is required (op: = <> < > <= >=)
CASE 1, 3 TO 5, IS > 9    mix list + range + IS in one CASE
CASE ELSE                 default (matches anything not already matched)
END SELECT                close the block
```

- First match wins; no fall-through.
- No match and no ELSE → falls through silently.
- Numeric and string CASEs don't mix (`CASE "5"` ≠ numeric 5).
- String matching is case-sensitive; string ranges and string `IS` work.
- `IS` is mandatory before operators; bare `CASE > 5` is a syntax error.
- Identical in line-numbered and label modes.
