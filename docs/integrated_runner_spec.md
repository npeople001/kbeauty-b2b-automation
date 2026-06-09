# Integrated Runner Specification

## 1. Scope

Task 011 defines a controlled local runner for the existing internal automation workflow.

Task 011 does:

- Orchestrate existing local automation scripts from Task 006-010 in the correct order.
- Run validation before and after generation steps.
- Produce a clear final run summary for internal review.
- Improve operating convenience for the sample buyer sales workflow.
- Preserve the existing Task 006-010 business logic and validation rules.

Task 011 does not do:

- It does not replace or rewrite existing business logic.
- It does not modify existing generator scripts.
- It does not modify existing validation scripts.
- It does not send emails, DMs, WeChat messages, WhatsApp messages, quotations, or any other external communication.
- It does not collect, scrape, enrich, verify, crawl, or search external data.
- It does not use live web research, automatic web search, APIs, browser automation, buyer enrichment, credit checks, email sending, messaging automation, quotation sending, or external sending.
- It does not create real data files.
- It does not create `data/private/` or `output/private/` folders.
- It does not create dashboard files.

The Integrated Runner is internal-review only. It should only orchestrate existing local scripts and should not weaken any privacy, approval, quotation, or external-use restrictions already defined in Task 001-010.

## 2. Background

Task 001-009 created the first-pass internal K-beauty B2B automation foundation:

- Brand master automation
- Market research and content strategy templates
- Market research report generation
- Channel content strategy generation
- Short-form video and feed planning
- Buyer lead templates
- Buyer scoring
- Internal-review proposal message drafts
- Internal-review quotation drafts

Task 010 added real data migration policy and Privacy Guard controls. Task 011 should improve operating convenience by running existing workflows in a controlled order, while preserving Task 010 privacy protections.

The runner must not make internal-review outputs look external-ready. Proposal messages, quotation drafts, scoring outputs, and generated summaries remain internal planning/review materials only.

## 3. Recommended Runner File

Future implementation target:

- `automations/run_internal_workflow.py`

This file must not be created in Step A. Step A is specification-only.

## 4. Supported Workflow

Initial supported workflow:

- `buyer_sales_sample`

The `buyer_sales_sample` workflow uses sample/internal-review data only. It should not accept real/private paths by default and should not create real operating data files.

## 5. Execution Order

The `buyer_sales_sample` workflow should run in this order.

### 1. Privacy Guard validation

```powershell
python tests/validate_privacy_guard.py
```

### 2. Buyer lead validation

```powershell
python tests/validate_buyer_leads.py --raw data/buyers_raw_sample.csv --master data/buyers_master_sample.csv
```

### 3. Buyer scoring generation

```powershell
python automations/buyer_scoring/generate_buyer_scores.py --input data/buyers_master_sample.csv --output data/buyers_scored_sample.csv --brands data/brands_master.csv
```

### 4. Buyer score validation

```powershell
python tests/validate_buyer_scores.py --input data/buyers_master_sample.csv --scored data/buyers_scored_sample.csv
```

### 5. Proposal message generation

```powershell
python automations/proposal_messages/generate_proposal_messages.py --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --brands data/brands_master.csv --csv-output data/proposal_messages_sample.csv --md-output output/proposal_messages_sample.md
```

### 6. Proposal message validation

```powershell
python tests/validate_proposal_messages.py --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --messages data/proposal_messages_sample.csv --markdown output/proposal_messages_sample.md --brands data/brands_master.csv
```

### 7. Quotation generation

```powershell
python automations/quotation_maker/generate_quotations.py --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --proposals data/proposal_messages_sample.csv --brands data/brands_master.csv --quote-inputs data/quotation_inputs_sample.csv --csv-output data/quotation_sample.csv --xlsx-output output/quotation_sample.xlsx --md-output output/quotation_sample.md
```

### 8. Quotation validation

```powershell
python tests/validate_quotations.py --quote-inputs data/quotation_inputs_sample.csv --quotations data/quotation_sample.csv --markdown output/quotation_sample.md --xlsx output/quotation_sample.xlsx --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --proposals data/proposal_messages_sample.csv --brands data/brands_master.csv
```

### 9. Final run summary

The runner should create a final run summary only after executing or simulating the requested workflow according to the selected mode.

## 6. CLI Design

Future runner command:

```powershell
python automations/run_internal_workflow.py --workflow buyer_sales_sample
```

Optional future arguments:

- `--workflow buyer_sales_sample`
- `--stop-on-fail`
- `--continue-on-warning`
- `--dry-run`
- `--skip-xlsx`
- `--output-summary output/internal_workflow_summary.md`

Recommended defaults:

- `--workflow buyer_sales_sample`
- `--stop-on-fail` enabled by default
- `--continue-on-warning` disabled by default
- `--dry-run` disabled by default
- `--skip-xlsx` disabled by default
- `--output-summary output/internal_workflow_summary.md`

## 7. Failure Policy

The runner should use strict failure behavior by default.

- Privacy Guard failure must stop the workflow immediately.
- Buyer lead validation failure must stop the workflow.
- Generation failure must stop the workflow.
- Output validation failure must stop the workflow.
- Warnings may continue only if the policy allows them.
- `--stop-on-fail` should be the default behavior.
- `--continue-on-warning` may allow continuation, but warnings must be recorded in the final summary.
- `--dry-run` must not generate or modify output files.
- Failed stage name, command, return code, stdout/stderr summary, and recommended next action must be recorded.

