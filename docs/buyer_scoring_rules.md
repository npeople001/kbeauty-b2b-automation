# Buyer Scoring Rules and Weight Table

## 1. Scope

This document defines the scoring logic, weights, risk flags, approval block behavior, and tier assignment rules for Task 007: Buyer Scoring Automation.

Buyer scoring is for internal sales prioritization only.

This scoring does not:

- verify buyer authenticity
- verify creditworthiness
- guarantee purchase probability
- verify payment reliability
- collect buyer data from external sources
- enrich buyer data from external sources
- scrape, crawl, search, or call APIs
- use browser automation, requests, crawlers, live web research, or automatic web search

Scores must be calculated only from local buyer master data, such as `data/buyers_master_sample.csv` or a future local `data/buyers_master.csv`.

## 2. Score Range

| Rule | Requirement |
|---|---|
| Base score | Start at `50`. |
| Score range | Final `score_total` must be between `0` and `100`. |
| Data basis | Add or subtract points based only on local buyer master data. |
| Clamp rule | If the calculated score is below `0`, set it to `0`. If it is above `100`, set it to `100`. |

The score must not be described as guaranteed order volume, buyer authenticity, creditworthiness, financial reliability, or purchase probability.

## 3. Recommended Weight Table

### A. MOQ Fit

| Input value | Points | Risk flag | Notes |
|---|---:|---|---|
| `yes` | `+20` |  | Buyer appears to meet the general MOQ 100+ rule. |
| `no` | `-30` | `moq_not_met` | Strong negative factor. Buyer may need quantity increase or category bundling. |
| `unknown` | `-10` | `moq_unknown` | Quantity must be confirmed before relying on the score. |

### B. Estimated Order Quantity

| Input condition | Points | Risk flag | Notes |
|---|---:|---|---|
| `estimated_order_qty >= 500` | `+10` |  | High estimated quantity, but not guaranteed order volume. |
| `estimated_order_qty` from `100` to `499` | `+5` |  | Meets the usual MOQ threshold. |
| `estimated_order_qty` from `1` to `99` | `-10` |  | Below the usual MOQ threshold. |
| Blank, `unknown`, `0`, or non-numeric | `0` | `quantity_unconfirmed` | Quantity must be confirmed manually. |

Estimated order quantity is a manually provided planning field. It must not be described as confirmed purchase order volume.

### C. Country Priority

| Input value | Points | Risk flag | Notes |
|---|---:|---|---|
| `China` | `+15` |  | Current priority market. |
| Southeast Asia country | `+8` |  | Examples: `Vietnam`, `Thailand`, `Indonesia`, `Malaysia`, `Philippines`, `Singapore`. |
| `Russia` | `+8` |  | Current active market. |
| Other country | `+3` |  | Neutral positive for overseas buyer workflow. |
| Unknown or blank | `-5` | `country_unknown` | Country must be confirmed. |

Country priority does not verify buyer quality or market feasibility.

### D. China Relevance

| Input value | Points | Risk flag | Notes |
|---|---:|---|---|
| `high` | `+10` | `china_platform_operation_unverified` when China workflow fields are used | Strong China workflow relevance. |
| `medium` | `+5` |  | Some China relevance. |
| `low` | `0` |  | No score change. |
| `unknown` | `-2` |  | China relevance is unclear. |

China relevance is a manual workflow indicator. It does not verify China platform operation, account restrictions, real-name requirements, or buyer quality.

### E. Buyer Type

| Input value | Points | Risk flag | Notes |
|---|---:|---|---|
| `importer` | `+12` |  | Strong B2B export fit. |
| `distributor` | `+12` |  | Strong B2B export fit. |
| `wholesaler` | `+10` |  | Strong MOQ-oriented fit. |
| `beauty_chain` | `+10` |  | Useful retail/channel fit. |
| `trading_company` | `+6` |  | Potential B2B fit. |
| `online_seller` | `+5` |  | Useful if MOQ and payment risk are acceptable. |
| `live_commerce` | `+5` |  | Useful if MOQ and platform plan are clear. |
| `influencer_commerce` | `+3` |  | Lower B2B confidence unless order quantity is strong. |
| `retailer` | `+4` |  | Evaluate by MOQ and repeat potential. |
| `unknown` | `-5` | `buyer_type_unknown` | Buyer type must be clarified. |
| `other` | `0` |  | No score change. |

Buyer type is manually provided and must not be externally verified by this automation.

### F. Sales Channel

| Input value | Points |
|---|---:|
| `distributor_network` | `+10` |
| `b2b_platform` | `+8` |
| `mixed` | `+6` |
| `marketplace` | `+5` |
| `offline` | `+5` |
| `online` | `+4` |
| `social_commerce` | `+4` |
| `live_commerce` | `+4` |
| `unknown` | `-3` |
| `other` | `0` |

