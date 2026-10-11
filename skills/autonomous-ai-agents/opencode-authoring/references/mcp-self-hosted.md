# Self-hosted MCP server replacements

Replacing MCP servers with free, self-hosted ones. Config lives in
`~/.user_config/home/.config/opencode/opencode.jsonc` under `mcp`.

## Dead reference servers

Anthropic's `modelcontextprotocol/servers` repo archived 13 reference servers
in late 2025 into `servers-archived`: GitHub, GitLab, Google Drive,
PostgreSQL, Puppeteer, Brave Search, Slack, Redis, Sentry, SQLite,
AWS KB Retrieval, EverArt, Google Maps. Their `@modelcontextprotocol/
server-*` npm packages are "no longer supported". Only 7 remain active
(filesystem, git, memory, fetch, everything, sequential-thinking, time).

## Replacements

| Need | Dead / hosted thing | Free self-hosted replacement | How |
|---|---|---|---|
| GitHub API | `@modelcontextprotocol/server-github` (archived) | `github/github-mcp-server` | Prebuilt binary from the releases page -> `~/.local/bin/github-mcp-server`, run `stdio` with `GITHUB_PERSONAL_ACCESS_TOKEN` (fine-grained PAT, repo read+write). Flags: `--read-only`, `--toolsets`, `--lockdown-mode`, `--gh-host`. |
| Filesystem | `@modelcontextprotocol/server-filesystem` (still active) | keep, or `mark3labs/mcp-filesystem-server` (Go/MIT; symlink protection, MIME detection, path validation) | Prebuilt binary from releases (no Go/Docker) -> `~/.local/bin/mcp-filesystem-server dir1 dir2 ...` (allowlisted dirs are positional args). Alt: `go install ...@latest`, the `ghcr.io/...` image, or `portertech/filesystem-mcp-server`. |
| Code retrieval | jcodemunch (freemium, "free for personal use") | already self-hosted; wire it correctly | `uvx jcodemunch-mcp` (NOT npx — it's a pip package). |
| Up-to-date library docs | context7 (`mcp.context7.com/mcp`, hosted SaaS) | NONE true self-hosted | The MIT MCP client still calls the hosted index/parser; that backend is NOT open. Partial substitute: self-hosted DevDocs + a community MCP wrapper. |

## Binary install procedure (GitHub + mark3labs both ship tarballs)

Neither server needs Docker/Go/build tooling — download the release binary
and drop it in `~/.local/bin`:

```sh
uname -m                              # x86_64 -> _linux_amd64 / _Linux_x86_64
curl -s https://api.github.com/repos/OWNER/REPO/releases/latest \
  | python3 -c 'import sys,json; [print(a["name"]) for a in json.load(sys.stdin)["assets"]]'
curl -sL -o /tmp/srv.tar.gz "https://github.com/OWNER/REPO/releases/download/TAG/ASSET"
tar xzf /tmp/srv.tar.gz               # yields the raw binary (+ LICENSE/README)
install -m 755 <binary> ~/.local/bin/<binary>
```

Asset naming differs per repo (`github-mcp-server_Linux_x86_64.tar.gz` vs
`mcp-filesystem-server_linux_amd64.tar.gz`) — always read the `assets` list
from the API rather than guessing the filename.

## OpenCode MCP config notes

- The local-server env-var key is `environment` (an object); OpenCode's
  `env` is a different concept. Interpolate secrets as `"{env:VAR_NAME}"`.
- OpenCode warns the GitHub MCP adds many tokens — scope `--toolsets`
  (default: context, copilot, issues, pull_requests, repos, users) to exactly
  what an agent uses, or the context limit gets eaten.
- A self-hosted PAT-based server needs the token present; without it the
  server starts but every tool call 401s. If the user refuses a PAT, the
  only no-token path is GitHub's hosted remote MCP over OAuth — which is
  hosted, not self-hosted.
- OpenCode does NOT native-load `.env` files — `{env:VAR}` resolves only
  from the launch process env. Wire secrets with a private `chmod 600`
  `.env` in the opencode config dir, sourced from `~/.bashrc`, so the token
  is present when opencode starts. Never accept or echo the secret value;
  confirm presence with `${#VAR}` length and a prefix mask.
- Verify a PAT actually works without exposing it:
  `curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN"
  https://api.github.com/user` (200 = valid; the JSON body's `login` names
  the account). A fine-grained PAT is ~93 chars with the `github_pat_`
  prefix (classic is `ghp_`).
- `github-mcp-server` (and other Go MCP servers) write their JSON-RPC
  responses to STDERR, not stdout — when smoke-testing over a pipe, redirect
  `2>&1` (not `2>/dev/null`) or the response vanishes.
- `mark3labs/mcp-filesystem-server` validates every allowlisted dir at
  STARTUP and refuses to launch if one is missing — an unmounted external
  drive in the allowlist fails the whole server, not just that directory.
