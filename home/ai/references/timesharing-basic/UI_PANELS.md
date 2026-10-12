# Building UIs and Panels with BOXCHAR$ and CP310$

A cookbook of verified patterns for drawing terminal panels, menus, tables,
and status displays. Every pattern was run on the live interpreter.

## The two hard constraints

1. **No vertical cursor positioning.** There is no `LOCATE`/`GOTOXY`. You
   can only position horizontally (`TAB(n)`, `SPACE$(n)`); output flows
   top-to-bottom. Panels are drawn in sequence, never overlaid.
2. **255-char line limit.** A border built by concatenating many
   `BOXCHAR$(5)` calls exceeds 255 chars and the whole line is SKIPPED at
   load (`?WARNING: LINE TOO LONG`). Build long borders with a loop.

## The character toolkit

- Single-line box: `BOXCHAR$(1-6)` = `┌ ┐ └ ┘ ─ │`
- Double-line box: `CP310$(7-12)` = `╔ ╗ ╚ ╝ ═ ║`
- Rounded corners: `CP310$(41-44)` = `╭ ╮ ╰ ╯`
- T-junctions: `CP310$(13-16)` = `├ ┤ ┬ ┴`; cross: `CP310$(17)` = `┼`
- Blocks/shades: `CP310$(21-28)` = `█ ▀ ▄ ▌ ▐ ░ ▒ ▓`
- Arrows: `CP310$(29-32)` = `← → ↑ ↓`
- Shapes: `CP310$(33-36)` = `■ □ ● ○`

## Pattern 1: a box (single-line)

```basic
W = 20
HL$ = ""                       ' build the horizontal line with a loop
FOR I = 1 TO W - 2
    HL$ = HL$ + BOXCHAR$(5)
NEXT I
PRINT BOXCHAR$(1) + HL$ + BOXCHAR$(2)     ' top
PRINT BOXCHAR$(6) + SPACE$(W-2) + BOXCHAR$(6)   ' blank row
PRINT BOXCHAR$(3) + HL$ + BOXCHAR$(4)     ' bottom
```

```
┌──────────────────┐
│                  │
└──────────────────┘
```

## Pattern 2: double-line and rounded boxes

```basic
PRINT CP310$(7) + CP310$(11) + CP310$(11) + CP310$(8)   ' ╔══╗
PRINT CP310$(41) + BOXCHAR$(5) + BOXCHAR$(5) + CP310$(42)  ' ╭──╮
```

Double-line renders correctly in data files but shows as `■` in x3270 (see
BOXCHAR_CP310_REFERENCE.md). Rounded corners render fine everywhere.

## Pattern 3: a grid / table (T-junctions)

```basic
PRINT BOXCHAR$(1) + BOXCHAR$(5) + CP310$(15) + BOXCHAR$(5) + CP310$(15) + BOXCHAR$(5) + BOXCHAR$(2)
PRINT BOXCHAR$(6) + " A " + BOXCHAR$(6) + " B " + BOXCHAR$(6) + " C " + BOXCHAR$(6)
PRINT CP310$(13) + BOXCHAR$(5) + CP310$(17) + BOXCHAR$(5) + CP310$(17) + BOXCHAR$(5) + CP310$(14)
PRINT BOXCHAR$(6) + " D " + BOXCHAR$(6) + " E " + BOXCHAR$(6) + " F " + BOXCHAR$(6)
PRINT BOXCHAR$(3) + BOXCHAR$(5) + CP310$(16) + BOXCHAR$(5) + CP310$(16) + BOXCHAR$(5) + BOXCHAR$(4)
```

```
┌─┬─┬─┐
│ A │ B │ C │
├─┼─┼─┤
│ D │ E │ F │
└─┴─┴─┘
```

`┬` (15) tops a column, `┴` (16) bottoms it, `├` (13) / `┤` (14) are side
junctions, `┼` (17) is a full cross.

## Pattern 4: progress bar (blocks)

