# Sequential File I/O — Complete Reference (v3.0.0)

Everything below was verified by running it on the live interpreter and by
inspecting the resulting files byte-for-byte. (ISAM indexed files are a
separate feature — see ISAM_REFERENCE.md.)

## OPEN

```basic
OPEN "name.dat" FOR INPUT  AS #1    ' read
OPEN "name.dat" FOR OUTPUT AS #1    ' write (truncates/creates)
OPEN "name.dat" FOR APPEND AS #1    ' add to end (creates if missing)
```

- **File names must end in `.dat`.** `.txt`, `.idx`, and anything else →
  `?ILLEGAL FILE NAME`. (The manual claims `.dat` or `.idx`; in v3.0.0 only
  `.dat` is accepted for sequential files.)
- No path separators allowed.
- `APPEND` creates the file if it does not exist.

## File handles: 1-8, not 1-4

**The valid handle range is `#1` through `#8`** — contradicting both the
manual ("Use #1 through #4") and the error message itself
(`?BAD FILE NUMBER (MUST BE 1-4)`). Verified: `#7` and `#8` work, `#9`
fails. Up to **8 files can be open at once** (all 8 opened simultaneously in
testing).

The handle must be a **literal number** — `OPEN "f" FOR OUTPUT AS #H`
(where `H` is a variable) → `?EXPECTED FILE NUMBER AFTER #`.

## PRINT #

```basic
PRINT #1, "text"          ' whole string, no padding
PRINT #1, "a"; "b"        ' semicolon = no separator  ->  "ab"
PRINT #1, "a", "b"        ->  "a             b"   (tab to next zone)
PRINT #1, 42              ->  "42"
PRINT #1, "x"; TAB(10); "y"
```

**There is no special string padding.** An earlier observation of "padding"
was actually the comma separator: a comma tabs to the next **14-column
print zone** (value 1 in cols 1-14, value 2 at col 15, etc.); a semicolon
concatenates with no separator. Same rules as screen PRINT.

## INPUT #

```basic
INPUT #1, LINE$           ' reads ONE line
```

**INPUT # reads one LINE per variable.** `INPUT #1, A, B, C` reads three
lines (not three comma-separated values from one line):

```basic
' file:  10 \n 20 \n 30
INPUT #1, A, B, C         ' A=10  B=20  C=30
' file:  10,20,30
INPUT #1, A, B, C         ' -> ?INPUT PAST END   (only 1 line available)
```

Numeric parsing of a line:
- `"10,20,30"` → `10` (parses the leading number, stops at the comma)
- `" 42 "` → `42` (leading/trailing spaces tolerated)
- `"abc"` → `0` (non-numeric becomes 0, no error)

Blank lines are read as empty strings (`""`).

### Gotcha: INPUT # cannot target an array element

`INPUT #1, N(2)` does NOT store into `N(2)`. The parser treats it as
`INPUT #1, N` — the value goes into the **scalar** `N`, and `N(2)` stays
`0`. Verified: after `INPUT #1, N(2)` on a line `"42"`, `N(2)=0` but
`N=42`. To load an array, read into a scalar then assign:

```basic
INPUT #1, TMP
L$(N) = TMP
```

## CLOSE and EOF

```basic
CLOSE #1        ' close one
CLOSE           ' close all
EOF(1)          ' 1 if at end of file
```

The idiomatic read loop:

```basic
WHILE NOT EOF(1)
    INPUT #1, L$
    PRINT L$
WEND
```

## Persistence: CLOSE (or normal END) is required

File writes are **buffered**, and the file is written at `CLOSE` or at
normal program end. A runtime error loses the buffered data:

- Write two lines, then hit `?UNDEFINED LINE` before `CLOSE` → the output
  file is **not created at all** (verified: file did not exist).
- A program that ends normally without `CLOSE` still gets its data written
  (auto-close at program end, verified).

So always `CLOSE` your files, and don't rely on a partially-written file
after an error.

## Error messages (all verified)

| Error | Cause |
|-------|-------|
| `?FILE NOT FOUND` | `FOR INPUT` on a file that doesn't exist |
| `?ILLEGAL FILE NAME` | extension not `.dat` (e.g. `.txt`, `.idx`) |
| `?FILE ALREADY OPEN` | opening a handle that's already open |
| `?FILE OPENED FOR INPUT` | `PRINT #` to a file opened FOR INPUT |
| `?FILE NOT OPENED FOR INPUT` | `INPUT #` from a file opened FOR OUTPUT/APPEND |
| `?FILE SIZE LIMIT EXCEEDED` | write would exceed the 256 KB limit |
| `?INPUT PAST END` | reading past EOF |
| `?BAD FILE NUMBER (MUST BE 1-4)` | handle outside 1-8 (message text is wrong) |
| `?EXPECTED FILE NUMBER AFTER #` | non-literal handle (`AS #H`) |

There is **no error handling** — `ON ERROR GOTO` is not supported
(`?ILLEGAL FUNCTION CALL`). A runtime error terminates the program.

## File format

- Plain text, one record per line.
- **Line endings are LF (`0x0A`)**, not CRLF.
- A blank `PRINT #1, ""` writes a bare newline.
- Max file size 256 KB.

## Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Open files | 8 | handles `#1`-`#8` (manual says 4 — wrong) |
| File size | 256 KB | `?FILE SIZE LIMIT EXCEEDED` |
| Line length (source) | 255 chars | separate from data lines |

## Working pattern (copy this)

```basic
OPEN "scores.dat" FOR OUTPUT AS #1
PRINT #1, "Player1,1500"
PRINT #1, "Player2,1200"
CLOSE #1

OPEN "scores.dat" FOR INPUT AS #1
WHILE NOT EOF(1)
    INPUT #1, L$
    PRINT L$
WEND
CLOSE #1
```
