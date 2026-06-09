# Buyer Lead Schema

## Purpose

This schema defines the standardized buyer lead data structure for managing overseas buyer candidates for a K-beauty B2B export business.

The schema is for manual lead management, CSV/XLSX templates, and future validation rules. It does not implement scraping, live web research, automatic web search, APIs, browser automation, crawlers, or external data collection.

## Required Fields

The following fields are required for every buyer lead record:

- `buyer_id`
- `company_name`
- `country`
- `lead_status`
- `created_at`

All other fields are recommended optional fields, including `updated_at`.

## Field Definitions

| Field | Meaning | Required | Format | Allowed values | Example | Notes |
|---|---|---:|---|---|---|---|
| `buyer_id` | Unique identifier for the buyer lead. | Required | Text ID, preferably `BUYER-0001` style. | Unique value per record. | `BUYER-0001` | Must not be reused. Future validation should check uniqueness. |
| `company_name` | Buyer company or store name. | Required | UTF-8 text. | Free text. | `Shanghai Beauty Trading Co.` | Samples must use fictional or placeholder company names only. |
| `country` | Buyer country or target market. | Required | UTF-8 text. | Free text; prefer consistent English country names. | `China` | Priority markets include China, Southeast Asia, and Russia. |
| `city` | Buyer city or operating location. | Optional | UTF-8 text or blank. | Free text. | `Shanghai` | Leave blank if unknown. |
| `buyer_type` | Type of buyer or business model. | Optional | Lowercase controlled value. | `importer`, `distributor`, `wholesaler`, `retailer`, `online_seller`, `live_commerce`, `influencer_commerce`, `beauty_chain`, `trading_company`, `unknown`, `other` | `distributor` | Use `unknown` if the buyer type is not confirmed. |
| `sales_channel` | Main sales or distribution channel used by the buyer. | Optional | Lowercase controlled value. | `offline`, `online`, `marketplace`, `social_commerce`, `live_commerce`, `b2b_platform`, `distributor_network`, `mixed`, `unknown`, `other` | `marketplace` | Use one primary value. Add details in `notes` if multiple channels apply. |
| `platform` | Main platform or channel related to the buyer. | Optional | Controlled platform value. | `Xiaohongshu`, `Douyin`, `WeChat`, `Taobao`, `1688`, `TikTok`, `Instagram`, `Shopee`, `Lazada`, `Amazon`, `Telegram`, `VK`, `website`, `offline`, `unknown`, `other` | `WeChat` | For China workflows, `Xiaohongshu`, `Douyin`, `WeChat`, `Taobao`, and `1688` may be relevant. |
| `website` | Buyer company website. | Optional | URL starting with `http://` or `https://`, or blank. | Free text URL. | `https://example-buyer.invalid` | Samples must use placeholder or fictional URLs only. Do not invent real buyer websites. |
| `sns_url` | Social media or marketplace profile URL. | Optional | URL starting with `http://` or `https://`, or blank. | Free text URL. | `https://social.example/buyer` | Privacy and platform terms must be reviewed before external sharing. |
| `contact_name` | Name of the buyer contact person. | Optional | UTF-8 text or blank. | Free text. | `Sample Contact` | Privacy-sensitive. Samples must not contain real personal names. |
| `contact_email` | Buyer contact email. | Optional | Email format or blank. | Free text email. | `contact@example.invalid` | Privacy-sensitive. Use only with permission and for internal business purposes. |
| `contact_phone` | Buyer phone number. | Optional | Text or blank. | Free text. | `+86-000-0000-0000` | Privacy-sensitive. Store as text to preserve leading zeros and country codes. |
| `wechat_id` | WeChat ID for China buyer communication. | Optional | Text or blank. | Free text. | `sample_wechat_id` | Privacy-sensitive. Supports manual China buyer workflow only; do not auto-collect. |
| `whatsapp` | WhatsApp number or account. | Optional | Text or blank. | Free text. | `+84-000-000-000` | Privacy-sensitive. Store as text to preserve country codes. |
| `language` | Preferred communication language. | Optional | Controlled value. | `Korean`, `English`, `Chinese`, `Russian`, `Vietnamese`, `Thai`, `Indonesian`, `Malay`, `Arabic`, `Spanish`, `unknown`, `other` | `Chinese` | Supports localization planning and follow-up message preparation. |
| `interested_brands` | Brands requested or mentioned by the buyer. | Optional | Semicolon-separated UTF-8 text. | Free text brand names; validate against brand master where possible. | `아누아; 토리든` | Buyer-requested interest may be recorded, but approval-required brands must not be automatically recommended externally. |
| `interested_categories` | Product categories requested or relevant to the buyer. | Optional | Semicolon-separated UTF-8 text. | Free text; prefer normalized categories. | `skincare; sunscreen` | Use categories such as skincare, toner, serum, sunscreen, derma, premium skincare where relevant. |
| `estimated_order_qty` | Estimated first order quantity in units. | Optional | Integer greater than or equal to 0, or blank. | Numeric value or blank. | `120` | Used to evaluate MOQ fit. Non-numeric, blank, unknown, or 0 should be treated as unknown. |
| `moq_fit` | Whether the buyer appears to meet the general MOQ rule. | Optional | Controlled value. | `yes`, `no`, `unknown` | `yes` | Must be validated against `estimated_order_qty`. See MOQ Rules. |
| `china_relevance` | Relevance of the buyer to China market development. | Optional | Controlled value. | `high`, `medium`, `low`, `unknown` | `high` | Use with `platform`, `wechat_id`, `sales_channel`, `language`, `lead_source`, and `next_action`. |
| `payment_risk` | Estimated payment or collection risk. | Optional | Controlled value. | `high`, `medium`, `low`, `unknown` | `medium` | This is an internal assessment, not a verified credit rating unless documented. |
| `repeat_purchase_potential` | Estimated potential for repeat orders. | Optional | Controlled value. | `high`, `medium`, `low`, `unknown` | `medium` | Mark as `unknown` if there is no evidence. |
| `lead_source` | How the lead was obtained or recorded. | Optional | UTF-8 text. | Free text; recommended values include `manual`, `referral`, `trade_show`, `website`, `sns`, `internal_note`, `china_channel_research`, `unknown`, `other`. | `manual` | Must not imply automatic collection. If manually observed, record the source context in `notes`. |
| `lead_status` | Current sales pipeline status. | Required | Controlled value. | `new`, `researching`, `contacted`, `replied`, `qualified`, `sample_requested`, `quotation_sent`, `negotiating`, `won`, `lost`, `on_hold`, `disqualified` | `new` | Future validation should reject blank or unsupported statuses. |
| `priority` | Internal follow-up priority. | Optional | Controlled value. | `high`, `medium`, `low`, `unknown` | `high` | Priority should consider MOQ fit, China relevance, buyer type, and business potential. |
| `next_action` | Next manual follow-up action. | Optional | UTF-8 text. | Free text. | `Send introductory product list after approval check.` | Do not include external proposal actions for approval-required brands unless approval is confirmed. |
| `notes` | Internal notes, cautions, or context. | Optional | UTF-8 text. | Free text. | `Source materials need review before contact.` | Do not store unnecessary personal data. Include evidence limitations where relevant. |
| `created_at` | Date the lead record was created. | Required | ISO date `YYYY-MM-DD`. | Valid date. | `2026-06-08` | Required for auditability and follow-up timing. |
| `updated_at` | Date the lead record was last updated. | Optional | ISO date `YYYY-MM-DD` or blank. | Valid date or blank. | `2026-06-08` | Recommended optional field. Update when lead status or business-critical fields change. |