```basic
PRINT "[" + CP310$(21) + CP310$(21) + CP310$(21) + CP310$(21) + CP310$(21) + CP310$(21) + CP310$(26) + CP310$(26) + CP310$(26) + CP310$(26) + "]"
```

```
[██████░░░░]
```

`█` (21) = filled, `░` (26) = empty. For a dynamic bar, build the string in
a loop: `FOR I = 1 TO PCT: BAR$ = BAR$ + CP310$(21): NEXT I`.

## Pattern 5: centering text in a panel

```basic
T$ = "MAIN MENU"
PAD = (W - 2 - LEN(T$)) / 2
PRINT BOXCHAR$(6) + SPACE$(PAD) + T$ + SPACE$(PAD) + BOXCHAR$(6)
```

`PAD` truncates (floors), so odd leftover space lands on the right. For
exact centering, put the extra space on one side explicitly:
`LEFT = INT((W-2-LEN(T$))/2)` then `RIGHT = W-2-LEN(T$)-LEFT`.

## Pattern 6: reusable box subroutine (GOSUB)

GOSUB takes no parameters, so pass the size through globals:

```basic
BW = 24: BH = 6
GOSUB 300          ' draw top border
... body ...
GOSUB 400          ' draw bottom border
END

300 REM top border of width BW
HL$ = ""
FOR I = 1 TO BW - 2: HL$ = HL$ + BOXCHAR$(5): NEXT I
PRINT BOXCHAR$(1) + HL$ + BOXCHAR$(2)
RETURN

400 REM bottom border of width BW
HL$ = ""
FOR I = 1 TO BW - 2: HL$ = HL$ + BOXCHAR$(5): NEXT I
PRINT BOXCHAR$(3) + HL$ + BOXCHAR$(4)
RETURN
```

## Pattern 7: a full panel (title + body + footer)

```basic
BW = 24
GOSUB 300                                   ' top border
T$ = "SYSTEM STATUS"
PAD = (BW - 2 - LEN(T$)) / 2
PRINT BOXCHAR$(6) + SPACE$(PAD) + T$ + SPACE$(PAD) + BOXCHAR$(6)
PRINT BOXCHAR$(6) + "  " + CP310$(30) + " Next  " + CP310$(29) + " Prev  " + BOXCHAR$(6)
PRINT BOXCHAR$(6) + "  " + CP310$(31) + " Up    " + CP310$(32) + " Down  " + BOXCHAR$(6)
PRINT BOXCHAR$(6) + "  Status: OK          " + BOXCHAR$(6)
GOSUB 400                                   ' bottom border
```

```
┌──────────────────────┐
│    SYSTEM STATUS    │
│  → Next  ← Prev  │
│  ↑ Up    ↓ Down  │
│  Status: OK          │
└──────────────────────┘
```

## Pattern 8: COLOR styling

`COLOR` goes at the end of the PRINT and colors the whole line:

```basic
PRINT BOXCHAR$(1) + HL$ + BOXCHAR$(2) COLOR GREEN
PRINT BOXCHAR$(6) + " OK " + BOXCHAR$(6) COLOR GREEN
```

Colors: WHITE RED YELLOW PINK GREEN BLUE TURQUOISE; modifiers BLINK,
REVERSEVIDEO. Use color to distinguish panel types (title bars, alerts,
status).

## Gotchas

- **`PRINT #` uses the same comma(tab)/semicolon(concat) rules as screen
  PRINT**, which breaks box alignment in data files if you use commas.
  When writing a panel to a file, concatenate each row into ONE string with
  `+` (no `;` or `,` separators) to avoid the tab-to-zone behavior.
- **Long borders hit the 255-char line limit.** Always build horizontal
  lines with a loop, never by concatenating 20+ `BOXCHAR$(5)` calls inline.
- **Double-line box (CP310$ 7-12) shows as `■` in x3270.** Use single-line
  `BOXCHAR$` for anything that must look right in x3270; reserve double-line
  for real CP310 terminals.
- **No vertical positioning** — design panels top-to-bottom. A 24x80 (Mod2)
  screen fits a 24-row panel; leave room for the `>` prompt if the program
  returns to READY.
