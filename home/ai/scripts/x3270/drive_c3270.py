#!/usr/bin/env python3
"""Drive a persistent c3270 -scriptport session over TCP.

c3270 has no -script (stdin) mode; instead it listens on a TCP port given by
-scriptport and speaks the same s3270 action protocol x3270 uses. This is a
drop-in for drive.py: same arguments, same printed screen.

Usage:
    drive_c3270.py 'String("admin")' Tab 'String("admin")' Enter
    drive_c3270.py --raw                 # just dump the screen
    drive_c3270.py --wait 6 --port 12352 ...
"""
import socket
import sys
import time

HOST = "127.0.0.1"
PORT = 12352


def read_until(sock, want, timeout=15.0):
    """Read until `want` terminators (ok/error) have arrived."""
    buf = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf += chunk
        except socket.timeout:
            continue
        text = buf.decode("utf-8", "replace")
        n = text.count("\nok\n") + text.count("\nerror\n")
        if text.startswith("ok\n") or text.startswith("error\n"):
            n += 1
        if n >= want:
            break
    return buf.decode("utf-8", "replace")


def send_actions(port, actions):
    s = socket.create_connection((HOST, port), timeout=5)
    s.settimeout(0.5)
    try:
        for a in actions:
            s.sendall((a + "\n").encode())
        return read_until(s, len(actions))
    finally:
        s.close()


def send_ascii(port):
    s = socket.create_connection((HOST, port), timeout=5)
    s.settimeout(0.5)
    try:
        s.sendall(b"Ascii\n")
        return read_until(s, 1)
    finally:
        s.close()


def screen_from(text):
    data = []
    for line in text.splitlines():
        if line.startswith("data:"):
            data.append(line[5:].rstrip())
        elif data and line.strip() == "ok":
            break
    return "\n".join(data)


def main():
    args = sys.argv[1:]
    wait, port = 3.0, PORT
    while args and args[0] in ("--wait", "--port"):
        if args[0] == "--wait":
            wait = float(args[1])
        else:
            port = int(args[1])
        args = args[2:]
    if args and args[0] != "--raw":
        send_actions(port, args)
        time.sleep(wait)
    print(screen_from(send_ascii(port)))


if __name__ == "__main__":
    main()
