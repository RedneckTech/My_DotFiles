#!/usr/bin/env python3
"""
Upload a local BASIC source file to the 3270BBS via the ISPF editor,
driving a persistent `x3270 -script` session through a fifo.

Usage:
    python3 uploader.py FILE.bas [--verify] [--timeout N]

The session must already be logged in and sitting at the BASIC READY
prompt (this script does not log in).

Editor interaction model (rows/cols are 1-origin screen coords):
  - `edit "name"` from READY opens the editor with ONE empty data line
    at row 4 and the cursor in the Command field (row 2).
  - The Scroll field (row 2, cols 70+) is set to HALF so that PF(8)
    advances roughly half a page -- deliberately less than a page, so the
    last typed line stays on screen after the jump.
  - Line 1 is typed at (4, 9).
  - Appending lines: insert BATCH (default 50) blank lines at once by
    typing `I50` over the prefix at (cur_row, 3), then type the pending
    lines into those blanks one per row. Scroll down with PF(8) whenever
    the cursor reaches the last data row (23).
  - The scroll amount is NOT assumed: after every scroll the last typed
    line is located on screen by matching the tail of the typed lines
    (`locate_tail`), which also handles blank last lines by anchoring on
    the nearest non-blank line above. Screen reads poll the host because
    repaints can lag by seconds. Track `blank_below` so the next `I50`
    fires only after the current batch is used up.
  - PF(12) saves and returns to READY.
"""
import os
import sys
import time

FIFO = "/tmp/x3270.fifo"
OUT = "/tmp/x3270.out"

MAX_DATA_ROW = 23          # last data row in the editor (rows 4-23)
DATA_COL = 9               # text starts here
PREFIX_COL = 3             # where the '' '''' prefix command goes
SETTLE = 0.2               # settle after each step; step() waits for host output
VERIFY_EVERY = 25          # Ascii-verify the screen every N lines
BATCH = 50                 # blank lines to insert at once (I50)