## MOQ Rules

The business generally targets buyers who can order 100 or more units.

- If `estimated_order_qty` is 100 or higher, `moq_fit` should be `yes`.
- If `estimated_order_qty` is between 1 and 99, `moq_fit` should be `no`.
- If `estimated_order_qty` is blank, unknown, 0, or non-numeric, `moq_fit` should be `unknown`.
- Future validation should flag records where `moq_fit` does not match `estimated_order_qty`.
- `moq_fit` is an internal screening field and should not be treated as a final sales decision by itself.

## Brand Approval Rules

Approval-required brands may be recorded as buyer interest, but they must be controlled before external use.

- `interested_brands` may include brands requested by the buyer.
- If `interested_brands` includes `메디큐브`, the record must trigger an approval warning in the master file or validation output.
- If `interested_brands` includes any brand where `approval_required` is true or `proposal_allowed` is false in `data/brands_master.csv`, the record must trigger an approval warning.
- Approval-required brands can be recorded as interest, but must not be automatically recommended for external posting, buyer-facing proposals, public content, or advertising copy.
- `메디큐브` remains approval-required unless explicit approval is provided.
- Brand approval status is business-critical data and must not be changed casually.

## Privacy and Contact Rules

Contact-related fields are privacy-sensitive:

- `contact_name`
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `website`
- `sns_url`

Rules:

- Sample files must not contain real personal data.
- Use fictional, placeholder, or clearly non-real contact data in samples.
- Real contact information is for internal business use only.
- External sharing requires masking, permission, and review.
- Do not store unnecessary personal details.
- Do not use this schema to automatically collect personal data from platforms or websites.

## China Workflow Rules

The schema supports manual China buyer workflows without automatic collection.

Relevant fields:

- `wechat_id`
- `platform`
- `sales_channel`
- `china_relevance`
- `language`
- `lead_source`
- `next_action`

China-related records should:

- Identify whether the buyer is relevant to China market development through `china_relevance`.
- Capture the main China platform only when manually provided or manually observed.
- Use `language` to plan Chinese localization and follow-up.
- Use `next_action` for manual follow-up, such as approval check, WeChat contact preparation, or buyer qualification.
- Avoid implying scraping, crawling, automated search, or automatic collection from Xiaohongshu, Douyin, WeChat, Taobao, 1688, or other platforms.

## Encoding Rules

- CSV files intended for Excel or business users must be written with UTF-8 with BOM, using `utf-8-sig`.
- Scripts that read business-facing CSV files must use an encoding compatible with `utf-8-sig`.
- XLSX is preferred for business-facing outputs when Korean, English, or Chinese text is included.
- Korean, English, and Chinese text must be preserved after CSV/XLSX generation.
- Korean brand names must be validated after CSV/XLSX generation.

## Validation Requirements

Future validation for buyer lead files should check:

- Required fields are present: `buyer_id`, `company_name`, `country`, `lead_status`, `created_at`.
- `buyer_id` values are unique and non-empty.
- Controlled fields use allowed values.
- `created_at` and `updated_at` use `YYYY-MM-DD` when present.
- `estimated_order_qty` is numeric when provided.
- `moq_fit` matches the MOQ rules.
- `interested_brands` triggers warnings for approval-required or proposal-restricted brands.
- `메디큐브` is always treated as approval-required unless explicit approval is provided.
- Contact fields are treated as privacy-sensitive.
- Sample records use fictional or placeholder contact data only.
- Korean, English, and Chinese text is preserved.

## Step B Scope

This schema update does not create or modify CSV files, XLSX files, scripts, generated reports, scraping workflows, live web research workflows, APIs, browser automation, crawlers, or external data collection.
