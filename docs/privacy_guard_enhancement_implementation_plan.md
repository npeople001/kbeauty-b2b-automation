# Privacy Guard Enhancement Implementation Plan

## 1. Purpose

Task 014 enhances Privacy Guard before any future real/private workflow is attempted.

The implementation goal is to make `tests/validate_privacy_guard.py` better at detecting and blocking real/private data risks before buyer contact data, price data, stock data, expiry data, approval records, private commercial terms, final quotation files, or external-ready wording can be committed or used by workflows.

This plan defines the implementation sequence, validation matrix, false-positive prevention strategy, staged/tracked path checks, content-sensitivity rules, and PASS/WARNING/FAIL model for later implementation steps.

## 2. Scope

Task 014 should enhance detection for:

- Private/final paths.
- Staged or tracked private files.
- Sensitive filename patterns.
- Contact fields.
- Real price, stock, and expiry markers.
- Final quotation markers.
- External-ready and send-ready wording.
- External automation implementation patterns.
- False-positive handling for documentation and validator deny-lists.

The enhanced Privacy Guard should remain local-only, use Python standard library only, and never delete, move, rewrite, stage, commit, push, send, scrape, collect, enrich, or verify external data.

## 3. Non-Goals

Task 014 must not:

- Create real data files.
- Create `data/private/`, `output/private/`, or `output/final/` folders.
- Create private CSV or XLSX templates.
- Enable real/private workflow.
- Enable final quotation workflow.
- Send external communication.
- Scrape, search, crawl, enrich, verify, or credit-check buyers.
- Modify business automation logic.
- Modify `.gitignore` unless a later explicit step confirms a gap and authorizes the change.

## 4. Baseline Summary

Current Privacy Guard baseline:

- Current command: `python tests/validate_privacy_guard.py`
- Current result: `PASS`
- Current `files_scanned`: `83`
- Current warnings: `0`
- Current failures: `0`
- Current `.gitignore` protects:
  - `data/private/**`
  - `output/private/**`
  - `output/final/**`
  - `local_config/**`
  - real/private filename patterns such as `*_real.csv`, `*_private.csv`, `*_contacts.csv`, `*_prices.csv`, `*_stock.csv`, `*_expiry.csv`, and `*_quotation_final.*`
  - generated output files under `output/*` except `output/.gitkeep`
- Current private/final folder state:
  - `data/private/` does not exist.
  - `output/private/` does not exist.
  - `output/final/` does not exist.

Current validator capabilities:

- Checks required `.gitignore` privacy patterns.
- Confirms sample/source files are not accidentally ignored.
- Checks sensitive filenames and paths.
- Checks sample contact placeholder safety.
- Checks non-placeholder email patterns.
- Checks phone-like values for review.
- Checks proposal/quotation internal-review disclaimers.
- Checks approval-required brand context.
- Checks forbidden external automation imports and code patterns.
- Supports `working-tree` and `staged-only` modes.

## 5. Recommended Step A-I Sequence

### Step A: Implementation Plan Document

Create this document. No code changes.

Validation:

- Confirm the plan exists.
- Confirm Privacy Guard still passes.
- Confirm no code, `.gitignore`, data, private folders, templates, or automation logic changed.

### Step B: Baseline Behavior Document or Update

Document current Privacy Guard behavior, current PASS output, known limitations, current `.gitignore` coverage, and a test matrix for future implementation.

Validation:

- Run `python tests/validate_privacy_guard.py`.
- Run `python tests/validate_privacy_guard.py --mode staged-only`.
- Confirm no behavior changes yet.

### Step C: Path-Based Blocker Implementation

Enhance path checks so staged or tracked private/final paths are always blocking.

Validation:

- Run Privacy Guard in working-tree and staged-only modes.
- Use `git check-ignore` example paths without creating files.
- Confirm existing sample workflows are not affected.

### Step D: Sensitive Filename Blocker Implementation

Enhance sensitive filename patterns for real/private contact, price, stock, expiry, final quotation, and external-ready files.

Validation:

- Use synthetic path classification tests or temporary safe paths outside `data/private/` and `output/private/`.
- Confirm sample files such as `data/*_sample.csv` remain allowed.

### Step E: Content-Based Checker Implementation

Enhance content scanning for strict data and output files, including contact fields, real price/stock/expiry markers, final quotation markers, external-ready wording, and private commercial terms.

