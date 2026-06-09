# Quotation Maker Specification

## 1. Scope

Task 009: Quotation Maker defines and later implements a local automation workflow that generates internal-review quotation draft tables and files for K-beauty B2B export sales.

Task 009 does:

- Use local buyer lead data, scored buyer data, proposal message outputs, local brand approval rules, and manually provided quotation input data.
- Generate internal-review quotation draft data and files.
- Help the team review quotation readiness, missing commercial information, MOQ fit, brand approval restrictions, and compliance cautions.
- Preserve Korean, English, and Chinese text in business-facing files.

Task 009 does not:

- Send quotations externally.
- Create final commercial offers.
- Approve quotations for external sharing.
- Send emails, DMs, WeChat messages, WhatsApp messages, platform messages, or any other external communication.
- Implement email sending, messaging automation, quotation sending, external sending, or platform posting.
- Scrape, search, crawl, enrich, verify, or collect external data.
- Implement live web research, automatic web search, APIs, browser automation, crawlers, buyer enrichment, credit checks, requests, or external data collection.
- Invent price, stock, inventory, expiry date, supply availability, certifications, exclusive rights, contract terms, or final trade terms.

All generated quotation outputs are internal-review drafts only. Price, stock, expiry date, supply availability, and final trade terms must come from manually provided quotation input data only.

## 2. Input Files

### Required Existing Inputs

| File | Purpose | Notes |
|---|---|---|
| `data/buyers_master_sample.csv` | Buyer master sample data. | Provides buyer identity, country, MOQ fit, interested brands, approval warnings, and privacy-sensitive source fields. |
| `data/buyers_scored_sample.csv` | Scored buyer sample data. | Provides internal priority tier, risk flags, and `approval_block`. |
| `data/proposal_messages_sample.csv` | Proposal message sample data. | Provides proposal readiness status, recommended brands, excluded brands, and internal review notes. |
| `data/brands_master.csv` | Local brand approval reference. | Must be used to block approval-required or proposal-restricted brands. |

### New Quotation Input To Be Created Later

| File | Purpose | Notes |
|---|---|---|
| `data/quotation_inputs_sample.csv` | Manually provided sample quotation input data. | Must contain only manually provided price, stock, expiry, MOQ, delivery, supply, and approval data. |

### Optional Future Inputs

- `data/buyers_master.csv`
- `data/buyers_scored.csv`
- `data/proposal_messages.csv`
- `data/quotation_inputs.csv`
- Manually provided price list
- Manually provided stock list
- Manually provided expiry list
- Manually approved brand list

All CSV files intended for Excel or business users must use UTF-8 with BOM, `utf-8-sig`.

## 3. Output Files

Recommended future outputs:

| File | Purpose | Notes |
|---|---|---|
| `data/quotation_sample.csv` | Structured internal quotation draft data. | Used for validation and later automation steps. |
| `output/quotation_sample.xlsx` | Business-facing internal review workbook. | Preferred for Excel review and Korean, English, and Chinese text. |
| `output/quotation_sample.md` | Optional internal review summary. | Useful for quick management review, but not required as the primary structured output. |

Clarifications:

- CSV output is structured internal data.
- XLSX output is a business-facing internal review file.
- Markdown output is an optional internal review summary.
- None of these outputs are final external quotations.
- None of these outputs should be sent externally without human review, brand approval, price/stock/expiry confirmation, and commercial approval.

## 4. Recommended Quotation Input Fields