def x3270_alive():
    import subprocess
    r = subprocess.run(["pgrep", "-f", "x3270 -script"],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def send(action):
    """Write one action line into the fifo (non-blocking)."""
    if not x3270_alive():
        raise RuntimeError("x3270 session is not running")
    fd = os.open(FIFO, os.O_WRONLY | os.O_NONBLOCK)
    try:
        os.write(fd, action.encode() + b"\n")
    finally:
        os.close(fd)


def out_size():
    try:
        return os.path.getsize(OUT)
    except OSError:
        return 0


def read_out_from(offset):
    with open(OUT, "r", errors="replace") as f:
        f.seek(offset)
        return f.read()


def step(actions, timeout=25.0, verbose=False):
    """
    Send a batch of actions followed by a Wait(N,Output) and block until
    EVERY action's result — including the Wait — has arrived. Each action
    prints a status line followed by its result line ('ok'/'error'), so a
    batch of A actions plus the Wait yields 2*(A+1) output lines; the Wait
    result is the LAST one (the host output has arrived by then). Returns
    (ok, new_output_text).
    """
    prev = out_size()
    n = 2 * (len(actions) + 1)   # one status + one result line per action
    for a in actions:
        send(a)
    send("Wait(%d,Output)" % int(timeout))
    deadline = time.time() + timeout + 5
    while time.time() < deadline:
        time.sleep(0.15)
        new = read_out_from(prev)
        lines = new.rstrip("\n").splitlines()
        if len(lines) >= n:
            last = lines[-1]
            # treat ANY mid-batch x3270 error as a failure
            if last != "ok" or "error" in lines:
                return False, new
            return True, new
    return False, read_out_from(prev)


def xstring(s):
    """Escape a line for use inside String(\"...\")."""
    if "\n" in s or "\r" in s:
        raise ValueError("line contains newline")
    out = []
    for ch in s:
        if ch == '"':
            out.append('\\"')
        elif ch == '\\':
            out.append('\\\\')
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def norm(s):
    """Collapse whitespace runs so screen text and source text can be
    compared independent of the editor's column padding."""
    return " ".join(s.split())


def screen_rows():
    """Return the most recent complete 24-row Ascii dump (80-col strings),
    or None if no full dump has arrived yet (host still painting)."""
    scr = read_out_from(0)
    dlines = [l[6:] for l in scr.splitlines() if l.startswith("data:")]
    if len(dlines) < 24:
        return None
    return dlines[-24:]


def dump_screen():
    send("Ascii")
    time.sleep(0.5)


def find_row(needle, tries=10, pause=1.0):
    """Return the 1-origin screen row containing the LAST occurrence of
    needle, or None if not visible.  Polls the screen because host repaints
    can lag; blank needles cannot be located by text and return None."""
    want = norm(needle)
    if not want:
        return None
    for _ in range(tries):
        dump_screen()
        d = screen_rows()
        if d is not None:
            row = None
            for i, l in enumerate(d):
                if want in norm(l):
                    row = i + 1
            if row is not None:
                return row
        time.sleep(pause)
    return None


def verify_screen(expect_text):
    """Check that the expected text is visible, polling for slow paints.
    A blank line counts as verified (there is nothing to match)."""
    if not expect_text.strip():
        return True
    return find_row(expect_text, tries=8, pause=1.0) is not None


def locate_tail(typed_lines, tries=10, pause=1.0):
    """Return the 1-origin screen row of the LAST typed line, or None.

    Matches the tail of `typed_lines` against the screen bottom-up.  The
    last typed line may itself be blank, so it is anchored by the nearest
    non-blank line above it, using the known distance between them.  Up to
    three more known lines above the candidate must also line up on screen,
    so repeated-text false positives are unlikely."""
    n = len(typed_lines)
    if n == 0:
        return None
    lo = max(0, n - 12)
    for _ in range(tries):
        dump_screen()
        d = screen_rows()
        if d is not None:
            rows = [norm(l) for l in d]
            for k in range(n - 1, lo - 1, -1):
                txt = norm(typed_lines[k])
                if not txt:
                    continue
                cand = None
                for i, r in enumerate(rows):
                    if txt in r:
                        cand = i + 1
                if cand is None:
                    continue
                row_last = cand + (n - 1 - k)
                if not (4 <= row_last <= 24):
                    continue
                ok = True
                for j in range(max(lo, n - 4), n - 1):
                    rr = row_last - (n - 1 - j)
                    if not (1 <= rr <= 24):
                        ok = False
                        break
                    exp = norm(typed_lines[j])
                    if exp and exp not in rows[rr - 1]:
                        ok = False
                        break
                if ok:
                    return row_last
        time.sleep(pause)
    return None


def set_scroll(value="HALF"):
    """Set the editor's Scroll field (row 2, cols 70-72) and verify it took.
    HALF keeps PF(8) jumps small enough that the last typed line stays on
    screen, unlike a full PAGE jump."""
    ok, out = step([
        "MoveCursor1(2,70)",
        'String("%s")' % value,
        "Enter",
    ], timeout=40)
    if not ok:
        print("FAILED setting Scroll field:\n" + out, flush=True)
        sys.exit(1)
    time.sleep(SETTLE)
    for _ in range(5):
        dump_screen()
        d = screen_rows()
        if d is not None and value in norm(d[1]):
            return
        time.sleep(1.0)
    print("could not verify Scroll field = %s" % value, flush=True)
    sys.exit(1)


def wait_for_ready(timeout=90.0):
    """Poll the screen until the editor has closed and BASIC is back at its
    command prompt.

    The editor's F12-save transition (and the M;B menu jump) paint a blank
    screen first and can take up to 60s, so a single Wait() returns on the
    blank and the next command would be typed into the still-open editor.
    Poll Ascii until the save confirmation ('SAVED') or the READY banner
    appears instead.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        dump_screen()
        d = screen_rows()
        if d is not None:
            for line in d:
                if "SAVED" in line or "READY" in line:
                    return True
        time.sleep(1.0)
    return False


def main():
    if len(sys.argv) < 2:
        print("usage: uploader.py FILE.bas [--verify] [--timeout N]")
        sys.exit(2)
    path = sys.argv[1]
    verify = "--verify" in sys.argv[2:]
    timeout = 25.0
    for i, a in enumerate(sys.argv):
        if a == "--timeout" and i + 1 < len(sys.argv):
            timeout = float(sys.argv[i + 1])

    name = os.path.basename(path)
    if name.lower().endswith(".bas"):
        name = name[:-4]
    # BBS filenames cannot contain underscores
    if "_" in name:
        raise SystemExit("BBS filenames cannot contain '_': " + name)

    with open(path, "r", errors="replace") as f:
        raw = f.read()
    lines = [l.rstrip() for l in raw.splitlines()]
    # drop leading/trailing empty lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    for l in lines:
        if len(l) > 71:
            raise SystemExit("line longer than 71 chars: %r" % l)
    for l in lines:
        for ch in l:
            if ord(ch) > 126:
                raise SystemExit("non-ASCII char in line: %r" % l)

    print("uploading %s: %d lines" % (name, len(lines)), flush=True)

    # Open the editor
    ok, out = step(['String("edit \\"%s\\"")' % name, "Enter"],
                   timeout=timeout)
    if not ok:
        print("FAILED opening editor:\n" + out, flush=True)
        sys.exit(1)
    time.sleep(SETTLE)
    set_scroll("HALF")

    cur_row = 4          # screen row of the last-typed line
    blank_below = 0      # blank lines available below the last-typed line
    typed_lines = []     # every line typed so far, in order (re-locate anchor)
    t0 = time.time()

    def ensure_visible(lbl, pending):
        """Scroll down (HALF page per PF(8)) until the last-typed line is
        visible with at least one row below it, then update cur_row.  The
        scroll amount is not predicted: the line is located on screen after
        every scroll (locate_tail handles blank last lines too)."""
        nonlocal cur_row
        if cur_row < MAX_DATA_ROW:
            return
        for _attempt in range(8):
            ok, out = step(["PF(8)"], timeout=timeout)
            if not ok:
                print("FAILED PF(8) at line %d (%r):\n%s"
                      % (lbl, pending, out), flush=True)
                sys.exit(1)
            time.sleep(SETTLE)
            r = locate_tail(typed_lines)
            if r is None:
                # Possibly overshot and left the window; one scroll back
                # up and retry, anything else is a hard failure.
                ok, out = step(["PF(7)"], timeout=timeout)
                if not ok:
                    print("FAILED PF(7) at line %d (%r):\n%s"
                          % (lbl, pending, out), flush=True)
                    sys.exit(1)
                time.sleep(SETTLE)
                r = locate_tail(typed_lines)
            if r is None:
                print("FAILED to locate last typed line after scroll "
                      "(line %d, %r)" % (lbl, pending), flush=True)
                sys.exit(1)
            if r <= MAX_DATA_ROW - 1:
                cur_row = r
                print("  scroll: last line now at row %d" % r, flush=True)
                return
            # line sits on the bottom row -- no room below -- scroll again
        print("FAILED to reach a usable position after 8 scrolls "
              "(line %d, %r)" % (lbl, pending), flush=True)
        sys.exit(1)

    for idx, line in enumerate(lines):
        if idx == 0:
            ok, out = step([
                "MoveCursor1(%d,%d)" % (cur_row, DATA_COL),
                "String(%s)" % xstring(line),
                "Enter",
            ], timeout=timeout)
            time.sleep(SETTLE)
            if not ok:
                print("FAILED at line %d (%r):\n%s" % (idx + 1, line, out),
                      flush=True)
                sys.exit(1)
        else:
            if blank_below == 0:
                ensure_visible(idx + 1, line)
                ok, out = step([
                    "MoveCursor1(%d,%d)" % (cur_row, PREFIX_COL),
                    'String("I%d")' % BATCH,
                    "Enter",
                ], timeout=timeout)
                time.sleep(SETTLE)
                if not ok:
                    print("FAILED batch-insert at line %d (%r):\n%s"
                          % (idx + 1, line, out), flush=True)
                    sys.exit(1)
                blank_below = BATCH
            ensure_visible(idx + 1, line)
            new_row = cur_row + 1
            ok, out = step([
                "MoveCursor1(%d,%d)" % (new_row, DATA_COL),
                "String(%s)" % xstring(line),
                "Enter",
            ], timeout=timeout)
            time.sleep(SETTLE)
            if not ok:
                print("FAILED at line %d (%r):\n%s" % (idx + 1, line, out),
                      flush=True)
                sys.exit(1)
            cur_row = new_row
            blank_below -= 1

        typed_lines.append(line)

        if (idx + 1) % VERIFY_EVERY == 0 or idx == len(lines) - 1:
            if not verify_screen(line):
                print("VERIFY FAILED at line %d: %r" % (idx + 1, line),
                      flush=True)
                sys.exit(1)
        if (idx + 1) % 100 == 0:
            el = time.time() - t0
            print("  %d/%d lines (%.1fs, %.2fs/line)"
                  % (idx + 1, len(lines), el, el / (idx + 1)), flush=True)

    # Save and exit editor. The F12-save transition paints blank for up to
    # 60s, so wait for READY to actually appear before claiming success or
    # running the verify step (otherwise the next command lands in the
    # still-open editor as a data line).
    ok, out = step(["PF(12)"], timeout=timeout)
    if not ok:
        print("FAILED saving:\n" + out, flush=True)
        sys.exit(1)
    if not wait_for_ready():
        print("FAILED: editor did not return to READY after save", flush=True)
        sys.exit(1)
    time.sleep(SETTLE)
    print("saved %s.bas" % name, flush=True)

    if verify:
        ok, out = step(['String("load \\"%s\\"")' % name, "Enter"],
                       timeout=timeout)
        if not ok:
            print("FAILED loading for check:\n" + out, flush=True)
            sys.exit(1)
        time.sleep(SETTLE)
        ok, out = step(['String("check")', "Enter"], timeout=120)
        if not ok:
            print("CHECK did not complete:\n" + out, flush=True)
            sys.exit(1)
        time.sleep(SETTLE)
        # grab the screen to read the check result
        send("Ascii")
        time.sleep(2.0)
        screen = read_out_from(0)
        tail = [l for l in screen.splitlines() if l.startswith("data:")]
        print("CHECK result screen:")
        for l in tail[-24:]:
            print(l)
        if "NO ERRORS" not in screen:
            sys.exit(1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
