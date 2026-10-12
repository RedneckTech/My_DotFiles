# BOXCHAR$(n) and CP310$(n) — Box-Drawing & Graphics Characters

Everything below was verified by dumping the raw bytes the functions return
on the live v3.0.0 interpreter (not just eyeballing the screen, which is
misleading for the double-line characters).

## BOXCHAR$(n) — single-line box (n = 1-6)

| n | Char | Unicode | Name |
|---|------|---------|------|
| 1 | ┌ | U+250C | top-left corner |
| 2 | ┐ | U+2510 | top-right corner |
| 3 | └ | U+2514 | bottom-left corner |
| 4 | ┘ | U+2518 | bottom-right corner |
| 5 | ─ | U+2500 | horizontal line |
| 6 | │ | U+2502 | vertical line |

`BOXCHAR$(1-6)` is byte-for-byte identical to `CP310$(1-6)`.

## CP310$(n) — extended graphics (n = 1-50)

| n | Char | Unicode | Description |
|---|------|---------|-------------|
| 1-6 | ┌ ┐ └ ┘ ─ │ | U+250C..U+2502 | single-line box (same as BOXCHAR$) |
| 7 | ╔ | U+2554 | double top-left |
| 8 | ╗ | U+2557 | double top-right |
| 9 | ╚ | U+255A | double bottom-left |
| 10 | ╝ | U+255D | double bottom-right |
| 11 | ═ | U+2550 | double horizontal |
| 12 | ║ | U+2551 | double vertical |
| 13 | ├ | U+251C | T-junction (right) |
| 14 | ┤ | U+2524 | T-junction (left) |
| 15 | ┬ | U+252C | T-junction (down) |
| 16 | ┴ | U+2534 | T-junction (up) |
| 17 | ┼ | U+253C | cross (single) |
| 18 | ╬ | U+256C | cross (double) |
| 19 | ╠ | U+2560 | double vert, single right |
| 20 | ╣ | U+2563 | double vert, single left |
| 21 | █ | U+2588 | full block |
| 22 | ▀ | U+2580 | upper half block |
| 23 | ▄ | U+2584 | lower half block |
| 24 | ▌ | U+258C | left half block |
| 25 | ▐ | U+2590 | right half block |
| 26 | ░ | U+2591 | light shade |
| 27 | ▒ | U+2592 | medium shade |
| 28 | ▓ | U+2593 | dark shade |
| 29 | ← | U+2190 | left arrow |
| 30 | → | U+2192 | right arrow |
| 31 | ↑ | U+2191 | up arrow |
| 32 | ↓ | U+2193 | down arrow |
| 33 | ■ | U+25A0 | black square |
| 34 | □ | U+25A1 | white square |
| 35 | ● | U+25CF | black circle |
| 36 | ○ | U+25CB | white circle |
| 37 | ▲ | U+25B2 | black up triangle |
| 38 | ▼ | U+25BC | black down triangle |
| 39 | ◄ | U+25C4 | black left triangle |
| 40 | ► | U+25BA | black right triangle |
| 41 | ╭ | U+256D | rounded top-left |
| 42 | ╮ | U+256E | rounded top-right |
| 43 | ╰ | U+2570 | rounded bottom-left |
| 44 | ╯ | U+256F | rounded bottom-right |
| 45 | · | U+00B7 | middle dot |
| 46 | • | U+2022 | bullet |
| 47 | ╳ | U+2573 | diagonal cross |
| 48 | ╱ | U+2571 | diagonal slash |
| 49 | ╲ | U+2572 | diagonal backslash |
| 50 | ∙ | U+2219 | bullet operator |

## Argument handling (verified)

- **Out-of-range is a runtime error, not a silent return:**
  - `BOXCHAR$(0)` → `?BOXCHAR$ INDEX MUST BE 1-6`
  - `CP310$(0)` → `?CP310$ INDEX 0 NOT DEFINED (USE 1-50)`
  - (7, negative, and >6 / >50 all error the same way.)
- **Non-integer arguments are truncated** (floored): `BOXCHAR$(1.5)` = `┌`
  (index 1), `BOXCHAR$(2.9)` = `┐` (index 2).
- **String argument → `?TYPE MISMATCH`** (`BOXCHAR$("1")` fails).

## Usage

### Drawing a box (the primary use)
```basic
PRINT BOXCHAR$(1) + BOXCHAR$(5) + BOXCHAR$(5) + BOXCHAR$(2)
PRINT BOXCHAR$(6) + "  " + BOXCHAR$(6)
PRINT BOXCHAR$(3) + BOXCHAR$(5) + BOXCHAR$(5) + BOXCHAR$(4)
```
```
┌──┐
│  │
└──┘
```

### With COLOR
`PRINT BOXCHAR$(1) + BOXCHAR$(5) + BOXCHAR$(2) COLOR GREEN` works — the
characters take the color attribute like any other text.

### Inside DEF FN
```basic
DEF FNH$(N) = BOXCHAR$(5)     ' horizontal line
DEF FNV$(N) = BOXCHAR$(6)     ' vertical line
PRINT FNH$(0) + FNH$(0) + FNH$(0)   ' ───
```

### Codepage guard (from the manual, recommended)
```basic
DIM T{} : T{} = $TermInfo
IF T{"codepage"} <> "310" THEN PRINT "Need CP310 terminal" : END
```
`$TermInfo` `codepage` is `"310"` (graphics available) or `"037"`
(standard EBCDIC, no graphics). On CP037 terminals the box characters do
not render; fall back to ASCII `+ - |`.

## Rendering caveat (important)

The functions return the correct Unicode characters, but **x3270 is not a
CP310-capable terminal for these graphics.** Verified: a double-line box
drawn with `CP310$(7)+CP310$(11)+CP310$(11)+CP310$(8)` shows as `■  ■` on
screen even though the bytes are the correct `╔ ═ ═ ╗`.

Why: x3270 v4.1ga10's host code page list does NOT include CP310 (it has
cp037, cp273, ..., and `bracket` as the default). x3270 has *some* CP310
support via the "Graphic Escape" (X'08') mechanism, but that is for APL
symbols (underlined letters A-Z), not the box-drawing/graphics characters
that `CP310$` returns. So the double-line set (7-12) and double-line
junctions (18-20) have no mapping and fall back to `■`.

Single-line box (BOXCHAR$, CP310$ 1-6), blocks (21-28), arrows (29-32),
and shapes (33-36) all render correctly in x3270.

Note the BBS's `$TermInfo` `codepage` reports `"310"` on this box, which is
misleading — it means the BBS *believes* the terminal is CP310-capable (or
defaults to 310), not that the emulator can actually render the graphics.

So: use BOXCHAR$ (single-line) for portable boxes; reserve CP310$ 7-12 for
terminals that actually support them (a real CP310-capable emulator or
hardware 3270).
