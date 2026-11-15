# Building UIs and Panels with BOXCHAR$, CP310$, and TAB

A cookbook of verified patterns for drawing terminal panels, menus, tables,
and status displays. Every pattern here was run on the live interpreter
(v3.0.1), and the rendering claims were checked on **both** x3270 and
c3270 v4.1ga10.

## The three hard constraints

1. **No vertical cursor positioning.** There is no `LOCATE`/`GOTOXY`.
   Output flows top-to-bottom; the only horizontal control is `TAB(n)` and
   `SPACE$(n)`. Panels are drawn in sequence, never overlaid.
2. **79 usable columns.** An 80-character line loses its LAST character
   silently (`PRINT "A"+SPACE$(78)+"B"` prints only `A`). `TAB(80)` and
   above drop the following text. Design to 79.
3. **Only the single-line box set renders.** `BOXCHAR$(1-6)` and the
   matching `CP310$(1-6)` draw correctly. The double-line set and most
   other graphics fall back to `■` in **both** x3270 and c3270 (details
   below), so a panel that must look right uses single-line box characters
   only.

## What actually renders (x3270 and c3270 are identical)

The functions return correct Unicode either way — verified by writing all
50 characters to a file and reading it back:

```
1=┌ 2=┐ 3=└ 4=┘ 5=─ 6=│    7=╔ 8=╗ 9=╚ 10=╝ 11=═ 12=║
13=├ 14=┤ 15=┬ 16=┴ 17=┼   18=╬ 19=╠ 20=╣
21=█ 22=▀ 23=▄ 24=▌ 25=▐   26=░ 27=▒ 28=▓
29=← 30=→ 31=↑ 32=↓        33=■ 34=□ 35=● 36=○
37=▲ 38=▼ 39=◄ 40=►        41=╭ 42=╮ 43=╰ 44=╯
45=· 46=• 47=╳ 48=╱ 49=╲   50=∙
```

Screen rendering, measured from an `Ascii` dump:

| Range | Characters | Renders? |
|---|---|---|
| 1-6 | `┌ ┐ └ ┘ ─ │` | yes |
| 7-10 | `╔ ╗ ╚ ╝` | **no** — `■ ■ ■ ■` |
| 11-12 | `═ ║` | **no** — blank (spaces) |
| 13-17 | `├ ┤ ┬ ┴ ┼` | yes |
| 18-20 | `╬ ╠ ╣` | **no** — `■ ■ ■` |
| 21 | `█` full block | **no** — `■` |
| 22-25 | `▀ ▄ ▌ ▐` half blocks | yes |
| 26-28 | `░ ▒ ▓` shades | **no** — `■ ■ ■` |
| 29-32 | `← → ↑ ↓` | yes |
| 33 | `■` black square | partial — renders as `∎` |
| 34-35 | `□ ●` | **no** — `■ ■` |
| 36 | `○` white circle | yes |
| 37-44 | `▲ ▼ ◄ ► ╭ ╮ ╰ ╯` | **no** — all `■` |
| 45-46 | `· •` | yes |
| 47-49 | `╳ ╱ ╲` | **no** — all `■` |
| 50 | `∙` | yes |

### Why c3270 does not help

c3270 is the curses (no-X11) member of the same suite and was re-tested
specifically because a wide-curses build looks like it should handle the
extended graphics. It does not:

- c3270 has **no CP310 code page**: `c3270 -codepage cp310` exits with
  `Warning: Cannot find code page "cp310"`. Its code-page list is the same
  as x3270's (cp037, cp273, ..., `bracket`).
- The BBS sends the graphics as **3270 Graphic Escape** sequences — the
  trace shows `SUB SUB GraphicEscape 'b'` (`3F 3F 08 82`) — and the
  `bracket` charset (CP037 modified) maps only the bracket-range glyphs,
  not the CP310 double-line/graphics set.
- The BBS user record's code page is **CP437**, not CP310, and the User
  Profile screen has no field to change it.

So c3270 renders exactly the same subset as x3270. The win of c3270 is
headless operation, not better graphics.

**Practical rule:** build panels from `BOXCHAR$(1-6)` (or `CP310$(1-6)`),
`CP310$(13-17)` for T-junctions, `CP310$(22-25)` for half blocks, and
`CP310$(29-32)` for arrows. Never rely on 7-12, 18-21, 26-28, or 33-44.

## TAB: the horizontal positioning function

`TAB(n)` is **a string function that returns spaces**, not a cursor
command. It returns enough spaces to reach column `n` from the current
print position, and `""` if that position is already at or past `n`.

