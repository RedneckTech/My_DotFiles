# A Memory Stack in TIMESHARING BASIC (v3.0.1)

TIMESHARING BASIC has no built-in stack data structure, but a LIFO stack is
one array + one integer "top" pointer, with PUSH/POP as GOSUB subroutines
over global variables. Everything below was verified by running it on the
live server.

## The pattern

```
OPTION BASE 1
DIM STK(100)          ' the stack (capacity 100)
TOP = 0               ' top pointer; 0 means "empty"
```

- **PUSH** a value: increment `TOP`, store into `STK(TOP)`.
- **POP** a value: read `STK(TOP)`, decrement `TOP`.
- **PEEK** the top: read `STK(TOP)` without decrementing.
- **EMPTY** test: `TOP = 0`.

Because there are no functions with parameters or local variables, the
subroutines communicate through globals: a value travels in `V` (or `V$`),
the stack in `STK`/`TOP`. Every subroutine follows the same GOSUB/RETURN
conventions from GOTO_GOSUB_REFERENCE.md.

## Numeric stack

```basic
10 OPTION BASE 1
20 DIM STK(100)
30 TOP = 0
...
1000 REM ---- PUSH: V -> STK ----
1010 TOP = TOP + 1
1020 IF TOP > 100 THEN PRINT "STACK OVERFLOW": END
1030 STK(TOP) = V
1040 RETURN
2000 REM ---- POP: STK -> V ----
2010 IF TOP = 0 THEN PRINT "STACK UNDERFLOW": END
2020 V = STK(TOP)
2030 TOP = TOP - 1
2040 RETURN
3000 REM ---- PEEK: STK(TOP) -> V (no pop) ----
3010 IF TOP = 0 THEN PRINT "STACK UNDERFLOW": END
3020 V = STK(TOP)
3030 RETURN
4000 REM ---- EMPTY: V = 1 if empty else 0 ----
4010 IF TOP = 0 THEN V = 1 ELSE V = 0
4020 RETURN
```

Use it by setting `V` and GOSUB-ing:

```basic
V = 10 : GOSUB 1000
V = 20 : GOSUB 1000
GOSUB 2000 : PRINT V      ' 20 (LIFO)
```

## String stack

Same idea with a string array and a `$` value:

```basic
DIM SSTK$(100)
TOPS = 0                 ' NOT "STOP" — STOP is a reserved word

PUSHS:  TOPS = TOPS + 1 : SSTK$(TOPS) = V$ : RETURN
POPS:   V$ = SSTK$(TOPS) : TOPS = TOPS - 1 : RETURN
```

**Gotcha: `STOP` is a reserved word** (the `STOP` statement) and cannot be a
variable name — `STOP = 0` is `?SYNTAX ERROR`. Name the string top pointer
`TOPS`, `SP`, or anything else.

## Verified demo — LIFO order + string reversal

`examples/stackdemo.bas` (run on the live server) produced:

```
numeric stack (pushed 10,20,30):
  pop  -> 30
  pop  -> 20
  peek -> 99
  empty? 0
  pop  -> 99
  pop  -> 10
  empty? 1
reverse HELLO -> OLLEH
```

`reverse HELLO -> OLLEH` is the classic use: push a string's characters one
by one, then pop them — they come back reversed.

## Multiple stacks

For several stacks, use a 2D array and a pointer array. Verified with 3
stacks:

```basic
OPTION BASE 1
DIM MS(3, 100)          ' 3 stacks, capacity 100 each
DIM MTOP(3)             ' one top pointer per stack
FOR S = 1 TO 3 : MTOP(S) = 0 : NEXT S

1000 REM push V onto stack S
1010 MTOP(S) = MTOP(S) + 1
1020 IF MTOP(S) > 100 THEN PRINT "OVERFLOW": END
1030 MS(S, MTOP(S)) = V
1040 RETURN
2000 REM pop stack S into V
2010 IF MTOP(S) = 0 THEN PRINT "UNDERFLOW": END
2020 V = MS(S, MTOP(S))
2030 MTOP(S) = MTOP(S) - 1
2040 RETURN
```

## Capacity and limits

- A 1D stack holds up to the array dimension — **10,000 elements** (the
  array-dimension limit). The 2D form scales to 100,000,000 total elements.
- This is far beyond the **1024** GOSUB-nesting limit, which is why you use
  an ARRAY as the stack instead of abusing GOSUB recursion (recursion is
  bounded at 1024 and is for call/return, not data).

## Underflow / overflow

- On overflow (`TOP` past the array bound) or underflow (`TOP = 0` on pop),
  print a message and `END` (or set an error flag and `RETURN` — your
  choice).
- A buffered `PRINT #1` before `END` DOES land in the file: `END` counts as
  a normal program end and flushes the buffer (verified — see
  FILE_IO_REFERENCE.md). Only a runtime ERROR loses the buffer.

## Gotchas

- **Global scope only.** The subroutines read/write `STK`, `TOP`, and `V`
  directly — there is no local state. Reentrancy and recursion are NOT
  possible; a second GOSUB of PUSH while one is in flight shares the same
  `TOP`. This is fine for a single-threaded BASIC program.
- **0-based vs 1-based.** `OPTION BASE 1` makes the top pointer start at 0
  (empty) and grow 1,2,3,… Cleanly. With the default 0-based arrays you
  would either waste element 0 or track the "next free slot" instead.
- **Comparisons return -1/0** in this BASIC, so write the EMPTY test as
  `IF TOP = 0 THEN V = 1 ELSE V = 0` rather than `V = (TOP = 0)` (which
  would set `V = -1` for empty).
- **Reserved words** (`STOP`, `PRINT`, `IF`, …) can't be variable names —
  watch out when naming your top pointer.

## A queue (FIFO) — same idea, two pointers

Add a HEAD pointer and you have a queue instead of a stack:

```
DIM Q(100)
HEAD = 1 : TAIL = 0        ' empty queue

ENQ:  TAIL = TAIL + 1 : Q(TAIL) = V : RETURN
DEQ:  V = Q(HEAD) : HEAD = HEAD + 1 : RETURN
```

(To avoid the queue "drifting" past the end of the array, wrap the indices
with a ring buffer: `HEAD = HEAD MOD 100 + 1`.)

## Label mode

Identical — the subroutines are labels instead of line numbers:

```basic
START:
OPTION BASE 1
DIM STK(100)
TOP = 0
V = 10 : GOSUB PUSH
GOSUB POP : PRINT V
END
PUSH:
TOP = TOP + 1 : STK(TOP) = V : RETURN
POP:
V = STK(TOP) : TOP = TOP - 1 : RETURN
```
