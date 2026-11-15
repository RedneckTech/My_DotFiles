# Modern Coding Patterns in TIMESHARING BASIC (v3.0.1)

How to do the things a modern programmer reaches for — recursion,
memoization, sorting, searching, linked lists, trees, objects — in a
line-numbered 1970s-style BASIC. Every pattern below was verified by
running it on the live server.

## The one rule that matters: no automatic locals

`GOSUB` gives you call/return but **no local variables and no frame**.
Every subroutine shares the same globals. A recursive subroutine that needs
a value to survive a nested call must save it in a **depth-indexed array**:

```basic
DIM S(1024)              ' one slot per recursion level
D=0

1000 REM fact(N) -> R
1010 D=D+1: S(D)=N       ' save this frame's N
1020 IF N<=1 THEN R=1: GOTO 1060
1030 N=N-1
1040 GOSUB 1000          ' recurse (clobbers N, R, everything)
1050 R=R*S(D)            ' this frame's saved N
1060 D=D-1
1070 RETURN
```

`fact(6)` = `720` (verified). Skip the `S(D)` save and the result is wrong.

**Tail recursion needs no frame** — when the state is passed by mutation
and nothing is used after the call, one global set is enough:

```basic
1000 REM gcd(A,B) -> R
1010 IF B=0 THEN R=A: RETURN
1020 T=A MOD B: A=B: B=T
1030 GOSUB 1000
1040 RETURN
```

`gcd(48,36)` = `12` (verified).

**`DEF FN` cannot recurse** — a self-call is `?RECURSION TOO DEEP`.
Recursion must be `GOSUB`-based, and is capped at **1024** active calls.

## Memoization

Cache results in an associative array keyed by the argument. Because the
recursive calls clobber the shared globals, save the argument and the key
per frame too:

```basic
DIM CACHE{}, M(100), MK$(100), MA(100), MB(100)
D=0

1000 REM fib(N) -> R, memoized
1010 IF N<=1 THEN R=N: RETURN
1020 D=D+1: M(D)=N: MK$(D)="k"+TRIM$(STR$(N))
1030 IF CACHE{MK$(D)}>0 THEN R=CACHE{MK$(D)}: D=D-1: RETURN
1040 N=M(D)-1: GOSUB 1000: MA(D)=R
1050 N=M(D)-2: GOSUB 1000: MB(D)=R
1060 R=MA(D)+MB(D): CACHE{MK$(D)}=R
1070 D=D-1
1080 RETURN
```

Verified: `fib_memo(30)` = `832040` in **0.0117 sec**. The naive
recursion (no cache) for the same N **never finishes** — it dies at the
15-second limit (`?EXECUTION TIME LIMIT REACHED`). Naive `fib(20)` takes
0.63 s; `fib(30)` is ~100× more work and blows the budget.

## Sorting

All three verified on `[5,3,8,1,9,2,7,4]` → `1 2 3 4 5 7 8 9`.

- **Bubble** (O(n²), fine for small n):
  ```basic
  FOR I=1 TO N-1: FOR J=1 TO N-I
    IF A(J)>A(J+1) THEN T=A(J): A(J)=A(J+1): A(J+1)=T
  NEXT J: NEXT I
  ```
- **Insertion** (O(n²), faster in practice):
  ```basic
  FOR I=2 TO N
    K=A(I): J=I-1
    WHILE J>=1
      IF A(J)<=K THEN GOTO Done
      A(J+1)=A(J): J=J-1
    WEND
  Done:
    A(J+1)=K
  NEXT I
  ```
- **Quicksort** (recursive, O(n log n)). Use a **Lomuto partition with a
  FOR loop** — a Hoare partition built from nested `WHILE`+`GOTO` produced
  corrupt output in testing. Frame arrays hold LO/HI:
  ```basic
  3000 REM quicksort A(LO..HI)
  3010 D=D+1: QL(D)=LO: QH(D)=HI
  3020 IF LO<HI THEN GOSUB 3200
  3030 D=D-1
  3040 RETURN
  3200 REM Lomuto partition + recurse
  3210 P=A(HI): I=LO-1
  3220 FOR J=LO TO HI-1
  3230 IF A(J)<=P THEN I=I+1: T=A(I): A(I)=A(J): A(J)=T
  3240 NEXT J
  3250 T=A(I+1): A(I+1)=A(HI): A(HI)=T
  3260 QP(D)=I+1
  3270 HI=QP(D)-1: GOSUB 3000
  3280 LO=QP(D)+1: HI=QH(D): GOSUB 3000
  3290 LO=QL(D): HI=QH(D)
  3300 RETURN
  ```

## Searching

```basic
1000 REM linear search X in A(1..N) -> R (0 = not found)
1010 FOR I=1 TO N
1020 IF A(I)=X THEN R=I: RETURN
1030 NEXT I
1040 R=0: RETURN

2000 REM binary search X in sorted A(1..N) -> R
2010 LO=1: HI=N: R=0
2020 WHILE LO<=HI
2030 M=INT((LO+HI)/2)
2040 IF A(M)=X THEN R=M: RETURN
2050 IF A(M)<X THEN LO=M+1 ELSE HI=M-1
2060 WEND
2070 RETURN
```

Verified: linear and binary both find 14 at pos 7, report 13 as not found
(0), and binary finds 40 at pos 20.

## Linked list (parallel arrays)

No pointers, so use an index as a "pointer": `LD()` holds data, `LN()`
holds the index of the next node (0 = end).

```basic
DIM LD(20), LN(20)
HEAD=0: FREE=1

1000 REM insert V at head
1010 LD(FREE)=V: LN(FREE)=HEAD: HEAD=FREE: FREE=FREE+1: RETURN
2000 REM delete node with value V
2010 P=HEAD: PREV=0
2020 WHILE P<>0
2030 IF LD(P)=V THEN GOTO 2070
2040 PREV=P: P=LN(P)
2050 WEND
2060 RETURN
2070 IF PREV=0 THEN HEAD=LN(P) ELSE LN(PREV)=LN(P)
2080 RETURN
```

