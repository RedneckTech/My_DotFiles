# Arrays and Associative Arrays (v3.0.1)

Everything below was verified by running it on the live interpreter.

## DIM and OPTION BASE

```basic
DIM A(10)            ' 1D numeric array
DIM GRID(5, 5)       ' 2D numeric array
DIM NAMES$(20)       ' string array
DIM A%(10)           ' %-suffixed array (see the note below)
DIM PHONE${}         ' associative (string) array
DIM SCORES{}         ' associative (numeric) array
```

- `DIM A(N)` reserves an array whose largest legal index is `N`. The lower
  bound comes from `OPTION BASE`:
  - **Default is base 0**: `DIM A(10)` makes 11 elements, `A(0)..A(10)`.
  - **`OPTION BASE 1`**: `DIM A(10)` makes 10 elements, `A(1)..A(10)`.
    `A(0)` then raises `?SUBSCRIPT OUT OF RANGE`.
- `OPTION BASE 0` or `OPTION BASE 1` **must precede every `DIM`**.
  Issuing it after a `DIM` → `?OPTION BASE MUST PRECEDE ANY DIM`.
- Subscripts may be expressions (`A(I+1)`, `M$(I, J)`).

## Limits (verified)

| Limit | Value | Error |
|-------|-------|-------|
| Single dimension | 10,000 | `DIM A(10000)` is fine (10,001 elements) |
| **Total elements** | **65,535** | `?ARRAY TOO LARGE (MAX 65535 ELEMENTS)` |

Verified: `DIM A(200, 200)` (40,401 elements) loads; `DIM A(300, 300)`
(90,601 elements) → `?ARRAY TOO LARGE (MAX 65535 ELEMENTS)`. The manual's
old "100,000,000 elements for 2D" figure is wrong; the real cap is 65,535
cells total.

## Type-suffixed arrays — a gotcha

`DIM A%(N)`, `DIM A!(N)`, `DIM A#(N)`, `DIM A$(N)` are all valid names and
are DISTINCT arrays from each other and from `A(N)`.

**But the type suffix only coerces SCALAR variables, not array elements:**

```basic
X% = 3.7        ' scalar: stores 3 (truncated toward zero)
DIM A%(5)
A%(1) = 3.7     ' array element: stores 3.7  (NOT truncated)
```

Verified live. If you need integer array values, convert on read/write
(`A%(I) = INT(X)`) or use a plain numeric array.

## Associative arrays (dictionaries)

```basic
DIM PH${}                ' string associative array
DIM S{}                  ' numeric associative array
PH${"Alice"} = "555-1234"
S{"Alice"} = 95
```

- **Keys are case-sensitive**: `K{"A"}` and `K{"a"}` are two entries
  (verified). The ONE exception is arrays filled from BBS data or ISAM
  `GET` — those are *records* whose keys ignore case (see below).
- **Reading an unset key gives `0`** (numeric) **or `""`** (string) — no
  error. So a counter needs no setup: `COUNT{W$} = COUNT{W$} + 1`.
- **Keys may be variables or expressions**: `PH${NAME$}`, `M{K$ + "x"}`.
- **There is no assignment of one of your own arrays to another**
  (`A{} = B{}` is not supported). The only whole-array assignment is from a
  BBS/ISAM source (`U{} = $UserInfo`).
- `DIM X{}` re-declares an empty array (reclaims its memory).

### Records (from BBS data or ISAM GET)

Arrays filled by `U{} = $UserInfo` (and the other `$`-sources) or by an
ISAM `GET` behave differently from your own arrays:

- A **missing key reads as `""`** whatever the array's name (not `0`).
- **Every value is a string.** Use `VAL()` for arithmetic
  (`VAL(M{"id"}) + 1`) and compare with strings (`IF M{"read"} = "1"`).
- **Key names ignore case** (`U{"USERNAME"}` = `U{"username"}`).
- A successful ISAM `PUT` empties the array (see ISAM_REFERENCE.md).

## Quick reference

```
DIM A(N)               numeric array, N = largest index (base 0/1)
DIM A(N, M)            2D array
DIM A$(N)              string array
DIM A%(N) / A!(N) / A#(N)   distinct names; suffix does NOT coerce elements
DIM K{}                associative array (numeric)
DIM K${}               associative array (string)
OPTION BASE 0|1        lower bound; must precede every DIM
```

- Default base 0; `OPTION BASE 1` for 1-based.
- Dimension ≤ 10,000; total elements ≤ 65,535.
- Associative keys case-sensitive; unset → 0/""; records (BBS/ISAM) use
  case-insensitive keys and "" defaults.
- No array-to-array assignment.
