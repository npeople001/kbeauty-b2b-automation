# Integrated Runner Workflow

## 1. Purpose

The future Integrated Runner will orchestrate existing local scripts for the internal sample buyer sales workflow.

It is designed to reduce manual command execution errors by running existing validation and generation steps in a controlled order. It does not replace existing validators, business rules, approval rules, quotation rules, or privacy rules.

The Integrated Runner does not send, scrape, collect, enrich, verify, search, or externally communicate. It must not send emails, DMs, WeChat messages, WhatsApp messages, quotations, or any other external communication.

All generated outputs remain internal-review drafts.

## 2. Supported Workflow

Initial supported workflow:

- `buyer_sales_sample`

The `buyer_sales_sample` workflow:

- Uses sample/internal-review data only.
- Does not use real/private data paths.
- Does not create external-ready outputs.
- Does not create real operating data.
- Does not create private folders.
- Is intended to reduce manual command execution errors.

This workflow is not a real buyer operation workflow. Any future real/private workflow requires separate design, Privacy Guard review, and explicit approval.

## 3. Operator Preconditions

Before running the future runner, the operator must:

- Confirm Task 010 Privacy Guard is passing.
- Confirm no real/private data is staged.
- Confirm sample inputs exist.
- Confirm output files are okay to regenerate.
- Close quotation XLSX files if needed.
- Understand that all outputs remain internal-review drafts.
- Review `.gitignore` and `git status --short` when preparing files for commit.

Recommended pre-run command:

```powershell
python tests/validate_privacy_guard.py
```

If Privacy Guard fails, do not continue.

## 4. Standard Command

Future standard command:

```powershell
python automations/run_internal_workflow.py --workflow buyer_sales_sample
```

Optional future commands:

```powershell
python automations/run_internal_workflow.py --workflow buyer_sales_sample --dry-run
python automations/run_internal_workflow.py --workflow buyer_sales_sample --stop-on-fail
python automations/run_internal_workflow.py --workflow buyer_sales_sample --continue-on-warning
python automations/run_internal_workflow.py --workflow buyer_sales_sample --skip-xlsx
python automations/run_internal_workflow.py --workflow buyer_sales_sample --output-summary output/internal_workflow_summary.md
```

## 5. Execution Stages

### Stage 1: Privacy Guard validation

Command:

```powershell
python tests/validate_privacy_guard.py
```

Failure behavior:

- Stop immediately.
- Do not run downstream generation or validation stages.
- Record the failed stage, return code, output summary, and next action.

### Stage 2: Buyer lead validation

Command:

```powershell
python tests/validate_buyer_leads.py --raw data/buyers_raw_sample.csv --master data/buyers_master_sample.csv
```

Failure behavior:

- Stop on failure.
- Check buyer lead column order, row count, required fields, allowed values, MOQ consistency, placeholder contacts, brand approval warnings, and Korean/Chinese text preservation.
- Do not modify source CSV files automatically.

### Stage 3: Buyer scoring generation

Command:

```powershell
python automations/buyer_scoring/generate_buyer_scores.py --input data/buyers_master_sample.csv --output data/buyers_scored_sample.csv --brands data/brands_master.csv
```

Failure behavior:

- Stop on failure.
- Check that the buyer master input and brand master reference exist.
- Do not alter `data/buyers_master_sample.csv` directly.

### Stage 4: Buyer score validation

Command:

```powershell
python tests/validate_buyer_scores.py --input data/buyers_master_sample.csv --scored data/buyers_scored_sample.csv
```

Failure behavior:

- Stop on failure.
- Check score columns, row consistency, score range, priority tier, approval block, MOQ rules, manual-source flags, privacy exclusion, and forbidden external collection indicators.

### Stage 5: Proposal message generation

Command:

```powershell
python automations/proposal_messages/generate_proposal_messages.py --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --brands data/brands_master.csv --csv-output data/proposal_messages_sample.csv --md-output output/proposal_messages_sample.md
```

Failure behavior:

- Stop on failure.
- Do not send generated messages.
- Do not expose buyer contact fields in proposal outputs.
- Do not override approval blocks.

### Stage 6: Proposal message validation

Command:

```powershell
python tests/validate_proposal_messages.py --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --messages data/proposal_messages_sample.csv --markdown output/proposal_messages_sample.md --brands data/brands_master.csv
```

Failure behavior:

- Stop on failure.
- Check proposal columns, row consistency, approval block handling, restricted brand exclusion, MOQ/payment review status, forbidden unsupported claims, privacy/contact exclusion, language preservation, and no external sending implication.

### Stage 7: Quotation generation

Command:

```powershell
python automations/quotation_maker/generate_quotations.py --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --proposals data/proposal_messages_sample.csv --brands data/brands_master.csv --quote-inputs data/quotation_inputs_sample.csv --csv-output data/quotation_sample.csv --xlsx-output output/quotation_sample.xlsx --md-output output/quotation_sample.md
```

Failure behavior:

- Stop on failure.
- Do not send quotations.
- Do not create final commercial offers.
- Do not invent price, stock, expiry, MOQ, delivery, supply, or final trade terms.
- If the XLSX output is locked, the quotation generator may create a timestamped fallback output according to its own rules.

### Stage 8: Quotation validation

Command:

```powershell
python tests/validate_quotations.py --quote-inputs data/quotation_inputs_sample.csv --quotations data/quotation_sample.csv --markdown output/quotation_sample.md --xlsx output/quotation_sample.xlsx --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --proposals data/proposal_messages_sample.csv --brands data/brands_master.csv
```

Failure behavior:

- Stop on failure.
- Check quotation CSV, Markdown, XLSX, row consistency, approval blocks, price/stock/expiry/MOQ handling, total amount calculation, privacy/contact exclusion, forbidden commercial claims, external sending prohibition, and encoding preservation.

### Stage 9: Final run summary

Future output:

- `output/internal_workflow_summary.md`

The summary should be generated after a dry run or full workflow run. It should not imply external sending or final commercial approval.

## 6. Dry Run Workflow

`--dry-run` should:

- Print planned stages.
- Print planned commands.
- Print expected input paths.
- Print expected output paths.
- Print the planned summary path.
- Avoid executing generation scripts.
- Avoid modifying output files.
- Avoid creating real/private files.
- Avoid creating private folders.
- Avoid sending anything externally.
- Show external automation restrictions.
- Clearly state that the run is a simulation only.

Dry run may be used before the full workflow to confirm that the operator understands the planned sequence.

## 7. Stop / Continue Policy

Default behavior should be stop-on-fail.

- Privacy Guard failure is always blocking.
- Validation failure is blocking.
- Generation failure is blocking.
- Warnings should be recorded.
- `--continue-on-warning` may continue only when there are warnings but no failures.
- Failure stage, command, return code, stdout/stderr summary, and next action must be recorded.

The runner must not auto-fix input files, generated files, privacy issues, approval rules, quotation terms, or encoding issues.

## 8. Summary Interpretation

Future summary statuses:

- `PASS`: all stages completed and validations passed.
- `WARNING`: all required stages completed, but non-blocking warnings require review.
- `FAIL`: one or more stages failed, and the workflow stopped.

The summary must include:

- Workflow name
- `started_at`
- `finished_at`
- Stage results
- Commands
- Return codes
- Output paths
- Warnings
- Failures
- Next action
- Internal-review only disclaimer
- No external sending disclaimer

The summary is not a business approval document. It is only an operational run record.

## 9. Input and Output Handling

Source CSV files are not modified directly by the runner.

Source/sample inputs:

- `data/buyers_raw_sample.csv`
- `data/buyers_master_sample.csv`
- `data/brands_master.csv`
- `data/quotation_inputs_sample.csv`

Generated sample CSV outputs:

- `data/buyers_scored_sample.csv`
- `data/proposal_messages_sample.csv`
- `data/quotation_sample.csv`

Generated Markdown/XLSX outputs:

- `output/proposal_messages_sample.md`
- `output/quotation_sample.md`
- `output/quotation_sample.xlsx`
- `output/internal_workflow_summary.md`

`output/*` remains generated/ignored according to existing project rules. XLSX files may need to be closed before running. If an XLSX file is locked, the underlying generator may create a timestamped fallback output.

No real/private paths should be used by default.

## 10. Privacy and Real Data Restrictions

Privacy Guard must run first. If Privacy Guard fails, no downstream generation should occur.

Rules:

- Real data is not part of `buyer_sales_sample`.
- `data/private/**` is not used.
- `output/private/**` is not used.
- `output/final/**` is not used.
- `local_config/**` is not used.
- The runner must not bypass `.gitignore` or privacy policy.
- The runner must not create real data files.
- The runner must not create private folders.
- The runner must not stage, commit, move, or delete files.