Verified: head-inserting 10,20,30 traverses as `30 20 10`; deleting 20
leaves `30 10`.

## Binary search tree (arrays)

`TK()` = key, `TL()`/`TR()` = left/right child indices, `ROOT` = root
index. Insert iteratively; traverse recursively (frame array `TP()` saves
the node across calls).

```basic
1000 REM insert V
1010 NODES=NODES+1: TK(NODES)=V: TL(NODES)=0: TR(NODES)=0
1020 IF ROOT=0 THEN ROOT=NODES: RETURN
1030 P=ROOT
1040 WHILE 1
1050 IF V<TK(P) THEN
1060 IF TL(P)=0 THEN TL(P)=NODES: RETURN
1070 P=TL(P)
1080 ELSE
1090 IF TR(P)=0 THEN TR(P)=NODES: RETURN
1100 P=TR(P)
1110 END IF
1120 WEND
2000 REM in-order traversal from P
2010 IF P=0 THEN RETURN
2020 D=D+1: TP(D)=P
2030 P=TL(TP(D)): GOSUB 2000
2040 PRINT TK(TP(D));
2050 P=TR(TP(D)): GOSUB 2000
2060 D=D-1: RETURN
```

Verified: inserting 50,30,70,20,40,60,80 and traversing in order gives
`20 30 40 50 60 70 80`; searching 40 finds node 5, 45 is not found (0).

## Objects / records

An associative array is a struct; a `GOSUB` is a method. Fields are
numeric or string by the array's type (mixed-type records need an
all-string array and `VAL` — that is the BBS/ISAM model).

```basic
DIM ACCT{}
ACCT{"balance"}=100: ACCT{"limit"}=200

1000 REM deposit AMT
1010 ACCT{"balance"}=ACCT{"balance"}+AMT: RETURN
2000 REM withdraw AMT, refuse if it would go negative
2010 IF ACCT{"balance"}-AMT < 0 THEN PRINT "refused": RETURN
2020 ACCT{"balance"}=ACCT{"balance"}-AMT: RETURN
```

Verified: 100 + 50 − 30 = 120; a 500 withdrawal is refused and the balance
stays 120.

## State machines (lexers)

A finite state machine is a `STATE` variable plus a transition routine per
state. Dispatch to exactly ONE handler with `ON STATE+1 GOSUB` — a chain of
`IF STATE=0 THEN GOSUB ...` followed by `IF STATE=1 THEN GOSUB ...` runs
the SAME character through the new state too and doubles the first token
(verified bug).

```basic
STATE=0: TOK$=""
FOR I=1 TO LEN(S$)
  C$=MID$(S$,I,1)
  ON STATE+1 GOSUB 2000,2100,2200
NEXT I

2000 REM state 0: START
2010 IF C$=" " THEN RETURN
2020 IF C$>="0" AND C$<="9" THEN STATE=1: TOK$=C$: RETURN
2030 IF (C$>="A" AND C$<="Z") OR (C$>="a" AND C$<="z") THEN STATE=2: TOK$=C$: RETURN
2040 PRINT "TOKEN: "; C$: RETURN
2100 REM state 1: IN_NUMBER
2110 IF C$>="0" AND C$<="9" THEN TOK$=TOK$+C$: RETURN
2120 PRINT "TOKEN: "; TOK$: TOK$="": STATE=0: GOSUB 2000: RETURN
2200 REM state 2: IN_IDENT  (same shape)
```

Verified on `"A1 + 42 * BC2"` → `A1`, `+`, `42`, `*`, `BC2`.

## Parsers (tokenizer + recursive descent)

Tokenize into a string array, then parse with `expr → term → factor`
(precedence climbing). `factor` recurses into `expr` for parentheses.
**Save the operator per frame** — the recursive call clobbers `OP$`, so
re-reading it after the call gives the wrong operator (this cost a bug:
`12 + 3 * (4 - 1)` came out as `11` instead of `21`).

```basic
DIM TK$(50), EA(20), EB(20), TA(20), TB(20), FA(20), OPF$(20)
' ... tokenize into TK$(1..NT), then:
P=1: D=0: GOSUB 2000

2000 REM expr -> R
2010 D=D+1
2020 GOSUB 2100: EA(D)=R
2030 WHILE P<=NT
2040 OP$=TK$(P)
2050 IF OP$<>"+" AND OP$<>"-" THEN GOTO 2090
2055 OPF$(D)=OP$
2060 P=P+1: GOSUB 2100: EB(D)=R
2070 IF OPF$(D)="+" THEN EA(D)=EA(D)+EB(D) ELSE EA(D)=EA(D)-EB(D)
2080 WEND
2090 R=EA(D): D=D-1: RETURN
2100 REM term -> R
2110 D=D+1
2120 GOSUB 2200: TA(D)=R
2130 WHILE P<=NT
2140 OP$=TK$(P)
2150 IF OP$<>"*" AND OP$<>"/" THEN GOTO 2190
2155 OPF$(D)=OP$
2160 P=P+1: GOSUB 2200: TB(D)=R
2170 IF OPF$(D)="*" THEN TA(D)=TA(D)*TB(D) ELSE TA(D)=TA(D)/TB(D)
2180 WEND
2190 R=TA(D): D=D-1: RETURN
2200 REM factor -> R
2210 D=D+1
2220 IF TK$(P)="(" THEN
2230 P=P+1: GOSUB 2000: FA(D)=R
2240 IF TK$(P)=")" THEN P=P+1
2250 ELSE
2260 FA(D)=VAL(TK$(P)): P=P+1
2270 END IF
2280 R=FA(D): D=D-1: RETURN
```

