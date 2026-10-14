# TIMESHARING BASIC/3270BBS — Manual Errata & Discrepancy Report

**For:** the BASIC/3270BBS developer (moshix)
**From:** testing against the live dev server
**Subject:** everything where the shipped `basic_manual.md` disagrees with the
interpreter, plus behavior bugs found while exercising the language.

## Summary

The manual is **v2.9.2**; the running interpreter is **v3.0.0**. Most of the
language matches, but the following items are wrong, out of date, or
inconsistent. Each was reproduced on the live server and is quoted with the
actual observed output.

---

## A. Manual statements that are WRONG

### A1. `DEF FN` distance example gives the wrong answer

**Manual:** the "Distance" example claims `FND(0)` = `5`:

```basic
DEF FND(X) = SQR(X^2 + Y^2)
X = 3: Y = 4
PRINT "Distance: "; FND(0)      ' manual says 5
```

**Actual:** `FND(0)` = **`4`**. The `DEF FN` parameter `X` shadows the global
`X=3`, so the call evaluates `SQR(0^2 + 4^2)`. The manual's comment is wrong
and the example teaches an incorrect mental model of parameter scope.

### A2. The "random number in range" example never produces random numbers

**Manual:**

```basic
DEF FNR(N) = INT(RND(1) * N + 1)
```

**Actual:** returns **`N+1` every time** (verified: five calls all printed
`Random 1-10: 11`). `RND(1)` is `1` (see B1), so `INT(1*N+1)` = `N+1`.

### A3. `RND` description is wrong

**Manual:** "`RND(x)` — Random number 0-1".
**Actual:** the argument is a **range**, not a seed or a 0-1 switch:

- `RND(0)` → random float in `[0, 1)`
- `RND(n)` for n≥1 → random **integer** in `[1, n]`
- `RND(1)` → `1` (deterministic)
- `RND(0.5)` → `?ILLEGAL QUANTITY ERROR`

### A4. 8-character label limit is stated but NOT enforced

**Manual:** "Labels … every label-mode program must have a `START:` label";
the binary even contains the string `Label '%s' exceeds 8 characters`.
**Actual:** a **24-character label** (`ThisIsAVeryLongLabelName`) loads and
runs fine; CHECK reports no warning. Either enforce it or remove the claim.

### A5. File handle range is wrong (says 1-4; actually 1-8)

**Manual:** "File Numbers: Use #1 through #4 (max 4 files open at once)."
**Actual:** handles **`#1`-`#8`** work; `#9` fails. **8 files can be open at
once** (verified opening all 8 simultaneously). The error message is also
wrong — it says `?BAD FILE NUMBER (MUST BE 1-4)` even though `#5`-`#8` are
accepted.

### A6. `.idx` extension is documented but rejected

**Manual:** "File names must end in `.dat` or in `.idx`".
**Actual:** `OPEN "f18.idx" FOR OUTPUT` → `?ILLEGAL FILE NAME`. Only `.dat`
is accepted for sequential files.

### A7. Strings are NOT unlimited

**Manual:** "Strings are dynamically sized with no fixed maximum length."
**Actual:** the limit is **2048 bytes**. A 2048-char string works; a
2049-char string → `?STRING TOO LONG (MAX 2048 BYTES)`.
(`SPACE$`/`STRING$` are separately capped at 255.)

### A8. Three of the four documented CHECK warnings are not implemented

**Manual** lists: loop-without-SLEEP, overly complex lines, very long lines,
insufficient comments.
**Actual:** only **loop-without-SLEEP** fires. Verified clean:

- a 13-line program with **zero comments** → no "insufficient comments"
  warning.
- a line with **4 colon-separated statements** → no "complex line" warning.
- a **168-character line** → no "long line" warning.

### A9. `INPUT #` with multiple variables

**Manual:** "Each `INPUT` reads one line from the file."
**Actual:** true for one variable, but `INPUT #1, A, B, C` reads **three
lines** (one per variable), NOT three comma-separated values from one line.
A line `10,20,30` read into three variables raises `?INPUT PAST END`.

### A10. `STRING$()` is referenced but does not exist

**Manual:** "String functions like `SPACE$()` and `STRING$()` cap repetition
at 255 characters."
**Actual:** `STRING$(3, "*")` → `?ARRAY NOT DIMENSIONED: STRING$`. It is not
a function; it parses as an array reference.

### A11. `?ARRAY NOT DEFINED` — the real message is different