```basic
PRINT "A";TAB(10);"B"        ' B at column 10
PRINT "[";TAB(5);"]"         ' [   ]   (] at column 5)
PRINT "[";TAB(1);"]"         ' []      (no backward movement)
PRINT "[";TAB(0);"]"         ' []      (TAB(0) is empty)
PRINT "X";TAB(5.9);"Y"       ' Y at column 5 (truncates)
PRINT TAB("5");"Z"           ' Z at column 1 (string arg = no move)
X$ = TAB(5)                  ' X$ = four spaces (a string!)
PRINT LEN(TAB(5))            ' 4
```

Verified semantics:

- **Absolute, 1-based**: `TAB(10)` targets column 10, not "10 more".
- **Never moves backward**: if the current position is past `n`, it
  returns `""`.
- **Truncates** non-integers: `TAB(5.9)` = `TAB(5)`.
- **String argument is a no-op** (`TAB("5")` returns `""`, no error).
- **Works in file output**: `PRINT #1, "A";TAB(10);"B"` writes
  `A        B`.
- **Continues across PRINTs** with a trailing semicolon:
  `PRINT "A";TAB(5);` then `PRINT "B"` gives `A   B` on one line.
- **`;` vs `+` matters.** With `;` each item is printed in order, so TAB
  sees the real current column. With `+` the whole expression is
  evaluated first, so TAB is evaluated at the start of the expression and
  over-pads:
  `PRINT "A";TAB(5);"B"` → B at 5; `PRINT "A"+TAB(5)+"B"` → B at 6.
- **Commas are not TAB.** `,` advances to the next 14-column zone
  (15, 29, 43, 57, 71); `PRINT "B",TAB(10),"C"` puts C at 29 because the
  comma already jumped past 10. Use `;` with TAB.
- **Maximum is 79.** `TAB(80)` and above drop the following text.

### The TAB gotcha that matters: it counts UTF-8 bytes

TAB's column counter advances by the character's **UTF-8 byte length**,
not by one per character. `LEN()` correctly returns 1 for these
characters, but TAB still counts 3 bytes for a box character and 2 for
`·`:

| Text before TAB | Bytes | `TAB(20)` lands at |
|---|---|---|
| `X` (ASCII) | 1 | column 21 (correct) |
| `·` (`CP310$(45)`) | 2 | column 20 (1 early) |
| `■` / `│` (3-byte graphics) | 3 | column 19 (2 early) |
| `AB` (ASCII) | 2 | column 21 (correct) |

So `PRINT BOXCHAR$(6);TAB(20);BOXCHAR$(6)` draws a row 2 columns short of
a 20-wide top border. **Do not use TAB after box characters.** Build panel
rows with `+` and explicit `SPACE$` instead — that is exact, because no
column counter is involved:

```basic
PRINT BOXCHAR$(6) + SPACE$(18) + BOXCHAR$(6)
```

Verified aligned: left and right `│` both at screen column 2 and 21,
matching a `┌` + 18×`─` + `┐` border.

## Pattern 1: a box (single-line, verified aligned)

```basic
W = 20
HL$ = ""                       ' build the horizontal line with a loop
FOR I = 1 TO W - 2
    HL$ = HL$ + BOXCHAR$(5)
NEXT I
PRINT BOXCHAR$(1) + HL$ + BOXCHAR$(2)            ' top
PRINT BOXCHAR$(6) + SPACE$(W - 2) + BOXCHAR$(6)  ' blank row
PRINT BOXCHAR$(3) + HL$ + BOXCHAR$(4)            ' bottom
```

```
┌──────────────────┐
│                  │
└──────────────────┘
```

Build the horizontal line with a loop, never by concatenating 20+
`BOXCHAR$(5)` calls inline — the 255-character line limit skips the whole
line at load (`?WARNING: LINE TOO LONG`).

## Pattern 2: a titled panel (verified)

```basic
W = 20
GOSUB 300                                        ' top border
PRINT BOXCHAR$(6) + "  TITLE" + SPACE$(W - 9) + BOXCHAR$(6)
PRINT BOXCHAR$(6) + SPACE$(W - 2) + BOXCHAR$(6)
PRINT BOXCHAR$(6) + "  Status: OK" + SPACE$(W - 14) + BOXCHAR$(6)
GOSUB 400                                        ' bottom border
END

300 HL$ = "": FOR I = 1 TO W - 2: HL$ = HL$ + BOXCHAR$(5): NEXT I
PRINT BOXCHAR$(1) + HL$ + BOXCHAR$(2): RETURN

400 HL$ = "": FOR I = 1 TO W - 2: HL$ = HL$ + BOXCHAR$(5): NEXT I
PRINT BOXCHAR$(3) + HL$ + BOXCHAR$(4): RETURN
```

Verified output:

```
┌──────────────────┐
│  TITLE           │
│                  │
│  Status: OK      │
└──────────────────┘
```

## Pattern 3: a table (T-junctions)

Only the single-line junctions render: `┬` (15), `┴` (16), `├` (13),
`┤` (14), `┼` (17).