Verified: `"12 + 3 * (4 - 1)"` tokenizes to `12 + 3 * ( 4 - 1 )` and
evaluates to **21**.

## Graph traversal (BFS / DFS)

An adjacency matrix `G(n,n)` plus a visited array. BFS uses a queue
(head/tail); DFS uses a stack (top) — both are just arrays + an index.

```basic
1000 REM BFS from node 1
1010 HEAD=1: TAIL=0
1020 TAIL=TAIL+1: Q(TAIL)=1: VIS(1)=1
1030 WHILE HEAD<=TAIL
1040 U=Q(HEAD): HEAD=HEAD+1
1050 PRINT U;
1060 FOR V=1 TO NV
1070 IF G(U,V)=1 AND VIS(V)=0 THEN TAIL=TAIL+1: Q(TAIL)=V: VIS(V)=1
1080 NEXT V
1090 WEND
1100 RETURN
2000 REM DFS from node 1 (push neighbours in reverse for ascending order)
2010 TOP=0: TOP=TOP+1: ST(TOP)=1
2020 WHILE TOP>0
2030 U=ST(TOP): TOP=TOP-1
2040 IF VIS(U)=0 THEN
2050 VIS(U)=1: PRINT U;
2060 FOR V=NV TO 1 STEP -1
2070 IF G(U,V)=1 AND VIS(V)=0 THEN TOP=TOP+1: ST(TOP)=V
2080 NEXT V
2090 END IF
2100 WEND
2110 RETURN
```

Verified on a 5-node graph: BFS from 1 = `1 2 4 3 5`; DFS = `1 2 3 5 4`.

## Dynamic programming

**0/1 knapsack** — a 1D rolling array, iterating capacity DOWN so each item
is used at most once:

```basic
DIM W(3), V(3), K(5)
FOR I=0 TO NI-1
  FOR C=CAP TO W(I) STEP -1
    T=K(C-W(I))+V(I)
    IF T>K(C) THEN K(C)=T
  NEXT C
NEXT I
```

Verified: items (2,3),(3,4),(4,5),(5,6), capacity 5 → max value **7**.

**Edit distance (Levenshtein)** — a 2D table (default 0-based so the
`0..n` row/column works):

```basic
DIM ED(10,10)
FOR I=0 TO LA: ED(I,0)=I: NEXT I
FOR J=0 TO LB: ED(0,J)=J: NEXT J
FOR I=1 TO LA
  FOR J=1 TO LB
    C=1
    IF MID$(A$,I,1)=MID$(B$,J,1) THEN C=0
    M=ED(I-1,J)+1
    IF ED(I,J-1)+1<M THEN M=ED(I,J-1)+1
    IF ED(I-1,J-1)+C<M THEN M=ED(I-1,J-1)+C
    ED(I,J)=M
  NEXT J
NEXT I
```

Verified: `kitten` → `sitting` = **3**.

## Event loops / dispatch tables

A menu-driven program is a `FOR`/`WHILE` loop reading the next event, with
`ON choice GOSUB handler1, handler2, ...` dispatching to a handler table.
State lives in globals the handlers mutate.

```basic
TOTAL=0
FOR I=1 TO 5
  CHOICE=CH(I)                 ' event source
  IF CHOICE=0 THEN GOTO Quit
  ON CHOICE GOSUB 1000,2000,3000
  PRINT "step"; I; " total="; TOTAL
NEXT I
1000 TOTAL=TOTAL+10: RETURN    ' add
2000 TOTAL=TOTAL-3: RETURN     ' subtract
3000 TOTAL=0: RETURN           ' reset
```

Verified sequence add/sub/add/reset/quit → totals `10, 7, 17, 0`, then
`quit at step 5`.

## Backtracking (N-Queens)

Recursive backtracking with constraint arrays (columns + two diagonals).
The trap: **the FOR loop variable is a global and the recursive call
clobbers it** — after the call, `C` is the callee's value, so the caller's
`NEXT C` breaks (`?SUBSCRIPT OUT OF RANGE`). Save it per frame:

```basic
1000 REM place a queen in ROW
1005 D=D+1
1010 IF ROW>N THEN COUNT=COUNT+1: GOSUB 2000: D=D-1: RETURN
1020 FOR C=1 TO N
1030 IF COL(C)=1 THEN GOTO 1090
1040 IF D1(ROW-C+8)=1 THEN GOTO 1090
1050 IF D2(ROW+C)=1 THEN GOTO 1090
1060 COL(C)=1: D1(ROW-C+8)=1: D2(ROW+C)=1: Q(ROW)=C
1065 CF(D)=C                 ' save the loop variable for this frame
1070 ROW=ROW+1: GOSUB 1000: ROW=ROW-1
1075 C=CF(D)                 ' restore it before NEXT
1080 COL(C)=0: D1(ROW-C+8)=0: D2(ROW+C)=0
1090 NEXT C
1100 D=D-1
1110 RETURN
```

Verified: 8-queens finds the first solution `1 5 8 6 3 7 2 4` and counts
**92** solutions.

## String algorithms (KMP + palindrome)

KMP builds an LPS (longest prefix-suffix) table, then scans in O(n+m).
**`FOUND` is a reserved built-in** (the ISAM status function) — naming a
variable `FOUND` is `?UNKNOWN STATEMENT: FOUND`; use `POS`.

```basic
' LPS(1..LP): length of the longest proper prefix that is also a suffix
LPS(1)=0: K=0: I=2
WHILE I<=LP
  IF MID$(P$,I,1)=MID$(P$,K+1,1) THEN
    K=K+1: LPS(I)=K: I=I+1
  ELSE
    IF K>0 THEN K=LPS(K) ELSE LPS(I)=0: I=I+1
  END IF
WEND

' search
I=1: J=1: POS=0
WHILE I<=LT
  IF MID$(T$,I,1)=MID$(P$,J,1) THEN
    I=I+1: J=J+1
    IF J>LP THEN POS=I-LP: GOTO Done
  ELSE
    IF J>1 THEN J=LPS(J-1)+1 ELSE I=I+1
  END IF
WEND
```