**Manual** (ISAM error table): "`?ARRAY NOT DEFINED` — Associative array not
declared with DIM."
**Actual:** the observed message is `?ARRAY NOT DIMENSIONED: <name>`.

---

## B. Interpreter bugs / inconsistent behavior

Each item below carries a runnable reproduction and the actual output on
v3.0.0 (verified on the live server, build 4.3.0.4). Line-numbered
programs — enter them at READY (or `SAVE`/`LOAD`) and `RUN`.

### B1. `STR$` differs between compile-time and runtime (optimizer bug)

The constant-folding optimizer precomputes `STR$` **without** the leading
space the runtime function adds:

| Expression                   | Result                          |
| ---------------------------- | ------------------------------- |
| `STR$(5)` (literal)          | `"5"` (FUNC_PRECOMPUTE)         |
| `H = 5 : STR$(H)` (variable) | `" 5"` (runtime, leading space) |

Runtime `STR$` prepends a space to **non-negative** numbers (`STR$(0)`=`" 0"`,
`STR$(12)`=`" 12"`, `STR$(3.5)`=`" 3.5"`); negatives have none (`STR$(-5)`=`"-5"`).
The CHECK listing confirms the precompute: `FUNC_PRECOMPUTE STR$(5) "5"`.
This breaks the common padding idiom `RIGHT$("0" + STR$(n), 2)`, which gives
`" 5"` for a variable but `"05"` for a literal. `LEN`, `ASC`, `CHR$`, `VAL`
are consistent — only `STR$` is affected.

**Reproduce:**
```basic
10 REM B1: STR$ differs between compile-time (optimizer) and runtime
20 H = 5
30 PRINT "STR$(5) literal  = ["; STR$(5); "]"
40 PRINT "STR$(H) variable = ["; STR$(H); "]"
50 PRINT "STR$(-5) negative = ["; STR$(-5); "]"
60 PRINT "LEN lit="; LEN(STR$(5)); "  LEN var="; LEN(STR$(H))
70 P$ = "0" + STR$(5)        : PRINT "pad lit = ["; RIGHT$(P$, 2); "]"
80 Q$ = "0" + STR$(H)        : PRINT "pad var = ["; RIGHT$(Q$, 2); "]"
90 R$ = "0" + TRIM$(STR$(H)) : PRINT "pad fix = ["; RIGHT$(R$, 2); "]"
100 END
```
Actual output — note `pad lit` and `pad var` disagree for the *same* value 5:
```
STR$(5) literal  = [5]
STR$(H) variable = [ 5]
STR$(-5) negative = [-5]
LEN lit=1  LEN var=2
pad lit = [05]
pad var = [ 5]
pad fix = [05]
```

### B2. ISAM `PUT`/`GET` do not clear the record array (data corruption)

The associative array is reused between operations, so fields from the
previous record leak into the next:

```basic
C{"id"}="1": C{"name"}="Alice": C{"age"}=30: PUT #1, C{}
C{"id"}="2": C{"city"}="NYC": PUT #1, C{}    ' only id+city intended
```

The second record is written as `id=2  name=Alice  age=30  city=NYC` — the
leaked `name`/`age` are persisted. Same on GET (a missing field returns the
stale value, not empty). Re-`DIM arr{}` before each PUT/GET is the
workaround; the interpreter should clear the array itself.

**Reproduce:**
```basic
10 REM B2: ISAM PUT does not clear the record array
20 OPEN "b2.dat" FOR INDEXED AS #1 KEY = "id"
30 DIM C{} : C{"id"} = "1" : C{"name"} = "Alice" : C{"age"} = 30 : PUT #1, C{}
40 C{"id"} = "2" : C{"city"} = "NYC" : PUT #1, C{}
50 CLOSE #1
60 OPEN "b2.dat" FOR INDEXED AS #1 KEY = "id"
70 DIM R{} : GET #1, R{}, KEY = "2"
80 PRINT "record 2: id=["; R{"id"}; "] name=["; R{"name"}; "] age=["; R{"age"}; "] city=["; R{"city"}; "]"
90 CLOSE #1
100 END
```
Actual output — `name` and `age` leaked from record 1 into record 2:
```
record 2: id=[2] name=[Alice] age=[30] city=[NYC]
```

### B3. ISAM `DELETED(n)` reports the wrong record

During a sequential scan after deleting record 2, `DELETED(1)` returned `1`
for the *first* (undeleted) record and `0` for a later one. The function is
not reporting the current record's deleted state.

