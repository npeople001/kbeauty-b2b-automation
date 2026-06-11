# Privacy Guard Enhancement Specification

## 1. Purpose

This document defines future Privacy Guard enhancements required before real/private operations can be attempted.

It is specification only. It does not implement code, modify `tests/validate_privacy_guard.py`, modify `.gitignore`, create real data files, create private/final folders, create CSV/XLSX templates, modify automation logic, or add external sending, scraping, live research, APIs, browser automation, buyer enrichment, credit checks, or external data collection.

The purpose is to describe how Privacy Guard should be strengthened before future real buyer contacts, real buyer legal names, real prices, real stock, real expiry, supplier/distributor private terms, approval records, or final quotation files are introduced.

## 2. Current Privacy Guard Baseline

The current Privacy Guard:

- Scans repository files.
- Blocks obvious real/private data risk.
- Supports the current sample/internal-review workflow.
- Must pass before commit.
- Validates repository privacy policy compliance.
- Checks sensitive file and path patterns.
- Checks sample contact placeholder safety.
- Checks approval-required brand context.
- Checks forbidden external collection and sending implementation patterns.
- Checks required `.gitignore` protections.
- Confirms sample files remain trackable.

Current Privacy Guard is useful for sample workflow protection, but it is not a full DLP system and does not replace human review.

## 3. Why Enhancement Is Needed

Future real/private operation introduces higher risk because the repository may need to handle or reference:

- Real buyer contacts.
- Real buyer legal names.
- Real prices.
- Real stock.
- Real expiry.
- Supplier/distributor private terms.
- Payment terms.
- Incoterms.
- Internal margin.
- Final quotation terms.
- External-ready proposal or quotation wording.

These data types can expose privacy-sensitive buyer information, confidential commercial terms, approval-sensitive brand decisions, or final commercial documents. Enhanced Privacy Guard checks should block or warn before such data can be staged, committed, or used by workflows.

## 4. Future Blocking Checks

Privacy Guard should fail if any of the following are detected in staged or tracked paths where they are not explicitly allowed:

- `data/private/**`
- `output/private/**`
- `output/final/**`
- Real buyer contact files.
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

Policy documentation and validator forbidden-pattern lists may mention these terms. The implementation should distinguish documentation or configuration references from real/private data files where possible.

## 5. Private and Final Path Checks

Expected future behavior:

- Fail if a `data/private/**` path is tracked or staged.
- Fail if an `output/private/**` path is tracked or staged.
- Fail if an `output/final/**` path is tracked or staged.
- Warn or fail if private/final folders exist locally, depending on future validation mode.
- Never allow force-added private/final files.
- Stop commit preparation if private/final paths appear in `git status --short`.
- Stop commit preparation if private/final paths appear in `git ls-files`.

Future validation modes may distinguish:

- Working-tree safety checks.
- Staged-only checks before commit.
- Strict real-operation preflight checks.

In all modes, tracked or staged private/final files should be blocking.

## 6. Real Data Pattern Checks

Sensitive data pattern categories:

- Contact fields.
- Real buyer legal names.
- Real price columns.
- Real stock columns.
- Real expiry columns.
- Payment and incoterm fields.
- Supplier/distributor private terms.
- Final quotation markers.
- External-ready wording.

Pattern handling rules:

- Sample-safe placeholder values should not create false positives if clearly synthetic.
- `example.invalid`, `+00-0000-0000`, and `placeholder_*` values should remain sample-safe.
- Real/private wording in documentation should not fail when it clearly describes prohibited categories.
- Code may contain prohibited terms inside validator configuration or forbidden-pattern lists.
- Data and generated output files should be treated more strictly than policy docs.
- Implementation should distinguish documentation from data files where possible.

## 7. File Type and Path Sensitivity

Future Privacy Guard should apply stricter checks by file type and path.

### Stricter paths

- `data/*.csv`
- `output/*.csv`
- `output/*.xlsx`
- `output/*.md`

These files are more likely to contain business data or generated operating outputs. Real/private indicators in these files should be treated as high risk unless explicitly sample-safe.

### Documentation paths

- `docs/*.md`

Documentation may include prohibited terms as policy language. Privacy Guard should allow policy references when they are clearly framed as blocked, prohibited, or internal-review-only categories.

### Code paths

- `tests/*.py`
- `automations/*.py`

Code may include prohibited terms inside validators, deny lists, or safety rules. Privacy Guard should avoid false positives on forbidden-pattern lists while still failing actual implementation of external collection, sending, scraping, API use, browser automation, buyer enrichment, or credit checks.

## 8. Git Staging Checks

Future checks should inspect:

- Staged private files.
- Tracked private files.
- `git status --short`.
- `git ls-files`.
- `git ls-files --others --exclude-standard`.
- `git check-ignore` for planned private paths.

Required behavior:

- Private/final files must not be staged.
- Private/final files must not be tracked.
- `git add -f` on private/final paths must be treated as blocking.
- Commit should stop if private/final paths appear.
- Privacy Guard should report exact paths and suggested next action.

Recommended checks:

```powershell
git status --short
git ls-files
git ls-files --others --exclude-standard
git check-ignore -v data/private/example.csv
git check-ignore -v output/private/example.md
git check-ignore -v output/final/example.pdf
```

## 9. External Automation Checks

Privacy Guard should continue or expand checks for:

- `requests`
- `urllib.request`
- `httpx`
- `selenium`
- `playwright`
- `smtplib`
- `SMTP`
- `sendmail`
- Email sending.
- Messaging automation.
- WeChat sending.
- WhatsApp sending.
- Quotation sending.
- External sending.
- Crawling.
- Scraping.
- Buyer enrichment.
- Credit checks.
- API calls.

Rules:

- Actual implementation usage should fail.
- Appearances inside documentation, policy lists, validator deny lists, or explanatory text should not cause false positives.
- Code that imports or invokes external collection/sending modules should be treated as blocking unless explicitly approved in a future separate task.

## 10. Approval and Final Quotation Checks

Future Privacy Guard should support these blocking rules:

- `approval_block=true` must not be bypassed.
- 메디큐브/Medicube cannot be externally proposed without explicit approval.
- Final quotation cannot be generated into `output/final/**`.
- Quotation validation `PASS` does not mean final commercial approval.
- External-ready quotation wording should fail outside an approved final process.
- A high `score_total`, `priority_tier=A`, large order quantity, or buyer interest must not override approval restrictions.

Privacy Guard should not decide final business approval. It should block unsafe paths, unsafe wording, and missing safety context so manual review can happen before external use.

## 11. Recommended Future Implementation Strategy

Recommended implementation approach:

- Add clear configuration sections to `tests/validate_privacy_guard.py`.
- Separate path checks, staged/tracked checks, content checks, and code-pattern checks.
- Use Python standard library only.
- Avoid `shell=True`.
- Keep clear PASS/WARNING/FAIL output.
- Provide line-level failure details where possible.
- Avoid false positives from docs and validator forbidden lists.
- Keep sample workflows working without changes.
- Keep current internal-review disclaimers enforced.
- Never auto-delete, auto-move, auto-stage, auto-commit, or auto-push files.

Suggested internal structure:

- Path classification rules.
- File type sensitivity rules.
- Allowed documentation-context rules.
- Sample placeholder allowlist.
- Real/private blocking pattern list.
- External automation blocking pattern list.
- Git staging/tracking inspection functions.

## 12. Proposed Severity Model

### FAIL

Use FAIL for:

- Private/final path staged or tracked.
- Real contact data in a committed or staged file.
- Real price, stock, or expiry in a committed or staged file.
- External sending implementation.
- Scraping, API collection, browser automation, buyer enrichment, or credit-check implementation.
- Final quotation output.
- Privacy Guard bypass.
- `approval_block=true` bypass.
- 메디큐브/Medicube external proposal without explicit approval.

### WARNING

Use WARNING for:

- Private/final folder exists locally but is ignored and untracked.
- Policy docs mention sensitive terms.
- Generated output is ignored but exists.
- Ambiguous business terms require human review.
- Future real/private path examples appear only in documentation.

### INFO

Use INFO for:

- Sample-safe synthetic data.
- Documentation-only references.
- Validator deny-list terms.
- Placeholder contact values.
- Internal-review-only wording.

## 13. Future Validation Commands

Expected commands:

```powershell
python tests/validate_privacy_guard.py
git status --short
git ls-files
git ls-files --others --exclude-standard
git check-ignore -v data/private/example.csv
git check-ignore -v output/private/example.md
git check-ignore -v output/final/example.pdf
```

Recommended timing:

- Before commit.
- Before push.
- Before real/private data migration.
- Before and after any real/private workflow test.
- After `.gitignore` changes.
- After Privacy Guard rule changes.

## 14. Completion Criteria for Future Implementation

Privacy Guard enhancement should be considered complete only when:

- Enhanced checks are implemented.
- False positive handling is tested.
- Private/final path tests pass.
- Sample workflow still passes.
- Integrated Runner still passes.
- Operations Dashboard still passes.
- No real/private data is created.
- No external automation is added.
- No existing sample workflow is broken.
- Documentation explains PASS/WARNING/FAIL behavior.

Future implementation must remain local-only and must not add scraping, live research, APIs, browser automation, buyer enrichment, credit checks, email sending, messaging automation, quotation sending, or external sending.

## 15. Recommended Next Steps

- Step E: Optional ignored template plan, without creating templates.
- Step F: Sample-to-real mapping document.
- Step G: Manual approval gate document.
- Step H: Roadmap/task log update.
- Step I: Final review.

Do not proceed to Step E until Step D is reviewed and Privacy Guard passes.

## 16. Step D Completion Criteria

Step D passes when:

- `docs/privacy_guard_enhancement_spec.md` exists.
- No code is implemented.
- `tests/validate_privacy_guard.py` is not modified.
- `.gitignore` is not modified.
- No real data files are created.
- No `data/private`, `output/private`, or `output/final` folders are created.
- No CSV/XLSX templates are created.
- Existing automation logic is not modified.
- Privacy Guard still passes.