Verified: `ABABCABAB` in `ABABDABACDABABCABAB` → position **11**.

Palindrome — two pointers walking inward:

```basic
PAL=1: L=1: R=LEN(W$)
WHILE L<R
  IF MID$(W$,L,1)<>MID$(W$,R,1) THEN PAL=0: RETURN
  L=L+1: R=R-1
WEND
```

Verified: `racecar` = 1, `hello` = 0.

## Simulation (Conway's Game of Life)

Double-buffer two grids (`G` current, `H` next) so a generation is computed
from the unchanged previous one. Count neighbours with a `-1..1` double
loop, bounds-checked (no short-circuit `AND`, but the array indices are
guarded by the `IF`).

```basic
FOR I=1 TO N: FOR J=1 TO N
  C=0
  FOR DI=-1 TO 1: FOR DJ=-1 TO 1
    R=I+DI: C2=J+DJ
    IF R>=1 AND R<=N AND C2>=1 AND C2<=N THEN
      IF DI<>0 OR DJ<>0 THEN C=C+G(R,C2)
    END IF
  NEXT DJ: NEXT DI
  IF G(I,J)=1 THEN
    IF C=2 OR C=3 THEN H(I,J)=1 ELSE H(I,J)=0
  ELSE
    IF C=3 THEN H(I,J)=1 ELSE H(I,J)=0
  END IF
NEXT J: NEXT I
' copy H back into G
```

Verified: a glider on a 10×10 grid advances correctly through 4
generations (each generation shifts it one cell down-right).

## Matrix operations

Rows × columns loops; `DIM` sizes must match the maths.

```basic
' C = A(2x3) * B(3x2)
FOR I=1 TO 2: FOR J=1 TO 2
  S=0
  FOR K=1 TO 3: S=S+A(I,K)*B(K,J): NEXT K
  C(I,J)=S
NEXT J: NEXT I

' transpose T(J,I) = A(I,J)
FOR I=1 TO 2: FOR J=1 TO 3: T(J,I)=A(I,J): NEXT J: NEXT I

' 3x3 determinant (cofactor expansion)
D=M(1,1)*(M(2,2)*M(3,3)-M(2,3)*M(3,2))-M(1,2)*(M(2,1)*M(3,3)-M(2,3)*M(3,1))+M(1,3)*(M(2,1)*M(3,2)-M(2,2)*M(3,1))
```

Verified: `A*B` = `58 64 / 139 154`, transpose `1 4 / 2 5 / 3 6`,
determinant `-3`.

## A tiny stack VM (interpreter)

A bytecode interpreter is a `PC`, an operand stack, and a `WHILE` dispatch
loop. Advance `PC` BEFORE dispatching, so a jump can simply overwrite it.
Opcodes: 1=PUSH 2=ADD 3=SUB 4=MUL 5=PRINT 6=JMP 7=JZ 8=HALT 9=DUP.

```basic
PC=1: SP=0
WHILE PC<=NIN
  OPCODE=OP(PC): ARG=AR(PC)
  PC=PC+1
  IF OPCODE=1 THEN SP=SP+1: ST(SP)=ARG
  IF OPCODE=2 THEN SP=SP-1: ST(SP)=ST(SP)+ST(SP+1)
  IF OPCODE=3 THEN SP=SP-1: ST(SP)=ST(SP)-ST(SP+1)
  IF OPCODE=4 THEN SP=SP-1: ST(SP)=ST(SP)*ST(SP+1)
  IF OPCODE=5 THEN PRINT "OUT: "; ST(SP)
  IF OPCODE=6 THEN PC=ARG
  IF OPCODE=7 THEN V=ST(SP): SP=SP-1: IF V=0 THEN PC=ARG
  IF OPCODE=8 THEN GOTO Done
  IF OPCODE=9 THEN SP=SP+1: ST(SP)=ST(SP-1)
WEND
Done:
```

Verified with a countdown program (push 3; loop print/sub 1/dup/jz/jmp) →
`OUT: 3`, `OUT: 2`, `OUT: 1`, `halted`.

## Priority queue (binary min-heap)

A 1-based array `H()` plus a count `N`. Push = append + sift up; pop = swap
root with last, shrink, sift down.

```basic
1000 REM push V
1010 N=N+1: H(N)=V: I=N
1020 WHILE I>1
1030 P=INT(I/2)
1040 IF H(P)<=H(I) THEN GOTO 1090
1050 T=H(P): H(P)=H(I): H(I)=T: I=P
1080 WEND
1090 RETURN
2000 REM pop min -> V
2010 V=H(1): H(1)=H(N): N=N-1: I=1
2020 DONE=0
2030 WHILE DONE=0
2040 L=2*I: R=2*I+1: S=I
2050 IF L<=N AND H(L)<H(S) THEN S=L
2060 IF R<=N AND H(R)<H(S) THEN S=R
2070 IF S=I THEN DONE=1 ELSE T=H(S): H(S)=H(I): H(I)=T: I=S
2080 WEND
2090 RETURN
```

Verified: push 5,3,8,1,9,2 → pops `1 2 3 5 8 9`. (`L<=N AND H(L)<H(S)` is
safe without short-circuit: when `L>N`, the first operand is false and the
whole AND is false.)

## Union-Find (disjoint set)

`PAR()` parent + `RK()` rank. `find` walks to the root and compresses the
path; `union` links by rank.