**Reproduce:**
```basic
10 REM B3: DELETED(n) reports the wrong record
20 OPEN "b3.dat" FOR INDEXED AS #1 KEY = "id"
30 DIM C{} : C{"id"} = "1" : C{"name"} = "one" : PUT #1, C{}
40 DIM C{} : C{"id"} = "2" : C{"name"} = "two" : PUT #1, C{}
50 DIM C{} : C{"id"} = "3" : C{"name"} = "three" : PUT #1, C{}
60 DELETE #1, REC = 2
70 RESET #1
80 WHILE NOT EOF(1)
90   DIM R{} : GET #1, R{}, NEXT
100   IF FOUND(1) THEN PRINT "id="; R{"id"}; "  DELETED(1)="; DELETED(1)
110 WEND
120 CLOSE #1
130 END
```
Actual output — record 1 is NOT deleted yet reports `DELETED(1)=1`; record 3
reports `0`:
```
id=1  DELETED(1)=1
id=3  DELETED(1)=0
```

### B4. `INPUT #` silently ignores an array-element target

`INPUT #1, N(2)` consumes a line but stores the value in the **scalar** `N`,
not `N(2)`. Verified: after reading `"42"`, `N(2)=0` but `N=42`. It should
either honor the subscript or raise an error.

**Reproduce:**
```basic
10 REM B4: INPUT # silently ignores an array-element target
20 DIM N(3)
30 OPEN "b4.dat" FOR OUTPUT AS #1
40 PRINT #1, "42"
50 CLOSE #1
60 OPEN "b4.dat" FOR INPUT AS #1
70 INPUT #1, N(2)
80 CLOSE #1
90 PRINT "N(2)=["; N(2); "]  scalar N=["; N; "]"
100 END
```
Actual output — the value landed in the scalar, not the array element:
```
N(2)=[0]  scalar N=[42]
```

### B5. `$UserInfo` `country` returns the username

On the dev box `$UserInfo{"country"}` returned `"admin"` (the username), not
a country or an empty string.

**Reproduce:**
```basic
10 REM B5: $UserInfo country returns the username
20 DIM U{} : U{} = $UserInfo
30 PRINT "username=["; U{"username"}; "]"
40 PRINT "country =["; U{"country"}; "]"
50 END
```
Actual output — `country` is the username, not a country:
```
username=[admin]
country =[admin]
```

### B6. Sequential ISAM scan is insertion order, not key order

`RESET` + `GET ... NEXT` returns records in insertion order, not sorted by
the key. This may be intended (the index is for random access only) but is
not documented and is surprising for an "indexed" file.

**Reproduce:**
```basic
10 REM B6: sequential ISAM scan is insertion order, not key order
20 OPEN "b6.dat" FOR INDEXED AS #1 KEY = "id"
30 DIM C{} : C{"id"} = "003" : PUT #1, C{}
40 DIM C{} : C{"id"} = "001" : PUT #1, C{}
50 DIM C{} : C{"id"} = "002" : PUT #1, C{}
60 CLOSE #1
70 OPEN "b6.dat" FOR INDEXED AS #1 KEY = "id"
80 RESET #1
90 WHILE NOT EOF(1)
100   DIM R{} : GET #1, R{}, NEXT
110   IF FOUND(1) THEN PRINT "id="; R{"id"}
120 WEND
130 CLOSE #1
140 END
```
Actual output — insertion order `003, 001, 002`, not key order:
```
id=003
id=001
id=002
```

### B7. `CHAIN` into a label-mode program silently fails

`CHAIN` only works when the **callee** is a line-numbered program. Chaining
a label-mode program does not run it: the interpreter prints `READY`, the
run ends, and the caller never resumes at the line after `CHAIN` — with no
error message. The caller's mode does not matter (both label and numbered
callers chain correctly into numbered callees). A missing callee, by
contrast, fails loudly: `?PROGRAM NOT FOUND: <name> IN LINE <n>`. `CHAIN`
also cannot be used at the READY prompt (`?UNKNOWN STATEMENT: CHAIN`).

Verified on v3.0.0 (build 4.3.0.4) across all four caller/callee mode
combinations; a label-mode callee containing a file-write side effect
proved the callee never executes. Neither the manual nor the reference
docs mention this requirement.

**Reproduce:** the callee must be label mode, so create it in the editor
(a bare `START:` cannot be typed at READY):

```
caller.bas (label mode):            callee.bas (label mode, via editor):
START:
PRINT "caller start"                START:
CHAIN "callee"                      PRINT "callee ran"
PRINT "caller resumed"              END
END
```

