# K-Beauty B2B Automation

Automation tools and structured data for a K-beauty B2B export business.

## Project Purpose

This repository supports sourcing Korean cosmetics and health product brands through domestic distributors and selling them to overseas buyers. The automation focus is to keep brand data structured, safe for proposal workflows, and usable by business users.

## Folder Structure

```text
automations/
  brand_master/
    generate_brands_master_xlsx.py
data/
  brands_raw.csv
  brands_master.csv
docs/
  brand_master_schema.md
output/
  brands_master.xlsx
tests/
  validate_brands_master.py
```

## Business Context

The business sources Korean brands domestically and sells to overseas buyers. Priority markets are China, Southeast Asia, Russia, and later global buyers. Buyer type is flexible when the buyer can order 100+ units.

Important operating rules:

- MOQ is generally 100+ units.
- Delivery lead time is generally 20-30 days.
- Korean, English, and Chinese text must be handled with UTF-8.

## Brand Master Automation

The brand master automation converts the raw available brand list into a structured master CSV and business-user XLSX output.

- `data/brands_raw.csv` stores the raw brand list with category and source note.
- `data/brands_master.csv` stores normalized brand records and approval controls.
- `output/brands_master.xlsx` is the business-user spreadsheet output.
- `docs/brand_master_schema.md` defines required columns, defaults, and allowed values.

## Validate Brand Data

Run the validation script before using the brand master for proposals or XLSX generation:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" tests\validate_brands_master.py
```

The validation checks required files, required columns, row counts, approval rules, Korean text preservation, blank brand names, and priority values.

## Generate XLSX Output

Run the XLSX generation script:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" automations\brand_master\generate_brands_master_xlsx.py
```

The script reads `data/brands_master.csv` and creates `output/brands_master.xlsx`. It validates required columns before generation, preserves Korean text, freezes the header row, adjusts column widths, and highlights approval inspection columns.

## Business Rules

- `메디큐브` requires director approval before external posting/proposal.
- Approval-required brands must not be `proposal_allowed` by default.
- Approval-required brands can only be included in external proposal outputs after explicit approval.
- Unknown official English brand names should not be guessed.
- Priority values should use `high`, `medium`, `low`, or `unknown`.

## Real Data & Privacy Guard

Tasks 001-009 are the first-pass internal automation foundation for brand master, market/content planning, buyer lead templates, buyer scoring, internal-review proposal drafts, and internal-review quotation drafts.

The current sample files are safe, fictitious test data. Real buyer, contact, price, stock, expiry, supplier, quotation, and approval-sensitive data must not be committed to Git. Task 010 adds policy and guardrails for real operation, but the system remains internal-review only.

### Before Using Real Data

- Confirm repository privacy and access control.
- Confirm `.gitignore` protects private folders and sensitive filename patterns.
- Do not place real data in tracked sample files.
- Use ignored/private paths for real operating data only after policy is applied.
- Do not commit buyer contact data.
- Do not commit real price, stock, expiry, or supplier terms.
- Do not commit final quotations or external-ready documents.
- Run Privacy Guard validation before commit.
- Manually review `git status` before commit.
- Keep external communication manual and separately approved.

### Privacy Guard Command

Run the Privacy Guard before committing or before introducing real operating data:

```powershell
python tests/validate_privacy_guard.py
```

Optional modes:

```powershell
python tests/validate_privacy_guard.py --root .
python tests/validate_privacy_guard.py --mode working-tree
python tests/validate_privacy_guard.py --staged-only
```

The validation checks:

- Sensitive file names and paths.
- Real/private/contact/price/stock/expiry/final quotation patterns.
- Sample contact placeholder safety.
- `메디큐브` approval-required context.
- Forbidden external collection or sending implementation.
- Required `.gitignore` protections.
- Sample files remain trackable.

### Safe Sample Data Rules

- Sample data must be fictional.
- Sample emails should use `example.invalid`.
- Sample phone numbers must be placeholders.
- Sample WeChat and WhatsApp values must be placeholders.
- Sample price, stock, and expiry values must be marked as fictional/manual sample values.
- Sample proposal and quotation outputs must remain internal-review drafts.

### Real Data Rules

The following must not be committed:

- Real buyer contact details.
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- Real buyer notes with private business context.
- Real supplier price lists.
- Real stock lists.
- Real expiry lists.
- Real supply availability.
- Real quotation inputs.
- Real quotation outputs.
- Final quotations.
- Supplier payment terms.
- Private contract terms.
- Incoterms.
- Confidential brand approval records.
- Credentials, tokens, or local config.

### External Automation Restrictions

This repository does not currently implement:

- Scraping.
- Live web research.
- Automatic search.
- APIs.
- Browser automation.
- Crawlers.
- Buyer enrichment.
- Credit checks.
- Email sending.
- Messaging automation.
- Quotation sending.
- External sending.

### Operating Principle

Internal-review outputs are not final external documents. Proposal drafts and quotation drafts require human review before external use.

Price, stock, expiry, MOQ, delivery, tax, shipping, duties, payment terms, and incoterms must be manually verified.

