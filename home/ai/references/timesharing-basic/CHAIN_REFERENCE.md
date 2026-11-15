# Program Chaining — COMMON and CHAIN (v3.0.1)

Everything below was verified by running it on the live interpreter, in
both numbered and label mode. The label-mode section is the one that was
previously thin — it is now covered program-by-program.

## The model

`CHAIN "prog"` loads and runs another program. When the chained program
ends (via `END`, or by running off its last line), control returns to the
calling program at the statement AFTER the `CHAIN`; `STOP` ends the whole
run (v3.0.1). `COMMON` declares which variables survive the transition.

```
main.bas:                          sub.bas:
  A = 100                            PRINT A        ' sees 100
  COMMON A                           A = 999
  CHAIN "sub"                        END
  PRINT A          ' sees 999
```

This is a **call stack across programs** — like `GOSUB`, but the callee is
a separate `.bas` file. Nested and even recursive chains unwind correctly.

## COMMON is required for variables to cross

Without `COMMON`, variables do NOT cross the boundary in either direction:

```
main: A=100, B$="hello"  →  CHAIN "sub"
sub sees:  A=0, B$=""          (reset to defaults)
sub sets:  A=999, B$="changed"
main after: A=100, B$="hello"  (unchanged — sub's writes are lost)
```

With `COMMON A, B$` in the caller, the values flow both ways.

## The callee does NOT need to declare COMMON

Only the CALLER's `COMMON` declaration matters. The chained program
automatically receives the COMMON variables and its changes propagate back,
even if it never mentions `COMMON`:

```
main: COMMON A, B$ : CHAIN "sub"
sub (no COMMON):  A = 999 : B$ = "changed" : END
main after: A=999, B$="changed"     ' changes came back
```

## What COMMON can carry

- Simple numeric and string variables.
- Arrays: `DIM A(3)` then `COMMON A` — the whole array crosses, both ways.
- Associative arrays: `DIM P${}` then `COMMON P$` — crosses both ways.

Verified in label mode: `charr` (caller `DIM A(3)`, `A(1)=10 A(2)=20
A(3)=30`, `COMMON A`; callee prints `A(2)` = **20** and sets `A(2)=99`;
caller then prints `A(1)=10 A(2)=99`).

## What else persists across CHAIN (verified)

- **Open files.** A file opened with `OPEN ... AS #1` in the caller stays
  open in the chained program; both can write to the same handle. Verified
  in label mode: caller writes `from main`, callee writes `from sub`,
  caller writes `after chain` — the file contains all three lines in order.
- **DEF FN functions.** A function defined in the caller is callable in the
  chained program. Verified in label mode: callee prints `FNSQ(4)=16`,
  caller prints `FNSQ(3)=9`.
- **The calling program's source.** After CHAIN returns, `LIST` still shows
  the caller — CHAIN does not clear it from memory. Verified after a
  label-mode chain returned.

## Label-mode chaining (verified end to end)

Label-mode programs work as both caller and callee, in every combination.

### Label caller → label callee

```basic
' chmain.bas                     ' chsub.bas
START:                            START:
A = 100                           PRINT "sub sees: A="; A; " B$="; B$
B$ = "hello"                      A = 999
COMMON A, B$                      B$ = "changed"
CHAIN "chsub"                     END
PRINT "main after: A="; A; " B$="; B$
END
```

Verified output:

```
sub sees: A=100 B$=hello
main after: A=999 B$=changed
```

The callee starts at its `START:` label; `COMMON` is bidirectional exactly
as in numbered mode.

### Cross-mode chaining works both ways

- **Numbered caller → label callee:** caller `10 A=100 : 20 COMMON A :
  30 CHAIN "chsub" : 40 PRINT ...`; the label callee runs from `START:`,
  sees `A=100`, sets `A=999`; caller prints `main3 after: A=999`.
- **Label caller → numbered callee:** label caller `CHAIN "chsub3"` where
  `chsub3.bas` is numbered; callee sees `A=100`, sets `A=999`; caller
  prints `main4 after: A=999`.

No conversion or special syntax is needed — CHAIN detects the callee's mode
the same way LOAD does.

### The callee MUST have `START:`

A label-mode file with no `START:` cannot be chained (or loaded):
`?MISSING START: LABEL` at LOAD time.

### CHAIN inside a GOSUB (label mode)

```basic
START:
GOSUB Sub1
PRINT "back in main"
END
Sub1:
PRINT "in sub"
CHAIN "chsub"
PRINT "after chain in sub"
RETURN
```

