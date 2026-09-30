# AGENT HANDOFF — First Agri Sales-Ops (Rui) · Annual Payment Plan proposals

**Last updated:** 2026-07-29
**Branch:** `claude/levalicious-australia-b2b-f9rnks` (repo `ruisasase-pyrenee/pyrenee-slack-agent`)
**User:** Rui Sasase — Founding Member & Global Sales Manager, First Agri Inc. (Japanese matcha B2B exporter), on a Melbourne/Sydney sales trip. Uses this agent as his sales-ops AI. Casual Japanese, direct, moves fast, corrects tersely.

---

## 0. READ THIS FIRST — the golden rules (絶対ルール, from CLAUDE.md)

These override defaults. Violating them destroys trust.

1. **送信しない** — NEVER send emails/DMs/Slack. Always output as copy-paste drafts. Rui sends.
2. **顧客名の守秘** — never expose existing customer names externally (HIKARI, Matcha Mate, T2, etc.). Say "供給実績あり (name withheld)".
3. **受注前案件を受注計上しない** — don't count un-signed deals as won.
4. **数字は一次資料で確認** — verify every price/stock/figure against repo data (`sales-ops/*`), never from memory. **We verify all proposal math in Python before every render.**
5. 検疫・輸出書類は事実のみ.
6. **推定と確定を必ず分ける** — label ✅確定 / ⚠️推定.

Style: Slack = 報告型・箇条書き・■見出し, casual first person (〜らしい, 〜と思ってます). Proposals = clean, English, First Agri green `#38761D`.

---

## 1. WHAT THE USER IS ASKING FOR RIGHT NOW (current task thread)

The dominant deliverable is a **client-facing "Annual Payment Plan" proposal** — one A4 page per client, First Agri × Client collaboration lockup, a 12-month agreement where the **final (12th) month is discounted ~70%** so the effective annual discount is **≈5.8%**. Produced as **PDF** (and optionally editable docx).

Three clients: **Sneaker Laundry**, **itteki 一滴 Matcha**, **Matcha Mami**. Plus a **contents/index page** (目次) that lists all three.

