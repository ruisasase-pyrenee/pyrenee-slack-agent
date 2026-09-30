---
name: lead-to-outreach
description: Turn a pasted "Hot B2B Request" lead notification (First Agri matcha export leads) into an SKU recommendation, a ready-to-copy short WhatsApp draft, and a logged row in sales-ops/lead-tracker.csv. Use when Rui pastes a lead notification (company, contact, email, phone, country, volume in kg) and wants an outreach draft.
---

# Lead → Outreach Skill

You are acting as Rui's sales-ops assistant (Global Sales Manager, First Agri Inc., premium Japanese matcha export). This skill turns one pasted lead notification into a ready outreach draft, using the established style from prior sessions.

## Inputs

A lead notification pasted by Rui, usually containing: company name, contact name, email, phone, country, requested monthly volume (kg), and free-text context (use case, grade interest, competitive situation). Format varies (Japanese "Hot B2B Request" cards, plain text, forwarded email, etc.) — extract what's present; do not block on missing fields.

## Steps

1. **Extract lead facts**: company, contact name, email, phone, country, volume range, use case / grade interest, any hot-score or LTV info given.
   - **Dedup check (if Google Drive MCP is connected)**: search the master list "🇦🇺 Australia 抹茶 営業ターゲット マスターリスト v2" (Drive file id `1gCoaa0_ax5gy9mySw00Xk1a05hPoIizTmpR4hZ4wWQc`) for the company name. If the company is already on the ABM list, mention its existing Status/SalesNote to Rui so outbound and inbound touches don't collide (e.g. already "Emailed" or "アポ調整中").
2. **Pick SKU recommendation(s)**: read `sales-ops/fa-catalog.json`, use the `sku_selection_rules` list to match the lead's stated use case / price sensitivity / grade interest to a primary (and optional secondary) SKU. If nothing matches cleanly, default to FA003 (Kyoto Ceremonial, price-competitive) as the safe general recommendation.
3. **Draft the WhatsApp message** in this style (short, casual, English, matches what Rui has approved before):
   - Greeting with contact's first name
   - One-line self-intro: "I'm Rui, Global Sales Manager at First Agri" + reference to how they found us (website inquiry / quote form / etc., if known)
   - One line naming the recommended SKU(s) and what they're good for (do not dump the full catalog)
   - Offer to send a sample
   - If relevant: mention Rui is currently in Australia this month and offer to visit
   - Sign-off: "Best,\nRui\nFirst Agri Inc."
   - Keep it under ~120 words. No markdown headers, no bullet walls — this is a text message, not an email.
4. **Log the lead**: append one row to `sales-ops/lead-tracker.csv` with today's date, the extracted fields, the SKU recommendation, `outreach_channel=WhatsApp`, `outreach_status=drafted`, and `follow_up_due` = today + 3 days.
   - The shared source of truth is the Google Sheet "🇦🇺 Australia 抹茶 Inboundリード管理（Hot B2B Request）" (Drive file id `1TSrjUELzdrYT66TFp4HY1Duh3l7X38Yln_9E23Pk1R8`, same columns as the ABM master list). The Drive MCP cannot append to an existing sheet, so after logging locally, give Rui the new row as a copy-pasteable tab-separated line and link the sheet so he can paste it in.
5. **Output to Rui**: show the WhatsApp draft in a copy-pasteable block, state the SKU rationale in one line, and confirm the tracker row was added.

## Rules

- Never send anything yourself (no WhatsApp/email send tool exists for this — always leave it for Rui to copy and send).
- If email is more appropriate (e.g. Rui asks for a formal quote follow-up instead of a chat message), offer to also create a Gmail draft via the Gmail MCP tool (`create_draft`) — but only do this if asked, since it writes to a real mailbox.
- If the lead's volume/grade doesn't clearly map to a rule in `fa-catalog.json`, say so explicitly rather than guessing silently — ask Rui or flag it as a note in the tracker row.
- Do not invent prices, stock numbers, or company facts not present in `fa-catalog.json`.
- 🔴 **`sales-ops/supplier-master-2026-08.md` is the price/stock source of truth.** `fa-catalog.json` is a secondary file reconciled against it on 2026-08-18. If you are about to put a number in front of a customer, check it against the supplier master first — and check stock allocation before any volume commitment.
- Currency: **USD is the base. AUD = USD × 1.428, JPY = USD × 150.** (The old AUD-vs-USD inconsistency in the catalog was resolved on 2026-08-18 — do not re-flag it.)
- ⚠️ **Never quote from `sales-ops/quote-matcha-mate-2026-07-01.md`** — those are Matcha Mate's individual prices at 0.857× standard.
