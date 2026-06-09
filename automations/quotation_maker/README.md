# Quotation Maker

## Purpose

This automation generates internal-review quotation draft files for K-beauty B2B export sales.

It uses only local buyer data, buyer scoring results, proposal message outputs, local brand approval rules, and manually provided quotation input values. It does not send quotations externally, create final commercial offers, approve quotations for external sharing, scrape, search, crawl, enrich, verify, or automatically collect external data.

This automation also does not implement email sending, messaging automation, quotation sending, external sending, platform posting, APIs, browser automation, crawlers, buyer enrichment, credit checks, or live web research.

## Input Files

- `data/buyers_master_sample.csv`
- `data/buyers_scored_sample.csv`
- `data/proposal_messages_sample.csv`
- `data/brands_master.csv`
- `data/quotation_inputs_sample.csv`

Quotation input data must be manually prepared. Price, stock, expiry date, MOQ, delivery lead time, supply status, approval status, and price validity period must come from manually provided local input values.

## Output Files

- `data/quotation_sample.csv`
- `output/quotation_sample.xlsx`
- `output/quotation_sample.md`

If `output/quotation_sample.xlsx` is locked or cannot be overwritten, the generator creates a timestamped fallback XLSX file in `output/`.

## Schema and Rules References

- `docs/quotation_maker_spec.md`
- `docs/quotation_schema.md`
- `docs/quotation_rules.md`
- `docs/buyer_lead_schema.md`
- `docs/buyer_scoring_schema.md`
- `docs/proposal_message_schema.md`

## Generation Command

```powershell
python automations/quotation_maker/generate_quotations.py
```

Optional arguments:

```powershell
python automations/quotation_maker/generate_quotations.py `
  --buyers data/buyers_master_sample.csv `
  --scores data/buyers_scored_sample.csv `
  --proposals data/proposal_messages_sample.csv `
  --brands data/brands_master.csv `
  --quote-inputs data/quotation_inputs_sample.csv `
  --csv-output data/quotation_sample.csv `
  --xlsx-output output/quotation_sample.xlsx `
  --md-output output/quotation_sample.md
```

## Validation Command

```powershell
python tests/validate_quotations.py --quote-inputs data/quotation_inputs_sample.csv --quotations data/quotation_sample.csv --markdown output/quotation_sample.md --xlsx output/quotation_sample.xlsx --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --proposals data/proposal_messages_sample.csv --brands data/brands_master.csv
```

## Standard Workflow

1. Prepare buyer master, scored buyer, and proposal message data.
2. Manually prepare quotation input data.
3. Confirm price, stock, expiry date, MOQ, delivery lead time, and supply status are manually provided.
4. Generate quotation draft outputs.
5. Run the validation script.
6. Review blocked rows and confirmation-needed rows internally.
7. Confirm brand approval, price, stock, expiry, MOQ, delivery, tax, shipping, duties, and incoterms before external use.
8. Do not send quotations externally through this automation.

## Quotation Status Rules

- `draft_ready_for_internal_review`: the row has enough structured data for internal review only.
- `blocked_approval_required`: approval rules block external-ready quotation.
- `needs_price_confirmation`: unit price is blank, unknown, zero, invalid, or missing.
- `needs_stock_confirmation`: stock status or available quantity is missing, unknown, or invalid.
- `needs_expiry_confirmation`: expiry date is missing or unknown.
- `needs_moq_confirmation`: requested quantity is below MOQ or MOQ cannot be checked.
- `needs_buyer_review`: buyer data or internal review status requires additional review.
- `not_quotable`: the row cannot be quoted because supply, stock, or data conditions make it unsuitable.

`draft_ready_for_internal_review` is still internal review only. It is not an external-ready final quotation.

## Approval Block Rules

- `approval_block=true` must block external-ready quotation.
- Buyer scored `approval_block=true` must produce `blocked_approval_required`.
- Proposal message status `blocked_approval_required` must produce `blocked_approval_required`.
- `메디큐브` remains approval-required unless explicit approval is recorded.
- Brands with `approval_required=true` or `proposal_allowed=false` must be blocked unless explicit approval is recorded.
- A high score or A tier must not override `approval_block`.
- Blocked rows may remain visible only for internal review.

## Manual Commercial Data Rules

- `unit_price` must come from manual quotation input only.
- `stock_status` must come from manual quotation input only.
- `available_qty` must come from manual quotation input only.
- `expiry_date` must come from manual quotation input only.
- `supply_status` must come from manual quotation input only.
- `price_valid_until` must come from manual quotation input only.
- `delivery_lead_time` should come from manual quotation input or be clearly marked as general/default.
- The generator must not invent missing price, stock, expiry, availability, supply, or final trade terms.

## Price, Stock, Expiry, and MOQ Rules

- Missing price -> `needs_price_confirmation`.
- Missing stock or available quantity -> `needs_stock_confirmation`.
- Missing expiry date -> `needs_expiry_confirmation`.
- `requested_qty < moq` -> `needs_moq_confirmation`.
- `total_amount` is calculated only when `requested_qty` and `unit_price` are valid positive numbers.
- `total_amount` excludes tax, shipping, duties, discounts, insurance, customs fees, and incoterms.

## Compliance Review Rules

Before any external use, manually verify:

- brand approval
- price
- stock
- available quantity
- expiry date
- MOQ
- delivery lead time
- supply status
- currency
- price validity period
- tax
- shipping
- duties
- incoterms
- country-specific regulatory constraints

## Privacy and Contact Rules

- Quotation outputs must not include `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp` by default.
- Buyer contact data is privacy-sensitive and internal-use only.
- External sharing requires permission, masking, and review.

## Claim and Commercial Term Restrictions

Quotation outputs must not include unsupported:

- cosmetic efficacy claims
- medical claims
- clinical claims
- dermatological claims
- before/after claims
- guaranteed results
- official certification
- exclusive rights
- final contract terms
- final payment terms
- final incoterms
- final shipping terms

## Excel and Encoding Rules

- CSV files use UTF-8 with BOM, `utf-8-sig`.
- XLSX is preferred for business review.
- Korean, English, and Chinese text must be preserved.
- If the XLSX output is locked, a timestamped fallback should be generated.

## PASS / FAIL Usage

- `PASS`: quotation draft outputs passed structural and safety validation.
- `PASS` does not mean the quotation is external-ready.
- `PASS WITH CAUTION`: may be used for internal review only when commercial data still needs business confirmation.
- `FAIL`: quotation outputs must not be used until fixed.

## Known Limitations

- This automation does not verify real price.
- This automation does not verify real stock.
- This automation does not verify real expiry date.
- This automation does not verify buyer authenticity.
- This automation does not verify payment ability.
- This automation does not send quotations.
- Final commercial quotation requires human review and approval.
