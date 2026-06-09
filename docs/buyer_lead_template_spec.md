# Buyer Lead Template Specification

## Purpose

This document defines how buyer lead data should be structured, validated, protected, and converted into business-facing CSV/XLSX templates for K-beauty B2B export sales.

Task 006 supports manual overseas buyer lead management for markets such as China, Southeast Asia, Russia, and later global buyers. It is intended to help the business organize buyer candidates, check MOQ fit, protect contact information, respect brand approval restrictions, and prepare internal follow-up workflows.

## 1. Scope

### What Task 006 Does

- Defines a standardized buyer lead template for manually provided buyer lead data.
- Defines the buyer lead schema and required fields.
- Defines validation rules for raw and master buyer lead files.
- Defines how buyer lead data should be converted into business-facing CSV/XLSX outputs.
- Supports K-beauty B2B export sales workflows, including China buyer channel development.
- Supports MOQ 100+ logic, lead status tracking, priority handling, next-action workflow, and contact/privacy handling.
- Uses `data/brands_master.csv` as the brand approval reference where available.
- Preserves Korean, English, and Chinese text in CSV/XLSX outputs.

### What Task 006 Does Not Do

- Does not perform buyer scraping.
- Does not perform live web research.
- Does not perform automatic web search.
- Does not call APIs.
- Does not use browser automation.
- Does not use `requests`.
- Does not use crawlers.
- Does not collect external data automatically.
- Does not find buyer leads automatically from Xiaohongshu, Douyin, WeChat, Taobao, 1688, websites, social media, trade platforms, or any other external platform.
- Does not send messages to buyers.
- Does not score buyer leads beyond simple template validation.
- Does not recommend approval-required brands for external proposal, public content, buyer-facing pitch, or quotation.

Task 006 only creates templates, schema, validation rules, and business-facing outputs for manually provided buyer lead data.

## 2. Existing File Handling

- `docs/buyer_lead_schema.md` already exists and may be updated in Step B.
- `data/buyers_raw.csv` already exists as an early draft and should not be silently overwritten.
- Existing data files must not be overwritten without explicit confirmation.
- Future sample files should use clear names that do not replace existing business data:
  - `data/buyers_raw_sample.csv`
  - `data/buyers_master_sample.csv`
- Scripts may read existing files for validation or transformation, but must not silently alter source data.
- If a future output file is locked or cannot be overwritten, the automation should create a timestamped fallback output and report the actual path generated.

## 3. Input Files

### Recommended Input

| Input | Required | Format | Notes |
|---|---|---|---|
| `data/buyers_raw_sample.csv` | Required for Task 006 sample workflow | CSV, `utf-8-sig` | Sample raw buyer lead input. Must contain fictional or placeholder contacts only. |

### Optional Future Inputs

| Input | Required | Format | Notes |
|---|---|---|---|
| `data/buyers_raw.csv` | Optional future business input | CSV, `utf-8-sig` | Existing early draft. Must not be overwritten without explicit confirmation. |
| Manually provided buyer lists | Optional | CSV/XLSX/Markdown/text | Must be provided by the user or team. |
| Manually collected contact notes | Optional | Markdown/text/CSV | Internal-use only when contact data is included. |
| Internal sales notes | Optional | Markdown/text/CSV | May support next action and lead status fields. |

All input data must be manually provided by the user or team. No automatic external data collection is allowed.

## 4. Output Files

### Recommended Outputs

| Output | Format | Language | Notes |
|---|---|---|---|
| `data/buyers_master_sample.csv` | CSV, `utf-8-sig` | Korean, English, Chinese supported | Normalized sample master lead file derived from sample raw input. |
| `output/buyers_master_sample.xlsx` | XLSX | Korean, English, Chinese supported | Business-facing workbook for review and internal use. |

### Optional Future Outputs

| Output | Format | Notes |
|---|---|---|
| `output/buyer_lead_review_{date}.xlsx` | XLSX | Review workbook for a dated buyer lead review. |
| `output/buyer_follow_up_plan_{date}.md` | Markdown, UTF-8 | Internal follow-up plan; must not expose personal contact data publicly. |

Generated outputs are internal planning and sales-operation documents unless reviewed for privacy, brand approval, and external sharing suitability.