```basic
1000 REM find(A) -> R (path compression)
1010 R=A
1020 WHILE PAR(R)<>R: R=PAR(R): WEND
1030 X=A
1040 WHILE PAR(X)<>R: NX=PAR(X): PAR(X)=R: X=NX: WEND
1050 RETURN
2000 REM union(A,B) by rank
2010 GOSUB 1000: RA=R
2020 A=B: GOSUB 1000: RB=R
2030 IF RA=RB THEN RETURN
2040 IF RK(RA)<RK(RB) THEN T=RA: RA=RB: RB=T
2050 PAR(RB)=RA
2060 IF RK(RA)=RK(RB) THEN RK(RA)=RK(RA)+1
2070 RETURN
```

Verified on 8 nodes / 5 unions: `find(1)=find(4)=1` (same), `find(1)≠find(7)`,
**3 components**.

## Topological sort (Kahn)

Compute in-degrees, enqueue the zero in-degree nodes, then repeatedly pop
one and decrement its neighbours' in-degrees.

```basic
FOR I=1 TO NV: FOR J=1 TO NV: IND(J)=IND(J)+ADJ(I,J): NEXT J: NEXT I
HEAD=1: TAIL=0
FOR I=1 TO NV
  IF IND(I)=0 THEN TAIL=TAIL+1: Q(TAIL)=I
NEXT I
WHILE HEAD<=TAIL
  U=Q(HEAD): HEAD=HEAD+1: CNT=CNT+1
  FOR V=1 TO NV
    IF ADJ(U,V)=1 THEN
      IND(V)=IND(V)-1
      IF IND(V)=0 THEN TAIL=TAIL+1: Q(TAIL)=V
    END IF
  NEXT V
WEND
' CNT < NV means a cycle
```

Verified on 1→2,1→3,2→4,3→4,4→5: order `1 2 3 4 5`, acyclic.

## Huffman coding

Count frequencies, repeatedly merge the two smallest nodes into a parent,
then walk up from each leaf to build its code, and use the tree to decode.

**`LET` is a reserved keyword** (the LET statement) — `DIM LET(60)` is
`?EXPECTED VARIABLE NAME`. Use another name (`LTK`).

```basic
' leaves: one per unique char (NK$=char, NF=freq)
' merge: find the two roots (NP=0) with the smallest NF, make a parent
WHILE NA>1
  A=0: B=0
  FOR I=1 TO NN
    IF NP(I)<>0 THEN GOTO 240
    IF A=0 THEN A=I: GOTO 240
    IF NF(I)<NF(A) THEN B=A: A=I: GOTO 240
    IF B=0 THEN B=I: GOTO 240
    IF NF(I)<NF(B) THEN B=I
240 NEXT I
  NN=NN+1: NF(NN)=NF(A)+NF(B): NL(NN)=A: NR(NN)=B: NP(NN)=0
  NP(A)=NN: NP(B)=NN: NA=NA-1
WEND
' code: walk up; left child = "0", right = "1" (prepend)
' decode: from the root, follow bits until a leaf (NL=0 and NR=0)
```

Verified on `ABRACADABRA` (11 chars → **23 bits**): codes A=0, B=110,
C=100, D=101, R=111; decode round-trips exactly.

## Compiler pipeline (infix → RPN → execute)

The shunting-yard algorithm turns infix into RPN with an operator stack
and an output queue; a second stack executes the RPN. This is the same
tokenizer/VM pair from earlier, wired together.

```basic
' shunting-yard: numbers to OUT$, operators on OST$ by precedence
' ( = push; ) = pop until (; end = pop the rest
' eval: number -> push; operator -> pop B, pop A, push A op B
```

Verified: `12 + 3 * (4 - 1)` → RPN `12 3 4 1 - * +` → **21**.

## A* pathfinding

Grid + g/f/closed arrays + an open list of (row,col) pairs. Pick the
min-f node by linear scan (25 cells — a heap is overkill), expand its
4-neighbours, and keep a parent pointer for reconstruction.

```basic
120 WHILE NOPEN>0
130   MI=1: MF=FS(OL(1),OC(1))
140   FOR I=2 TO NOPEN
150     IF FS(OL(I),OC(I))<MF THEN MF=FS(OL(I),OC(I)): MI=I
160   NEXT I
170   CR=OL(MI): CC=OC(MI)
180   OL(MI)=OL(NOPEN): OC(MI)=OC(NOPEN): NOPEN=NOPEN-1
190   IF CR=TR AND CC=TC THEN FLG=1: GOTO Done
200   IF CL(CR,CC)=1 THEN GOTO 320
210   CL(CR,CC)=1
      ' for each 4-neighbour: TG=GS+1; if TG<GS(nb) then update f,g,parent,push
320 WEND
```

Verified on a 5×5 grid with a column of obstacles: path length **8**
(Manhattan-optimal), e.g. `(1,1) (1,2) (1,3) (2,3) (3,3) (4,3) (5,3) (5,4) (5,5)`.

## Perceptron (a one-neuron neural net)

Weights `W1,W2,B`, learning rate `LR`. For each sample: `sum = W·X + B`,
`out = (sum>0)`, then `W += LR*(Y-out)*X`. Repeat until a pass has no
errors.

```basic
FOR EP=1 TO 100
  ERR=0
  FOR I=1 TO 4
    SUM=W1*X1(I)+W2*X2(I)+B
    OUT=0: IF SUM>0 THEN OUT=1
    E=Y(I)-OUT
    IF E<>0 THEN ERR=ERR+1
    W1=W1+LR*E*X1(I): W2=W2+LR*E*X2(I): B=B+LR*E
  NEXT I
  IF ERR=0 THEN GOTO Converged
NEXT EP
```

Verified: learns AND in **6 epochs** (`w1=0.2 w2=0.1 b=-0.2`) and outputs
`0,0,0,1`.

## Glob / wildcard matching

Iterative matcher with a `*` backtrack point — O(n) typical, no recursion
(so no frame arrays). `?` = one char, `*` = any run.

