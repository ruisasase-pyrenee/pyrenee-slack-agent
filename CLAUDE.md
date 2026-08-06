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
- **三野 真代 (Mayo Mino)** — CEO三野龍太の配偶者。**デザイン担当**。
  `mayo.mino@pyrenee.net`. Pyrenee Driveのデザインモックを自ら設計。
  晴海オフィスの**発送実務・DHL集荷手配も担当**（印刷環境を使わない運用 —
  ペーパーレス通関前提）
- Tim Moore (`tim@timmoore.work`) — Director/cinematographer; Pyrenee Drive
  video collaboration partner. 映像歴25年（Motorola / Intel / GE Healthcare /
  Chick-Fil-A 等）。**ミズーリ州コロンビアへ転居完了**（2026年6月、アトランタ自宅売却済）.
  - 住所: 2612 Belfair Ct., Columbia, MO 65203, USA
  - 電話: 224.723.8150（メール署名由来。公式サイトは問い合わせフォームのみで
    裏取り不可 — **単一ソース依存**に留意）
- Daniel Stine (`stine@risingactfilms.org`) — Executive Director, Rising Act
  Films. Working with Tim on the Pyrenee Drive video project. Based in **Atlanta, GA**（Old Fourth Ward）.
  **Tim宛メールは原則Danielを CC に入れる**（既存スレッドの慣行）
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

### 映像制作 — Pyrenee Drive（2026-07 現況）

- 動画2本。**当初6月納品 → 7月納品に変更合意済**
- Tim不在期間: 6/29〜7/6（帰宅後すぐ撮影準備開始）
- 撮影用モックは**「機能なしのデザインモック」**。画面は**合成用グリーン（クロマキー）**
  - ⚠️ Timは6/30メールで "set it up for camera and function" と記載し
    **実機と誤認するリスク**があった（三野まよさんの指摘で発覚・是正）
- Pyrenee側の宿題: UI画面素材／参考映像／ブランドガイドをTimへ提供

#### 発送記録（2026-07-01 実施済）

- DHL Express / Waybill **7877583151** / 2.00kg・1個口 / TYO→STL→COU / 到着目安 7/7〜8
- 差出: Pyrenee Inc, Mayo Mino, 4-7-4 Harumi, CrossDock Harumi 601, Tokyo 104-0053
- 内容品申告: "Mock-up for photography" / Ref: "Shooting mock-up"

#### 国際物流の知見

- **Pyrenee Drive（モック含む）は内蔵リチウム電池なし**。シガーソケット（12V）給電のみ
  → 危険物（DG）申告不要
- 国際発送は**DHL Express推奨**（3〜4営業日・通関代行・追跡精緻）。
  EMSは6〜10日＋リチウム電池制限が厳しく精密機器に不向き
- 米国 **de minimis $800未満**なら受取人の輸入関税ほぼゼロ。
  試作・モックは "Prototype / Mock-up, not for resale" として申告
- HSコード: **非稼働モックは 9023.00**（実演・展示用モデル）。
  稼働する電子機器の 8543.70 とは区別

### 過去経緯 — 映像制作

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

## 運用ルール（セッションで確立）

- **事実確認は単一ソースに依存しない**。メール署名の情報は複数スレッド横断で
  一貫性を検証し、可能なら公開サイトでも裏取りする。裏取り不能なら
  「単一ソース依存」と正直に明示する
- **Google Meetのダイヤルイン番号**（+1 314-474-2729 / +81 3-4545-0450）を
  個人の電話番号と混同しない
- **外部送付物はGmail下書きまで作成し、送信は笹瀬さんが実行**する
- **PDF等バイナリのメール添付は base64 転記で破損する**。
  手動添付またはDriveリンクを使う
- **発送前に「何を送るのか」の仕様（稼働/非稼働・仕上げ）を関係者間で明示確認**する。
  今回は三野まよさんの指摘で認識齟齬を未然に防げた
- **PDF等の成果物を生成したら、毎回すぐにファイル送付（インライン表示）して
  笹瀬さんがその場で中身を確認できるようにする**。「できました」の報告だけで
  終わらせない（2026-08-06 確立）

## Slack agent (this repo)

Personal Slack AI agent powered by Claude. The bot acts as Rui's business
sparring partner (壁打ち相手) — direct, conclusion-first answers in the
language the user writes in.

- Entry point: `app.py`
- Stack: `slack-bolt` (Socket Mode), `anthropic` SDK
- Required env: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `ANTHROPIC_API_KEY`
