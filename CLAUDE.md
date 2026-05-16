# CLAUDE.md

This repo is Rui Sasase's personal Slack AI agent. Claude is also used as Rui's
general work assistant (email triage, calendar, meeting prep, follow-ups).

## About the user

- 笹瀬 類 (Rui Sasase) — US Evangelist at Pyrenee Inc. (株式会社Pyrenee)
- Primary email: `rui.sasase@pyrenee.net`
- Secondary email: `rui.sasase@first-agri.jp` (一番農業; some Pyrenee calendar
  events are organized from this address)
- Based: Palo Alto, CA (Japan Innovation Campus) / Tokyo Harumi (CROSS DOCK 601)

## Key people

- **三野 龍太 (Ryuta Mino)** — CEO of Pyrenee. Referred to as "三野さん" /
  "Ryuta". `ryuta.mino@pyrenee.net`
- **野口 颯人 (Hayato Noguchi)** — Management at Pyrenee.
  `hayato.noguchi@pyrenee.net`
- Tim Moore (`tim@timmoore.work`) — Director/cinematographer; Pyrenee Drive
  video collaboration partner.
- Daniel Stine (`stine@risingactfilms.org`) — Executive Director, Rising Act
  Films. Working with Tim on the Pyrenee Drive video project.

## Recurring meetings

- **Pyrenee【アメリカ戦略】** — 三野さんとのUS事業キャッチアップ（定例）.
  Organized from `rui.sasase@first-agri.jp`. Gemini transcripts are usually
  shared to `rui.sasase@pyrenee.net` after each session.
- **Pyrenee 定例** — Pyrenee internal weekly meeting.

## AI Prompting Philosophy (Rui's standard)

Rui follows a multi-agent orchestration approach — not single-AI prompting.
The mental model: **"AIチームの編成図を渡す"** (give the AI an org chart, not just instructions).

### 5 design patterns to apply

**1. Sub-Agent Orchestration**
Assign a lead commander AI that decomposes tasks into parallel specialist sub-agents
(fact research / competitive analysis / structure design / critic), then integrates outputs.
- Anthropic official: 90.2% accuracy improvement vs. single Claude
- Used in production by Netflix and Harvey

**2. Outcomes Loop**
Spin up a separate evaluator AI to score the main AI's output on a rubric (100-point scale).
If score < 80, evaluator writes specific correction instructions and triggers regeneration.
- Anthropic internal: +10.1% PowerPoint quality, +8.4% docx quality

**3. Architect-Implementer Split**
Fully separate the "design AI" (structure, persona, axes, headings) from the "execution AI" (writing).
Run them in separate sessions. Harvey achieved 6x task completion rate with this pattern.

**4. Memory + Dreaming**
Have AI review past 30 session logs overnight, extract recurring failure patterns,
and propose updates to the system prompt for future sessions. (Anthropic, May 2026)

**5. Phased Preamble Prompting**
Enforce 4 phases before any execution: ① receipt confirmation → ② plan presentation
→ ③ user approval → ④ execution. Prevents early stopping and runaway behavior.
(OpenAI/Codex official standard)

## Slack agent (this repo)

Personal Slack AI agent powered by Claude. The bot acts as Rui's business
sparring partner (壁打ち相手) — direct, conclusion-first answers in the
language the user writes in.

- Entry point: `app.py`
- Stack: `slack-bolt` (Socket Mode), `anthropic` SDK
- Required env: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `ANTHROPIC_API_KEY`
