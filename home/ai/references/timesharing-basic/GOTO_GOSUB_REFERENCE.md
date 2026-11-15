# GOTO, GOSUB/RETURN, ON…GOTO / ON…GOSUB (v3.0.1)

Everything below was verified by running it on the live interpreter
(TIMESHARING BASIC v3.0.1 on 3270BBS build 4.4.2). Exact error strings are
quoted verbatim from the screen.

## Program modes and jump targets

A program is auto-detected from its FIRST non-empty, non-comment line:

- **Line-numbered** (first line starts with a digit): jump targets are line
  numbers.
- **Label-based** (first line starts with anything else): jump targets are
  labels (`Name:` at the start of a line, case-insensitive).

The two modes do not mix. Jumping across the boundary is an error (see the
table at the bottom), but at DIFFERENT times — label→line-number is caught
at LOAD, line-number→label at RUN.

## Label mode specifics

Everything in this section was verified against label-mode programs (a
`START:` entry point and jump targets that are labels, not line numbers).

### The START entry point

- A label-mode program MUST define `START:` — without it, `LOAD` rejects the
  program: `?MISSING START: LABEL` (then `NO PROGRAM LOADED`).
- `START:` does **not** have to be the first label. It is the *entry point*
  wherever it appears; any labels before it are simply not executed at
  startup. (`start:` lowercase works too — labels are case-insensitive.)

### Label naming rules

- `Name:` at the start of a line, **case-insensitive**. `GOTO forward1`
  resolves `FORWARD1:`, and lowercase `start:` is a valid entry point.
- **Underscore is allowed** (`SUB_A:`, `SUB_2:`). **Digits are allowed
  except at the start** (`SUB1:` works; a label beginning with a digit is
  not a valid target — `GOTO 1SUB` → `?SYNTAX ERROR IN LINE n`).
- **`$` breaks label resolution.** A `SUB1$:` definition parses, but neither
  `GOSUB SUB1$` nor `GOSUB SUB1` reaches it (both `?UNDEFINED LABEL`). The
  `$` makes the name read as a string-variable name, so avoid `$` in label
  names.
- **Reserved words cannot be jump targets.** `GOTO PRINT` does not look up a
  label — `PRINT` is consumed as the keyword, leaving `GOTO` with no target:
  `?EXPECTED LINE NUMBER OR LABEL IN LINE n`.
- **Duplicate labels are a LOAD-time error**: `?DUPLICATE LABEL AT LINE 7
  (FIRST AT LINE 4): SUB1` (the program is not loaded).

### Labels do not block fall-through

Execution flows **sequentially through labels** — a label is a jump marker,
not a boundary. This is the one label-mode trap that bites:

```basic
START:
PRINT "main"
GOSUB SUB1
PRINT "after gosub"
SUB1:            ' the main flow falls INTO this label next
PRINT "in SUB1"
RETURN           ' no GOSUB on the stack -> error
```

`SUB1` runs twice — once via `GOSUB`, once when the main flow falls into its
label — and the second `RETURN` has no matching `GOSUB`, so the program
ends with `?RETURN WITHOUT GOSUB IN LINE n`. Put `END` (or a `GOTO`) before
inline subroutines so the main flow cannot fall into them:

```basic
START:
PRINT "main"
GOSUB SUB1
PRINT "after gosub"
END               ' stops the main flow before it reaches SUB1
SUB1:
PRINT "in SUB1"
RETURN
```

### RETURN, recursion, and jump errors

- `RETURN` with no matching `GOSUB` → `?RETURN WITHOUT GOSUB IN LINE n`
  (same as line-numbered mode).
- `GOSUB` self-recursion is bounded at the same **1024 levels** as
  line-numbered mode (1024 → OK, 1025 → `?OUT OF STACK`).
- `GOTO`/`GOSUB` to an undefined (non-reserved) label →
  `?UNDEFINED LABEL name IN LINE n`.

## GOTO

`GOTO line` (numbered) or `GOTO label` (label mode). Transfers control
unconditionally; nothing is remembered.

```basic
10 PRINT "top"
20 GOTO 40
30 PRINT "skipped"
40 PRINT "at 40"
```

- **Forward, backward, and self jumps all work.** The target line does not
  need to be declared or ordered specially; a forward `GOTO` can target a
  line that appears later in the file.