```basic
PRINT BOXCHAR$(1)+BOXCHAR$(5)+CP310$(15)+BOXCHAR$(5)+CP310$(15)+BOXCHAR$(5)+BOXCHAR$(2)
PRINT BOXCHAR$(6)+" A "+BOXCHAR$(6)+" B "+BOXCHAR$(6)+" C "+BOXCHAR$(6)
PRINT CP310$(13)+BOXCHAR$(5)+CP310$(17)+BOXCHAR$(5)+CP310$(17)+BOXCHAR$(5)+CP310$(14)
PRINT BOXCHAR$(6)+" D "+BOXCHAR$(6)+" E "+BOXCHAR$(6)+" F "+BOXCHAR$(6)
PRINT BOXCHAR$(3)+BOXCHAR$(5)+CP310$(16)+BOXCHAR$(5)+CP310$(16)+BOXCHAR$(5)+BOXCHAR$(4)
```

```
┌─┬─┬─┐
│ A │ B │ C │
├─┼─┼─┤
│ D │ E │ F │
└─┴─┴─┘
```

(Note the `│ A │` rows are 3 columns per cell while the borders are 2 —
add one more `BOXCHAR$(5)` per cell if you want them to line up; the
junctions themselves render correctly.)

## Pattern 4: a progress bar that actually renders

`█` (21) and `░` (26) both fall back to `■`, so the classic bar is
unusable. Use the half blocks that DO render, or plain ASCII:

```basic
' ASCII (always safe)
PRINT "[" + STRING$(6, "#") + STRING$(4, "-") + "]"

' half-block bar (22 = upper, 23 = lower)
BAR$ = ""
FOR I = 1 TO 10
    IF I <= 6 THEN BAR$ = BAR$ + CP310$(22) ELSE BAR$ = BAR$ + " "
NEXT I
PRINT "[" + BAR$ + "]"
```

## Pattern 5: centering text

```basic
T$ = "MAIN MENU"
LEFT = INT((W - 2 - LEN(T$)) / 2)
RIGHT = W - 2 - LEN(T$) - LEFT
PRINT BOXCHAR$(6) + SPACE$(LEFT) + T$ + SPACE$(RIGHT) + BOXCHAR$(6)
```

`LEN()` is character-accurate (returns 1 for a box character), so
centering arithmetic is safe — unlike TAB, which counts bytes.

## Pattern 6: reusable box subroutine (GOSUB)

GOSUB takes no parameters; pass the size through globals:

```basic
BW = 24
GOSUB 300          ' top border
PRINT BOXCHAR$(6) + SPACE$(BW - 2) + BOXCHAR$(6)
GOSUB 400          ' bottom border
END

300 HL$ = "": FOR I = 1 TO BW - 2: HL$ = HL$ + BOXCHAR$(5): NEXT I
PRINT BOXCHAR$(1) + HL$ + BOXCHAR$(2): RETURN

400 HL$ = "": FOR I = 1 TO BW - 2: HL$ = HL$ + BOXCHAR$(5): NEXT I
PRINT BOXCHAR$(3) + HL$ + BOXCHAR$(4): RETURN
```

## Pattern 7: COLOR styling

`COLOR` goes at the end of the PRINT and colors the whole line:

```basic
PRINT BOXCHAR$(1) + HL$ + BOXCHAR$(2) COLOR GREEN
PRINT BOXCHAR$(6) + " OK " + BOXCHAR$(6) COLOR GREEN
```

Colors: WHITE RED YELLOW PINK GREEN BLUE TURQUOISE; modifiers BLINK,
REVERSEVIDEO. Use color to distinguish panel types (title bars, alerts,
status).

## Gotchas

- **TAB after a box character is 2 columns early** (TAB counts UTF-8
  bytes). Use `+` and `SPACE$` for panel rows; reserve TAB for pure-ASCII
  lines.
- **`+` and `;` differ for TAB**: `;` evaluates TAB in print order (right
  result); `+` evaluates it at the start of the expression (over-pads by
  the length of the preceding text).
- **Commas jump to 14-column zones** (15, 29, 43, ...), not to TAB
  positions. Use `;` with TAB.
- **79 usable columns** — the 80th character is dropped, and `TAB(80+)`
  drops the following text.
- **Double-line and most graphics render as `■` in both x3270 and c3270**
  (see the table above). Single-line `BOXCHAR$` is the portable choice.
- **255-character line limit.** Build horizontal borders with a loop;
  an over-long line is skipped at load with a warning.
- **No vertical positioning** — design panels top-to-bottom. A 24×80
  screen fits a 24-row panel; leave a row for the `>` prompt if the
  program returns to READY.
- **`PRINT #` uses the same TAB/`;`/`,` rules as the screen**, including
  the byte-counting TAB. Build file lines with `+` and `SPACE$` when the
  content includes box characters.