Real operation workflow requires separate design and approval.

## 11. External Automation Restrictions

The runner must not implement:

- Scraping
- Live web research
- Automatic search
- APIs
- Browser automation
- Crawlers
- Buyer enrichment
- Credit checks
- Email sending
- Messaging automation
- Quotation sending
- External sending

The runner should only orchestrate local scripts through controlled local commands.

## 12. Operator Troubleshooting Guide

### Privacy Guard fails

Likely cause:

- Sensitive path, unsafe filename, non-placeholder contact, missing `.gitignore` protection, or unsafe implementation pattern was detected.

What to check:

- Run `git status --short`.
- Review staged and unstaged files.
- Check whether real/private data was placed in a tracked path.
- Check `.gitignore` protection.

What not to do:

- Do not continue the workflow.
- Do not auto-delete files.
- Do not commit until reviewed.

### Buyer lead validation fails

Likely cause:

- Missing required columns, invalid allowed values, row count mismatch, MOQ inconsistency, non-placeholder contact data, or approval warning issue.

What to check:

- `data/buyers_raw_sample.csv`
- `data/buyers_master_sample.csv`
- `data/brands_master.csv`

What not to do:

- Do not silently change source business data.
- Do not put real contact data into sample files.

### Buyer scoring generation fails

Likely cause:

- Missing buyer master input, missing required columns, missing brand master reference, or invalid input values.

What to check:

- `data/buyers_master_sample.csv`
- `data/brands_master.csv`
- Generator stdout/stderr summary.

What not to do:

- Do not modify approval-required brand rules without confirmation.
- Do not treat scoring as buyer verification.

### Buyer score validation fails

Likely cause:

- Score output columns are wrong, score values are outside 0-100, approval block is wrong, MOQ flags are missing, or privacy-sensitive contact data leaked.

What to check:

- `data/buyers_scored_sample.csv`
- `automations/buyer_scoring/generate_buyer_scores.py`

What not to do:

- Do not manually edit scored output unless the root cause is understood.
- Do not treat a high score as permission to override approval blocks.

### Proposal validation fails

Likely cause:

- Proposal output contains restricted brands, unsupported claims, contact-like data, missing internal-review disclaimer, or external sending implication.

What to check:

- `data/proposal_messages_sample.csv`
- `output/proposal_messages_sample.md`
- `data/brands_master.csv`

What not to do:

- Do not send drafts externally.
- Do not add buyer-facing copy for approval-blocked rows.

### Quotation XLSX is locked

Likely cause:

- The workbook is open in Excel or another application.

What to check:

- Close `output/quotation_sample.xlsx`.
- Check whether a timestamped fallback XLSX was generated.
- Review the actual output path printed by the quotation generator.

What not to do:

- Do not modify source CSV files to resolve an output permission issue.
- Do not delete files automatically.

### Quotation validation fails

Likely cause:

- Missing price, stock, expiry, MOQ, supply, approval block, total amount, compliance note, XLSX sheet, or forbidden commercial term issue.

What to check:

- `data/quotation_inputs_sample.csv`
- `data/quotation_sample.csv`
- `output/quotation_sample.md`
- `output/quotation_sample.xlsx`

What not to do:

- Do not invent price, stock, expiry, supply, or final commercial terms.
- Do not treat quotation drafts as final commercial offers.

### Summary output missing

Likely cause:

- Runner stopped before summary creation, output path is invalid, or the future runner implementation has a write failure.

What to check:

- Runner return code.
- Failed stage name.
- `--output-summary` path.
- `output/` write permission.

What not to do:

- Do not assume the workflow passed without a summary.
- Do not manually create a pass summary without rerunning validation.

### Sample file missing

Likely cause:

- A required sample input or generated sample dependency was moved, deleted, or ignored incorrectly.

What to check:

- `git status --short`
- `git ls-files data`
- Required input file paths in `docs/integrated_runner_spec.md`

What not to do:

- Do not replace missing sample files with real operating data.
- Do not create private folders as a shortcut.

## 13. Completion Criteria for Workflow Documentation

This workflow document is complete when it explains:

- Supported workflow
- Command usage
- Execution stages
- Failure policy
- Dry-run behavior
- Summary interpretation
- Privacy/external automation restrictions
- Troubleshooting guide

Task 011 must not proceed to code implementation until this workflow document is reviewed and accepted.

