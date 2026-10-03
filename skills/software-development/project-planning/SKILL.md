---
name: project-planning
description: "Use when planning a system or tech stack before building."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [planning, research, tech-stack, architecture, selection]
    related_skills: [spike, grounded-citations]
---

# Project Planning (research → compare → plan → build)

## When to Use
- The user wants to research, compare options, or write a plan for a new system, tech stack, or project, and is not ready to build yet.
- They ask for "best options" for components rather than a single recommendation.

## Workflow (in this order; do not skip ahead)

1. Gather before you recommend. Read existing local materials first (notes, transcripts, repo files, prior research in the project dir), then go to the web for current facts — versions, maintenance status, licenses, pricing.

2. When the user asks for "the best option" or "best X for each part," produce a COMPARISON, not a single pick. For each candidate give: what it is, license, maintenance status (active/abandoned as of now), strengths, weaknesses, cost. Then state one BEST PICK with a one-line justification and a runner-up. Also list what was rejected and why (dead libraries, license traps).

3. When the user asks for "a plan," write a basic plan file (plan.md): goal, principles/constraints, chosen stack (one line each — full detail lives in a separate decisions file), phases, undecided items, next step. Keep it basic; do not build.

4. Let the user advance phases. They sequence research → plan → build and will say when to move. Do not end a planning turn with "want me to start building?" unless building was actually requested.

## Standing preferences

- Free + open-source software is a hard filter. Prefer OSI-approved licenses; treat fair-code, BSL/SSPL, Elastic-2.0, and source-available-but-not-OSI as disqualifying for the primary pick.
- When a user says "free," confirm whether the constraint is cost (hosting) or licensing (open source) before selecting — the two lead to different answers.

## Technique

- Fan out heavy research to parallel subagents: one per component or question, each returning a ranked comparison + best pick + runner-up + cited URLs, then synthesize into one decisions file. This keeps the working context clean and parallelizes the lookups.

## Pitfalls

- Verify maintenance status and license from GitHub or official docs, not memory — abandoned projects (last commit years old, maintainer gone) and license changes (permissive → source-available/BSL) are the classic traps in tech selection.
- Treat subagent findings on fast-moving facts (e.g. "current best LLM model") as time-sensitive: flag exact versions to re-confirm at build time rather than hard-coding them.
