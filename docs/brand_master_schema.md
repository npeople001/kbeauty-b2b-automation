# Brand Master Schema

This document defines the schema for `data/brands_master.csv`.

All text must be stored and read as UTF-8 to support Korean, English, and Chinese.

## Business Rules

- `approval_required` must be `true` for `메디큐브`.
- `proposal_allowed` must be `false` when `approval_required` is `true`, unless explicit approval is recorded.
- Unknown official English brand names must not be guessed. Leave `brand_en` blank if uncertain.
- Categories should separate cosmetics and health products.
- Priority fields must use `high`, `medium`, `low`, or `unknown`.

## Columns

| Column | Meaning | Required | Allowed values or format | Default value | Example |
| --- | --- | --- | --- | --- | --- |
| `brand_ko` | Korean brand name used as the primary brand identifier. | Required | UTF-8 text; must not be blank. | None | `메디큐브` |
| `brand_en` | Official English brand name, if known. | Optional | UTF-8 text; leave blank if the official English name is uncertain. | Blank | `CLIO` |
| `category` | Main business category for the brand or product line. | Required | `cosmetics`, `health_products`, or `unknown`. | `unknown` | `cosmetics` |
| `sub_category` | More specific category, such as skincare, makeup, cleansing, supplement, or other business-relevant grouping. | Optional | UTF-8 text; use a concise category label or blank if unknown. | Blank | `skincare` |
| `approval_required` | Whether the brand requires internal approval before external posting or proposal. | Required | Boolean text: `true` or `false`. | `false` | `true` |
| `approval_note` | Approval condition, approver, or reason. | Optional | UTF-8 text; required when `approval_required` is `true`. | Blank | `Requires director approval before external posting/proposal.` |
| `china_priority` | Priority for China buyer channel development. | Required | `high`, `medium`, `low`, or `unknown`. | `unknown` | `high` |
| `global_priority` | Priority for Southeast Asia, Russia, and later global buyer development. | Required | `high`, `medium`, `low`, or `unknown`. | `unknown` | `medium` |
| `proposal_allowed` | Whether the brand can be included in external proposal outputs by default. | Required | Boolean text: `true` or `false`; must be `false` when `approval_required` is `true` unless explicitly approved. | `true` unless `approval_required` is `true`; then `false`. | `false` |
| `notes` | Internal notes for sourcing, buyer fit, category uncertainty, or later review. | Optional | UTF-8 text. | Blank | `Confirm official English name before buyer-facing use.` |
