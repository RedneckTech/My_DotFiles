# Hermes Agent

The Nous Research personal agent (this one) — used for general assistance,
browser automation, cron, and messaging-gateway work.

## Paths

| Thing | Path |
|-------|------|
| Config | `~/.hermes/config.yaml` → symlinks to `~/.user_config/home/.hermes/config.yaml` |
| Personality | `~/.hermes/SOUL.md` → symlinks to `~/.user_config/home/.hermes/SOUL.md` |
| Secrets | `~/.hermes/.env` |
| State DB | `~/.hermes/state.db` (SQLite) |
| Skills | `~/.hermes/skills/` |
| Binaries | `~/.hermes/bin/` (browser-use, uv, tirith) |
| CLI | `~/.local/bin/hermes` (+ `hermes-agent`, `hermes-acp`) |

## Key config (`config.yaml`)

- **Model**: `opencode-go/deepseek-v4-pro`, `base_url: https://openrouter.ai/api/v1`
- **Provider**: currently `opencode-zen` (per runtime) — the default routes
  through OpenRouter; keys in `.env`
- **Terminal**: `backend: local`, `cwd: .`, `timeout: 180`, `home_mode: auto`
- **Compression**: enabled (threshold 0.5, target ratio 0.2, protect last 20 turns)
- **Memory**: enabled, with per-session user profile + persistent memory (char
  limits 2200 / 1375)
- **Skills**: catalog under `~/.hermes/skills/` across categories (apple,
  autonomous-ai-agents, creative, devops, email, media, note-taking, productivity,
  research, social-media, software-development, web)
- **STT**: local `faster-whisper` (`base` model)
- **Browser**: built-in browser tooling (Browser Use, timeout 120s)

## Secrets (`.env`)

The `.env` is a large template (many providers document-stubbed with comments).
**Active keys** at the bottom:

```
OPENCODE_GO_API_KEY
OPENCODE_ZEN_API_KEY
```

Most other provider sections (Fireworks, OpenRouter, NovitaAI, Gemini, Ollama
Cloud, GLM, Kimi, Arcee, MiniMax, Hugging Face, DeepInfra, Tencent, etc.) are
present but commented out — available to enable by adding a key.

## Platform toolsets

Configured toolsets per platform: `hermes-cli`, `hermes-telegram`,
`hermes-discord`, `hermes-whatsapp`, `hermes-slack`, `hermes-signal`,
`hermes-homeassistant`, `hermes-qqbot`, `hermes-yuanbao`, `hermes-teams`,
`hermes-google_chat`. (Gateway is `null` — running primarily as a CLI agent.)

## Notes

- No cron jobs currently defined (`~/.hermes/cron/` is empty).
- SOUL.md currently contains only the standard Hermes base persona (one paragraph).
- Runs as the `default` Hermes profile.
