---
name: opencode-agent-authoring
description: "Use when writing/editing OpenCode agent .md definitions."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# OpenCode Agent Authoring

How to write and edit this user's OpenCode agent definition files (the
`.md` files that define custom agents — not delegating to the OpenCode CLI,
which is the separate `opencode` skill).

## Location

- Agents live in `~/.user_config/home/.config/opencode/agents/` — NOT the
  default `~/.config/opencode/agents/`. Do not assume the default path.
- opencode actually READS agents from `~/.config/opencode/agents/`, which is
  a directory of symlinks that stow creates into the repo path. A new agent
  `.md` committed to the repo is invisible to opencode until its symlink
  exists — re-run stow (or `ln -s ../../../.user_config/home/.config/opencode/agents/<name>.md ~/.config/opencode/agents/<name>.md`)
  and confirm with `opencode agent list` before assuming the agent is live.
- One `.md` per agent; filename = agent name (`ScriptDev.md`, `web-apps.md`).
- The directory mixes one-line stubs and dense full guides (`3270DEV.md`,
  `ispf-editor.md`). Read a sibling (one dense + one stub) before editing to
  learn the house conventions.

## Frontmatter format

```yaml
---
description: <one-line summary>
mode: primary            # or subagent
temperature: 0.2         # optional — only some agents set it
permission:              # always present
  bash: allow
  external_directory: ask
  edit: allow
  read: allow
  webfetch: allow
  websearch: allow
  task: allow
  skill: allow
  <tool>_*: allow        # e.g. filesystem-mcp_*, context7_*, jcodemunch-mcp_*
---
```

When editing an EXISTING agent, preserve its frontmatter verbatim — keep
`temperature`, `mode`, and the `permission` block exactly as found. Change
them only when the user explicitly asks.

## Target style: a dense full guide, not a stub

The user wants FULL detailed guides (when asked for scope, answered "full
detailed guide like 3270DEV"). Model on `3270DEV.md`, not the one-line
stubs. A finished agent has these sections, in this order:

1. Role statement (one line).
2. **Environment facts** — tools/languages with versions AND exact paths,
   verified by probing (never assumed).
3. Stack/approach policy — what's primary vs alternative, when to switch.
4. Coding rules — concrete do/don't.
5. Workflow — the exact lint/test/serve commands in the order run.
6. Worked patterns — short, copy-able snippets.
7. Pitfalls — each a generalizable rule + the mechanism why.
8. A terse "Rules" summary list at the end.

## Workflow for building an agent

1. Read the target file (if it exists) plus 1-2 siblings for conventions.
2. **Probe the environment first** — `command -v <tool>` and `--version` for
   every tool the agent will steer, and `python3 -c 'import <pkg>'` for
   libraries. Ground every "environment fact" in a real probe; do not state
   versions/paths from memory. This is what makes the guide trustworthy.
3. For genuinely ambiguous choices (framework/stack, shell dialect, lint/test
   tooling, deploy target), ask ONE `clarify` call with sensible defaults as
   the choices. Do not write a long guide on a guessed stack.
4. Write with `write_file` (whole-file overwrite), preserving frontmatter if
   editing an existing agent.
5. Report: what changed, which unanswered/terse choices you defaulted on
   (labeled), and offer to flip them.

## Subagents, MCP-backed agents, and repo scope

- `mode: subagent` marks a helper agent (reviewer, debugger, editor) that a
  `primary` agent spawns via the `task` tool. A primary agent must carry
  `task: allow` to spawn them, and its body should NAME which subagents to
  hand off to (not just permit the capability).
- Give review/debug subagents a real methodology, not vague advice: review →
  a structured pass/fail verdict (security / logic / regression vs
  suggestions, fail-closed); debug → a fixed phase order ending in "no fix
  without a root cause" plus a stop-condition (e.g. 3 failed fixes = question
  the architecture).
- `edit: ask` in a permission block means file writes surface a confirmation
  prompt — tell the agent to summarize mutating operations before firing them
  and never assume writes are silent.
- An agent backed by an MCP server that is `enabled: false` or unauth'd must
  carry a "stop and flag, never fabricate" rule so it does not invent API
  results when the tools error with auth/401.
- Do not trust memorized MCP tool names/schemas — package versions differ;
  instruct the agent to read each tool's live description before calling.
- NEVER hardcode a repository/owner into an agent meant to work on "whatever
  project". Derive `OWNER/REPO` from the working directory's
  `git remote get-url origin` (SSH or HTTPS form) each time, and stop and ask
  when there is no `origin`. For a helper script that only needs to TARGET
  the current project (not name an owner/repo), derive the repo ROOT with
  `git rev-parse --show-toplevel` of the cwd — it works in a freshly
  `git init`-ed repo with no remote, where `get-url origin` fails.

## User preferences

- Terse in clarify/feedback (e.g. "python", "unknown"). When an answer is
  blank or one word, choose a defensible default, label it explicitly, and
  offer to change it — do not re-ask repeatedly.
- Values grounding over generic advice: probe the real box rather than
  writing platform-neutral prose.
- Commit messages use an APPROVED plain-English verb list (Add, Fix, Update,
  Refactor, Clean up, Remove, Rename, Document, Test + `wip` savepoints) as
  the subject lead-in — NOT conventional `type(scope):`. Forbid process/meta
  prefixes like `code-review` or `backlog`. Encoding the verb list is not
  enough: the `git` subagent owns staging AND these messages, so author
  primary/build agents to HAND OFF committing to `git` (working tree + a
  one-line description of what changed) instead of running `git commit`
  themselves — and any helper script that auto-commits as a convenience must
  write the SAME approved verbs (never a self-invented prefix like `bbs:`),
  with a no-commit default so the agent prefers the subagent path. Encoded in
  the `git.md` and `github.md` agents (keep them in sync).

## Pitfalls

- Do not assume the default config path — this user's agents live under
  `.user_config/home/.config/opencode/agents/`, not `~/.config/opencode/`.
- Do not invent tool versions — shell/python/node versions differ per box;
  probe before writing environment facts. `/bin/sh` may be `dash`, not bash,
  which changes what "portable shell" means.
- Do not overwrite frontmatter when editing — preserve `temperature`,
  `permission`, and `mode` as-is.
- A broad "web apps"-style agent is underdetermined — clarify the stack
  before writing, or you produce a guide aimed at the wrong framework.
- An agent `.md` that exists in the repo but is missing from
  `opencode agent list` is a missing symlink, not a bad file — the file was
  committed but stow was never re-run. Create the symlink (or re-stow) and
  re-check the list before debugging the file content.
- Do not let an agent cite a manual/spec as its source of truth without
  verifying it. A bundled manual can be an OLDER version than the running
  system, and an agent told to "read the manual for exact syntax" will
  faithfully reproduce its errors. Once you have verified divergences,
  point the agent at the verified reference and add an explicit "trust the
  verified docs over the manual" rule plus a short corrections table —
  never leave the manual cited as authoritative.
- Repointing an agent's BODY at a new path is not a free edit — the
  `permission` block gates it. A body path outside the agent's allowed dirs
  surfaces an `ask` prompt at call time, and since frontmatter is preserved
  verbatim you cannot widen the allow-list as a side effect. Either leave
  the body on the permitted path, or flag the permission change the repoint
  requires and get the user's explicit OK before making it.