Validation:

- Use synthetic in-memory strings where possible.
- Confirm documentation policy language does not fail.
- Confirm sample placeholders remain allowed.

### Step F: False-Positive Prevention Implementation

Add context handling for documentation, validator deny-lists, safe placeholders, and explicit prohibited/blocked/internal-review wording.

Validation:

- Confirm docs containing prohibited terms pass when written as policy language.
- Confirm validator deny-list strings do not fail.
- Confirm actual risky strict-file content still fails in synthetic tests.

### Step G: Severity Model and Output Cleanup

Clarify PASS/WARNING/FAIL behavior, report exact file/path/line where possible, and keep non-blocking warnings visible.

Validation:

- Confirm failures return non-zero exit status.
- Confirm warnings do not fail unless configured as strict mode in a later approved step.
- Confirm output remains concise and actionable.

### Step H: Synthetic Validation and Regression Checks

Add safe synthetic validation coverage without creating real/private folders or real-looking data.

Validation:

- Run Privacy Guard.
- Run py_compile.
- Run Integrated Runner validation.
- Run Operations Dashboard validation.

### Step I: README, Roadmap, Task Log Update and Final Review

Record completed Task 014 changes, commands run, business decisions, remaining risks, and final review status.

Validation:

- Run all required commands.
- Confirm no real/private/final folders or files were created.
- Confirm no external automation was added.

## 6. Path-Based Blocker Design

Future checks should:

- Fail if `data/private/**` is tracked or staged.
- Fail if `output/private/**` is tracked or staged.
- Fail if `output/final/**` is tracked or staged.
- Fail if `local_config/**` is tracked or staged when applicable.
- Warn if private/final folders exist locally but are ignored and untracked.
- Never require creating private/final folders for tests.
- Use Git inspection where appropriate:
  - `git status --short`
  - `git ls-files`
  - `git diff --cached --name-only`
  - `git ls-files --others --exclude-standard`
  - `git check-ignore`

Expected behavior:

- Staged private/final path: FAIL.
- Tracked private/final path: FAIL.
- Ignored local private/final folder: WARNING, unless a future strict mode changes this.
- Documentation-only mention of private/final paths: INFO or allowed.

## 7. Sensitive Filename Blocker Design

The validator should block these filename patterns when they are tracked or staged:

- `*_real.csv`
- `*_private.csv`
- `*_contacts.csv`
- `*_contact*.csv`
- `*_prices.csv`
- `*_price*.csv`
- `*_stock.csv`
- `*_stock*.csv`
- `*_expiry.csv`
- `*_expiry*.csv`
- `*_quotation_final.*`
- `*_final_quotation.*`
- `*_external_ready.*`
- `*_send_ready.*`
- `*_approved_quotation.*`
- `*_commercially_approved.*`

Rules:

- Sensitive filenames in ignored paths should be reported as protected or ignored.
- Sensitive filenames staged or tracked should fail.
- Documentation examples should not fail.
- Sample files such as `data/*_sample.csv` should remain allowed when sample-safe.

## 8. Content-Based Checker Design

Stronger checks should apply to strict data and output files.

Sensitive markers:

- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `private_note`
- `real_contact`
- `real_price`
- `real_stock`
- `real_expiry`
- `final_quotation`
- `approved_quotation`
- `external_ready`
- `send_ready`
- `commercially_approved`
- `internal_margin`
- `supplier_private_terms`
- `distributor_private_terms`
- `payment_terms_real`
- `incoterms_real`

Rules:

- Strict files should fail on these markers unless clearly sample-safe.
- Policy docs may contain these terms as prohibited categories.
- Validator deny-lists may contain these terms.
- Documentation should fail only if context indicates actual data leakage or external-ready/final use, not policy description.
- Generated ignored output should be reviewed for warnings where appropriate, but internal-review-safe ignored files should not create false failures.

## 9. File Sensitivity Model

### STRICT

Paths:

- `data/*.csv`
- `output/*.csv`
- `output/*.xlsx`
- `output/*.md`

Rules:

- Fail on sensitive markers unless clearly sample-safe.
- Fail on real-looking contact values.
- Fail on final quotation or external-ready/send-ready markers.
- Sample files may pass only when placeholders and internal-review disclaimers are present where required.

