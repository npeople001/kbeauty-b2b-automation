# Buyer Scoring Automation Specification

## 1. Scope

### What Task 007 Does

Task 007 defines and implements an internal buyer lead scoring workflow for the K-beauty B2B export business.

The scoring workflow uses manually provided local buyer lead data to assign:

- an internal sales priority score
- a priority tier
- scoring reasons
- risk flags
- approval blocks
- a recommended next action

The purpose is to help the sales team decide which already-entered buyer leads should be reviewed or followed up first.

### What Task 007 Does Not Do

Task 007 must not:

- scrape buyer data
- perform live web research
- perform automatic web search
- call APIs
- use browser automation
- crawl websites or platforms
- use requests or external network collection
- enrich buyer profiles from external sources
- verify whether a buyer is real
- verify creditworthiness
- verify payment reliability
- guarantee purchase probability
- update or correct business master data without explicit instruction

The score is an internal prioritization aid only. It is not evidence that a buyer is authentic, financially reliable, approved for proposal, or likely to purchase.

## 2. Input Files

### Required Input

| File | Purpose | Encoding |
| --- | --- | --- |
| `data/buyers_master_sample.csv` | Sample normalized buyer lead master file from manually provided buyer data. | `utf-8-sig` |

The required input must already contain manually provided buyer lead fields such as buyer type, country, platform, estimated order quantity, MOQ fit, lead status, privacy status, approval warning, and next action.

### Optional Future Inputs

| File | Purpose | Encoding |
| --- | --- | --- |
| `data/buyers_master.csv` | Future real buyer lead master file for internal use. | `utf-8-sig` |
| `data/brands_master.csv` | Brand approval reference for approval-required or proposal-blocked brands. | `utf-8-sig` |

`data/brands_master.csv` may be used only as a local approval-rule reference. It must not be modified by the scoring automation.

## 3. Output Files

### Recommended Output

| File | Purpose | Encoding |
| --- | --- | --- |
| `data/buyers_scored_sample.csv` | Scored sample buyer leads for internal prioritization review. | `utf-8-sig` |

### Optional Future Outputs

| File | Purpose |
| --- | --- |
| `output/buyers_scored_sample.xlsx` | Business-facing scored buyer lead review workbook. |
| `output/buyer_priority_review_{date}.xlsx` | Date-stamped buyer priority review workbook for internal meetings. |

Generated XLSX outputs are for internal business review only. External sharing requires privacy review and approval.

## 4. Recommended Output Fields

| Field | Meaning | Format | Example | Notes |
| --- | --- | --- | --- | --- |
| `buyer_id` | Stable buyer lead identifier from the input file. | Text | `BUYER-0001` | Must match the input row. |
| `score_total` | Internal prioritization score. | Integer, recommended 0-100 | `82` | Higher means higher internal follow-up priority, not higher purchase certainty. |
| `priority_tier` | Internal follow-up tier. | `A`, `B`, `C`, `Hold` | `A` | Tier must follow the priority tier rules below. |
| `scoring_summary` | Short explanation of why the score was assigned. | Text | `MOQ fit and China relevance are strong, but approval review is required.` | Must mention major positive and negative factors. |
| `positive_factors` | Factors that increased the score. | Semicolon-separated text | `moq_fit=yes; country=China; repeat_purchase_potential=high` | Use only input-derived factors. |
| `negative_factors` | Factors that reduced the score. | Semicolon-separated text | `payment_risk=high; estimated_order_qty unknown` | Use only input-derived factors. |
| `risk_flags` | Operational, approval, MOQ, payment, privacy, or data-quality flags. | Semicolon-separated text | `approval_required_brand; payment_risk_high` | Must include key blockers and caution items. |
| `approval_block` | Whether approval rules block external proposal readiness. | Boolean text: `true` or `false` | `true` | Must be `true` when approval-required brands are present without explicit approval. |
| `recommended_next_action` | Internal next action for the sales team. | Text | `Confirm order quantity and run internal brand approval review before proposal.` | Must not recommend external proposal for approval-blocked brands. |
| `scoring_version` | Version of scoring rules used. | Text | `buyer_scoring_v1` | Helps future audit and comparison. |
| `scored_at` | Date when scoring was generated. | ISO date or datetime | `2026-06-08` | Use local generation date. |

## 5. Priority Tier Rules

| Tier | Meaning | Typical Use | Important Limitation |
| --- | --- | --- | --- |
| `A` | High internal follow-up priority. | Buyer appears operationally suitable based on manually provided fields. | Does not prove buyer authenticity, creditworthiness, or purchase likelihood. |
| `B` | Medium internal follow-up priority. | Buyer has useful potential but needs clarification or has moderate risk. | Requires manual review before proposal. |
| `C` | Low internal follow-up priority. | Buyer has weak MOQ fit, incomplete data, or limited immediate sales readiness. | May become higher priority after missing data is resolved. |
| `Hold` | Do not prioritize until a blocking issue is resolved. | Approval block, severe payment risk, missing required fields, or major data-quality issue. | Hold is not rejection; it means review is needed before follow-up. |