```basic
I=1: J=1: STAR=0: MARK=1: M=1
WHILE I<=LS
  MATCHED=0
  IF J<=LP THEN
    C$=MID$(P$,J,1)
    IF C$="?" OR C$=MID$(S$,I,1) THEN I=I+1: J=J+1: MATCHED=1
    IF MATCHED=0 AND C$="*" THEN STAR=J: MARK=I: J=J+1: MATCHED=1
  END IF
  IF MATCHED=0 THEN
    IF STAR>0 THEN J=STAR+1: MARK=MARK+1: I=MARK ELSE M=0: RETURN
  END IF
WEND
WHILE J<=LP AND MID$(P$,J,1)="*": J=J+1: WEND
IF J>LP THEN M=1 ELSE M=0
```

Verified: `hello~h*o`=1, `hello~h?llo`=1, `hello~h?l*o`=1, `abc~a*`=1,
`abc~a?c`=1, `abc~a?d`=0, `abc~*b*`=1.

**Control-flow note:** the first version used `GOTO` to the `WEND` as a
"continue" and produced wrong results; the flag-based loop (`MATCHED`)
works. Prefer a flag over `GOTO` for loop control in nontrivial code.

## Text-adventure / game-state engine

Data-driven: rooms and exits in associative arrays, items with a room id,
inventory flags, and a command loop that dispatches verbs to handlers.
No hard-coded room logic — the map is data.

```basic
DIM RM{}, EX{}, IT{}, INV{}
RM{1}="Hall": RM{2}="Kitchen": RM{3}="Cellar"
EX{11}=2: EX{22}=1: EX{24}=3: EX{33}=2     ' key = room*10 + dir(1=N,2=S,3=U,4=D)
IT{"key"}=2: IT{"lamp"}=1: IT{"coin"}=3    ' item -> room
INV{"key"}=0: INV{"lamp"}=0: INV{"coin"}=0

FOR K=1 TO 9
  V$=CV$(K): N$=CN$(K)
  IF V$="look" THEN GOSUB 1000
  IF V$="go"   THEN GOSUB 2000
  IF V$="take" THEN GOSUB 3000
NEXT K
```

Verified script: look (Hall, lamp) → north (Kitchen) → take key → down
(Cellar) → take coin → up (Kitchen) → take lamp (not here) → look
(nothing here) → quit.

## Dijkstra with a heap

Weighted graph in an adjacency matrix (`999` = no edge). The heap stores
**node ids plus the distance at push time** (`H`/`HD`); on pop, a stale
entry (`HD > DIST`) is skipped. This "lazy deletion" avoids a
decrease-key operation.

```basic
160 V=1: DVAL=0: GOSUB 1000          ' push start
170 WHILE N>0
180   GOSUB 2000                     ' pop -> V, DVAL
190   U=V
195   IF DVAL>DIST(U) THEN GOTO 170  ' stale entry
200   IF VIS(U)=1 THEN GOTO 170
210   VIS(U)=1
220   FOR X=1 TO NV
230     IF W(U,X)<999 THEN
240       IF DIST(U)+W(U,X)<DIST(X) THEN
250         DIST(X)=DIST(U)+W(U,X)
260         V=X: DVAL=DIST(X): GOSUB 1000
270       END IF
280     END IF
290   NEXT X
300 WEND
```

Verified on 5 nodes (`1-2:4, 1-3:1, 3-2:2, 2-4:1, 3-4:5, 4-5:3`):
`dist(1)=0 dist(2)=3 dist(3)=1 dist(4)=4 dist(5)=7`.

## Full regex (`.` and `*`)

The classic recursive `isMatch`. `.` = any one char; `x*` = zero or more
`x`. Three cases per call: pattern exhausted, `x*` (try zero, then one),
plain char. With no locals, each frame saves its entry `(i,j)` in
depth-indexed arrays.

```basic
2000 REM match(i,j) -> R   (D = depth)
2005 D=D+1: SI(D)=I: SJ(D)=J
2010 IF J>LP THEN
2020   IF I>LS THEN R=1 ELSE R=0
2030   D=D-1: RETURN
2040 END IF
2050 FM=0
2060 IF I<=LS THEN
2070   IF MID$(P$,J,1)="." OR MID$(P$,J,1)=MID$(S$,I,1) THEN FM=1
2080 END IF
2085 SM(D)=FM                        ' save: recursion clobbers FM
2090 STAR=0
2100 IF J<LP THEN
2110   IF MID$(P$,J+1,1)="*" THEN STAR=1
2120 END IF
2130 IF STAR=1 THEN
2140   I=SI(D): J=SJ(D)+2: GOSUB 2000: R1=R      ' zero occurrences
2150   IF R1=1 THEN R=1: D=D-1: RETURN
2160   IF SM(D)=1 THEN
2170     I=SI(D)+1: J=SJ(D): GOSUB 2000: R2=R    ' one, stay on x*
2180     IF R2=1 THEN R=1: D=D-1: RETURN
2190   END IF
2200   R=0: D=D-1: RETURN
2210 ELSE
2220   IF SM(D)=0 THEN R=0: D=D-1: RETURN
2230   I=SI(D)+1: J=SJ(D)+1: GOSUB 2000: R=R
2240   D=D-1: RETURN
2250 END IF
```

Verified: `aa~a`=0, `aa~a*`=1, `ab~.*`=1, `aab~c*a*b`=1,
`mississ~mis*is*`=1, `mississi~mis*is*i`=1, `mississippi~mis*is*p*`=0,
`mississippi~mis*is*p*.`=0, `mississippi~m.*i`=1, `ab~.*c`=0.

The last two are worth noting: `mis*is*p*.` matches `mississ` + `ippi`
only if `p*` can eat `ipp` — it can't, so **false** is correct (this is
the LeetCode 10 example; a hand-check confirms it).

