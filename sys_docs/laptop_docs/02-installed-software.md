# 02 — Installed Software

Software is installed through **five** paths. Know which one a tool came from
before upgrading it, or you'll break a symlink / leave an orphan. (This laptop
is leaner than the desktop — no flatpak, no cargo/go/rust/zig toolchains.)

| Manager | Prefix / scope | Notes |
|---------|---------------|-------|
| **apt** (`dpkg`) | system | 79 manually-installed packages (base + user apps) |
| **Homebrew** | `/home/linuxbrew/.linuxbrew` | only **starship** (`brew leaves`) |
| **snap** | `/snap` | browser/mail + bases/runtimes |
| **flatpak** | system | none installed |
| **uv / npm** | `~/.local`, `~/.hermes` | Hermes + agent/MCP toolchain |

## Toolchain versions (probe, don't trust these over time)

- **Node** v26.7.0 / npm 11.19.0 — Hermes-managed
  (`~/.hermes/tools/node-26.7.0-linux-x64`), shimmed to `~/.local/bin/node`.
- **Python** 3.14.7 — Hermes-managed (`~/.hermes/tools/python-3.14.7+…`).
- **uv** 0.12.10 (`~/.local/bin/uv`).
- **No** `cargo`/`rustc`, `go`, or `zig` installed on this laptop.

## Homebrew

`brew leaves` → **`starship`** only. Homebrew here is just the prompt; the Qt6/
mesa/ffmpeg/LLVM stack that lives in Homebrew on the desktop does not exist on
this laptop.

## snap

User apps: `firefox`, `thunderbird`, `marktext`, `firmware-updater`. Plus bases
and runtimes: `bare`, `core20/22/24`, `gnome-3-38-2004`, `gnome-42-2204`,
`gnome-46-2404`, `gtk-common-themes`, `mesa-2404`, `snapd`.

## uv tools (`uv tool list`)

- `markitdown-mcp` v0.0.1a7 (→ `~/.local/bin/markitdown-mcp`)

## User-local binaries (`~/.local/bin`)

```
celery  codegraph  django-admin  dotenv  email_validator  flask
github-mcp-server  hermes  hermes-acp  hermes-agent  jsonschema
markitdown-mcp  mcp-filesystem-server  mcp-server-filesystem
mcp-server-memory  mcp-server-sequential-thinking  node  npm  npx  pip  pip3
pip3.12  playwright-mcp  pyserial-miniterm  pyserial-ports  py.test  pytest
sqlformat  terminal-driver-mcp  tldr  uv  uvx
```

The MCP-server entries (`github-mcp-server`, `mcp-*-server`, `codegraph`,
`playwright-mcp`, `terminal-driver-mcp`, `markitdown-mcp`) were installed
2026-09-26 — see [06-mcp-servers.md](./06-mcp-servers.md).

## Language servers (LSP) present

None. Probed 2026-10-03: `bash-language-server`, `pylsp`/`python3-pylsp`,
`clangd`, `lua-language-server`, and `zls` are all **absent** on this laptop
(the desktop has them; re-install here if ever needed).

## Notable packages not on this laptop

- No **libvirt/virt-manager/qemu** (no local VMs here; the 3270 BBS host is
  remote via SSH, and no `~/.ssh/config` alias exists yet).
- No **RetroArch**/flatpak emulators.
- No **x3270/c3270** 3270 terminal emulator (present on the desktop).