Recommended score bands:

- `A`: 80-100, unless blocked by approval, severe payment risk, or missing critical data
- `B`: 60-79
- `C`: 30-59
- `Hold`: blocking issue exists, or score below 30

Approval blocks may force `Hold` or cap the buyer at `B` depending on the final scoring rules. External proposal readiness must remain blocked until approval is explicitly confirmed.

## 6. Scoring Factors

| Factor | How It Should Affect Score | Caution |
| --- | --- | --- |
| `moq_fit` | `yes` increases score; `no` reduces score strongly; `unknown` adds a risk flag. | MOQ fit is based on manually entered quantity, not confirmed purchase order data. |
| `estimated_order_qty` | Higher quantities may increase score when consistent with MOQ. | Do not treat as guaranteed order volume. |
| Country priority | China, Southeast Asia, and Russia may receive strategic priority. | Country priority does not verify buyer quality. |
| `china_relevance` | `high` increases China workflow priority. | China relevance is manually assessed. |
| `buyer_type` | Importer, distributor, wholesaler, and beauty chain may score higher for B2B export. | Buyer type must be manually provided. |
| `sales_channel` | Wholesale, offline, marketplace, live commerce, and social commerce may affect fit. | Channel information does not imply actual sales performance. |
| `platform` | WeChat, Douyin, Xiaohongshu, TikTok, Shopee, Telegram, VK, or offline may affect follow-up style. | Platform field must not trigger automatic platform collection. |
| `payment_risk` | `low` may increase score; `medium` adds caution; `high` reduces score strongly; `unknown` adds caution. | This is a manual risk indicator, not credit verification. |
| `repeat_purchase_potential` | `high` increases score; `unknown` should not be overinterpreted. | Internal estimate only. |
| `lead_status` | More actionable statuses may increase score. Closed or inactive statuses should reduce score. | Status must be manually maintained. |
| `interested_brands` | Useful for matching buyer interest to available brands. | Approval-required brands must not be externally recommended without approval. |
| `approval_warning` | Adds risk and may create approval block. | Must never be ignored for external proposal readiness. |
| `proposal_brand_check` | `approval_required_review` must block external proposal readiness. | Approval review is required before external use. |
| Contact completeness | May improve operational readiness for follow-up. | Contact fields are privacy-sensitive and must not be exposed unnecessarily. |
| Next action readiness | Clear `next_action` may increase operational readiness. | Must remain internal and practical. |

## 7. MOQ Scoring Rules

MOQ is generally 100+ units.

| Input Condition | Required Interpretation | Scoring Effect |
| --- | --- | --- |
| `estimated_order_qty >= 100` and `moq_fit=yes` | MOQ appears suitable. | Increase score. |
| `estimated_order_qty` between 1 and 99 and `moq_fit=no` | MOQ is below standard threshold. | Strongly reduce score and recommend quantity confirmation or category bundling. |
| Blank, `unknown`, 0, or non-numeric quantity and `moq_fit=unknown` | MOQ cannot be confirmed. | Add risk flag and recommend confirming estimated order quantity. |
| Quantity and `moq_fit` are inconsistent | Data-quality issue. | Add risk flag and recommend fixing the master row before scoring is used. |

The scoring automation must not silently change source buyer lead data. If inconsistency is detected, it should report the issue in scoring output or validation.

## 8. Country and China Priority

China is the current priority market, while Southeast Asia and Russia are also important active markets.

Recommended internal priority treatment:

- China: higher strategic priority when buyer fields are complete and `china_relevance` supports China workflow.
- Southeast Asia: relevant priority for TikTok, Instagram, Shopee, distributor, online seller, or beauty chain workflows.
- Russia: relevant priority for importer, distributor, Telegram, VK, offline, or premium/derma category workflows.
- Other/global markets: neutral unless business context indicates relevance.

China priority must not imply that a buyer is verified, that platform operation is permitted, or that account restrictions are solved. China-related fields are manually provided workflow indicators only.

## 9. Buyer Type and Channel Rules

The scoring automation should support flexible buyer types as long as MOQ and follow-up readiness are reasonable.

Typical scoring guidance:

- Importer, distributor, wholesaler, and beauty chain: generally strong B2B fit.
- Online seller, marketplace seller, live commerce, and influencer commerce: useful when MOQ, payment risk, and follow-up readiness are acceptable.
- Retailer or offline shop: evaluate by estimated order quantity and repeat purchase potential.
- Unknown buyer type: reduce confidence and request clarification.

Sales channel and platform fields should shape the recommended next action, not trigger external collection.

## 10. Payment Risk Rules

