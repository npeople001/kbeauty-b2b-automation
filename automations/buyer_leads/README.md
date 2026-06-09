# Buyer Leads Automation

## Purpose

This automation supports manually managed overseas buyer lead data for a K-beauty B2B export business.

It creates business-facing XLSX files from structured CSV templates so the team can review buyer candidates, MOQ fit, approval warnings, privacy status, and next actions in Excel.

This automation does not scrape, search, crawl, or automatically collect buyer data. It does not perform live web research, automated web search, browser automation, API calls, requests, crawlers, or external data collection.

## Input Files

- `data/buyers_raw_sample.csv`: safe sample raw buyer lead template using fictional and placeholder data only.
- `data/buyers_master_sample.csv`: normalized sample master CSV used for validation and XLSX generation.
- `data/buyers_raw.csv`: optional future business input. This existing early draft must not be overwritten without explicit confirmation.

Real buyer data should be handled as internal-use data. Contact fields and buyer notes must be reviewed before any external sharing.

## Output Files

- `output/buyers_master_sample.xlsx`: default business-facing Excel workbook.
- `output/buyers_master_sample_YYYYMMDD_HHMMSS.xlsx`: timestamped fallback output if the default XLSX file is locked or cannot be overwritten.

The XLSX generator prints the actual output path after generation.

## Schema Reference

- `docs/buyer_lead_schema.md`
- `docs/buyer_lead_template_spec.md`

These documents define the buyer lead fields, allowed values, MOQ rules, brand approval rules, privacy handling, China workflow fields, encoding requirements, and completion criteria for Task 006.

## Validation Command

Run validation before generating or using the XLSX workbook:

```powershell
python tests/validate_buyer_leads.py --raw data/buyers_raw_sample.csv --master data/buyers_master_sample.csv
```

The validation script checks column order, row count, required fields, allowed values, MOQ consistency, placeholder contact data, Korean/Chinese text preservation, and approval-required brand warnings.

## XLSX Generation Command

Default:

```powershell
python automations/buyer_leads/generate_buyer_leads_xlsx.py
```

Optional arguments:

```powershell
python automations/buyer_leads/generate_buyer_leads_xlsx.py --input data/buyers_master_sample.csv --output output/buyers_master_sample.xlsx
```

CSV values remain normalized English values for validation consistency. The XLSX workbook is for business review in Excel.

## Standard Workflow

1. Add buyer leads manually to the raw CSV template.
2. Normalize or review the raw data into the master CSV.
3. Run validation.
4. Fix validation issues if needed.
5. Generate the XLSX workbook.
6. Review buyer leads internally.
7. Prepare follow-up actions.
8. Do not use approval-required brands in external proposals without approval.

## MOQ Rules

- MOQ is generally 100+ units.
- `estimated_order_qty >= 100` means `moq_fit=yes`.
- `estimated_order_qty` from 1 to 99 means `moq_fit=no`.
- Blank, unknown, 0, or non-numeric `estimated_order_qty` means `moq_fit=unknown`.
- `moq_fit` must be validated against `estimated_order_qty`.

## Brand Approval Rules

- `메디큐브` is approval-required.
- If `interested_brands` includes `메디큐브` or any approval-required or proposal-blocked brand, `approval_warning` must be shown.
- Approval-required brands may be recorded as buyer interest.
- Approval-required brands must not be automatically recommended for external proposal, buyer-facing pitch, public content, quotation, advertising copy, or sales follow-up materials.
- Use `proposal_brand_check=approval_required_review` when approval review is needed.

## Privacy And Contact Handling

- Contact fields are privacy-sensitive.
- Sample files must use placeholder contact data only.
- Real buyer contact data should be internal-use only.
- Do not share buyer contact data externally without permission, masking, or review.
- Public outputs must not expose personal contact data.

Privacy-sensitive fields include:

- `contact_name`
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `website`
- `sns_url`
- personal details in `notes`

## China Buyer Workflow Support

Use these fields for China buyer workflows:

- `wechat_id`
- `platform`
- `sales_channel`
- `china_relevance`
- `language`
- `lead_source`
- `next_action`

China platform information is manually entered only. There is no automatic collection from Xiaohongshu, Douyin, WeChat, Taobao, 1688, websites, social media, marketplaces, or other platforms.

## Excel And Encoding Rules

- CSV files for business users must use UTF-8 with BOM, `utf-8-sig`.
- XLSX is preferred for business review.
- Korean, English, and Chinese text must be preserved.
- If the XLSX output is locked, a timestamped fallback file should be generated.
- Source CSV files must not be modified to resolve output permission issues.

## Known Limitations

- This automation does not verify whether a buyer is real.
- This automation does not check payment risk automatically.
- This automation does not collect buyer data automatically.
- Buyer quality, payment risk, and purchase potential still require manual review.
- Task 007 Buyer Scoring Automation may add structured scoring later.

## Workbook Sheets

The generated workbook includes:

- `Buyer Leads`: the main table from `data/buyers_master_sample.csv`.
- `Review Guide`: explanations for `moq_fit`, `validation_status`, `approval_warning`, `proposal_brand_check`, and `contact_privacy_level`.

The workbook highlights inspection columns such as `moq_fit`, `validation_status`, `approval_warning`, `contact_privacy_level`, `proposal_brand_check`, `priority`, and `next_action`.