`LOAD "caller"` + `RUN`. Actual output:

```
RUNNING...
caller start
READY
>
```

Expected per the documented model: `caller start` / `callee ran` /
`caller resumed`. Give the callee line numbers (the caller's mode does not
matter) and the chain works as documented.

---

## C. Documentation gaps (behavior not covered by the manual)

- **`ROUND`, `CEIL`, `FLOOR`, `MIN`, `MAX` do not exist.** `ROUND(3.5)`,
  `CEIL(3.2)`, `MIN(1,2)` all raise `?ARRAY NOT DIMENSIONED`. There is no
  documented replacement; users must use `INT` arithmetic.
- **`INT` floors** (`INT(-3.7)` = `-4`) — the manual's examples only use
  positive numbers and don't state the floor-vs-truncate behavior.
- **Operator precedence** is undocumented: `^` is right-associative
  (`2^3^2`=512) and binds tighter than unary minus (`-2^2`=-4); `/` is
  floating-point (`10/3`=3.333…); `MOD` sign follows the dividend.
- **`0^0` = 1** (defined). **`x/0` and `x MOD 0`** → `?DIVISION BY ZERO`.
  **`SQRT(-1)`, `LOG(0)`, `LOG(-1)`, `ASIN(2)`, `ACOS(2)`, `(-8)^(1/3)`** →
  `?ILLEGAL QUANTITY ERROR`.
- **`CHAIN`**: the callee does NOT need to declare `COMMON` (only the caller
  does); open files and `DEF FN` functions also persist across `CHAIN`;
  nested and recursive chains work; depth exceeds 200; the **callee must
  be a line-numbered program** — label-mode callees silently fail to run
  (see B7); `CHAIN` cannot be used at the READY prompt
  (`?UNKNOWN STATEMENT: CHAIN`).
- **`DEF FN` is runtime-defined**: it must execute before first use; a `GOTO`
  over the `DEF FN` line leaves the function undefined. Cleared by `NEW`,
  survives `CHAIN`, redefinable. The return type is set by the expression,
  not the `$` suffix.
- **Label mode**: a label program cannot be typed interactively (a bare
  `START:` is `?SYNTAX ERROR`); it must be `LOAD`ed or entered via the editor.
- **File writes are buffered** and only land at `CLOSE` or normal program
  end — a runtime error loses the buffer (the file may not be created at all).
- **Filename length cap is 10 chars** (`?FILE NAME TOO LONG (MAX 10
  CHARACTERS)`); the manual doesn't state a limit.
- **`VARS` lists simple variables only, not arrays.**
- **No error handling**: `ON ERROR GOTO` is unsupported
  (`?ILLEGAL FUNCTION CALL`).
- **`DATE$()`/`TIME$()`** are zero-padded strings; the component functions
  return plain numbers; `SLEEP` grants ~15% execution-time credit.

---

## D. Suggested fixes (priority order)

1. **B1 (STR$ optimizer)** — make FUNC_PRECOMPUTE for `STR$` match runtime
   (emit the leading space), or remove `STR$` from the precompute list. This
   silently changes program output based on whether an argument is a literal.
2. **B2 (ISAM array reuse)** — clear the record array on `PUT`/`GET`; this is
   silent data corruption.
3. **A5 / A6 / A7** — update the manual (or the code) for the 1-8 handle
   range, the `.idx` rejection, and the 2048-byte string cap.
4. **A1 / A2 / A3** — fix the `DEF FN` and `RND` examples; they teach wrong
   behavior.
5. **A4 / A8** — either implement the 8-char label limit and the three
   missing CHECK warnings, or remove them from the manual.
6. **B3 / B4 / B5** — fix `DELETED()`, `INPUT #` into array elements, and
   `$UserInfo.country`.
7. **C** — document the undocumented behavior (precedence, `INT` flooring,
   error semantics, `CHAIN`/`DEF FN` scope, buffered writes, filename cap).

---

*All findings reproduced on the live dev server (BASIC/3270BBS v3.0.0,
BBS build 4.3.0). Detailed write-ups live in the sibling reference docs:
LANGUAGE_REFERENCE.md, DEF_FN_REFERENCE.md, STRING_REFERENCE.md,
MATH_REFERENCE.md, TIME_REFERENCE.md, FILE_IO_REFERENCE.md,
ISAM_REFERENCE.md, CHAIN_REFERENCE.md, BOXCHAR_CP310_REFERENCE.md,
UI_PANELS.md, NOTES.md.*