- **Self-loop** — `GOTO` back to the line currently executing restarts that
  line (verified; the manual documents this too):
  `10 X=X+1: IF X<3 THEN GOTO 10`.
- **Jumping out of a FOR loop** with `GOTO` works cleanly: the loop is
  abandoned, the loop variable keeps its current value, and later loops run
  normally (no corrupted FOR stack).

### GOTO errors

| Situation | Error (verbatim) | When |
|---|---|---|
| Nonexistent line number | `?UNDEFINED LINE 999 IN LINE 30` | RUN |
| Nonexistent label (label mode) | `?UNDEFINED LABEL NOPE IN LINE 3` | RUN |
| Line number in a LABEL program | `?JUMP TO LINE NUMBER 50 IN LABEL PROGRAM AT LINE 3` | LOAD (program rejected, not loaded) |
| Label in a NUMBERED program | `?LABEL JUMP IN NUMBERED PROGRAM: LBL IN LINE 20` | RUN (program loads fine) |

The label→line-number case is the sneaky one: `LOAD` prints the error and
the program is NOT loaded (`LIST` then says `NO PROGRAM`). The
line-number→label case loads fine and only blows up when the jump executes.

## GOSUB / RETURN

`GOSUB line`/`GOSUB label` pushes a return address onto an internal stack
and jumps. `RETURN` pops the top address and resumes at the statement
immediately AFTER the `GOSUB`.

```basic
10 GOSUB 100
20 PRINT "back"        ' RETURN lands here
30 END
100 PRINT "in sub"
110 RETURN
```

- **Nesting works** — a sub can `GOSUB` another sub; `RETURN` unwinds one
  level at a time. Verified 2 levels; see recursion for the real depth.
- **Inside a FOR loop** — `GOSUB` from inside the loop body and `RETURN`
  resume the loop normally; the sub sees the loop variable (variables are
  global — there is no local scoping).
- **`RETURN` without a matching `GOSUB`** → `?RETURN WITHOUT GOSUB IN LINE
  n` (runtime error, program halts).
- **`GOSUB` to a sub that never `RETURN`s**: if the sub falls off the END of
  the program, the program just ends normally — the unpopped return address
  is abandoned, and the statement after the `GOSUB` is NOT executed. No
  error.

### GOSUB recursion — bounded at 1024

`GOSUB` may call itself (or any sub may recurse), but the return-address
stack is bounded:

- **1024 nested `GOSUB` levels succeed.**
- The **1025th raises `?OUT OF STACK IN LINE n`** (reported on the line that
  makes the call).

Measured exactly by binary search on the live server: depth 1024 → `OK`,
depth 1025 → `?OUT OF STACK`. The manual's v3.0.1 changelog ("GOSUB
recursion is now bounded — runaway recursion gives OUT OF STACK") is
correct; the concrete limit is 1024 levels.

```basic
10 INPUT "DEPTH:"; N
20 D=0
30 GOSUB 100           ' recurses to depth N, then unwinds
40 PRINT "OK depth"; N
50 END
100 D=D+1
110 IF D<N THEN GOSUB 100
120 RETURN
```

## ON expr GOTO / ON expr GOSUB

Computed jump / computed call. `ON expr` selects one target by position;
the targets are line numbers (numbered mode) or labels (label mode).

```basic
ON X GOTO 100, 200, 300      ' X=1 -> 100, X=2 -> 200, X=3 -> 300
ON X GOSUB 100, 200, 300     ' same, but RETURN comes back here
```

### Index semantics (verified exhaustively)

1. The index is a **full numeric expression**, not just a variable —
   `ON I+1 GOTO …` works.
2. **1-based.** `ON 1` selects the first target, `ON 2` the second, etc.
3. The expression is **truncated toward zero** (integer part), NOT floored
   with `INT` and NOT rounded:
   `2.7→2`, `1.9→1`, `3.9→3`, `0.9→0`, `-0.5→0`.
   (This matters because `INT()` floors — `INT(-0.5)` is `-1` — but `ON`
   truncates, so `ON -0.5 GOTO …` behaves as index 0.)
4. Result in **1..N** → jump/call that target.
5. Result **0 or > N** → **falls through** to the next statement. No error.
6. Result **negative** (after truncation) → `?ILLEGAL FUNCTION CALL IN LINE
   n` (runtime error, halts). Only `0` falls through; `< 0` errors.