These fields define manually provided quotation input data. The generator must not invent any of these values.

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---:|---|---|---|
| `quote_input_id` | Unique ID for a quotation input line. | Required | Text ID. | `QI-0001` | Must be unique within the quotation input file. |
| `buyer_id` | Buyer ID to quote for. | Required | Existing buyer ID. | `BUYER-0001` | Must match buyer master, scored buyer, and proposal message data. |
| `brand_name` | Brand name for the quotation line. | Required | UTF-8 text. | `아누아` | Must be checked against `data/brands_master.csv` when available. |
| `product_name` | Product name to quote. | Required | UTF-8 text. | `Sample Toner 200ml` | Must be manually provided. Do not invent official product names. |
| `product_category` | Product category. | Optional | UTF-8 text. | `toner` | Should be manually provided or derived only from the quotation input. |
| `sku_or_option` | SKU, option, size, shade, or package option. | Optional | UTF-8 text. | `200ml` | Leave blank if not provided. |
| `requested_qty` | Buyer-requested quantity for this line. | Required | Integer. | `150` | Must be manually provided or copied from confirmed quotation input. |
| `unit_price` | Unit price for this line. | Required for draft-ready status | Decimal number or blank. | `4.50` | Must be manually provided. Blank or unknown requires price confirmation. |
| `currency` | Currency for unit price and total amount. | Required when price exists | Controlled text or ISO-style code. | `USD` | Missing currency prevents treating total as final commercial value. |
| `stock_status` | Stock status. | Required for draft-ready status | Controlled text or manual note. | `available` | Must be manually provided. Blank or unknown requires stock confirmation. |
| `available_qty` | Available quantity. | Required for draft-ready status | Integer or blank. | `500` | Must be manually provided. Blank or unknown requires stock confirmation. |
| `expiry_date` | Product expiry date. | Required for draft-ready status | ISO date `YYYY-MM-DD`, month format, or blank. | `2027-12-31` | Must be manually provided. Blank or unknown requires expiry confirmation. |
| `moq` | Product-level MOQ. | Required for MOQ check | Integer. | `100` | Product-level MOQ should override the general 100+ rule when manually provided. |
| `delivery_lead_time` | Delivery lead time for the item or quotation. | Optional | Text. | `20-30 days` | Must be manually provided or clearly marked as a default/general condition. |
| `price_valid_until` | Date until which the provided price is valid. | Optional | ISO date `YYYY-MM-DD` or blank. | `2026-06-30` | Missing value should trigger review caution. |
| `supply_status` | Supply availability status. | Required for draft-ready status | Controlled text or manual note. | `available_for_internal_review` | Must be manually provided. Blank or unknown must be flagged. |
| `approval_status` | Explicit brand or quotation approval status. | Optional | Controlled text. | `not_approved` | Required to override approval-required brand blocks in a future controlled workflow. |
| `notes` | Internal notes. | Optional | UTF-8 text. | `가격은 내부 확인 필요.` | Must not include unsupported claims or unnecessary personal data. |
| `provided_by` | Person or internal source that provided the quotation input. | Optional | UTF-8 text. | `internal_sales` | Used for auditability. |
| `provided_at` | Date the quotation input was provided. | Optional | ISO date `YYYY-MM-DD`. | `2026-06-09` | Used for auditability and price freshness review. |

## 5. Recommended Quotation Output Fields

These fields define the future generated quotation output. The output must remain an internal-review draft.

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---:|---|---|---|
| `quotation_id` | Unique generated quotation line ID. | Required | Text ID. | `QUOTE-0001` | Must be unique in the output file. |
| `buyer_id` | Buyer ID. | Required | Existing buyer ID. | `BUYER-0001` | Must match input data. |
| `company_name` | Buyer company name. | Required | UTF-8 text. | `Shanghai Sample Beauty Trade` | From buyer master only. Do not invent. |
| `country` | Buyer country. | Required | UTF-8 text. | `China` | From buyer master only. |
| `quotation_status` | Internal quotation readiness status. | Required | Controlled value. | `draft_ready_for_internal_review` | See status rules. |
| `approval_block` | Whether approval rules block external quotation readiness. | Required | Boolean text. | `true` | Must reflect buyer scoring, proposal status, and brand approval rules. |
| `brand_name` | Quoted brand name. | Required | UTF-8 text. | `아누아` | From quotation input only. |
| `product_name` | Quoted product name. | Required | UTF-8 text. | `Sample Toner 200ml` | From quotation input only. |
| `product_category` | Product category. | Optional | UTF-8 text. | `toner` | From quotation input only. |
| `sku_or_option` | SKU, option, size, shade, or package option. | Optional | UTF-8 text. | `200ml` | From quotation input only. |
| `requested_qty` | Requested quantity. | Required | Integer or blank if invalid. | `150` | From quotation input only. |
| `moq` | MOQ used for checking. | Required | Integer or blank if missing. | `100` | Product-level MOQ from quotation input where available. |
| `moq_check` | Result of MOQ comparison. | Required | Controlled value. | `pass` | Recommended values: `pass`, `below_moq`, `missing_qty`, `missing_moq`, `review_needed`. |
| `unit_price` | Unit price. | Required for draft-ready status | Decimal or blank. | `4.50` | From quotation input only. |
| `currency` | Currency. | Required when price exists | Text. | `USD` | Missing currency requires caution. |
| `total_amount` | Calculated line total. | Optional | Decimal or blank. | `675.00` | Calculate only when `requested_qty` and `unit_price` are valid numbers. |
| `stock_status` | Stock status. | Required for draft-ready status | Text. | `available` | From quotation input only. |
| `available_qty` | Available quantity. | Required for draft-ready status | Integer or blank. | `500` | From quotation input only. |
| `expiry_date` | Expiry date. | Required for draft-ready status | Date text or blank. | `2027-12-31` | From quotation input only. |
| `delivery_lead_time` | Delivery lead time. | Optional | Text. | `20-30 days` | Must not be represented as guaranteed final lead time. |
| `price_valid_until` | Price validity date. | Optional | ISO date or blank. | `2026-06-30` | Missing value should be flagged for review. |
| `supply_status` | Supply availability status. | Required for draft-ready status | Text. | `available_for_internal_review` | From quotation input only. |
| `compliance_notes` | Internal caution notes. | Required | UTF-8 text. | `내부 검토용 견적 초안입니다.` | Must include relevant approval, price, stock, expiry, MOQ, delivery, claim, and localization cautions. |
| `required_internal_review` | Whether internal review is required before any external use. | Required | Boolean text. | `true` | Usually `true` for all Task 009 draft outputs. |
| `next_action` | Practical internal next action. | Required | UTF-8 text. | `가격/재고/유통기한 최종 확인 후 내부 승인 검토.` | Must not trigger external sending. |
| `generated_at` | Date the quotation draft was generated. | Required | ISO date `YYYY-MM-DD`. | `2026-06-09` | Use local generation date. |

