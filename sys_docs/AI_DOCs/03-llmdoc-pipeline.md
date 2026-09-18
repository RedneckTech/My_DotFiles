# LLMDoc — Self-Hosted Documentation Indexing Pipeline

The most involved piece of the setup: a local pipeline that turns documentation
websites into a searchable index the OpenCode `llmdoc` MCP server can query with
BM25.

> **STATUS (2026-09-13): DISABLED.** The `llmdoc` MCP server was repeatedly
> ballooning to ~23 GB RSS during indexing and triggering kernel OOM-kills that
> locked up the whole desktop (three events in one day — 23.8 GB, 22.9 GB,
> 24.0 GB). Root cause was compounded by the machine having zero active swap.
> The OpenCode MCP entry is now `enabled: false`, and `llmdoc-serve.service` is
> stopped + disabled. Re-enable with:
> `systemctl --user enable --now llmdoc-serve.service` and flip `enabled`
> back to `true` for the `llmdoc` MCP block in `opencode.jsonc`.

## Pipeline overview

```
sitemap/crawl        static file server          MCP server          DuckDB index
gen-llms-txt.py  ->  llmdoc-serve.service  ->    llmdoc         ->   index.db
(one .llms.txt       (127.0.0.1:8099)            (uv tool)            (BM25 search)
 per docs site)      serves the .llms.txt        ingests + chunks
```

1. **Generate** — `~/.local/bin/gen-llms-txt.py <name> <url>` reads a site's
   `sitemap.xml` (falls back to crawling internal links) and writes a markdown
   index of links to `<name>.llms.txt`.
2. **Serve** — a systemd user unit serves those files over HTTP so LLMDoc can
   fetch them over its own network stack (not via stdio).
3. **Index** — the `llmdoc` MCP server reads `LLMDOC_SOURCES`, fetches each page,
   converts HTML to markdown, chunks it, and stores chunks in a DuckDB database.
4. **Query** — OpenCode's `llmdoc` tool runs BM25 over `chunks` to answer
   framework/language questions.

## Files & paths

| Thing | Path |
|-------|------|
| Generator script | `~/.local/bin/gen-llms-txt.py` |
| Generated `.llms.txt` files | `~/.local/share/llmdoc/sources/` |
| Active search index | `~/.local/share/llmdoc/index.db` (DuckDB, ~285 MB) |
| LLMDoc install | `~/.local/bin/llmdoc` (uv tool → `~/.local/share/uv/tools/llmdoc/`) |

## Static file server

A systemd **user** unit `llmdoc-serve.service` (unit file at
`~/.config/systemd/user/llmdoc-serve.service`):

```ini
ExecStart=/home/linuxbrew/.linuxbrew/bin/python3 -m http.server 8099 \
  --bind 127.0.0.1 --directory /home/jpfeiff/.local/share/llmdoc/sources
Restart=on-failure
WantedBy=default.target
```

Manage with `systemctl --user status|restart|enable llmdoc-serve`.

## Indexed sources & current stats (2026-09-13)

| Source | Docs | Chunks |
|--------|------|--------|
| python | 400 | 159,437 |
| fastapi | 151 | 17,870 |
| bash | 142 | 9,848 |
| flask | 76 | 3,277 |
| zig | 1 | 1,377 |
| **Total** | **770** | **191,809** |

Zig is a single document ("Zig Language Reference", ~490 KB) because its language
reference is one server-rendered page, not a set of crawlable pages. It is
correctly chunked (1,377 chunks), so it is still searchable.

## Regenerating / reindexing

1. (Re)generate the `.llms.txt` files:
   ```
   ~/.local/bin/gen-llms-txt.py python https://docs.python.org/3/
   ~/.local/bin/gen-llms-txt.py fastapi https://fastapi.tiangolo.com/
   ~/.local/bin/gen-llms-txt.py flask   https://flask.palletsprojects.com/
   ~/.local/bin/gen-llms-txt.py bash    https://www.gnu.org/software/bash/manual/
   ```
   (Add `--crawl` to skip sitemap; `--prefix`, `--max`, `--out` tune the crawl.)
2. Rebuild the index. Either let the MCP server refresh on demand, or pre-warm
   directly with the venv Python (the stdio MCP path was flaky in the past):
   ```
   /home/jpfeiff/.local/share/uv/tools/llmdoc/bin/python /tmp/prewarm.py
   ```

## Gotchas learned (2026-09-13)

- `gen-llms-txt.py` **cannot** index Zig — the Zig language reference is one huge
  server-rendered page with no per-page URLs. Point LLMDoc at
  `https://ziglang.org/documentation/master/` directly instead.
- A `sitemap.xml` with <10 entries is a redirect stub, not a real index — the
  generator detects this and falls back to crawling.
- The index is **DuckDB**, not SQLite — don't try to open it with `sqlite3`.
- The active index is `~/.local/share/llmdoc/index.db` (per `LLMDOC_DB_PATH`).
  A stale `~/.llmdoc/` copy existed but was removed 2026-09-13.
- The system is a static file server over HTTP because LLMDoc fetches sources
  over its own network layer; point it at `127.0.0.1:8099/<name>.llms.txt`.
