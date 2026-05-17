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
- **杉江** (`sugie@actieus.com`) — actieus.com; introduced Matkins Digital to Rui.
- **Jake** (`matkinsdigital@gmail.com`) — Matkins Digital, video production.
- **Vin** (`vin.garc@gmail.com`) — Matkins Digital team.
- **Nick** — Video production intermediary (exact role TBC; Rui initially assumed
  Nick was handling Zoom/contact coordination for Tim & Daniel).
- **瀧弁護士** — 瀧法律事務所; E-2 visa consultation lead.
- **Lauren Buchanan** — Anthropic Partnerships. `linkedin.com/in/lauren-s-buchanan/`

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

## Active Projects (as of May 2026)

### 映像制作 — Pyrenee Drive

- **Rising Act Films** (Tim Moore + Daniel Stine): 5/13 MTG完了。
  月次15〜20秒ショートクリップ + 2〜3分説明動画。予算感$5K〜$10K/月。
  7月納品目標。コンセプト: ドラえもん（未来の友達）。
  CEO 三野龍太が東京オフィス周辺でAIインタラクション映像撮影予定。
  来週アトランタで対面MTG検討中（三野・野口はオンライン参加）。
- **Matkins Digital** (杉江紹介 → Jake + Vin): 見積り受領済み。
  5/20(火)US時間に追加MTG予定。その後Rising Act Films or Matkinsで発注先決定。
- Zoom meeting link: `https://us06web.zoom.us/j/84008535320?pwd=lbPHWoc3WHja9mKlw3NDXoMkPO8T3x.1`
- Sample footage Vimeo links (driving AI interaction):
  - `https://vimeo.com/1192206491/a08392fdd8` (車内AI対話映像)
  - `https://vimeo.com/1192207464/84cf3038ea` (車両・歩行者認識画面、音声なし)

### E-2ビザ — 瀧法律事務所

- 現状の米国法人では申請困難（実績・雇用実態が不十分）
- **推奨**: Pyreneeの兄弟会社または孫会社として新米国法人設立
- 投資要件: $200K〜$300K（使途確定後実行）+ 運用資金$100K以上
- 雇用要件: W-2正社員3名/申請者（米国市民・グリーンカード・E-2家族ビザ保持者。フリーランス不可）
- 費用: 事業計画書$4,000 + 着手金$8,800（確定後）+ 申請費$380
- 提出物: 1年・3年・5年事業計画書
- ESTA期限: **2026年6月12日**（入国2026年3月14日、90日滞在）
- 次回MTGで「確実に通るか」最終判断予定
- 1人目が通れば2人目は容易。将来的に3名申請予定。

### Anthropic連携

- Startup Program: 最大$25K APIクレジット（直接申請が有効）
- Claude Partner Network: $100Mパートナープログラム
- 連絡先候補: Lauren Buchanan (Anthropic Partnerships, LinkedIn DM推奨)
- Anthropic SF事務所: 500 Howard Street, SoMa

## Pyrenee Business Facts

- 累計資金調達: 13億円（2026年2月に2億円追加）
- トヨタKINTO提携: 来年1月正式オプション導入予定
- 米国法人: デラウェア州設立（2016年）
- 将来目標: NASDAQ上場
- 製品: Pyrenee Drive（AI事故防止・ドライビングパートナーデバイス）
- 米国対象市場: 約2億8900万台

## Current US Stay & Schedule (2026)

- 入国日: 2026年3月14日
- ESTA期限: **2026年6月12日**（90日）
- 次の入国: 2026年7〜8月予定
- 来週: アトランタ訪問予定（Tim & Daniel対面MTG検討中）
- 拠点: Palo Alto（Japan Innovation Campus）/ Las Vegas / San Francisco

## Slack agent (this repo)

Personal Slack AI agent powered by Claude. The bot acts as Rui's business
sparring partner (壁打ち相手) — direct, conclusion-first answers in the
language the user writes in.

- Entry point: `app.py`
- Stack: `slack-bolt` (Socket Mode), `anthropic` SDK
- Required env: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `ANTHROPIC_API_KEY`
