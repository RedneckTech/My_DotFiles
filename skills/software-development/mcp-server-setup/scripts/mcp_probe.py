#!/usr/bin/env python3
"""Probe an MCP server over stdio: send initialize + tools/list, report result.

Usage:
    mcp_probe.py [--env KEY=VALUE ...] -- CMD [ARG ...]

Keeps stdin open and reads incrementally so slow-starting servers
(e.g. Go-compiled github-mcp-server) are not falsely reported as failed.
Exit 0 on successful initialize, 1 otherwise.
"""
import json, subprocess, sys, os, time, select


def parse_args(argv):
    env, cmd = {}, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--":
            cmd = argv[i + 1:]
            break
        if a == "--env":
            k, v = argv[i + 1].split("=", 1)
            env[k] = v
            i += 2
            continue
        cmd = argv[i:]
        break
    return env, cmd


def main():
    env, cmd = parse_args(sys.argv[1:])
    if not cmd:
        print(__doc__)
        sys.exit(2)
    full_env = dict(os.environ)
    full_env.update(env)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=full_env, text=True)
    init = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2024-11-05",
                                  "capabilities": {},
                                  "clientInfo": {"name": "probe",
                                                 "version": "1.0"}}}) + "\n"
    listing = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                          "params": {}}) + "\n"
    p.stdin.write(init + listing)
    p.stdin.flush()

    init_ok, tools = False, None
    deadline = time.time() + 15
    while time.time() < deadline and not (init_ok and tools is not None):
        r, _, _ = select.select([p.stdout], [], [], 0.5)
        if r:
            line = p.stdout.readline()
            if not line:
                if p.poll() is not None:
                    break
                continue
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if m.get("id") == 1 and "result" in m:
                init_ok = True
            elif m.get("id") == 2 and "result" in m:
                tools = len(m["result"].get("tools", []))
        elif p.poll() is not None:
            break

    p.stdin.close()
    try:
        p.wait(timeout=3)
    except subprocess.TimeoutExpired:
        p.kill()
    err = p.stderr.read()

    print(f"{'OK' if init_ok else 'FAILED'} init={init_ok} tools={tools}")
    if err.strip():
        print("stderr:", err.strip()[-500:])
    sys.exit(0 if init_ok else 1)


if __name__ == "__main__":
    main()
