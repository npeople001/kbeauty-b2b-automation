# Buyer Scoring Automation

## Purpose

This automation scores manually provided buyer leads for internal sales prioritization.

The score helps the team decide which existing buyer lead rows should be reviewed or followed up first. It is not buyer verification, credit verification, payment ability verification, or purchase probability prediction.

This automation does not scrape, search, crawl, enrich, verify, or automatically collect buyer data. It does not perform live web research, automatic web search, browser automation, API calls, requests, crawlers, buyer enrichment, credit checks, or external data collection.

## Input Files

- `data/buyers_master_sample.csv`: default local buyer master sample input.
- `data/buyers_master.csv`: optional future real buyer master input for internal use.
- `data/brands_master.csv`: optional local brand approval reference.

Real buyer lead data should be manually provided and handled as internal-use business data.

## Output Files

- `data/buyers_scored_sample.csv`: scored buyer lead CSV for internal priority review.
- `output/buyers_scored_sample.xlsx`: business-facing XLSX review workbook.
- `output/buyers_scored_sample_YYYYMMDD_HHMMSS.xlsx`: timestamped fallback output if the XLSX file is locked or cannot be overwritten.

The scored CSV uses UTF-8 with BOM, `utf-8-sig`, for Excel compatibility. XLSX output is preferred for business review when Korean, English, or Chinese text is included.

## Schema and Rules References

- `docs/buyer_scoring_automation_spec.md`
- `docs/buyer_scoring_schema.md`
- `docs/buyer_scoring_rules.md`
- `docs/buyer_lead_schema.md`

## Scoring Command

Default:

```powershell
python automations/buyer_scoring/generate_buyer_scores.py
```

Optional arguments:

```powershell
python automations/buyer_scoring/generate_buyer_scores.py --input data/buyers_master_sample.csv --output data/buyers_scored_sample.csv --brands data/brands_master.csv
```

## Validation Command

```powershell
python tests/validate_buyer_scores.py --input data/buyers_master_sample.csv --scored data/buyers_scored_sample.csv
```

## XLSX Generation Command

Default:

```powershell
python automations/buyer_scoring/generate_buyer_scores_xlsx.py
```

Optional arguments:

```powershell
python automations/buyer_scoring/generate_buyer_scores_xlsx.py --input data/buyers_scored_sample.csv --output output/buyers_scored_sample.xlsx
```

## Standard Workflow

1. Prepare or update buyer master CSV manually.
2. Validate buyer lead data.
3. Generate buyer scores.
4. Validate scored buyer data.
5. Generate XLSX review file.
6. Review score, tier, risk flags, and approval block internally.
7. Decide follow-up action.
8. Do not use approval-required brands externally without explicit approval.

## Score Interpretation Rules

- `score_total` is 0-100.
- `A` = high internal follow-up priority.
- `B` = medium internal follow-up priority.
- `C` = low internal follow-up priority.
- `Hold` = do not prioritize until the issue is resolved.
- Score is only an internal prioritization signal.
- Score does not prove buyer authenticity, creditworthiness, payment ability, financial reliability, purchase intent, or purchase certainty.

## Major Scoring Factors

- MOQ fit
- estimated order quantity
- country priority
- China relevance
- buyer type
- sales channel
- platform
- payment risk
- repeat purchase potential
- lead status
- approval warning
- proposal brand check
- contact completeness
- next action readiness

All scoring factors must come from local buyer master data and local brand approval reference data only.

## MOQ Rules

MOQ is generally 100+ units.

- `moq_fit=yes` increases score.
- `moq_fit=no` lowers score and prevents `A` tier.
- `moq_fit=unknown` adds risk and requires quantity confirmation.
- `estimated_order_qty` must not be treated as guaranteed order volume.

The scoring automation must not silently change source buyer master CSV values.

## Brand Approval Rules

메디큐브 is approval-required.

- If `proposal_brand_check=approval_required_review`, `approval_block=true`.
- If `interested_brands` includes 메디큐브, `approval_block=true` unless explicit approval is recorded.
- If a local brand master row indicates `approval_required=true` or `proposal_allowed=false`, external proposal readiness must be blocked for that brand.
- `approval_block=true` does not mean the buyer is bad.
- `approval_block=true` means external proposal, buyer-facing pitch, quotation, public content, or ad copy must not proceed for the approval-required brand.
- Internal approval review is required before external action.

A high score must never override approval-required brand restrictions.

## Payment and Buyer Authenticity Limitations

- `payment_risk` is manually entered and is not credit verification.
- `buyer_unverified` and `source_manual_only` are expected risk flags.
- This automation does not verify whether a buyer is real.
- This automation does not verify financial reliability, payment ability, purchase authority, purchase intent, or purchase certainty.

## Privacy and Contact Handling

- Scored output should not include unnecessary contact fields.
- Contact completeness is only operational readiness.
- Real buyer contact data should remain internal-use only.
- Do not share buyer contact data externally without permission, masking, or review.
- Public outputs must not expose personal contact data.

## China Buyer Workflow

- China priority and `china_relevance` are internal strategy signals.
- WeChat, Douyin, Xiaohongshu, Taobao, and 1688 fields are manually provided only.
- This automation does not collect data from China platforms.
- China platform operation feasibility, account restrictions, real-name requirements, and buyer quality are not verified by scoring.

## Excel and Encoding Rules

- CSV files for business users use UTF-8 with BOM, `utf-8-sig`.
- XLSX is preferred for business review.
- Korean, English, and Chinese text must be preserved.
- If XLSX output is locked, a timestamped fallback should be generated.
- Source CSV files must not be modified to resolve output permission issues.

## Known Limitations

- No automatic buyer discovery.
- No external enrichment.
- No credit check.
- No payment verification.
- No platform account verification.
- No guarantee of purchase probability.
- No verification that a buyer is real.
- Task 008 Proposal Message Generator should use `approval_block` and `risk_flags` before generating external messages.