Sales channel is used for internal follow-up planning only. It does not imply verified sales performance.

### G. Platform

| Input value | Points | Notes |
|---|---:|---|
| `WeChat` | `+8` | Strong China workflow relevance when the lead is China-related. |
| `Douyin` | `+6` | China content/commerce workflow relevance. |
| `Xiaohongshu` | `+6` | China discovery/content workflow relevance. |
| `1688` | `+6` | China B2B platform workflow relevance. |
| `Taobao` | `+5` | China marketplace workflow relevance. |
| `TikTok` | `+4` | Useful for Southeast Asia/global social commerce. |
| `Instagram` | `+3` | Useful for content-led buyer review. |
| `Shopee` | `+5` | Useful for Southeast Asia marketplace workflows. |
| `Lazada` | `+5` | Useful for Southeast Asia marketplace workflows. |
| `Amazon` | `+4` | Useful for global marketplace workflows. |
| `Telegram` | `+3` | Useful for Russia/CIS workflow context. |
| `VK` | `+3` | Useful for Russia workflow context. |
| `offline` | `+2` | Offline workflow indicator. |
| `website` | `+2` | Basic operational context. |
| `unknown` | `-2` | Platform is unclear. |
| `other` | `0` | No score change. |

Platform scoring must not trigger automatic platform collection, account checking, crawling, or external verification.

### H. Payment Risk

| Input value | Points | Risk flag | Notes |
|---|---:|---|---|
| `low` | `+8` |  | Manual low-risk indicator. |
| `medium` | `-5` | `payment_risk_medium` | Requires caution and payment terms review. |
| `high` | `-20` | `payment_risk_high` | Strong negative factor; cannot be tier `A`. |
| `unknown` | `-3` | `payment_risk_unknown` | Payment risk must be reviewed manually. |

Payment risk is a manual indicator only. It is not credit verification.

### I. Repeat Purchase Potential

| Input value | Points | Notes |
|---|---:|---|
| `high` | `+10` | Strong positive internal estimate. |
| `medium` | `+5` | Moderate positive internal estimate. |
| `low` | `-5` | Lower repeat potential. |
| `unknown` | `0` | Do not overinterpret missing evidence. |

Repeat purchase potential is an internal estimate and must not be described as guaranteed repeat order likelihood.

### J. Lead Status

| Input value | Points | Risk flag | Tier note |
|---|---:|---|---|
| `new` | `0` |  | Default starting status. |
| `researching` | `+2` |  | Some review has started. |
| `contacted` | `+5` |  | Follow-up is active. |
| `replied` | `+10` |  | Buyer engagement exists in local records. |
| `qualified` | `+15` |  | Strong internal pipeline status. |
| `sample_requested` | `+15` |  | Strong internal pipeline status. |
| `quotation_sent` | `+12` |  | Proposal workflow has started. |
| `negotiating` | `+15` |  | Strong internal pipeline status. |
| `won` | `+5` |  | Existing success; review for repeat workflow rather than new lead priority. |
| `lost` | `-30` |  | Tier should normally be `C` or `Hold`. |
| `on_hold` | `-15` | `on_hold` | Tier should usually be capped or held. |
| `disqualified` | `-40` |  | Tier must be `Hold`. |

Lead status must be taken from local buyer master data only.

### K. Approval Warning / Proposal Brand Check

| Condition | Score effect | Approval effect | Risk flag |
|---|---:|---|---|
| `approval_warning` is not blank | `0` | Review required | `approval_required_brand` |
| `proposal_brand_check=approval_required_review` | `0` | `approval_block=true` | `approval_required_brand` |
| `interested_brands` includes `메디큐브` without explicit approval | `0` | `approval_block=true` | `approval_required_brand` |

`approval_block=true` must not automatically reduce `score_total` to zero. A buyer may still be commercially interesting, but external action for the approval-required brand must be blocked.

By default, `approval_block=true` should force `priority_tier=Hold` unless the recommended next action is strictly internal approval review.

`메디큐브` must always trigger `approval_block=true` unless explicit approval is recorded.

### L. Contact Completeness

| Condition | Points | Risk flag | Notes |
|---|---:|---|---|
| `contact_email` present | `+2` |  | Operational readiness only. |
| `wechat_id` present for China buyer | `+5` | `privacy_sensitive_contact` | Useful for China workflow but privacy-sensitive. |
| `whatsapp` present | `+2` | `privacy_sensitive_contact` | Operational readiness only. |
| All contact fields blank | `-10` | `contact_incomplete` | Follow-up readiness is weak. |

Contact completeness is operational readiness only, not buyer quality. Contact fields must not be copied into scored output unless necessary.

### M. Next Action Readiness