7. A **string** index → `?TYPE MISMATCH IN LINE n` (no coercion).

The complete table (3 targets):

| expr | truncated | result |
|---|---|---|
| 1 | 1 | target 1 |
| 2 | 2 | target 2 |
| 3 | 3 | target 3 |
| 0 | 0 | fall through |
| 4 | 4 | fall through (out of range) |
| -1, -2, -100 | negative | `?ILLEGAL FUNCTION CALL` |
| -0.5 | 0 | fall through |
| 2.7 | 2 | target 2 |
| 0.5, 0.9 | 0 | fall through |

Note the asymmetry worth remembering: `expr = 0` falls through quietly, but
`expr < 0` is an error. (The older language summary said "out of range falls
through" for `expr < 1`; that is only true for `0`, not for negatives.)

### ON … GOSUB specifics

- Same index semantics as `ON … GOTO`.
- `RETURN` in the selected sub returns to the statement AFTER the
  `ON … GOSUB` (verified).
- Out-of-range / zero index falls through WITHOUT calling any sub (verified:
  `X=5` skipped the subs entirely).

## Cross-mode jump-target rules

| Jump statement | In line-numbered program | In label program |
|---|---|---|
| `GOTO` line number | OK | LOAD error: `?JUMP TO LINE NUMBER n IN LABEL PROGRAM AT LINE m` |
| `GOTO` label | RUN error: `?LABEL JUMP IN NUMBERED PROGRAM: name IN LINE m` | OK |
| `GOSUB` line number | OK | same LOAD error as GOTO |
| `GOSUB` label | same RUN error as GOTO | OK |
| `ON … GOTO` line numbers | OK | same LOAD error |
| `ON … GOTO` labels | same RUN error | OK |
| `ON … GOSUB` line numbers / labels | as above | as above |

`GOTO`, `GOSUB`, `ON … GOTO`, and `ON … GOSUB` all share one jump-target
resolver, so the cross-mode behavior is identical across all four.

## Error messages (all verified verbatim)

```
?UNDEFINED LINE 999 IN LINE 30
?UNDEFINED LABEL NOPE IN LINE 3
?JUMP TO LINE NUMBER 50 IN LABEL PROGRAM AT LINE 3     (at LOAD)
?LABEL JUMP IN NUMBERED PROGRAM: LBL IN LINE 20         (at RUN)
?RETURN WITHOUT GOSUB IN LINE 30
?OUT OF STACK IN LINE 110
?ILLEGAL FUNCTION CALL IN LINE 30
?TYPE MISMATCH IN LINE 30
?MISSING START: LABEL                                   (label mode, at LOAD)
?DUPLICATE LABEL AT LINE 7 (FIRST AT LINE 4): SUB1      (at LOAD)
?EXPECTED LINE NUMBER OR LABEL IN LINE 3                (GOTO <reserved word>)
```

## Quick reference

```
GOTO line | label          unconditional jump (no return address)
GOSUB line | label         push return address, jump
RETURN                     pop and resume after the GOSUB
ON expr GOTO l1,l2,...     1-based computed jump (targets: lines or labels)
ON expr GOSUB l1,l2,...    1-based computed call; RETURN resumes after it
```

- GOTO/GOSUB/ON accept line numbers in numbered mode, labels in label mode.
- GOSUB nesting (incl. recursion) is limited to 1024 levels; deeper →
  `?OUT OF STACK`.
- RETURN without GOSUB → `?RETURN WITHOUT GOSUB`.
- GOSUB whose sub falls off the end exits the program normally (no RETURN
  needed at the very end).
- ON index: truncated toward zero, 1-based, `0`/`>N` falls through,
  negative → `?ILLEGAL FUNCTION CALL`, string → `?TYPE MISMATCH`.
- GOTO out of a FOR loop abandons it cleanly; the loop variable keeps its
  value and later loops are unaffected.
- Label mode: `START:` is required (`?MISSING START: LABEL` otherwise) but
  need not be first; execution falls THROUGH labels, so put `END`/`GOTO`
  before inline subroutines.
- Label names: case-insensitive; underscore and non-leading digits OK; no
  `$` (unresolvable), no reserved words, no leading digit; duplicates are a
  LOAD error.