Approval-required brands such as `메디큐브` must not be externally proposed, quoted, or used in public content without explicit approval.

## Integrated Runner

The Integrated Runner orchestrates the existing local Task 006-010 scripts for the internal sample buyer sales workflow. It does not replace existing validators, business rules, approval rules, quotation rules, or privacy rules.

The runner is internal-review only. It does not send, scrape, collect, enrich, verify, or externally communicate. It does not implement email sending, messaging automation, quotation sending, scraping, live web research, automatic search, APIs, browser automation, crawlers, buyer enrichment, credit checks, external data collection, or external sending.

### Supported Workflow

Supported workflow:

- `buyer_sales_sample`

This workflow uses sample/internal-review data only. It does not use `data/private/`, `output/private/`, or `output/final/` paths. It does not create external-ready outputs. Its purpose is to reduce manual command execution errors while preserving the existing Task 006-010 logic.

### Dry Run

Run dry-run before running the full sample workflow:

```powershell
python automations/run_internal_workflow.py --workflow buyer_sales_sample --dry-run
```

Dry-run prints the planned stages and commands. It does not execute generation scripts, does not create or modify output files, and should not create `output/internal_workflow_summary.md`.

### Full Sample Workflow

Run the full sample workflow:

```powershell
python automations/run_internal_workflow.py --workflow buyer_sales_sample --output-summary output/internal_workflow_summary.md
```

The full workflow runs Privacy Guard first, then buyer lead validation, buyer scoring generation, buyer score validation, proposal message generation, proposal message validation, quotation generation, quotation validation, and finally writes `output/internal_workflow_summary.md`.

### Validation Commands

Validate the runner and generated summary:

```powershell
python tests/validate_integrated_runner.py --check-summary --summary output/internal_workflow_summary.md
```

Also run:

```powershell
python tests/validate_privacy_guard.py
python -m py_compile automations/run_internal_workflow.py tests/validate_integrated_runner.py
```

### Execution Stages

The workflow stages run in this order:

1. `privacy_guard_validation`
2. `buyer_lead_validation`
3. `buyer_scoring_generation`
4. `buyer_score_validation`
5. `proposal_message_generation`
6. `proposal_message_validation`
7. `quotation_generation`
8. `quotation_validation`
9. `final_run_summary`

### Summary Interpretation

The summary result should be interpreted as:

- `PASS`: all stages completed and validations passed.
- `WARNING`: a non-blocking issue requires review.
- `FAIL`: the workflow stopped or validation failed.

`output/internal_workflow_summary.md` includes the workflow name, overall result, `started_at`, `finished_at`, stage commands, stage results, output paths, internal-review only disclaimer, no external sending disclaimer, and next action.

### Failure Handling

Privacy Guard failure stops the workflow. Buyer lead validation failure, generation failure, and output validation failure also stop the workflow.

The failed stage, command, return code, stdout/stderr summary, and next action are recorded. The operator should fix the failed stage and rerun from the beginning unless a later task defines partial rerun support.

### Input and Output Files

Source input files:

- `data/buyers_raw_sample.csv`
- `data/buyers_master_sample.csv`
- `data/brands_master.csv`
- `data/quotation_inputs_sample.csv`

Generated/intermediate files:

- `data/buyers_scored_sample.csv`
- `data/proposal_messages_sample.csv`
- `data/quotation_sample.csv`

Output files:

- `output/proposal_messages_sample.md`
- `output/quotation_sample.md`
- `output/quotation_sample.xlsx`
- `output/internal_workflow_summary.md`

The runner does not directly edit source input CSV files. Existing generation scripts may update their own generated sample outputs.

### Privacy and Real Data Restrictions

Privacy Guard runs first. `buyer_sales_sample` does not use real/private data. Real data workflows are not supported yet.

Do not pass `data/private/`, `output/private/`, or `output/final/` paths. Real data support requires separate design and approval. Run Privacy Guard before commit and before any real data migration.

### External Automation Restrictions

The Integrated Runner does not implement:

- Scraping.
- Live web research.
- Automatic search.
- APIs.
- Browser automation.
- Crawlers.
- Buyer enrichment.
- Credit checks.
- Email sending.
- Messaging automation.
- Quotation sending.
- External sending.

### Operator Checklist

Before running:

- Privacy Guard passes.
- Source sample CSV files exist.
- Output files can be regenerated.
- `output/quotation_sample.xlsx` is closed.
- No real/private data is staged.
- The operator understands outputs are internal-review only.

After running:

- Check overall `PASS`, `WARNING`, or `FAIL`.
- Review `output/internal_workflow_summary.md`.
- Review proposal and quotation outputs manually.
- Run Privacy Guard before commit.
- Do not externally send generated outputs without separate manual review.

### Known Limitations

- Sample workflow only.
- No real/private workflow support.
- No partial rerun support unless implemented later.
- No external sending.
- No commercial accuracy validation beyond existing validators.
- No buyer authenticity or credit verification.
- Operations Dashboard is handled separately by Task 012.