## 5. Required Buyer Lead Fields

| Field | Intended purpose |
|---|---|
| `buyer_id` | Stable internal identifier for one buyer lead. Used for deduplication, update tracking, validation, and follow-up references. |
| `company_name` | Buyer company, store, distributor, importer, or seller name. Required for active lead management. |
| `country` | Buyer country or primary market. Supports market prioritization such as China, Southeast Asia, Russia, and global buyers. |
| `city` | Buyer city or operating location. Useful for regional follow-up and logistics context. |
| `buyer_type` | Type of buyer, such as distributor, importer, wholesaler, marketplace seller, online store, offline store, live commerce seller, or other. |
| `sales_channel` | Main channel where the buyer sells, sources, or communicates, such as WeChat, Douyin, Xiaohongshu, Taobao, 1688, website, SNS, trade show, referral, distributor, importer, or wholesaler. |
| `platform` | Specific platform, marketplace, or account/channel name if manually provided. |
| `website` | Buyer website URL if manually provided. |
| `sns_url` | Social media or platform profile URL if manually provided. |
| `contact_name` | Main contact person's name. Privacy-sensitive and optional. |
| `contact_email` | Main contact email. Privacy-sensitive and optional. |
| `contact_phone` | Main phone number. Privacy-sensitive and optional. |
| `wechat_id` | WeChat contact ID for China-related leads. Privacy-sensitive and optional. |
| `whatsapp` | WhatsApp contact number or ID. Privacy-sensitive and optional. |
| `language` | Preferred communication language, such as Korean, English, Chinese, Russian, Thai, Vietnamese, Indonesian, multi, other, or unknown. |
| `interested_brands` | Brands the buyer has asked about or may be interested in. May include approval-required brands as buyer interest only, not as external proposal approval. |
| `interested_categories` | Product categories of interest, such as skincare, toner, serum, sunscreen, makeup, cleansing, derma, premium skincare, health, or unknown. |
| `estimated_order_qty` | Estimated order quantity in units. Used to validate MOQ fit. |
| `moq_fit` | Whether the buyer appears to meet the usual MOQ of 100+ units. Must be validated against `estimated_order_qty`. |
| `china_relevance` | Relevance to China buyer channel development. Useful for prioritizing China-focused workflow. |
| `payment_risk` | Initial internal assessment of payment or transaction risk. Must not be treated as a final credit decision. |
| `repeat_purchase_potential` | Initial internal estimate of repeat purchase potential. Used for prioritization before full buyer scoring automation. |
| `lead_source` | Where the lead came from, such as manual, referral, trade show, website, SNS, China channel research notes, internal note, other, or unknown. |
| `lead_status` | Current workflow status, such as new, researching, contacted, qualified, proposal_ready, proposal_sent, negotiating, closed_won, closed_lost, inactive, or unknown. |
| `priority` | Internal handling priority before detailed buyer scoring automation exists. |
| `next_action` | Next manual follow-up action, such as verify contact, confirm MOQ, request product interests, check approval-required brands, prepare catalog, or send internal review. |
| `notes` | Internal notes, context, cautions, source context, contact verification notes, or follow-up details. |
| `created_at` | Date the lead was created, using ISO date format `YYYY-MM-DD` when available. |
| `updated_at` | Date the lead was last updated, using ISO date format `YYYY-MM-DD` when available. |

## 6. Privacy and Contact Handling Rules

- Contact fields are privacy-sensitive.
- Privacy-sensitive fields include `contact_name`, `contact_email`, `contact_phone`, `wechat_id`, `whatsapp`, and any personal notes in `notes`.
- Sample files must not contain real personal data.
- Sample files must use placeholder or fictional contacts only.
- Real buyer contact data should be handled as internal-use data.
- External sharing should require masking, permission, or explicit review.
- Do not expose personal contact data in public outputs.
- Business-facing XLSX files should be treated as internal documents when they include contact fields.
- Future public or external outputs should remove or mask contact fields unless explicitly approved.

## 7. MOQ Logic