### CODE

Paths:

- `tests/*.py`
- `automations/*.py`

Rules:

- Fail on actual forbidden imports or operational calls.
- Do not fail on deny-list strings, comments, or safety-rule configuration.
- Prefer AST import/call checks where practical.

### DOCS

Paths:

- `docs/*.md`
- `README.md`
- `AGENTS.md`

Rules:

- Allow policy language describing prohibited terms.
- Allow planned path references.
- Fail only if a document appears to include actual private data or instructs unsafe external operation.

### GENERATED_IGNORED

Paths:

- `output/*` ignored files.

Rules:

- Generated ignored outputs should generally be treated as internal-review artifacts.
- Warn if ignored generated output exists and contains sensitive-looking terms.
- Fail if the output looks external-ready, send-ready, final quotation, or real/private data bearing.

## 10. False-Positive Prevention Strategy

Allow these cases:

- Documentation describing prohibited patterns.
- Validator deny-list strings.
- Sample-safe placeholders:
  - `example.invalid`
  - `+00-0000-0000`
  - `BUYER_EXAMPLE_001`
  - `CONTACT_NAME_EXAMPLE`
  - `WECHAT_EXAMPLE`
  - `WHATSAPP_EXAMPLE`
  - `PRICE_PLACEHOLDER`
  - `STOCK_PLACEHOLDER`
  - `EXPIRY_YYYY_MM_DD`
  - `APPROVAL_REQUIRED_PLACEHOLDER`
- Safe context phrases:
  - `must not`
  - `do not`
  - `prohibited`
  - `blocked`
  - `excluded`
  - `internal-review`
  - `not external-ready`
  - `not final quotation`
  - `no automatic sending`
  - `no external sending`

Recommended implementation direction:

- Classify file sensitivity before content scanning.
- Treat documentation and code configuration differently from strict data/output files.
- Prefer AST import/call checks for code where practical.
- Keep line-level messages so a human can distinguish actual leaks from policy examples.

## 11. External Automation Checker Design

Future checks should detect actual implementation use of:

- `requests`
- `urllib.request`
- `httpx`
- `selenium`
- `playwright`
- `smtplib`
- `SMTP`
- `sendmail`
- email sending
- messaging automation
- WeChat sending
- WhatsApp sending
- quotation sending
- external sending
- crawling
- scraping
- buyer enrichment
- credit checks
- API calls

Rules:

- Documentation and validator forbidden lists should not fail.
- Actual imports or operational calls in `automations/*.py` should fail.
- Actual imports or operational calls in non-validator scripts should fail unless a future approved task explicitly allows them.
- Comments and docstrings that say the repository does not perform prohibited behavior should not fail.

## 12. Severity Model

### FAIL

Use FAIL for:

- Private/final path staged or tracked.
- Real data file staged or tracked.
- Contact field or real contact value leaked in a strict committed file.
- Real price, stock, or expiry leaked in a strict committed file.
- Final quotation or external-ready output detected.
- External sending, scraping, API, browser automation, crawler, buyer enrichment, or credit-check implementation detected.
- Privacy Guard bypass detected.

### WARNING

Use WARNING for:

- Private/final folder exists locally but is ignored and untracked.
- Generated ignored output exists.
- Policy docs contain sensitive terms.
- Dashboard output exists but is ignored and internal-review safe.
- Ambiguous business terms require human review.

### INFO

Use INFO for:

- Sample-safe placeholders.
- Documentation-only prohibited terms.
- Validator deny-list entries.
- Internal-review-only wording.

Output rules:

- Any FAIL should return non-zero exit status.
- WARNING should be visible but should not fail unless a future strict mode is explicitly approved.
- INFO may be summarized or omitted from normal output if too noisy.

## 13. Validation Matrix

