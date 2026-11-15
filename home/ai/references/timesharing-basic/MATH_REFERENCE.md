# Math Functions & Operators — Complete Reference (v3.0.1)

Everything below was verified by running it on the live interpreter.

## The functions

| Function | Returns | Verified |
|----------|---------|----------|
| `ABS(x)` | absolute value | `ABS(-3.7)`=3.7 |
| `INT(x)` | **floor** (toward −∞) | `INT(-3.7)`=-4, `INT(3.7)`=3 |
| `SGN(x)` | −1 / 0 / 1 | `SGN(-0.001)`=-1 |
| `SQRT(x)` / `SQR(x)` | square root | `SQRT(2)`=1.4142… |
| `SIN/COS/TAN(x)` | trig (radians) | `SIN(PI/2)`=1 |
| `ATAN/ASIN/ACOS(x)` | inverse trig (radians) | `ACOS(-1)`=π |
| `LOG(x)` | natural log | `LOG(1)`=0 |
| `EXP(x)` | e^x | `EXP(10)`=22026.4657… |
| `RND(x)` | random | see below |
| `PI()` | π | 3.141592653589793 |
| `RADIANS(deg)` | deg→rad | `RADIANS(180)`=π |
| `DEGREES(rad)` | rad→deg | `DEGREES(PI)`=180 |

`INT` **floors**, it does not truncate toward zero — `INT(-3.7)` is `-4`.

## Operators and precedence

Operators: `+ - * / ^ MOD`.

Precedence, highest first (all verified):

1. `^` — **right-associative**: `2^3^2` = `512` (= 2^(3^2))
2. unary `-` : `-2^2` = `-4` (the `^` binds first)
3. `*` `/` `MOD`
4. `+` `-` — left-associative: `10-5-2` = `3`

`/` is **floating-point**: `10/3` = `3.3333333333333335`. There is no
integer-division operator.

`MOD` sign follows the dividend: `-7 MOD 3` = `-1`.

## RND — range for non-negative, seed for negative

| Call | Returns |
|------|---------|
| `RND(0)` | random float in `[0, 1)` |
| `RND(n)`, n≥2 | random **integer** in `[1, n]` (inclusive) |
| `RND(1)` (any arg in `[1,2)`) | random float in `[0, 1)` |
| `RND(n)`, n<0 | **reseeds** the generator with n; returns a float in `[0,1)` |
| `RND(x)`, 0<x<1 | `?ILLEGAL QUANTITY ERROR` |

Verified: `RND(2)` over 60 trials gave only 1s and 2s (zero 0s); `RND(3)`
gave 1, 2, 3; `RND(10)` gave values in 1-10.

**A negative argument reseeds** — a repeatable sequence. Verified live:
`R = RND(-7)` then two `RND(100)` calls give the same two values every
run (`29 91`). Use `RND(-seed)` for deterministic (testable) randomness.

`RND` without parentheses is `RND(1)` (GW-BASIC style):
`INT(RND * 6) + 1` is a die roll.

**Consequences:**
- For a random integer in `[1, N]`, just use `RND(N)`.
- For a random float in `[0, 1)`, use `RND(0)`.
- For a random integer in `[0, N-1]`, use `RND(N) - 1`.
- The manual's old example `INT(RND(1) * N + 1)` was wrong when `RND(1)`
  returned 1; with `RND(1)` now random 0-1 it works again, but `RND(N)` is
  simpler for a random integer in `[1,N]`.

## Error cases (verified)

| Expression | Result |
|------------|--------|
| `SQRT(-1)` | `?ILLEGAL QUANTITY ERROR` |
| `LOG(0)`, `LOG(-1)` | `?ILLEGAL QUANTITY ERROR` |
| `ASIN(2)`, `ACOS(2)` | `?ILLEGAL QUANTITY ERROR` |
| `(-8)^(1/3)` | `?ILLEGAL QUANTITY ERROR` (negative base, fractional exponent) |
| `1/0` | `?DIVISION BY ZERO` |
| `5 MOD 0` | `?DIVISION BY ZERO` |
| `0^0` | `1` (defined, no error) |
| `2^-1` | `0.5` (negative exponents fine) |

Note: division by zero is **not** a silent halt — it raises
`?DIVISION BY ZERO` and terminates the program.

## No ROUND / CEIL / FLOOR / MIN / MAX

These do NOT exist — they parse as arrays:
`ROUND(3.5)` → `?ARRAY NOT DIMENSIONED: ROUND`, same for `CEIL`, `MIN`
(and by extension `FLOOR`, `MAX`). Use `INT` arithmetic instead:

```basic
FLOOR(x) = INT(x)
CEIL(x)  = -INT(-x)          ' CEIL(3.2) = 4
ROUND(x) = INT(x + 0.5)      ' ROUND(3.5)=4, ROUND(3.4)=3
```

Note `INT(x+0.5)` rounds half **up** (`INT(-3.5+0.5)` = `-3`), not
half-away-from-zero.

## Number representation

Numbers are IEEE-754 doubles:

- `0.1 + 0.2` = `0.30000000000000004` — and `0.1 + 0.2 = 0.3` is **false**.
- `2^53` = `9007199254740992`; `2^53 + 1` = the same value (precision lost),
  so `2^53 + 1 = 2^53` is **true**. About 15-16 significant digits.
- `-0.0` prints as `0`.

### Display formatting

- Plain decimal up to `10^18` (`1000000000000000000`); `10^19` and above
  switch to scientific: `1e+19`.
- Small numbers: `0.0001` prints plain; `0.00001` prints as `1e-05`.
- Fractions show full double precision: `1/3` = `0.3333333333333333`.

## Quick reference

```basic
ABS INT SGN SQRT SQR SIN COS TAN ATAN ASIN ACOS LOG EXP RND PI RADIANS DEGREES
```

- `INT` floors; `^` is right-assoc and binds tightest; `/` is float.
- `RND(0)` = float [0,1); `RND(n)` n≥2 = int [1,n]; `RND(1)` = float [0,1);
  `RND(-seed)` reseeds (repeatable).
- `0^0`=1; `SQRT(-1)`/`LOG(0)`/`ASIN(2)` → ILLEGAL QUANTITY ERROR;
  `x/0` → DIVISION BY ZERO.
- No ROUND/CEIL/FLOOR/MIN/MAX — use `INT`.
