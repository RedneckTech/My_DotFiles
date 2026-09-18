# OpenAI Codex

OpenAI Codex CLI agent. Minimal configuration — a single model override plus
trusted-project declarations.

## Paths

- Config: `~/.codex/config.toml`
- Auth: `~/.codex/auth.json` (OpenAI login, chmod 600)
- Skills: `~/.codex/skills/` (empty)
- Memories: `~/.codex/memories/` (empty)

## Config (`config.toml`)

```toml
model = "gpt-5.4"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "cached"
model_reasoning_effort = "xhigh"
```

## Trusted projects

```toml
[projects."/home/jpfeiff"]
trust_level = "trusted"

[projects."/media/jpfeiff/NeonDrive/DevZone/Software_Dev/Python_Projects/lto-charm"]
trust_level = "trusted"

[projects."/media/jpfeiff/NeonDrive/DevZone/Software_Dev/DongleFree3_Project"]
trust_level = "trusted"
```

## Notes

- Not actively customized: no skills, no memories populated.
- `sandbox_mode = "workspace-write"` means Codex can write inside its workspace but
  needs approval outside it; the three trusted projects relax that guard.