## Spreadsheet engine (formulas + EVAL)

Cells live in an associative array: a literal (`"10"`) or a formula with
a leading `=` (`"=A1+B1"`). Evaluate by recursively substituting each
known cell reference with its computed value, then `EVAL` the resulting
arithmetic string.

```basic
1000 REM evalCell: parameter in NM$ -> R
1005 D=D+1: CNAM$(D)=NM$
1010 IF CELL${CNAM$(D)}="" THEN R=0: D=D-1: RETURN
1020 IF LEFT$(CELL${CNAM$(D)},1)<>"=" THEN R=VAL(CELL${CNAM$(D)}): D=D-1: RETURN
1030 FD$(D)=MID$(CELL${CNAM$(D)},2)
1040 FOR I=1 TO NC
1050   FI(D)=I
1060   NM$=NAMES$(I)
1070   IF INSTR(FD$(D),NM$)>0 THEN
1080     CREF$(D)=NM$
1090     GOSUB 1000
1095     I=FI(D)                     ' restore loop var after recursion
1100     FD$(D)=REPLACE$(FD$(D),CREF$(D),TRIM$(STR$(R)))
1110   END IF
1120 NEXT I
1130 R=EVAL(FD$(D))
1140 D=D-1
1150 RETURN
```

Verified: `A1=10`, `B1=20`, `C1` (`=A1+B1`) → **30**, `D1` (`=C1*2`)
→ **60**.

**Gotchas:** a formula needs the `=` marker or `VAL` silently yields 0.
Names starting with `FN` are parsed as function calls (`FN$` →
`?UNDEFINED FUNCTION`), so use `CNAM$`/`CREF$`. And the outer cell loop
must use a different variable (`K`) — the inner `FOR I` clobbers it.

## Longest common subsequence + diff

Classic O(n·m) DP, then backtrack from the **end** for a clean alignment
(backtracking from the front greedily inserts the whole prefix).

```basic
90 FOR I=1 TO LA
100   FOR J=1 TO LB
110     IF MID$(A$,I,1)=MID$(B$,J,1) THEN
120       L(I,J)=L(I-1,J-1)+1
130     ELSE
140       IF L(I-1,J)>=L(I,J-1) THEN L(I,J)=L(I-1,J) ELSE L(I,J)=L(I,J-1)
150     END IF
160   NEXT J
170 NEXT I
```

Then walk backwards from `(LA,LB)`, emitting `= c` for a match, `- c` for
an A-only char, `+ c` for a B-only char, and prepend each step.

Verified: `ABCBDAB` vs `BDCABA` → **LCS length 4**, LCS `BCBA`, diff
`- A = B + D = C + A = B - D = A - B` (4 matches, 3 deletes, 2 inserts;
both sides reconstruct exactly).

**Array note:** the DP needs row/column 0, so use the default 0-based
arrays — `OPTION BASE 1` makes `L(0,0)` a `?SUBSCRIPT OUT OF RANGE`.

## Lisp-style S-expression evaluator

Three stages: tokenize, parse into an array-based tree, evaluate. Nodes
carry a type tag (`0` number, `1` symbol, `2` list), a value, a child
count, and up to 10 child ids.

```basic
2000 REM parse -> node id in NID
2005 D=D+1: FTP(D)=TP
2010 TP=TP+1: T$=TK$(TP)
2020 IF T$="(" THEN
2030   NN=NN+1: NID=NN: FMY(D)=NID: NT(FMY(D))=2: NC(FMY(D))=0
2040   WHILE TK$(TP+1)<>")"
2050     GOSUB 2000: NC(FMY(D))=NC(FMY(D))+1: CH(FMY(D),NC(FMY(D)))=NID
2060   WEND
2070   TP=TP+1
2080 ELSE
2090   NN=NN+1: NID=NN: FMY(D)=NID
2100   IF T$="0" OR VAL(T$)<>0 THEN NT(FMY(D))=0: NV(FMY(D))=VAL(T$) ELSE NT(FMY(D))=1: NS$(FMY(D))=T$
2110 END IF
2115 NID=FMY(D)
2120 D=D-1
2130 RETURN
```

Evaluation recurses over the tree; each frame saves its node id, the
operator string, and the first operand:

```basic
3000 REM eval node NID -> R
3005 D=D+1: FEV(D)=NID
3010 IF NT(FEV(D))=0 THEN R=NV(FEV(D)): D=D-1: RETURN
3020 IF NT(FEV(D))=1 THEN R=VAL(NS$(FEV(D))): D=D-1: RETURN
3030 FOP$(D)=NS$(CH(FEV(D),1))
3040 NID=CH(FEV(D),2): GOSUB 3000: FA1(D)=R
3050 NID=CH(FEV(D),3): GOSUB 3000: A2=R
3060 IF FOP$(D)="+" THEN R=FA1(D)+A2
3070 IF FOP$(D)="-" THEN R=FA1(D)-A2
3080 IF FOP$(D)="*" THEN R=FA1(D)*A2
3090 IF FOP$(D)="/" THEN R=FA1(D)/A2
3100 D=D-1: RETURN
```

Verified: `(+ 1 2)`=3, `(* (+ 1 2) 3)`=9, `(+ (* 2 3) 1)`=7,
`(+ 1 (* 2 3))`=7, `(- 10 4)`=6, `(* 2 (+ 3 4))`=14,
`(+ (* 2 3) (- 10 4))`=**12**.

**The bug worth remembering:** allocating node ids with `NID=NID+1`
reuses ids after a sub-parse returns (it resets `NID` to the sub-node).
Two sibling sublists then collide and silently corrupt the tree — the
two-sublist case returned 6 instead of 12 until I switched to a
monotonic counter `NN=NN+1: NID=NN`. Also, only reset the fields you
read: `NV`/`NS$`/`NC` keep stale values across nodes, which is harmless
only because `NT` is checked first.