## 6. Quotation Status Rules

Allowed `quotation_status` values:

- `draft_ready_for_internal_review`
- `blocked_approval_required`
- `needs_price_confirmation`
- `needs_stock_confirmation`
- `needs_expiry_confirmation`
- `needs_moq_confirmation`
- `needs_buyer_review`
- `not_quotable`

Status priority:

1. `blocked_approval_required`
2. `needs_price_confirmation`
3. `needs_stock_confirmation`
4. `needs_expiry_confirmation`
5. `needs_moq_confirmation`
6. `needs_buyer_review`
7. `draft_ready_for_internal_review`
8. `not_quotable` where applicable

Notes:

- Approval and brand blocks must be evaluated before commercial readiness.
- Missing manually provided price, stock, expiry, or MOQ data must prevent draft-ready status.
- `draft_ready_for_internal_review` means the row is ready for internal review only. It does not mean the quotation is final or external-ready.
- `not_quotable` may be used when a row cannot be quoted because of severe data issues, invalid quantity, unavailable supply, unsupported product, or business decision.

## 7. Approval and Brand Rules

- If buyer `approval_block=true`, the quotation must not be external-ready.
- If proposal message `message_status=blocked_approval_required`, the quotation must use `quotation_status=blocked_approval_required`.
- If `brand_name` has `approval_required=true` or `proposal_allowed=false` in `data/brands_master.csv`, `quotation_status` must be `blocked_approval_required` unless explicit approval exists in a controlled local approval input.
- `메디큐브` must remain approval-required unless explicit approval is recorded.
- A high buyer score, high commercial interest, or `priority_tier=A` must not override `approval_block` or brand approval rules.
- Approval-required brands may appear only as blocked/internal-review items, not external-ready quotation items.
- Brand master rules are business-critical data and must not be changed by the quotation generator.

## 8. Price, Stock, Expiry, and Supply Rules

- `unit_price` must come from manually provided quotation input only.
- `stock_status` must come from manually provided quotation input only.
- `available_qty` must come from manually provided quotation input only.
- `expiry_date` must come from manually provided quotation input only.
- `supply_status` must come from manually provided quotation input only.
- If `unit_price` is blank or unknown, set `quotation_status=needs_price_confirmation`.
- If `stock_status` or `available_qty` is blank or unknown, set `quotation_status=needs_stock_confirmation`.
- If `expiry_date` is blank or unknown, set `quotation_status=needs_expiry_confirmation`.
- If `supply_status` is blank or unknown, `compliance_notes` must flag supply confirmation needed.
- The generator must not estimate, infer, backfill, or guess missing commercial values.
- Price, stock, expiry, and supply values can become stale quickly and must be reviewed before external use.

## 9. MOQ Rules

- MOQ is generally 100+ units.
- Product-level `moq` from quotation input should be used where available.
- `requested_qty` must be compared with `moq`.
- If `requested_qty < moq`, set `quotation_status=needs_moq_confirmation` or `not_quotable` depending on later quotation rules.
- If `requested_qty` or `moq` is missing, the quotation must require internal review.
- MOQ terms must not be presented as final external terms without review.
- The generator must not silently alter source buyer data or quotation input data to resolve MOQ conflicts.