### ⚠️ CRITICAL RECENT DIRECTION — PORTRAIT, NOT LANDSCAPE
- I built a **landscape (横)** "big collaboration" version at the user's request ("もっとクソデカくていいよ… 横でだして").
- The user then **reversed**: "横のじゃなくて縦の1ページ目のInの話" (not landscape, the PORTRAIT 1st-page index) + "**Sneakerも縦で作って！**" (make Sneaker in PORTRAIT too) + "**いらないそういうのは**" (I don't need the landscape stuff).
- **CONCLUSION: The user wants everything in PORTRAIT (縦). The landscape files are dead. Do not offer/push landscape again.**

### State of each portrait deliverable (all just delivered/confirmed this session):
| # | Client | Portrait PDF (scratchpad) | Status |
|---|--------|---------------------------|--------|
| — | Index/目次 | `First_Agri_Collaboration_Proposals_Index.pdf` | ✅ delivered, portrait, confirmed |
| 01 | Sneaker Laundry | `Annual_Payment_Plan_Sneaker_Laundry.pdf` | ✅ delivered (縦) |
| 02 | itteki 一滴 Matcha | `Annual_Payment_Plan_Itteki_Matcha.pdf` | ✅ delivered (縦) |
| 03 | Matcha Mami | `proposal_mami_fa003.html` / `proposal_mami_fa005.html` (2 SKUs) | HTML built; PDFs may need re-render (see §5) |

---

## 2. THE FINANCIAL MODELS (verified — do not guess these)

FX: **AUD 1 = JPY 114.5**. Effective discount always **≈5.8%** because `0.70 ÷ 12 = 5.83%`.

### Model A — "levelled" (function `make()` in `gen_proposal.py`)
Used for **Sneaker Laundry**. All 12 months pay the same level installment `P`; the final month is 70% off that installment.
```
P = round(total / 12)
final_pay = round(P * 0.30)      # final month = 30% of P (i.e. 70% off)
normal   = 12 * P                # standard annual total
discount = P - final_pay
plan     = normal - discount     # what they actually pay
rate     = discount / normal * 100   # ≈ 5.8%
```

### Model B — "ramp" (function `make_mami()` in `gen_proposal.py`)
Used for **itteki** and **Matcha Mami**. Actual per-month prices shown (volume ramps up); the final month is reduced by a fixed discount.
```
monthly      = [v*price for v in vols]
total        = sum(monthly)
discount     = round(0.70 * total / 12)   # = annual total ÷ 12 × 0.7
final_actual = monthly[-1]                # the last month's real delivery value
final_pay    = final_actual - discount    # final month = actual − discount
plan         = total - discount
rate         = discount / total * 100     # ≈ 5.8%
```
**This exact ramp formula was the subject of ~5 rounds of user correction. It is now CONFIRMED. Do not "improve" it.** The user's final word: "違うなー 最終月 120kg-(全体の注文量➗12✖️0.7)が割引" → final month = final-month-volume value − (total÷12×0.7).

### Verified numbers per client (✅確定):

**Sneaker Laundry** (Model A, AUD, landed DDP):
- `total = 490704` (= A$40,892/mo × 12). Landed A$40,892/mo covers 175 kg split **Melbourne 100 + Sydney 75**, incl. shipping + 10% import duty, effective **A$233.7/kg**.
- P = 40,892 · final = **12,268** · standard = 490,704 · save = **28,624** · plan = **462,080** · 5.8%.
- SKU **FA003**. Offer valid "11 August 2026".
- (Source of A$40,892: an uploaded landed PDF from Rinsho; an earlier figure A$41,370 / A$236.4/kg was superseded.)

**itteki 一滴 Matcha** (Model B, AUD, ex-freight):
- SKU **FA005** (Kagoshima) @ **A$131/kg**. `vols = [100,100] + [300]*10` = ramp 100→300 kg = **3.2 t/year**.
- total = **419,200** · discount = **24,453** · final_actual = 39,300 · final_pay = **14,847** · plan = **394,747** · 5.8%.
- Shipping = freight + 10% duty, **added separately** (ex-freight; quoted in the landed quotation). First order 14 Aug 2026.
- (⚠️ Deal also includes FA001 20–30 kg premium add-on — NOT in this proposal, which is FA005 only.)

**Matcha Mami** (Model B, JPY ¥, ex-shipping) — TWO proposals, one per SKU:
- `vols = [50,50] + [120]*10` = ramp 50→120 kg = **1.3 t/year**.
- **FA003** (Uji) @ **¥22,500/kg**: total ¥29,250,000 · discount ¥1,706,250 · final_actual ¥2,700,000 · final_pay **¥993,750** · plan **¥27,543,750** · 5.8%.
- **FA005** (Kagoshima) @ **¥15,000/kg**: total ¥19,500,000 · discount ¥1,137,500 · final_actual ¥1,800,000 · final_pay **¥662,500** · plan **¥18,362,500** · 5.8%.
- Shipping quoted separately, on top. Reference from Rinsho: FA003 50 kg → matcha ¥1,125,000 + shipping ¥104,936 = ¥1,229,936 (≈¥2,099/kg shipping). Offer valid "11 August 2026".
- **SKUs are FA003 & FA005** (user: "FA003,005でいいよ！" — earlier FA003/FA004 was wrong).

---

## 3. KEY FILES (all in the scratchpad unless noted)

**Scratchpad dir:** `/tmp/claude-0/-home-user-pyrenee-slack-agent/89cc7a24-869a-58d1-8d91-e189aed8d825/scratchpad/`

### Generators (Python → HTML):
- **`gen_proposal.py`** ← THE MAIN portrait generator. Contains `m()` (currency-aware money formatter using global `CUR`), `make()` (Model A levelled), `make_mami()` (Model B ramp, now fully generalized with params `cmark, ramp_desc, ship_box, ship_term, delivery_term, foot_basis`), and the deal calls at the bottom:
  - Sneaker → `make(...)` → `proposal_sneaker.html`
  - itteki → `make_mami(..., cur="A$", cmark=ITTEKI_MARK, IT_VOLS=[100,100]+[300]*10, price=131, ...)` → `proposal_itteki.html`
  - Matcha Mami → `make_mami(...)` ×2 (FA003 ¥22,500, FA005 ¥15,000, MM_VOLS=[50,50]+[120]*10) → `proposal_mami_fa003.html`, `proposal_mami_fa005.html`
  - Logos: `fa` (First Agri, from `logo_b64.txt`), `SNEAKER_MARK` (inline SVG asterisk), `ITTEKI_MARK` (`itteki_logo_b64.txt`, circular, `border-radius:50%`), `MM_LOGO` (`matcha_mami_logo.png` wordmark).
  - **NOTE:** `make_mami`'s CSS needed a `.lock .cust .clogo{height:42px;width:42px}` rule added (the itteki emblem rendered at natural/huge size without it and blew the layout to 2 pages). That fix is in.
- **`gen_index.py`** → `proposal_index.html` (portrait 目次). Title "A year of matcha, together." with 3 numbered rows (01 Sneaker / 02 itteki / 03 Matcha Mami), logos + descriptors + "Annual Payment Plan" tags. Uses `logo_b64.txt`, `itteki_logo.png`, `matcha_mami_logo.png`.
- **`gen_land.py`** → LANDSCAPE version (`land()` function). **DEAD — user rejected landscape.** Keep for reference only; do not deliver.
- **`gen_sneaker_split.py`** → `sneaker_split.html`, a landscape destination-split landed breakdown (Mel/Syd cards). Reproduces the uploaded A$40,892 landed math. Reference only.
- **`gen_schedule2.py`** → `payment_schedule_12mo.html`, a mobile-friendly Artifact-style schedule (published earlier). Reference.
- **`build_docx.js`** → editable .docx via `docx` npm lib. **Still uses the OLD levelled model for Matcha Mami/itteki — NOT updated to the ramp model.** If user asks for docx, update it to Model B first.

### Logo assets (scratchpad):
- `logo_b64.txt` — First Agri logo, base64 (raw, no data: prefix; code prepends `data:image/png;base64,`).
- `firstagri_logo.png`
- `itteki_logo.png` + `itteki_logo_b64.txt` — circular itteki emblem (masked/cropped from IMG_2401). **`itteki_logo_b64.txt` is huge (~630k tokens) — never `Read` it whole; it's only consumed by the generators.**
- `matcha_mami_logo.png` (591×258 wordmark, cropped from IMG_2420).
- `sneaker_mark.png` — PIL-drawn asterisk (SNEAKER_MARK is also available as inline SVG in the generators; the SVG is what's used).

### Rendering recipe (HTML → PDF → PNG to verify):
```bash
CHROME=$(ls /opt/pw-browsers/chromium-*/chrome-linux/chrome | head -1)
"$CHROME" --headless --no-sandbox --print-to-pdf=OUT.pdf --no-pdf-header-footer "file://$PWD/PAGE.html"
pdfinfo OUT.pdf | grep Pages          # MUST be 1 for a one-pager
pdftoppm -png -r 95 OUT.pdf check     # then Read check-1.png to eyeball
```

---

## 4. HARD-WON ENVIRONMENT GOTCHAS

- **Chromium headless enforces a min 500px viewport.** Screenshots rendered at 390/440px falsely look "cut off." Render at ≥500px (or just rasterize the PDF, which is A4-correct).
- **A one-pager that spills to page 2** is usually a few px of overflow. Fixes that worked: shrink top lockup/hero, and **position the footer `absolute; bottom:Xmm`** (only safe once no other element uses `margin-top:auto` to push into it). For portrait `make()`/`make_mami()` the layout already fits at 1 page.
- **`soffice`/LibreOffice is BROKEN** in this sandbox (fails even on .txt). Cannot render docx. Validate docx only by unzipping `word/document.xml` and grepping text.
- **`docx` npm was NOT preinstalled** — had to `npm install docx` in scratchpad.
- CJK font for PIL: `/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf`.
- `SendUserFile`: pass `files` as a JSON array. A bad earlier call failed because the path wasn't quoted in the array — always `["...path..."]`.

---

## 5. IMMEDIATE / SHORT-TERM NEXT STEPS

1. **Matcha Mami portrait PDFs** — the two HTMLs (`proposal_mami_fa003.html`, `proposal_mami_fa005.html`) are current (ramp model, `.clogo` fix in place). Re-render both to PDF with the recipe above, verify page count = 1 and numbers (FA003 final ¥993,750 / plan ¥27,543,750; FA005 final ¥662,500 / plan ¥18,362,500), and deliver if the user asks. (They were built; confirm they're the versions the user has.)
2. **Optional: editable docx** — only if requested. Update `build_docx.js` to Model B (ramp) first; it's stale.
3. **Optional: combine index + 3 proposals into one PDF** (e.g. `pdfunite`). Not yet requested for portrait.
4. Everything must stay **PORTRAIT**. Do not resurface landscape.

---

## 6. LONGER-TERM / STANDING TASKS

- **Task #2 (pending, never started):** 54-store café matcha drink-price survey — a "1杯経済" reverse-calc table (drink price AUD × 50 ≥ EXW+$20 判定). This is a real backlog item in the task list.
- CLAUDE.md CRM updates for the itteki & Matcha Mami 7/28 meetings and Matcha Mami visit are largely done; if new meeting notes come in, append in the established format and commit/push to the branch.

---

## 7. STANDING SUPPLY FLAGS (internal only — NEVER put in client docs)

Before committing any volume, confirm allocation (double-booking = incentive wipeout clause):
- **FA003**: this season tight (existing contracts Den's 1,680kg + JSY 1,000kg + Rocky's 2,300kg). Small orders only now; large annual = 来季予約. **BUT promoted to a "main product" next season (8–9t full allocation planned).** Sneaker's 175 kg/mo × 12 = 2.1 t and Mami's 1.3 t both lean on FA003 → must reconcile against allocation.
- **FA004**: ~1.5 t left, hard to reproduce (color-source depleted). Don't push large. Floor = list price (no discount). (Dropped from itteki & Mami deals.)
- **FA005**: near sold out. itteki's 3.2 t/yr (up to 300 kg/mo) and Mami's FA005 1.3 t are TIGHT → **裏取り必須** with production before confirming.
- FA001: no exclusivity, sellable all channels (成約実勢 $330). FA002: café/drink OK, retail-tin exclusivity being negotiated with T2; tightening (5t ≈ 10 months).

---

## 8. PRICING QUICK-REFERENCE (from CLAUDE.md, ✅確定 2026-07)

FA final prices (JPY): FA001 ¥50,000 / FA002 ¥40,000 / FA003 ¥22,500 / FA004 ¥25,000 / FA005 ¥15,000. USD @ ¥150: FA001 $333.3 / FA002 $266.7 / FA003 $150 / FA004 $166.7 / FA005 $100. 成約実勢: FA001 $330 / FA002 $260. These JPY values are also the floor (下限). FA series = USD basis; organic line (De/Df/Dg/AEc/AFb) = AUD basis — **never mix in a quote.** Shipping ≈ landed +$20/kg (20kg/$400), tapers with volume.

Signature block for outreach:
`Rui Sasase / Global Sales Manager & Founding Member / First Agri Inc. / first-agri.jp / rui.sasase@first-agri.jp / AU +61 43-160-3240 / WhatsApp +81 70-8446-6031`

---

## 9. FULL PRIOR-SESSION TRANSCRIPT

If you need exact earlier code/messages beyond this file:
`/root/.claude/projects/-home-user-pyrenee-slack-agent/89cc7a24-869a-58d1-8d91-e189aed8d825.jsonl`

CLAUDE.md (repo root) is the master CRM and the single source of truth for deals, stock, samples, and pricing — always reconcile against it (絶対ルール #4).