Verified output:

```
in sub
sub sees: A=0 B$=
after chain in sub
back in main
```

CHAIN returns to the statement after the `CHAIN`, and the pending `RETURN`
then completes normally. (The callee saw `A=0 B$=""` because this caller
declared no `COMMON`.)

### CHAIN inside FOR / WHILE loops (label mode)

The loop state survives the chain:

```basic
START:
COMMON I
FOR I = 1 TO 3
CHAIN "chforsub"
NEXT I
PRINT "for done"
END
```

```
sub I=1
sub I=2
sub I=3
for done
```

The same holds for `WHILE`: a `WHILE N < 3` loop that chains each pass
prints `sub N=1`, `sub N=2`, `sub N=3`, then `while done`.

### Variable filename

`P$ = "chsub" : CHAIN P$` works in label mode exactly as in numbered mode.

## CHAIN mechanics (errors and limits)

- **Nonexistent program:** `CHAIN "nope"` → `?PROGRAM NOT FOUND: nope IN
  LINE 2` (runtime error, program halts). Note the `LINE n` even in label
  mode — it is the statement index, not a source line number.
- **Syntax error in the callee:** `?SYNTAX ERROR IN chbadsyn LINE 2` — the
  error names the callee and its line.
- **STOP ends the whole run** (v3.0.1; it used to return to the caller).
  `END` returns to the caller. A callee that simply runs off its last line
  also returns to the caller (verified).
- **Depth limit 256.** A self-chain past the limit gives
  `?CHAIN NESTED TOO DEEPLY (MAX 256) IN chdepth LINE 4` — the error names
  the program and statement where the limit was hit.
- **Filename can be a variable:** `P$ = "sub"` then `CHAIN P$` works.

## Nested and recursive chaining (label mode)

Nested chains unwind in LIFO order, with COMMON flowing through the whole
chain:

```basic
' cha.bas       ' chb.bas          ' chc.bas
START:           START:             START:
A = 1            A = A + 10         A = A + 100
COMMON A         CHAIN "chc"        PRINT "C sees: "; A
CHAIN "chb"      PRINT "B after: "; A   END
PRINT "A after: "; A   END
END
```

Verified output:

```
C sees: 111
B after: 111
A after: 111
```

A program can CHAIN to itself (recursion):

```basic
START:
COMMON N
N = N + 1
IF N < 5 THEN CHAIN "chrec"
PRINT "level "; N
END
```

Verified output: `level 5` five times. That is correct for the program as
written — `N` is a **global**, so every unwinding frame prints the final
value 5. To see per-level values, save the counter in a depth-indexed
array exactly as with GOSUB recursion:

```basic
START:
COMMON N, D
D = D + 1
N = N + 1
S(D) = N
IF N < 5 THEN CHAIN "chrec2"
PRINT "level "; S(D)
D = D - 1
END
```

(Requires `COMMON S` and `DIM S(300)` in the caller.)

## Testing note: filenames may not contain `_`

When creating label-mode test programs directly on the host
(`~/3270BBS/basic/admin/*.bas`), the BBS reserves `_` for community files:
`ch_main.bas` shows in `FILES` but `LOAD "ch_main.bas"` answers
`?FILE NOT FOUND`. Rename to `chmain.bas` (no underscore) and it loads.
Program names also cap at 10 characters.

## Quick reference

```
COMMON var1, var2$        declare variables that persist across CHAIN
CHAIN "prog"              load+run another program; return on its END
CHAIN var$                filename from a string variable
```

- COMMON is bidirectional; only the caller needs to declare it.
- Without COMMON, variables reset to 0/"" in the callee.
- Arrays, associative arrays, open files, and DEF FN functions all persist.
- Label-mode callers and callees work in every combination; the callee must
  have `START:` and starts there.
- CHAIN returns to the statement after it, even inside a GOSUB (the pending
  RETURN then completes) and inside FOR/WHILE (the loop continues).
- `END` (or falling off the end) returns; `STOP` ends the whole run.
- Nested and recursive chains work; depth is limited to 256 with
  `?CHAIN NESTED TOO DEEPLY (MAX 256) IN <prog> LINE <n>`.
- CHAIN to a missing program is `?PROGRAM NOT FOUND: <name> IN LINE <n>`;
  a callee syntax error is `?SYNTAX ERROR IN <callee> LINE <n>`.
