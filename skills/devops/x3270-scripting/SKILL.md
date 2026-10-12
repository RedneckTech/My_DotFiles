---
name: x3270-scripting
description: "Use when driving a 3270 terminal via x3270 -script, or writing/testing TIMESHARING BASIC on the user's 3270BBS."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [3270, x3270, terminal, mainframe, automation, tn3270]
    related_skills: [opencode]
---

# x3270 Scripting

Drive a 3270 terminal emulator programmatically with `x3270 -script` (the
peer-script facility: actions on stdin, responses on stdout). Use this for
any 3270 host automation — the user's 3270 BBS dev environment is one
application; the lock/reset semantics below apply to every 3270 host.

## When to Use

- Automating a 3270 host (BBS, mainframe, ISPF) from a script or agent.
- Diagnosing a locked/frozen 3270 session and recovering it without dropping
  the connection.
- Writing, testing, or debugging TIMESHARING BASIC programs on the user's
  3270BBS host — `references/3270bbs.md` carries the verified language
  gotchas (DEF FN, ISAM, CHAIN, file I/O, math, strings, BOXCHAR$/CP310$,
  panels) and the
  fast test loop (write the `.bas` to the host over SSH, `LOAD`+`RUN` via
  the fifo, capture output to a `.dat`). The bundled manual is v2.9.2 and
  has errors; the repo `basic-learning/*.md` docs are the verified source.

## Core actions

- `String("text")` — type into the current field (escape `"` as `\"`)
- `Enter`, `Tab`, `PF(n)` (1..24), `PA(n)` (1..4) — AID keys
- `Clear` — send AID Clear to the HOST (clears screen, asks host to reset)
- `Reset` — send the terminal RESET key (LOCAL only, see below)
- `Wait(N,Output)` — wait up to N seconds for host output
- `Ascii` — dump the screen as text (lines prefixed `data:`)
- `Quit` — end the session

`Wait(N,Output)` argument order is N-first. `Wait(Output,N)` errors.

## Lock and reset semantics (the part that costs time)

A 3270 keyboard locks when an AID key is sent (Enter/PF/Clear/PA) or on an
operator error (typing into a protected field, field overflow). Only the
RESET key — or a host command carrying the reset flag — clears a lock.

- `Reset` is the RESET key and is purely LOCAL: it unlocks the keyboard and
  sends nothing to the host, so it never ends the session or loses the
  connection. `Clear` is different — it sends AID Clear to the host. Do not
  reach for `Clear` when you only need to unlock the keyboard.
- `Reset` is TWO-STAGE only when typeahead is actually buffered: the first
  invocation flushes the buffered keystrokes, the second does the full
  reset. In script mode a `String()` into a protected field is REJECTED
  (returns `error`), not buffered, so a single `Reset` usually unlocks the
  keyboard. Send a second `Reset` only if the status line still shows `L`
  after the first — the second is a harmless no-op when already unlocked.
- "Keyboard locked / Operator error" is a DIFFERENT lock from "waiting for
  host". x3270 clears an operator-error lock with any cursor-movement key
  (`Tab`, `Home`, `Up`/`Down`/`Left`/`Right`, `Newline`) — try `Tab` first;
  it is simpler and safer than `Reset`.
- Read the lock state instead of guessing: the status line x3270 prints
  before each `ok`/`error` has 12 blank-separated fields; the FIRST is the
  keyboard state — `U` = unlocked, `L` = locked. (`E` = operator error is
  documented in the man page, but typing into a protected field shows `L`,
  not `E`, in practice — treat `L` + the THIRD field as the real signal.)
  The THIRD field is the current field's protection — `P` = protected, `U` =
  unprotected. If it reads `P`, the next `String()` will fail and lock the
  keyboard; `Tab` to an unprotected field first.

## Pitfalls

- Do not queue actions during a blank-screen transition (menu change, save,
  paging). They execute later on whatever screen appears and corrupt state
  (e.g. a queued `logoff` at READY becomes `?SYNTAX ERROR`). Poll `Ascii`
  until the expected screen paints before sending the next action.
- Do not `Quit` the emulator mid-save or mid-transition — an interrupted
  save can deadlock the session SERVER-side, and reconnects resume the same
  wedged session. `Reset`/`Clear`/`PA(1)` cannot fix that; only a host-side
  restart clears it.
- `MoveCursor` is 0-origin, `MoveCursor1` is 1-origin. Use `MoveCursor1`
  with coordinates matching what `Ascii` shows.