## Operations Dashboard

The Operations Dashboard summarizes the local sample/internal-review buyer sales workflow. It reads existing Task 006-011 outputs and turns workflow status, buyer priority, approval blocks, proposal draft status, quotation draft status, commercial confirmation gaps, and next actions into one internal review Markdown document.

The dashboard is internal-review only. It is not an external sending tool, buyer verification tool, credit check tool, market verification tool, or final quotation approval tool.

### v1 Markdown-Only Policy

Task 012 v1 uses Markdown only.

- v1 output: `output/operations_dashboard.md`
- v1 does not create `output/operations_dashboard.xlsx`.
- v1 does not create `data/operations_dashboard_summary.csv`.
- XLSX/CSV outputs are deferred until separately approved and validated.
- Markdown-only v1 reduces file lock risk, validation complexity, privacy exposure risk, and accidental external-use risk.

### Dashboard Inputs

The dashboard uses local sample/internal-review files only:

- `output/internal_workflow_summary.md`
- `data/buyers_master_sample.csv`
- `data/buyers_scored_sample.csv`
- `data/proposal_messages_sample.csv`
- `data/quotation_sample.csv`
- `data/brands_master.csv`

Do not use `data/private/`, `output/private/`, or `output/final/` paths for v1 dashboard generation.

### Generate Dashboard

Run a dry run first:

```powershell
python automations/operations_dashboard/generate_operations_dashboard.py --dry-run
```

Generate the Markdown dashboard:

```powershell
python automations/operations_dashboard/generate_operations_dashboard.py --output output/operations_dashboard.md
```

### Validate Dashboard

Validate the generated dashboard:

```powershell
python tests/validate_operations_dashboard.py --dashboard output/operations_dashboard.md
```

Validate generator safety and source expectations without requiring a dashboard file:

```powershell
python tests/validate_operations_dashboard.py --skip-dashboard
```

Also run:

```powershell
python tests/validate_privacy_guard.py
python -m py_compile automations/operations_dashboard/generate_operations_dashboard.py tests/validate_operations_dashboard.py
```

### Recommended Dashboard Workflow

1. Run Privacy Guard.
2. Run Integrated Runner if buyer/proposal/quotation sample outputs need refresh.
3. Run the Operations Dashboard generator.
4. Run the Operations Dashboard validator.
5. Review `output/operations_dashboard.md` manually.
6. Do not externally send dashboard outputs.
7. Run Privacy Guard before commit.

### Dashboard Sections

The Markdown dashboard includes:

1. Executive Summary
2. Integrated Runner Status
3. Buyer Pipeline Summary
4. Buyer Priority Summary
5. Approval & Brand Risk Summary
6. Proposal Message Summary
7. Quotation Summary
8. MOQ / Price / Stock / Expiry Issues
9. Next Action Summary
10. Internal Review Required Items
11. Key Risks and Warnings
12. Final Operational Recommendation

### Dashboard Privacy Restrictions

The dashboard must not expose:

- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `phone`
- `email`
- `private_note`
- `real_contact`
- `real_price`
- `real_stock`
- `real_expiry`

### Approval and Brand Restrictions

- `approval_block=true` must be reviewed first.
- `硫붾뵒?먮툕`/Medicube remains approval-required.
- `approval_required=true` means review-required.
- `proposal_allowed=false` means blocked/not allowed for external proposal.
- `priority_tier=A` or high `score_total` must not override `approval_block`.
- `score_total` is only an internal prioritization signal, not buyer authenticity, creditworthiness, or purchase probability.

### Proposal and Quotation Restrictions

- Proposal messages are internal drafts.
- Quotations are internal drafts.
- `PASS` does not mean final commercial approval.
- Price, stock, expiry, MOQ, delivery, tax, shipping, duties, payment terms, and incoterms require manual review before external use.
- Dashboard output must not be used as send-ready or final quotation material.

### Dashboard Output Policy

`output/operations_dashboard.md` is generated output. It may be ignored by `.gitignore` under `output/*`.

Do not force-add ignored output files unless explicitly approved. The generated dashboard can be regenerated from the committed generator and sample inputs.

### Known Dashboard Warning

The dashboard validator may produce a non-blocking warning if the `brands` row count is not directly printed in the dashboard body. This does not block v1 if brand risk and approval warnings are still summarized.

Do not modify generator output solely to remove this warning unless later approved.

### Dashboard External Automation Restrictions

The Operations Dashboard does not implement:

- Scraping.
- Live web research.
- Automatic search.
- APIs.
- Browser automation.
- Crawlers.
- Buyer enrichment.
- Credit checks.
- Email sending.
- Messaging automation.
- Quotation sending.
- External sending.

### Commit Safety Workflow

1. Update sample/source files only.
2. Keep real data outside tracked paths.
3. Run:

   ```powershell
   python tests/validate_privacy_guard.py
   ```

4. Run:

   ```powershell
   git status --short
   ```

5. Review staged files manually.
6. Commit only source, docs, tests, automation, and sample-safe files.
7. Do not commit ignored/private files or final external documents.
