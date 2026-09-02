# Hot Lead Follow-up Checklist (3-Day Rule)

## When a Hot B2B Request notification arrives

- [ ] Log the lead in `sales-ops/lead-tracker.csv` (or run the `lead-to-outreach` skill, which does this automatically)
- [ ] Confirm auto-reply was sent (notification usually says "自動返信済み")
- [ ] Pick SKU recommendation(s) using `sales-ops/fa-catalog.json` -> `sku_selection_rules`
- [ ] Draft outreach (WhatsApp short version + optional email via Gmail draft)
- [ ] Set `follow_up_due` = date received + 3 days

## If no reply within 3 days -> phone follow-up call

Call script / things to confirm before preparing a custom quote:

- [ ] 店舗展開規模 (how many stores / locations, current and planned)
- [ ] 競合状況 (who else are they sourcing from or evaluating — any competitor pricing mentioned?)
- [ ] Confirmed monthly volume within the stated range (low end vs high end of e.g. "50-100kg")
- [ ] Delivery cadence preference (single monthly shipment vs split shipments)
- [ ] Packaging / private-label requirements
- [ ] Target landed price per kg, if they have one
- [ ] Sample shipping address + receiving contact confirmed

## After the call

- [ ] Update `lead-tracker.csv`: `follow_up_done = yes`, add notes
- [ ] If sample requested: email `corporate@first-agri.jp` sample request (address, SKU(s), attention name) — 2 business day turnaround
- [ ] If quantity-slide / custom quote requested: prepare tiered pricing (higher volume commitment = better AUD/kg) referencing `fa-catalog.json` prices
- [ ] If visiting Australia this trip: check if the lead's city fits the current travel window before offering a visit

## Safety / send-before-you-send checks

- [ ] Never auto-send WhatsApp/email — always draft and let Rui review + send personally
- [ ] Do not quote a firm AUD or USD number to a customer without resolving the catalog's AUD-vs-USD inconsistency first (see `fa-catalog.json` -> `_note_currency`)
- [ ] Don't share other customers' pricing, volumes, or names across leads