- After any AID (`Enter`/`PF`/`Clear`), the host repaints and may reset the
  cursor — `Wait` before the next `MoveCursor1`/`String`. Rapid-firing
  `MoveCursor1` + `String` + `Enter` back-to-back with no `Wait` between them
  (e.g. several editor line commands in a row) can lose input and, worse,
  wedge the session SERVER-side: blank screen even after 90s of polling, and
  the wedge survives reconnect until the host is restarted. Drive one step
  per `Wait`-sync and read the screen between steps.
- The user's BBS VM is on DHCP, so its IP drifts across reboots. "No route
  to host" / connection refused on the BBS usually means the IP changed,
  not that the VM is down. Find the current IP with
  `virsh net-dhcp-leases default` (match the MAC), then update
  `~/.ssh/config` (alias `3270BBS`) and any doc references to the old IP.
  The BBS binary `tsu` also does not auto-start: if port 3270 is closed
  after the VM is up, start it with
  `ssh 3270BBS 'cd ~/3270BBS && nohup ./tsu > tsu.log 2>&1 &'`.
- Launch a persistent session so the agent's bash-tool call returns cleanly.
  Run x3270 DIRECTLY (never wrap in `sh -c '...'` — the wrapper leaves an
  intermediate shell alive holding the tool's stdout pipe) and redirect
  stdout/stderr BEFORE the fifo, so the fifo open is last:
  `setsid x3270 -script -model 3279-2 <host> > /tmp/x3270.out 2>&1 < /tmp/x3270.fifo & disown`,
  plus a keeper `setsid sh -c 'sleep 86400 > /tmp/x3270.fifo' </dev/null >/dev/null 2>&1 & disown`.
  Opening the fifo first blocks the process (a read-open waits for a writer)
  while its stdout is still the tool's pipe, so the call never sees
  end-of-file and spins until killed — both mistakes together are a
  hard hang, not a slow step.
  In Hermes the terminal tool REJECTS `setsid`/`disown`/`nohup` wrappers —
  launch the keeper and x3270 with `background=true` instead, and set
  `persist_on_release=true` on BOTH or they die at the next turn boundary
  (the session silently vanishes and the next fifo write blocks forever).
  Re-check `pgrep -x x3270` at the start of each turn and relaunch if dead.
- Only ONE x3270 session at a time. `pgrep -x x3270` first and reuse a live
  session; a second x3270 against the same 3270 user logs the first one out
  and two processes fight over the fifo. (`-x` exact name, never `pgrep -f`,
  which self-matches your own shell.) A fifo write BLOCKS when the reader
  (x3270) is gone — if the session died, `pgrep -x x3270` is empty and the
  next write hangs forever. Re-check `pgrep -x x3270` before driving and
  relaunch the session + keeper if it is dead.
- When reading `x3270 -script` responses in a driver loop, count TWO output
  lines per action: every action prints a status line then a `ok`/`error`
  line. After sending N actions plus a trailing `Wait(N,Output)`, wait for
  `2*(N+1)` lines before deciding the step finished — waiting for `N+1`
  returns after only the first couple of actions, while the `Enter`/scroll
  is still in flight, so the driver races (or silences the race with a big
  blind sleep). The `Wait` result line is always the LAST of the batch.
- `Wait(N,Output)` unblocks on the FIRST host write, and the editor's heavy
  transitions (bulk line-insert `I n`, `PF(8)` scroll, editor open) repaint
  in TWO writes — a blank, then the content — so the `Wait` returns on the
  blank. Keep a settle after the `Wait` for those transitions, and expect the
  bulk-insert repaint to be host-side slow (tens of seconds for `I50`). A
  plain per-line type is single-write and needs almost no settle.
- The `\"` inside `String()` is consumed by x3270, not by your shell. Match
  the backslash escaping to the TRANSPORT: `printf` also interprets
  backslashes, so a `printf` format string needs `\\\"` to deliver `\"` to
  x3270; a direct write (Python `os.write`, a single-quoted shell arg, a
  heredoc) passes bytes verbatim and needs only `\"`. Double-escaping through
  a non-interpreting transport types literal backslashes into the field and
  the host rejects the line with a `Syntax error: ")" or "," expected`
  message.

## Reference

The x3270 wiki is authoritative for action semantics:
https://x3270.miraheze.org/wiki/Reset()_action and
https://x3270.miraheze.org/wiki/3270_data_stream_protocol ("Keyboard lock
and reset" section).

The user's 3270BBS dev environment (login, menus, ISPF editor coordinates,
recovery, and TIMESHARING BASIC language gotchas incl. DEF FN) is in
`references/3270bbs.md`.
