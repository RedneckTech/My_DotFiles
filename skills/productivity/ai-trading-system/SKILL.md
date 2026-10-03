---
name: ai-trading-system
description: "Use when working on the user's AI trading system."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [trading, ibkr, hermes, planning, research]
---

# AI Trading System (Hermes + IBKR)

Multi-session project: a safe, self-improving AI trading system on Hermes Agent +
Interactive Brokers, paper-first with human-in-the-loop, maximizing free + open-source
software. Strategy comes later; the safe foundation comes first.

## Project anchors

- Project dir: `/media/jpfeiff/MassStorge/DevZone/AI_Trader`
- `plan.md` — the working plan (goal, principles, phases, open questions).
- `STACK_DECISIONS.md` — settled per-component picks + license traps + caveats. THE source
  of truth for the stack; check it before re-deciding anything.
- `RESEARCH_NOTES.md` — transcript synthesis + IBKR/safety/compliance findings.
- `RESEARCH_LLM_BRAIN.md` — open-weight LLM brain write-up.
- `transcripts/` — collected transcripts (17 from a playlist + the RevelioTrading channel).

## Working style (the user's corrected workflow — follow it)

- Research and COMPARE options for each component BEFORE committing to one. Present a ranked
  comparison with a clear best pick, a runner-up, and a one-line why, then let the user approve
  or swap. Do not silently pick a default and start using it.
- Do NOT jump ahead to building or implementation until the user says go. Planning and building
  are separate; the user has repeatedly stopped to keep it at planning/plan.md only.
- Work incrementally, one part at a time, and let the user drive the pace. When they say
  "leave the plan for now", stop — do not push to the next phase.
- Keep deliverables as files in the project dir and reference them. Re-read STACK_DECISIONS.md
  instead of re-running settled research.
- Respond in plain text — the user is in a CLI; markdown does not render there.

## Guiding principles (always-on)

- Paper first, always. No real money until the system runs clean for weeks.
- Human in the loop. The AI proposes; a human approves anything that touches money.
- Safety before strategy: kill switch, hard limits, read-only mode before any edge.
- Maximize free + open-source software. Pay only for VPS, broker data, and LLM API.

## Settled stack (see STACK_DECISIONS.md for detail and license traps)

Agent: Hermes · Broker bridge: ib_async + IB Gateway + IBC · History data: Tiingo free ·
Backtesting: NautilusTrader · Storage: DuckDB + Parquet · Scheduling: systemd timers ·
Dashboard: Streamlit · Control/notifications: Discord · Runtime: Podman · Secrets: age+sops ·
LLM brain: DeepSeek/Qwen (hosted) · Decision layer: Laya (open-source Jev-style, Apache-2.0).

## Fetching more transcripts

Use the `youtube-transcript-collection` skill for the fetch workflow. RevelioTrading channel
video IDs/titles are already enumerated in `fetch_revelio_transcripts.py` and
`fetch_revelio_retry.py` in the project dir (the retry script exists because YouTube
rate-limits burst transcript fetches).
