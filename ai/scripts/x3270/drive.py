#!/usr/bin/env python3
"""Drive the persistent x3270 -script session via its input fifo.

The session reads actions from /tmp/x3270.fifo and writes responses to
/tmp/x3270.out. This helper sends a batch of actions, waits for the host to
settle, and prints the current screen (the `data:` lines from the last Ascii).

Usage:
    drive.py 'String("10 PRINT \"hi\"")' Enter 'String("RUN")' Enter
    drive.py --raw 'Ascii'          # just dump the screen, no actions
    drive.py --wait 6 ...           # settle for 6s instead of 3s
"""
import sys
import time

FIFO = "/tmp/x3270.fifo"
OUT = "/tmp/x3270.out"


def send(actions):
    with open(FIFO, "w") as f:
        for a in actions:
            f.write(a + "\n")
            f.flush()


def read_screen():
    """Return the current screen text from the last Ascii dump in OUT."""
    with open(OUT, "r") as f:
        text = f.read()
    lines = text.splitlines()
    data = []
    for line in reversed(lines):
        if line.startswith("data:"):
            data.append(line[5:].rstrip())
        elif data:
            break
    data.reverse()
    return "\n".join(data)


def main():
    args = sys.argv[1:]
    wait = 3.0
    if args and args[0] == "--wait":
        wait = float(args[1])
        args = args[2:]
    if not args:
        print(read_screen())
        return
    if args[0] == "--raw":
        send(["Ascii"])
        time.sleep(1.5)
        print(read_screen())
        return
    actions = list(args)
    actions.append("Ascii")
    send(actions)
    time.sleep(wait)
    print(read_screen())


if __name__ == "__main__":
    main()