| Condition | Points | Risk flag | Notes |
|---|---:|---|---|
| `next_action` not blank | `+5` |  | Clear follow-up action improves operational readiness. |
| `next_action` blank | `-5` | `next_action_missing` | Follow-up path must be defined. |

## 4. Priority Tier Rules

Assign `priority_tier` after calculating and clamping `score_total`.

### Default Score-Based Tier

| Score range | Default tier |
|---|---|
| `score_total >= 80` | `A` |
| `score_total` from `60` to `79` | `B` |
| `score_total` from `40` to `59` | `C` |
| `score_total < 40` | `Hold` |

### Override Rules

| Condition | Required override |
|---|---|
| `approval_block=true` | `Hold`, unless `recommended_next_action` is strictly internal approval review only. |
| `lead_status=disqualified` | `Hold`. |
| `lead_status=lost` | `C` or `Hold` depending on context. |
| `payment_risk=high` | Cannot be `A`. Cap at `B` or lower. |
| `moq_fit=no` | Cannot be `A`. Cap at `B` or lower. |
| Missing `company_name` or `country` | `Hold`. |
| Missing `buyer_id` | Invalid record; do not score. |

Overrides are safety controls. They do not prove that a buyer is bad; they show that the row is not ready for normal high-priority follow-up.

## 5. Risk Flags

Allowed risk flags:

- `moq_not_met`
- `moq_unknown`
- `quantity_unconfirmed`
- `country_unknown`
- `buyer_type_unknown`
- `payment_risk_medium`
- `payment_risk_high`
- `payment_risk_unknown`
- `approval_required_brand`
- `contact_incomplete`
- `next_action_missing`
- `on_hold`
- `buyer_unverified`
- `source_manual_only`
- `privacy_sensitive_contact`
- `china_platform_operation_unverified`

Rules:

- `source_manual_only` should be included because buyer data is manually provided.
- `buyer_unverified` should be included unless a future local field explicitly records manual verification.
- `china_platform_operation_unverified` should be included for China platform workflows where platform/account operation is not verified.
- Risk flags must be based on local input data only.

## 6. Approval Block Behavior

`approval_block=true` means external action must not proceed for the approval-required brand.

Blocked external actions include:

- external proposal
- buyer-facing pitch
- public content
- ad copy
- quotation

`approval_block=true` does not mean the buyer is bad. It means internal approval is required before external action.

The `recommended_next_action` should state that internal approval check is required before any proposal, quotation, public content, ad copy, or buyer-facing pitch involving the approval-required brand.

## 7. Recommended Next Action Rules

Recommended next action should be generated from:

- `priority_tier`
- `moq_fit`
- `approval_block`
- `lead_status`
- `payment_risk`
- existing `next_action`

Examples:

| Scenario | Recommended next action direction |
|---|---|
| `A` without approval block | Prepare proposal or quotation review based on approved brands only. |
| `B` | Confirm missing details and prepare follow-up. |
| `C` | Keep as low-priority follow-up or nurture lead. |
| `Hold` with approval block | Perform internal brand approval review first. |
| `Hold` with MOQ issue | Confirm whether buyer can meet MOQ 100+. |
| `Hold` with payment risk | Require safer payment terms or management review. |

The recommended next action must be practical and written in Korean.

## 8. Output Text Rules

- `scoring_summary` must be in Korean.
- `positive_factors`, `negative_factors`, and `risk_flags` can use semicolon-separated values.
- `recommended_next_action` must be practical and in Korean.
- Do not state that the score proves buyer authenticity, creditworthiness, financial reliability, or purchase certainty.
- Do not introduce new facts that are not present in local buyer master data.
- Do not copy personal contact fields into scored output unless necessary for an internal workflow.
- Korean, English, and Chinese text must be preserved.

## 9. Validation Requirements

Future scoring output must be validated for:

- `score_total` is numeric and between `0` and `100`.
- `priority_tier` is one of `A`, `B`, `C`, or `Hold`.
- `approval_block=true` when `proposal_brand_check=approval_required_review`.
- `approval_block=true` when `interested_brands` includes `메디큐브` without explicit approval.
- `risk_flags` include `moq_not_met` or `moq_unknown` where applicable.
- `risk_flags` include `source_manual_only` because buyer data is manually provided.
- `recommended_next_action` is not blank.
- `scoring_summary` is not blank.
- Korean and Chinese text is preserved.
- No personal contact fields are unnecessarily copied into scoring output.
- No scraping, live web research, automatic web search, browser automation, APIs, requests, crawlers, buyer enrichment, credit checks, or external data collection is implied.

## Step C Scope

This rules document does not create or modify code, CSV files, XLSX files, generated outputs, scraping workflows, live web research workflows, automatic web search, browser automation, APIs, requests, crawlers, buyer enrichment, credit checks, or external data collection.

