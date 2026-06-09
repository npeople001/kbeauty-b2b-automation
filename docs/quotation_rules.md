# Quotation Rules and Templates

## 1. Scope

This document defines executable business rules for Task 009: Quotation Maker.

Quotation outputs are internal-review drafts only. Task 009 does not send quotations externally, create final commercial offers, verify price, verify stock, verify expiry date, verify supply availability, or collect external data.

Task 009 does not implement:

- Email sending
- Messaging automation
- Quotation sending
- External sending
- Platform posting
- Scraping
- Live web research
- Automatic web search
- APIs
- Browser automation
- Crawlers
- Buyer enrichment
- Credit checks
- External data collection

The Quotation Maker must only structure and evaluate local data and manually provided quotation inputs for internal review.

## 2. Source-of-Truth Rules

The generator may only use:

- Local buyer master data
- Local buyer scoring data
- Local proposal message data
- Local brands master data
- Manually provided quotation input data

The generator must not invent:

- `unit_price`
- `stock_status`
- `available_qty`
- `expiry_date`
- `supply_status`
- `price_valid_until`
- Certifications
- Exclusive rights
- Incoterms
- Shipping cost
- Taxes
- Discounts
- Final trade terms

If a required commercial value is missing, blank, invalid, or `unknown`, the output must keep the value blank or marked as `unknown` and assign the correct confirmation-needed status.

## 3. Status Priority Rules

`quotation_status` must be selected using this priority order:

1. `blocked_approval_required`
2. `needs_price_confirmation`
3. `needs_stock_confirmation`
4. `needs_expiry_confirmation`
5. `needs_moq_confirmation`
6. `needs_buyer_review`
7. `draft_ready_for_internal_review`
8. `not_quotable`

Rules:

- The strongest applicable issue should determine `quotation_status`.
- `blocked_approval_required` overrides all other statuses.
- Missing commercial data should prevent `draft_ready_for_internal_review`.
- `draft_ready_for_internal_review` is still internal review only. It is not external-ready and must not be treated as a final quotation.
- `not_quotable` should be used for rows that cannot be quoted because of severe commercial, supply, or data issues, unless an approval block applies first.

## 4. Approval Block Rules

Approval blocking protects approval-required brands and prevents restricted items from becoming external quotation-ready.

Use `quotation_status=blocked_approval_required` when:

- Buyer scoring `approval_block=true`.
- Proposal message `message_status=blocked_approval_required`.
- `brand_name` has `approval_required=true` in `data/brands_master.csv`, unless explicit approval exists.
- `brand_name` has `proposal_allowed=false` in `data/brands_master.csv`, unless explicit approval exists.
- `brand_name` is `메디큐브` and explicit approval is not recorded.

Additional rules:

- A high buyer score, `priority_tier=A`, or strong buyer fit must not override approval blocking.
- Blocked rows may remain in the internal quotation table only as blocked/internal-review items.
- Blocked rows must not be treated as external quotation-ready.
- Approval-required brands must not appear as quote-ready items in external-facing outputs.
- Brand master approval rules are business-critical data and must not be changed by the generator.

## 5. Price Rules

- `unit_price` must come from manually provided quotation input only.
- If `unit_price` is blank, `unknown`, zero, invalid, or non-numeric, use `quotation_status=needs_price_confirmation` unless a stronger status applies.
- Do not infer `unit_price` from brand, product, country, category, previous rows, buyer score, proposal message, or historical assumptions.
- Do not fill missing price with placeholders that look real.
- If `price_valid_until` is blank or `unknown`, `compliance_notes` must flag price validity confirmation needed.
- `currency` must be present for `total_amount` to be meaningful.
- Prices can become stale quickly and must be reviewed before external use.

## 6. Stock and Supply Rules

- `stock_status`, `available_qty`, and `supply_status` must come from manually provided quotation input only.
- If `stock_status` is blank or `unknown`, use `quotation_status=needs_stock_confirmation` unless a stronger status applies.
- If `available_qty` is blank, `unknown`, invalid, zero when stock is expected, or non-numeric, use `quotation_status=needs_stock_confirmation` unless a stronger status applies.
- If `supply_status` is blank or `unknown`, `compliance_notes` must flag supply confirmation needed.
- If `stock_status=out_of_stock` or `supply_status=unavailable`, use `quotation_status=not_quotable` unless a stronger approval block applies.
- Do not infer stock or supply availability from brand, buyer interest, country, channel, prior message status, or score.

## 7. Expiry Date Rules

- `expiry_date` must come from manually provided quotation input only.
- If `expiry_date` is blank or `unknown`, use `quotation_status=needs_expiry_confirmation` unless a stronger status applies.
- Expiry date must not be invented.
- If expiry date is provided, it must be preserved as provided.
- The generator does not validate whether the expiry date is commercially acceptable unless explicit future rules are added.
- If expiry date looks unusual or non-standard, preserve it and flag review instead of correcting it silently.

## 8. MOQ Rules

- General business MOQ is 100+ units.
- Product-level `moq` from quotation input should be used when provided.
- If product-level `moq` is missing, use `100` as a default only if clearly marked as default/general MOQ.
- `requested_qty` must be compared with `moq`.
- If `requested_qty < moq`, set `moq_check=fail`.
- If `requested_qty >= moq`, set `moq_check=pass`.
- If `requested_qty` or `moq` is missing, blank, `unknown`, invalid, zero, or non-numeric, set `moq_check=unknown`.
- If `moq_check=fail`, use `quotation_status=needs_moq_confirmation` or `not_quotable` depending on stock, supply, approval, and later business rules.
- MOQ must not be presented as a final external term without internal review.
- The generator must not silently alter source buyer data or quotation input data to make MOQ pass.