## 2-3 tree (B-tree of order 3)

Every node holds 1 or 2 sorted keys and 2 or 3 children. Insert descends
to a leaf, adds the key, and **splits on the way back up** when a node
reaches 3 keys: left keeps `k1`, `k2` is promoted as the median, right
gets `k3`.

```basic
30 DIM NK(100), K(100,3), C(100,3)   ' key count, keys, children
...
1000 REM insert(node,key) -> SP, SMED, SNEW
1005 D=D+1: ND(D)=NODE: FC(D)=KY
1010 IF C(ND(D),0)=0 THEN                       ' leaf
1020   GOSUB 2000                              ' add KY sorted
1030   IF NK(ND(D))<3 THEN SP=0: D=D-1: RETURN
1040   NODE=ND(D): GOSUB 3000                  ' split
1050   D=D-1: RETURN
1060 END IF
1070 I=0                                        ' pick child
1080 IF I<NK(ND(D)) THEN
1085   IF FC(D)>K(ND(D),I+1) THEN I=I+1: GOTO 1080
1090 END IF
1100 FI(D)=I
1110 NODE=C(ND(D),I): KY=FC(D): GOSUB 1000
1130 IF SP=0 THEN D=D-1: RETURN
1140 NODE=ND(D): GOSUB 4000                     ' absorb median + new child
1150 IF NK(ND(D))<3 THEN SP=0: D=D-1: RETURN
1160 NODE=ND(D): GOSUB 3000
1170 D=D-1: RETURN
```

The split itself:

```basic
3000 REM split NODE (3 keys) -> SMED, SNEW
3010 NN=NN+1: NW=NN: NK(NW)=1: K(NW,1)=K(NODE,3)
3020 SMED=K(NODE,2)
3030 NK(NODE)=1: K(NODE,2)=0: K(NODE,3)=0
3040 C(NW,0)=C(NODE,2): C(NW,1)=C(NODE,3)
3050 C(NODE,2)=0: C(NODE,3)=0
3060 SP=1: SNEW=NW
3070 RETURN
```

If the root splits, allocate a new root holding the median with the old
root and the new node as its two children.

Verified on keys `10,20,5,6,12,30,7,17`:
`in-order: 5 6 7 10 12 17 20 30`, **7 nodes**, `search 12 = 1`,
`search 99 = 0`, `search 5 = 1`.

**Reserved-word traps hit here:** `KEY` (keyed-file built-in) →
`?UNKNOWN STATEMENT: KEY`; `FN` (DEF FN) → `?EXPECTED FUNCTION NAME
AFTER FN`; `NEW` (clear program). Renamed to `KY`, `ND`, `NW`. Also,
`PRINT #1, x;` with a trailing semicolon still ends the line in file
output — build the line in a string and print once.

## No short-circuit evaluation

**`AND` and `OR` evaluate BOTH operands.** `IF A<>0 AND 10/A>1` with
`A=0` raises `?DIVISION BY ZERO` — it does not skip the second test.
Guard with a nested `IF`:

```basic
IF A<>0 THEN
    IF 10/A > 1 THEN PRINT "ok"
END IF
```

## Performance reality check

| Task | Result |
|------|--------|
| `fib_iter(40)` (bottom-up) | 102334155 in **0.0011 s** |
| `fib_naive(20)` | 6765 in **0.63 s** |
| `fib_naive(30)` | `?EXECUTION TIME LIMIT REACHED` (15 s) |
| `fib_memo(30)` | 832040 in **0.0117 s** |

Limits that shape the choice of algorithm: **15 s wall clock / 55M
iterations**, `GOSUB` depth **1024**, array **65,535** elements. Prefer
iterative or memoized algorithms for anything exponential.

## Quick reference

```
Recursion      GOSUB + depth-indexed frame arrays (no locals)
Tail recursion state passed by mutation; no frame needed
DEF FN         single expression, cannot recurse
Memoization    DIM CACHE{} keyed by arg + frame arrays
Sorting        bubble / insertion / quicksort (Lomuto + FOR)
Searching      linear / binary (sorted array)
Linked list    LD() data + LN() next-index (0 = end)
Tree           TK()/TL()/TR() + ROOT, recursive in-order
Objects        DIM OBJ{} + GOSUB methods
State machine  STATE + ON STATE+1 GOSUB (exactly one dispatch)
Parser         tokenize -> expr/term/factor; save OP$ per frame
Graph          BFS queue (head/tail) / DFS stack (top)
DP             knapsack 1D rolling; edit distance 2D table
Event loop     FOR/WHILE + ON choice GOSUB handler table
Backtracking   recursion + constraint arrays; save the FOR var per frame
String match   KMP LPS table; palindrome two-pointer
Simulation     double-buffer grids (Life)
Matrices       row*col loops; cofactor determinant
Tiny VM        PC + operand stack + WHILE dispatch (advance PC first)
Heap           H() 1-based; sift up/down (push/pop min)
Union-Find     PAR()+RK(); path compression + union by rank
Topo sort      in-degrees + queue (Kahn)
Huffman        merge two smallest; codes by walking up
Compiler       infix -> RPN (shunting-yard) -> stack eval
A*             open list + g/f/closed + Manhattan h
Perceptron     W += LR*(Y-out)*X until no errors
Glob           '?' one char, '*' any run; backtrack MARK
Adventure      associative-array rooms/items + command loop
Dijkstra       heap of (node,dist) + lazy deletion
Regex          recursive isMatch; save (i,j),FM per depth
Spreadsheet    '=' formulas; substitute refs then EVAL
LCS / diff     DP table + backward walk for alignment
Lisp eval      tokenize -> typed-node tree -> recursive eval
2-3 tree       NK/K/C arrays; split on the way up
AND / OR       NOT short-circuiting; nest IFs to guard
```