Recommended `moq_check` values:

- `pass`: `requested_qty` is greater than or equal to `moq`.
- `below_moq`: `requested_qty` is lower than `moq`.
- `missing_qty`: `requested_qty` is missing or invalid.
- `missing_moq`: `moq` is missing or invalid.
- `review_needed`: MOQ cannot be confidently interpreted.

## 10. Total Amount Calculation Rules

- `total_amount` should be calculated only when `requested_qty` and `unit_price` are valid numbers.
- Calculation formula: `total_amount = requested_qty * unit_price`.
- If `currency` is missing, `total_amount` should not be treated as a final commercial value.
- The calculation is for internal review only.
- Taxes, shipping, duties, discounts, incoterms, payment terms, insurance, customs costs, and other trade terms must not be invented.
- If those terms are needed, mark them as verification needed in `compliance_notes` or `next_action`.

## 11. Delivery Lead Time Rules

- Delivery lead time is generally 20-30 days.
- It may be used only if manually provided or clearly marked as a default/general condition.
- It must not be presented as guaranteed final lead time.
- If `delivery_lead_time` is missing, mark delivery confirmation needed.
- Delivery terms, shipment method, incoterms, customs duties, and logistics costs require separate manual confirmation.

## 12. Privacy and Contact Rules

- Quotation output must not include `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp` by default.
- Buyer contact data is privacy-sensitive and internal-use only.
- External sharing requires permission, masking, and review.
- Quotation outputs should identify buyers by `buyer_id`, `company_name`, and `country` only unless a later task explicitly approves broader data handling.
- The Quotation Maker must not collect buyer contact data automatically.

## 13. Claim and Compliance Rules

- Quotation output must not include cosmetic efficacy claims.
- Do not include medical, clinical, dermatological, functional, before/after, or guaranteed result claims.
- Do not include official certification, exclusive rights, distribution rights, contract terms, regulatory approvals, or final trade terms unless manually provided and verified.
- Compliance notes must flag review needs for brand approval, price, stock, expiry, MOQ, delivery, claims, localization, payment, currency, and final trade terms where relevant.
- Chinese, English, Korean, or other localized quotation wording must be reviewed before external use.

## 14. Encoding and Excel Rules

- CSV files intended for Excel or business users must use UTF-8 with BOM, `utf-8-sig`.
- Scripts must read business-facing CSV files using an encoding compatible with `utf-8-sig`.
- XLSX is preferred for business review.
- Korean, English, and Chinese text must be preserved.
- Korean brand names must be validated after CSV/XLSX generation.
- XLSX generation should include timestamp fallback if the output file is locked or cannot be overwritten.
- Source CSV files must not be modified to resolve output permission issues.

## 15. Validation Requirements

Future quotation outputs must be validated for:

- Required input and output columns.
- Row consistency with quotation inputs.
- `buyer_id` matching buyer master, scored buyer, and proposal message data.
- `approval_block` behavior.
- `메디큐브` and approval-required brand blocking.
- `proposal_allowed=false` brand blocking.
- Price, stock, expiry, and supply values not being invented.
- Status assignment for missing price, stock, expiry, MOQ, buyer review, or approval data.
- `total_amount` calculation correctness.
- Currency presence when total amount exists.
- No buyer contact field exposure, including `contact_email`, `contact_phone`, `wechat_id`, and `whatsapp`.
- No external sending automation.
- No email, messaging, quotation sending, platform posting, or external communication workflow.
- No scraping, live research, automatic search, APIs, browser automation, crawlers, requests, buyer enrichment, credit checks, or external data collection indicators.
- Korean, English, and Chinese text preservation.
- Internal-review disclaimer present.
- No unsupported cosmetic, medical, clinical, functional, certification, exclusive rights, contract, stock, price, or final trade term claims.

## 16. Completion Criteria

Task 009 is complete only when:

- `docs/quotation_maker_spec.md` exists.
- Quotation schema exists.
- Quotation rules/template document exists.
- Quotation input sample CSV exists.
- Quotation generator exists.
- Quotation CSV/XLSX/optional Markdown outputs are generated.
- Validation script exists and passes.
- README/workflow documentation exists.
- Roadmap and task log are updated.
- Final review passes.

## Step A Scope

This Step A specification does not implement code, create CSV files, create Markdown output files, create XLSX files, send quotations, automate email or messaging, scrape, search, crawl, enrich, verify, or collect external data.
