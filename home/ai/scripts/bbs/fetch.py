#!/usr/bin/env python3
"""Pull BBS program/data files back into the local project (the mirror of
uploader.py).

Usage:
    python3 fetch.py                  # pull files into <repo>/bbs (no commit)
    python3 fetch.py --commit         # pull + one commit per program
    python3 fetch.py --dry-run        # list remote files, transfer nothing
    python3 fetch.py --dest DIR       # extract under DIR (default <repo>/bbs)

The BBS stores each user's files as plain files on the host:
    ~/3270BBS/basic/<user>/*.bas *.list *.idx *.dat
    ~/3270BBS/assembler/<user>/*.asm *.list
This script streams only those five extensions (everything else in the trees
is ignored) and writes them under <dest>, preserving the basic/<user>/ and
assembler/<user>/ layout.

After a pull it groups CHANGED files by program name (the path minus its
extension). With --commit it makes ONE git commit PER PROGRAM using the
approved-verb subject convention (Add for a new program, Update for a
changed one) — NOT a "bbs:" prefix and not one big commit. The 3270BBS
agent normally runs fetch.py WITHOUT --commit and hands the tree to the
`git` subagent to stage + commit; --commit is the standalone convenience.
Deletes on the server are NOT propagated (fetch only ever adds/updates) --
say the word and I'll add a --prune to remove files that vanished upstream.
"""

import argparse
import os
import shlex
import subprocess
import sys

REMOTE_ROOT = "~/3270BBS"
SSH_ALIAS = "3270BBS"
LANGS = ("basic", "assembler")
EXTENSIONS = (".bas", ".asm", ".list", ".idx", ".dat")


def remote_file_list():
    """Return the server-relative paths of every file matching the exts."""
    conds = " ".join("-name '*%s' -o" % e for e in EXTENSIONS).rstrip(" -o")
    find = "find %s -type f \\( %s \\)" % (" ".join(LANGS), conds)
    cmd = "ssh %s 'cd %s && %s'" % (SSH_ALIAS, REMOTE_ROOT, find)
    out = subprocess.check_output(cmd, shell=True, text=True)
    return sorted(line.strip() for line in out.splitlines() if line.strip())


def fetch(dest):
    """Stream the five file types from the server and extract under dest."""
    conds = " ".join("-name '*%s' -o" % e for e in EXTENSIONS).rstrip(" -o")
    find = "find %s -type f \\( %s \\) -print0" % (" ".join(LANGS), conds)
    remote = "cd %s && %s | tar --null -T - -cf -" % (REMOTE_ROOT, find)
    os.makedirs(dest, exist_ok=True)
    full = "ssh %s %s | tar -xf - -C %s" % (
        SSH_ALIAS, shlex.quote(remote), shlex.quote(dest))
    subprocess.run(full, shell=True, check=True)


def git_root(start):
    """Return the repo root containing start, or None if not in a repo."""
    try:
        out = subprocess.check_output(
            ["git", "-C", start, "rev-parse", "--show-toplevel"],
            text=True)
        return out.strip()
    except subprocess.CalledProcessError:
        return None


def commit_incremental(dest):
    """Stage the dest dir and commit one commit per program (approved verbs)."""
    root = git_root(dest)
    if root is None:
        print("not in a git repo -- cannot commit", file=sys.stderr)
        return 0

    rel_dest = os.path.relpath(dest, root)
    subprocess.run(["git", "-C", root, "add", "-A", "--", rel_dest],
                   check=True)

    # path -> staged status (A=added, M=modified, ...) under dest
    status = {}
    out = subprocess.check_output(
        ["git", "-C", root, "diff", "--cached", "--name-status", "--", rel_dest],
        text=True)
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            status[parts[1]] = parts[0]

    if not status:
        print("no changes")
        return 0

    # group by (language, program name).  Each file lives at
    # <dest>/<lang>/<user>/<name>.<ext>; group and label on the parts that
    # matter, and pick Add vs Update per the git subagent's approved verbs.
    groups = {}
    for path in status:
        rel = os.path.relpath(path, rel_dest)
        parts = rel.split(os.sep)
        lang = parts[0] if parts else ""
        stem = os.path.splitext(os.path.basename(rel))[0]
        groups.setdefault((lang, stem), []).append(path)

    commits = 0
    for (lang, stem), files in sorted(groups.items()):
        files = sorted(files)
        all_new = all(status[f] == "A" for f in files)
        verb = "Add" if all_new else "Update"
        msg = "%s %s/%s" % (verb, lang, stem)
        subprocess.run(
            ["git", "-C", root, "commit", "-m", msg, "--"] + files,
            check=True)
        print("committed", msg)
        commits += 1
    return commits


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dest", default=None,
                    help="extract destination (default: <current repo>/bbs)")
    ap.add_argument("--commit", action="store_true",
                    help="also commit: one commit per program, approved-verb subjects")
    ap.add_argument("--dry-run", action="store_true",
                    help="print remote files that would be pulled, then exit")
    args = ap.parse_args()

    if args.dest:
        dest = args.dest
    else:
        # Work with whatever repo you run this from: default destination is
        # a bbs/ mirror at the root of the current git repo (fall back to the
        # process cwd when not inside a repo).
        root = git_root(os.getcwd()) or os.getcwd()
        dest = os.path.join(root, "bbs")

    if args.dry_run:
        files = remote_file_list()
        if not files:
            print("no matching files on %s" % SSH_ALIAS)
            return
        for f in files:
            print(f)
        print("%d file(s) would be pulled" % len(files))
        return

    fetch(dest)
    pulled = len(remote_file_list())
    print("pulled %d file(s) into %s" % (pulled, dest))

    if args.commit:
        n = commit_incremental(dest)
        if n:
            print("%d program commit(s) created" % n)
    else:
        print("fetched only -- run with --commit, or hand the tree to the git subagent")


if __name__ == "__main__":
    main()