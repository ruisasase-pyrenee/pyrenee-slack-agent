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

## Slack agent (this repo)

Personal Slack AI agent powered by Claude. The bot acts as Rui's business
sparring partner (壁打ち相手) — direct, conclusion-first answers in the
language the user writes in.

- Entry point: `app.py`
- Stack: `slack-bolt` (Socket Mode), `anthropic` SDK
- Required env: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `ANTHROPIC_API_KEY`