`payment_risk` is a manually entered indicator only.

The scoring automation must not:

- perform credit checks
- claim creditworthiness
- verify payment reliability
- infer financial health from external sources

Recommended treatment:

- `low`: no major payment concern based on manually entered data
- `medium`: add caution and require payment terms review
- `high`: reduce score strongly and add risk flag
- `unknown`: add caution and recommend payment-risk review before proposal

## 11. Repeat Purchase Potential

`repeat_purchase_potential` is an internal estimate.

Recommended treatment:

- `high`: increase score if MOQ and risk profile are acceptable
- `medium`: moderate positive factor
- `low`: lower priority unless other strategic factors are strong
- `unknown`: do not penalize heavily, but mark as information gap when relevant

The score must not claim that repeat orders are likely unless supported by actual manually provided evidence.

## 12. Brand Approval Rules

Approval-required brands are business-critical.

Rules:

- `restricted_or_approval_required` indicators must be respected.
- If `approval_warning` is populated, add an approval risk flag.
- If `proposal_brand_check=approval_required_review`, set `approval_block=true`.
- If `interested_brands` includes `메디큐브`, set `approval_block=true` unless explicit approval is provided in a future approved input field.
- `메디큐브` remains approval-required unless explicit approval is provided.
- Approval-required brands may be recorded as buyer interest.
- Approval-required brands must not be automatically recommended for external proposal, buyer-facing pitch, public content, advertising copy, or quotation.
- A high score must not override approval restrictions.

Recommended next actions for approval-blocked rows should include internal approval review before any external proposal.

## 13. Contact and Privacy Rules

Buyer contact fields are privacy-sensitive.

Privacy rules:

- Sample files must use placeholder contact data only.
- Real buyer contact data is internal-use data.
- Scoring outputs should avoid exposing full contact details unless necessary for an internal workflow.
- Contact completeness may be used only as an operational readiness indicator.
- Public outputs must not expose buyer contact details.
- External sharing requires permission, masking, or privacy review.

Contact fields may include:

- `contact_name`
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `website`
- `sns_url`

The scoring automation must not collect, validate, enrich, or search these fields externally.

## 14. Evidence and Limitation Rules

The score must remain cautious and internal.

The automation must not claim:

- the buyer is real
- the buyer has purchasing authority
- the buyer is financially reliable
- the buyer will purchase
- the buyer can legally import or sell products
- the buyer's platform presence is verified
- the buyer's sales performance is verified

Missing or uncertain input data must be reflected in:

- `scoring_summary`
- `negative_factors`
- `risk_flags`
- `recommended_next_action`

Recommended caution labels:

- `data_missing`
- `moq_unknown`
- `payment_risk_unknown`
- `approval_required_brand`
- `privacy_review_needed`
- `manual_verification_needed`

## 15. Encoding and File Handling

CSV files intended for Excel or business users must use `utf-8-sig`.

Rules:

- Read CSV files using an encoding compatible with `utf-8-sig`.
- Write scored CSV outputs using `utf-8-sig`.
- Preserve Korean, English, and Chinese text.
- Do not modify source CSV files while generating scored outputs.
- XLSX is preferred for business-facing review when Korean, English, or Chinese text is included.
- If XLSX output is added later and the target file is locked, create a timestamped fallback output file.

## 16. Validation Requirements

Future validation for scored buyer leads must check:

- scored output file exists
- scored output is readable with `utf-8-sig`
- required output columns exist in exact order
- row count matches the input buyer master file
- every `buyer_id` exists in the input buyer master file
- `buyer_id` values are unique
- `score_total` is numeric and within the allowed range
- `priority_tier` is one of `A`, `B`, `C`, or `Hold`
- `approval_block` is `true` or `false`
- `approval_block=true` when `proposal_brand_check=approval_required_review`
- `approval_block=true` when `interested_brands` includes `메디큐브` without explicit approval
- rows with `moq_fit=no` include MOQ-related negative factor or risk flag
- rows with `moq_fit=unknown` include MOQ confirmation in risk flags or recommended next action
- payment risk is treated as a manual indicator, not verified credit data
- Korean and Chinese text is preserved
- sample output does not introduce real personal data
- no external data collection behavior or language is introduced
- approval-required brands are not recommended externally

## 17. Completion Criteria

Task 007 is complete only when:

- buyer scoring automation specification exists
- buyer scoring schema exists
- scoring rules and weight table exist
- scoring script exists and reads only local buyer lead CSV files
- `data/buyers_scored_sample.csv` is generated from `data/buyers_master_sample.csv`
- validation script for scored buyer leads exists and passes
- XLSX generation decision or implementation is documented
- workflow README is updated
- roadmap and task log are updated
- final review confirms no scraping, live research, automatic search, APIs, browser automation, crawlers, requests, buyer enrichment, credit checks, or external data collection were added

