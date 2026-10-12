# Time & Date Functions — Complete Reference (v3.0.0)

Everything below was verified by running it on the live interpreter.

## The functions

| Function | Returns | Example |
|----------|---------|---------|
| `DATE$()` | string `YYYY-MM-DD` (10 chars) | `2026-10-12` |
| `TIME$()` | string `HH:MM:SS` (8 chars) | `05:35:24` |
| `YEAR()` | numeric year | `2026` |
| `MONTH()` | numeric month 1-12 | `10` |
| `DAY()` | numeric day 1-31 | `12` |
| `HOUR()` | numeric hour 0-23 | `5` |
| `MINUTE()` | numeric minute 0-59 | `35` |
| `SECOND()` | numeric second 0-59 | `24` |
| `TIMER()` | seconds since midnight (float) | `20124.906895882` |
| `SLEEP(n)` | pause n seconds, returns 0 | — |

### Format details

- `DATE$()` and `TIME$()` are **zero-padded strings** (`05:35:24`, not
  `5:35:24`). `LEN(DATE$())` = 10, `LEN(TIME$())` = 8.
- The component functions (`HOUR()`, etc.) return **plain numbers**, NOT
  zero-padded strings. `HOUR()` = `5`, not `"05"`.
- `TIMER()` = seconds since midnight with sub-second precision
  (`20124.906895882`). At `05:35:24`, `TIMER()` = `20124.9…` (matches
  `HOUR()*3600 + MINUTE()*60 + SECOND()` plus a fractional part).

## Timezone

The functions return the **host system's local time**. On the dev VM the
host is configured `Etc/UTC`, so the BBS reports UTC. There is no
timezone function.

## SLEEP

```basic
X = SLEEP(1.5)      ' pause 1.5 seconds; returns 0
```

- **Valid range: 0.1 to 255 seconds.** `SLEEP(0)`, `SLEEP(0.05)`,
  `SLEEP(-1)`, and `SLEEP(256)` all raise
  `?SLEEP VALUE OUT OF RANGE (0.1-255)`.
- Fractional values work (verified `SLEEP(0.1)`, `SLEEP(0.5)`, `SLEEP(1)`
  all paused for the requested duration, within ~2ms).
- Returns `0`.
- Non-busy wait (doesn't burn CPU).
- **SLEEP gives execution-time credit** — see below.

## No day-of-week / day-of-year functions

There is no `DAYOFWEEK()`, `DAYOFYEAR()`, or similar. Undefined function
calls don't error — they evaluate to empty (like an undefined variable), so
`PRINT DAYOFWEEK()` just prints nothing. You must compute the day of week /
day of year yourself from the date components.

## Extracting and formatting components

`DATE$()` / `TIME$()` can be sliced with the string functions, and
converted with `VAL`:

```basic
D$ = DATE$() : T$ = TIME$()
LEFT$(D$, 4)      ' "2026"   year
MID$(D$, 6, 2)    ' "10"     month
RIGHT$(D$, 2)     ' "12"     day
LEFT$(T$, 2)      ' "05"     hour
MID$(T$, 4, 2)    ' "40"     minute
RIGHT$(T$, 2)     ' "28"     second
VAL(LEFT$(T$, 2)) ' 5        hour as number
```

**Zero-padding a number for output:** at runtime `STR$` prepends a space to
non-negative numbers (`STR$(5)` = `" 5"`), so naive padding fails. (Note:
for a *literal* argument the optimizer precomputes it without the space —
see STRING_REFERENCE.md. `TRIM$` handles both.)

```basic
RIGHT$("0" + STR$(H), 2)          ' -> " 5"  (wrong)
RIGHT$("0" + TRIM$(STR$(H)), 2)   ' -> "05"  (correct)
```

## Comparing times

Because `TIME$()` is zero-padded, plain string comparison is correct:

```basic
IF "05:00:00" < "06:00:00" THEN ...   ' works lexicographically
```

You can also reconstruct a padded `HH:MM:SS` and compare it against
`TIME$()` (verified equal).

## Arithmetic

Date/time components are ordinary numbers, so you can do arithmetic, but
there is **no built-in date arithmetic** (no "add N days"):

```basic
YEAR() + 1     ' 2027
DAY() + 1      ' 13   (no month rollover handling)
```

Rolling dates forward means handling month lengths and leap years yourself.

## Execution-time limit and SLEEP credit

- A program that runs too long is halted with
  `?EXECUTION TIME LIMIT REACHED` (documented limit: 15s wall clock /
  55M iterations).
- **`SLEEP` grants credit that extends the limit.** Verified: a 3M-iteration
  loop (~16s of CPU, over the 15s limit) completed when it called
  `SLEEP(0.2)` every 250k iterations, but a 4M-iteration loop (~21.6s) still
  hit the limit. So the credit extends the limit by roughly **15%**
  (the manual's "Sleep credit: 15%"). Note the credit only helps when SLEEP
  is called frequently enough to matter — a handful of sleeps in a huge loop
  won't save it.

## Quick reference

```basic
DATE$()          ' "2026-10-12"
TIME$()          ' "05:35:24"
YEAR() MONTH() DAY() HOUR() MINUTE() SECOND()   ' numbers
TIMER()          ' 20124.906895882
SLEEP(1.5)       ' pause 1.5s, returns 0, range 0.1-255
```