The runner should not attempt automatic fixes. It should stop, report, and require manual review.

## 8. Dry Run Policy

Dry run should:

- Print planned stages.
- Print planned commands.
- Print expected input paths.
- Print expected output paths.
- Avoid executing generation scripts.
- Avoid writing generated outputs.
- Avoid creating real/private data.
- Avoid sending anything externally.
- Clearly state that it is a simulation only.

Dry run may validate that planned paths and commands are configured, but it must not modify workflow outputs.

## 9. Summary Output

Recommended future output:

- `output/internal_workflow_summary.md`

The summary should include:

- Overall result: `PASS`, `WARNING`, or `FAIL`
- Workflow name
- `started_at`
- `finished_at`
- Stage list
- Command for each stage
- Result for each stage
- Return code for each stage
- Short stdout/stderr summary for each stage
- Output paths
- Warnings
- Failures
- Next action
- Internal-review only disclaimer
- No external sending disclaimer

The summary must not imply that messages, proposals, quotations, or any external communication were sent.

## 10. Input and Output Files

The runner should use these source input files:

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

The runner should not directly edit source input CSV files. Existing generation scripts may create or update their defined generated sample outputs.

## 11. Source Data Protection

The runner must follow Task 010 data protection rules:

- It must not modify source CSV files directly.
- It must not create real data files.
- It must not create private folders.
- It must not accept `data/private/`, `output/private/`, `output/final/`, or `local_config/` paths by default.
- It must not stage, commit, move, or delete files.
- It must not auto-fix privacy issues.
- It must not overwrite source CSV files to resolve output permission issues.
- It must keep real/private workflows out of scope until a separate design and approval exists.

Any future real/private workflow must require separate specification, Privacy Guard review, and explicit approval.

## 12. Privacy Guard Requirements

Privacy Guard must be the first runner stage.

- If Privacy Guard fails, no downstream generation should run.
- The runner must not bypass Privacy Guard.
- The runner must record Privacy Guard result in the summary.
- The runner must preserve Task 010 real data protection principles.
- The runner must keep sample files and real operating data clearly separated.
- The runner must keep outputs internal-review only.

Privacy Guard is not a full DLP system. The runner should still recommend manual review of `git status` and generated outputs before commit or business use.

## 13. External Automation Restrictions

The runner must not include or use:

- `requests`
- `urllib.request`
- `httpx`
- `selenium`
- `playwright`
- Browser automation
- Scraping
- Crawling
- APIs
- Buyer enrichment
- Credit checks
- `smtplib`
- `SMTP`
- Email sending
- DM sending
- WeChat sending
- WhatsApp sending
- Quotation sending
- Messaging automation
- External sending

The runner should only call local Python scripts through controlled local subprocess commands.

## 14. Implementation Strategy

Future implementation should use:

- Python standard library only
- `subprocess.run` with list arguments, not `shell=True`
- `pathlib` for paths
- `argparse` for CLI
- `datetime` for summary timestamps
- A controlled command registry for workflow stages
- Explicit stage names and expected output paths

Subprocess orchestration is preferred because it:

- Preserves existing validated scripts.
- Avoids duplicating business logic.
- Makes failure points explicit.
- Reduces risk of changing Task 006-010 behavior.
- Keeps each existing validator responsible for its own domain.

The runner should not import and call internal generator functions unless a later design proves it is safer. The current existing scripts already expose clear CLI interfaces.

## 15. Validation Requirements

Future validation should check:

- Runner script syntax passes.
- Dry run works.
- Full sample workflow runs.
- Summary file is created.
- All required stages appear in the correct order.
- Failure policy is documented in the summary.
- Privacy Guard runs first.
- No forbidden imports or external automation code exist.
- No real/private data files are created.
- No private folders are created.
- No source CSV files are modified directly by the runner.
- Existing validators still pass.
- Privacy Guard still passes.
- Output files remain internal-review only.

Recommended future validation commands:

```powershell
python tests/validate_privacy_guard.py
python -m py_compile automations/run_internal_workflow.py tests/validate_integrated_runner.py
python automations/run_internal_workflow.py --workflow buyer_sales_sample --dry-run
python automations/run_internal_workflow.py --workflow buyer_sales_sample
python tests/validate_integrated_runner.py --summary output/internal_workflow_summary.md
```

## 16. Completion Criteria

Task 011 should be considered complete only when:

- Integrated runner specification exists.
- Workflow document exists.
- Runner script exists.
- Dry run works.
- Full sample workflow runs successfully.
- Summary output is generated.
- Integrated runner validator exists and passes.
- README guidance is updated.
- Roadmap and task log are updated.
- Final review passes.

## 17. Recommended Future Steps

Recommended Task 011 sequence:

- Step B: Create `docs/integrated_runner_workflow.md`.
- Step C: Create `automations/run_internal_workflow.py` with controlled subprocess orchestration.
- Step D: Implement dry-run and failure policy.
- Step E: Create summary output.
- Step F: Create `tests/validate_integrated_runner.py`.
- Step G: Update README/workflow documentation.
- Step H: Update roadmap/task log.
- Step I: Perform final review.

Do not proceed to Step B until Step A is reviewed and accepted.