| Check category | Example input | Expected severity | Expected action | False positive risk | Mitigation |
| --- | --- | --- | --- | --- | --- |
| Private path staged | `data/private/buyers_real.csv` staged | FAIL | Stop commit/workflow. Report path. | Low | Use Git staged/tracked inspection. |
| Private path ignored local | `data/private/example.csv` exists but ignored and untracked | WARNING | Review local state. Do not commit. | Medium | Do not require folder creation in tests. |
| Sensitive filename tracked | `supplier_terms_private.csv` tracked | FAIL | Stop commit. Remove from tracking after review. | Low | Match filename patterns only for tracked/staged files. |
| Contact column in strict CSV | `contact_email` in `data/buyers_real.csv` | FAIL | Stop commit/workflow. | Medium | Allow sample placeholder columns only in approved sample files. |
| Contact placeholder in docs | `CONTACT_NAME_EXAMPLE` in `docs/*.md` | INFO | Allow. | Medium | DOCS sensitivity model and placeholder allowlist. |
| External automation import in automations | `import requests` in `automations/*.py` | FAIL | Stop commit/workflow. | Low | AST import checks. |
| Forbidden pattern string in validator | `requests` inside deny-list | INFO | Allow. | High | CODE context with validator allowlist handling. |
| Final quotation wording in docs | `final quotation must not be generated` | INFO | Allow. | High | Safe context phrase detection. |
| Final quotation wording in output | `final_quotation` in `output/*.md` | FAIL or WARNING depending context | Block if external-ready/final; warn if ignored/internal-review policy. | Medium | GENERATED_IGNORED plus internal-review disclaimer check. |
| Generated ignored dashboard | `output/operations_dashboard.md` exists and is ignored | WARNING | Review if needed, do not force-add. | Medium | Check ignored status and internal-review wording. |
| Sample placeholder contact | `buyer001@example.invalid` | INFO | Allow. | Low | Placeholder email domain allowlist. |
| Approval block policy docs | `approval_block=true must block external proposal` | INFO | Allow. | High | DOCS safe context phrase handling. |

## 14. Test Strategy Without Real/Private Data

Implementation tests should:

- Use synthetic in-memory strings where possible.
- Use temporary files under safe temporary directories if file behavior must be tested.
- Avoid creating `data/private/`, `output/private/`, or `output/final/`.
- Avoid creating real-looking buyer, contact, price, stock, or expiry data.
- Avoid committing test fixtures with real-sensitive names unless explicitly safe and policy-approved.
- Regression test existing sample workflow.
- Regression test Integrated Runner validation.
- Regression test Operations Dashboard validation.

Safe approaches:

- Unit-style helper functions for path classification.
- Unit-style helper functions for file sensitivity classification.
- Synthetic content strings passed to scanner helpers.
- `git check-ignore` on example paths without creating files.

Unsafe approaches:

- Creating private/final folders.
- Creating real-looking CSV fixtures.
- Force-adding ignored paths.
- Using real contact, price, stock, expiry, supplier, or quotation data.

## 15. Required Validation Commands for Implementation Steps

Run these during later implementation steps:

```powershell
python tests/validate_privacy_guard.py
python tests/validate_privacy_guard.py --mode staged-only
python -m py_compile tests/validate_privacy_guard.py
git status --short
git check-ignore -v data/private/example.csv
git check-ignore -v output/private/example.md
git check-ignore -v output/final/example.pdf
python tests/validate_integrated_runner.py --check-summary --summary output/internal_workflow_summary.md
python tests/validate_operations_dashboard.py --skip-dashboard
```

Additional recommended checks:

```powershell
git diff --name-only
git ls-files
git ls-files --others --exclude-standard
```

## 16. .gitignore Policy

- Do not modify `.gitignore` in Step A.
- `.gitignore` may be reviewed in later steps only if the validator finds a confirmed gap.
- `.gitignore` changes require explicit step instruction.
- The validator should report potential `.gitignore` gaps before modification.
- Existing sample/source files must remain trackable.
- Existing generated output ignore behavior should not be weakened.

## 17. Completion Criteria for Task 014

Task 014 should complete only when:

- This implementation plan exists.
- Privacy Guard enhancement is implemented step by step.
- False-positive handling is validated.
- Baseline sample workflow still passes.
- Integrated Runner validation still passes.
- Operations Dashboard validation still passes.
- No real/private/final folders are created.
- No real data is introduced.
- No external automation is added.
- Roadmap and task log are updated.
- Final review passes.

Task 014 should still be considered internal guardrail work only. It must not enable real/private operation by itself.

## 18. Recommended Next Step

Recommended next step:

- Step B: document or update the current Privacy Guard baseline and test matrix before code changes.

Step B should still avoid code changes unless explicitly requested. It should capture current behavior, current limitations, current expected PASS result, and a concise test matrix for Step C-H implementation.
