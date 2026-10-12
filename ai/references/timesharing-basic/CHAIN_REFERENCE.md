# Program Chaining — COMMON and CHAIN (v3.0.0)

Everything below was verified by running it on the live interpreter.

## The model

`CHAIN "prog"` loads and runs another program. When the chained program
ends (via `END` or `STOP`), control returns to the calling program at the
line AFTER the `CHAIN`. `COMMON` declares which variables survive the
transition.

```
main.bas:                          sub.bas:
  A = 100                            PRINT A        ' sees 100
  COMMON A                           A = 999
  CHAIN "sub"                        END
  PRINT A          ' sees 999
```

This is a **call stack across programs** — like `GOSUB`, but the callee is a
separate `.bas` file. Nested and even recursive chains unwind correctly.

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

(The manual's examples declare `COMMON` in both programs; that's harmless
but unnecessary for the callee.)

## What COMMON can carry

- Simple numeric and string variables.
- Arrays: `DIM A(3)` then `COMMON A` — the whole array crosses, both ways.
- Associative arrays: `DIM P${}` then `COMMON P$` — crosses both ways.

## What else persists across CHAIN (verified)

- **Open files.** A file opened with `OPEN ... AS #1` in the caller stays
  open in the chained program; both can write to the same handle.
- **DEF FN functions.** A function defined in the caller is callable in the
  chained program (see DEF_FN_REFERENCE.md).
- **The calling program's source.** After CHAIN returns, `LIST` still shows
  the caller — CHAIN does not clear it from memory.

## CHAIN mechanics

- **Filename can be a variable:** `P$ = "sub"` then `CHAIN P$` works.
- **Nonexistent program:** `CHAIN "nope"` → `?PROGRAM NOT FOUND: nope IN
  LINE n` (runtime error, program halts).
- **STOP and END both return** to the caller. `STOP` in the chained program
  terminates it and returns control, same as `END`.
- **Depth:** at least 200 levels of self-chaining work (no small limit; the
  manual lists the CHAIN stack as memory-bounded only).

## Nested and recursive chaining

Nested chains unwind in LIFO order, with COMMON flowing through the whole
chain:

```
main: A=1 → CHAIN sub1 → CHAIN sub2 → (A=11) → (A=111) → back to sub1 → back to main
```

A program can CHAIN to itself (recursion), using a COMMON counter as the
base case:

```basic
10 COMMON N
20 N = N + 1
30 IF N < 5 THEN CHAIN "self"
40 PRINT "level "; N
50 END
```

## Quick reference

```
COMMON var1, var2$        declare variables that persist across CHAIN
CHAIN "prog"              load+run another program; return on its END/STOP
CHAIN var$                filename from a string variable
```

- COMMON is bidirectional; only the caller needs to declare it.
- Without COMMON, variables reset to 0/"" in the callee.
- Arrays, associative arrays, open files, and DEF FN functions all persist.
- Nested and recursive chains work; depth is effectively unlimited.
- CHAIN to a missing program is a runtime error.