- Minimum order quantity is generally 100+ units.
- `estimated_order_qty >= 100` means `moq_fit` should be `yes`.
- `estimated_order_qty` between `1` and `99` means `moq_fit` should be `no`.
- Blank, unknown, `0`, or non-numeric `estimated_order_qty` means `moq_fit` should be `unknown`.
- `moq_fit` must be validated against `estimated_order_qty`.
- Buyer type is flexible if the buyer can order 100+ units.
- If `estimated_order_qty` is unknown but the buyer type appears promising, the next action should ask the team to confirm MOQ fit manually.

## 8. Brand Approval Rules

- Use `data/brands_master.csv` as the brand approval reference where available.
- If `interested_brands` includes brands with `approval_required=true` or `proposal_allowed=false`, the buyer record must show an approval warning.
- `메디큐브` must remain approval-required unless explicit approval is provided.
- Approval-required brands may be recorded as buyer interest.
- Approval-required brands must not be automatically recommended for:
  - external proposal
  - public content
  - buyer-facing pitch
  - quotation
  - advertising copy
  - social media posting
  - sales follow-up materials
  unless explicit approval is provided.
- Brand approval warnings must not be silently removed.
- Validation should flag approval-required brands without changing brand master data.
- Scripts must not change `approval_required`, `proposal_allowed`, approval notes, or brand names without explicit instruction.

## 9. China Buyer Workflow Support

Task 006 supports China buyer workflows through these fields:

- `wechat_id`
- `platform`
- `sales_channel`
- `china_relevance`
- `language`
- `lead_source`
- `next_action`

Rules:

- China fields support manual lead management only.
- No automatic collection from Xiaohongshu, Douyin, WeChat, Taobao, 1688, websites, SNS, marketplaces, or other platforms is allowed.
- China buyer records should include account/contact verification notes where needed.
- `wechat_id` and other contact identifiers are privacy-sensitive.
- `china_relevance` should help prioritize manual review, not imply confirmed buyer quality.
- China platform/account rules and local communication expectations may change and should be checked before external use.

## 10. Encoding and Excel Compatibility

- Business-facing CSV files must use UTF-8 with BOM, `utf-8-sig`.
- Scripts must read CSV files with an encoding compatible with `utf-8-sig`.
- XLSX should be preferred for business users when Korean, English, or Chinese text is included.
- Korean, English, and Chinese text must be preserved.
- XLSX generation should include safe fallback if the target file is locked.
- If an XLSX target file cannot be overwritten, create a timestamped fallback output and clearly report the actual output path.
- Do not modify source CSV files to resolve output permission issues.
- Do not report encoding-related work as complete until Korean and Chinese text are verified in the generated output.

## 11. Validation Requirements

Buyer lead data must be validated for:

- Required columns exist.
- `buyer_id` is unique when populated.
- Required fields such as `buyer_id`, `company_name`, `country`, and `lead_status` are present where required.
- `estimated_order_qty` is numeric or blank.
- `moq_fit` is consistent with `estimated_order_qty`.
- Allowed values are used for:
  - `buyer_type`
  - `sales_channel`
  - `platform` where normalized values are used
  - `language`
  - `moq_fit`
  - `china_relevance`
  - `payment_risk`
  - `repeat_purchase_potential`
  - `lead_status`
  - `priority`
- Basic email, URL, and contact format checks are performed where applicable.
- Approval warning appears if `interested_brands` includes approval-required or proposal-blocked brands.
- `메디큐브` is treated as approval-required unless explicit approval is provided.
- Korean and Chinese text are preserved.
- Sample files do not contain real personal data.
- Source row count is preserved during validation or transformation unless a task explicitly asks to add or remove records.
- Validation must not silently alter source data.

## 12. Completion Criteria

Task 006 is complete only when:

- Buyer lead template specification exists.
- Buyer lead schema is updated.
- `data/buyers_raw_sample.csv` exists.
- `data/buyers_master_sample.csv` exists.
- Validation script exists and passes.
- XLSX generation script exists and generates a business-facing XLSX file.
- Workflow README exists.
- Roadmap and task log are updated.
- Final review passes.

Step A is complete when `docs/buyer_lead_template_spec.md` exists and no code, CSV, XLSX, scraping, live research, automatic search, browser automation, API use, `requests`, crawler, or external data collection has been added.