## 9. Total Amount Calculation Rules

- `total_amount` may be calculated only when `requested_qty` and `unit_price` are valid positive numbers.
- Calculation formula: `total_amount = requested_qty * unit_price`.
- If `requested_qty` or `unit_price` is invalid, `total_amount` must be blank.
- If `currency` is blank or `unknown`, `total_amount` may be calculated for internal arithmetic review, but `compliance_notes` must flag currency confirmation needed.
- `total_amount` does not include:
  - Tax
  - Shipping
  - Duties
  - Discounts
  - Insurance
  - Customs fees
  - Incoterms
- Do not invent any additional commercial terms.
- Do not present calculated totals as final payable amounts without internal review.

## 10. Delivery Lead Time Rules

- Delivery lead time is generally 20-30 days.
- `delivery_lead_time` should come from quotation input where possible.
- If blank, use `20-30 days general estimate` only if clearly marked as general/default and not guaranteed.
- If `delivery_lead_time` is blank or defaulted, `compliance_notes` must flag delivery confirmation needed.
- Do not present delivery lead time as a final guaranteed term.
- Shipping method, logistics cost, customs process, and incoterms require separate manual confirmation.

## 11. Required Internal Review Rules

`required_internal_review` must be `true` when:

- `quotation_status` is not `draft_ready_for_internal_review`.
- `approval_block=true`.
- `unit_price`, `stock_status`, `available_qty`, `expiry_date`, `supply_status`, or `delivery_lead_time` needs confirmation.
- `moq_check=fail` or `moq_check=unknown`.
- `compliance_notes` include price, stock, expiry, MOQ, delivery, approval, claim, or localization review.
- `currency` is missing or `unknown`.
- The quote row includes any approval-sensitive brand.

Even when `quotation_status=draft_ready_for_internal_review`, external use still requires human review and approval outside Task 009.

## 12. Compliance Notes Rules

`compliance_notes` must include relevant cautions from this list:

- `내부 검토용 견적 초안`
- `외부 발송 전 검토 필요`
- `브랜드 승인 확인 필요`
- `가격 확인 필요`
- `재고 확인 필요`
- `유통기한 확인 필요`
- `MOQ 확인 필요`
- `배송 리드타임 확인 필요`
- `공급 가능 여부 확인 필요`
- `화장품 표현/클레임 포함 금지`
- `세금/운임/관세/인코텀즈 미포함`
- `개인정보 비노출`

Rules:

- All quotation outputs must include an internal-review disclaimer.
- Compliance notes should be Korean-first for internal business review.
- Notes must not create the impression that the quote has been approved, sent, or finalized.
- If Chinese or English text appears elsewhere, Korean internal compliance notes must still be included.

## 13. Next Action Rules

`next_action` should be practical and internal.

Recommended examples:

- `내부 브랜드 승인 여부 확인`
- `가격 확인 후 견적 재생성`
- `재고 및 공급 가능 수량 확인`
- `유통기한 확인`
- `MOQ 충족 가능 여부 확인`
- `통화 및 가격 유효기간 확인`
- `외부 발송 전 대표/담당자 검토`

Rules:

- `next_action` must not trigger sending, posting, messaging, or buyer-facing automation.
- Approval-blocked rows must direct the team to internal approval review first.
- Missing commercial values must direct the team to confirm those values manually.

## 14. Privacy Rules

- Quotation output must not include `contact_email`, `contact_phone`, `wechat_id`, `whatsapp`, or other buyer contact fields by default.
- Buyer contact data is internal-use only.
- External sharing requires permission, masking, and review.
- Quotation outputs should identify buyers by `buyer_id`, `company_name`, and `country` only unless a later approved task explicitly changes the privacy model.

## 15. Claim and Commercial Term Restrictions

Quotation outputs must not include:

- Cosmetic efficacy claims
- Medical claims
- Clinical claims
- Dermatological claims
- Before/after claims
- Guaranteed results
- Official certification unless manually provided and verified
- Exclusive distribution rights unless manually provided and verified
- Final contract terms
- Final payment terms
- Final incoterms
- Final shipping terms

If any of these terms are needed for a future business workflow, they must be manually provided, separately verified, and explicitly supported by a later approved task.

## 16. Output Template Guidance

Output rows should be structured as:

- One row per buyer-product quote item.
- Blocked rows should remain visible for internal review.
- Missing commercial values should not be filled.
- Korean internal compliance notes should always be included.

If an optional Markdown summary is created later, it must clearly state:

- `내부 검토용 견적 초안`
- `외부 발송 금지`
- `가격/재고/유통기한/승인 확인 필요`

Markdown summaries must not replace structured CSV/XLSX validation.

## 17. Validation Requirements

Future quotation outputs must be validated for:

- Required input and output columns.
- `quotation_status` allowed values.
- `approval_block` behavior.
- `메디큐브` and approval-required brand blocking.
- Missing price, stock, or expiry producing the correct status.
- MOQ check correctness.
- `total_amount` calculation correctness.
- No invented commercial terms.
- No contact field exposure.
- Internal-review disclaimer.
- No external sending automation.
- No scraping, API, or external data collection indicators.
- Korean, English, and Chinese text preservation.

## Step C Scope

This rules and template document does not implement code, create or modify CSV files, create Markdown output files, create XLSX files, send quotations, automate external communication, scrape, search, call APIs, crawl, enrich buyers, perform credit checks, or collect external data.
