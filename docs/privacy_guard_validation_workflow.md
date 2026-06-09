# Privacy Guard Validation Workflow

## 1. Purpose

Privacy Guard validation is required before committing files or using real operating data in this repository.

The guard helps protect against accidental exposure of:

- Buyer/contact data
- Price data
- Stock data
- Expiry data
- Quotation data
- Supplier terms
- Private business data
- Approval-sensitive brand data

This workflow does not create, store, move, or simulate real sensitive data. It documents how to run and interpret the validator safely.

## 2. When to Run Privacy Guard

Run Privacy Guard:

- Before every commit
- Before adding new CSV files
- Before adding buyer/contact data
- Before adding price, stock, expiry, or quotation data
- Before pushing to GitHub
- Before migrating from sample to real operation
- After modifying `.gitignore`
- After modifying data or output handling rules

## 3. Commands

Default working-tree validation:

```powershell
python tests/validate_privacy_guard.py
```

Optional commands:

```powershell
python tests/validate_privacy_guard.py --root .
python tests/validate_privacy_guard.py --mode working-tree
python tests/validate_privacy_guard.py --staged-only
```

Expected PASS output includes:

- `PASS`
- `files_scanned`
- `warnings`
- `failures`

Example:

```text
PASS: privacy guard validation passed
files_scanned=66
warnings=0
failures=0
```

## 4. What the Guard Checks

The guard checks:

- Sensitive filenames and paths
- Real/private/contact/price/stock/expiry/final quotation patterns
- Sample contact placeholder safety
- `example.invalid` usage
- Placeholder phone values
- Placeholder WeChat/WhatsApp values
- Internal-review disclaimers in proposal/quotation outputs
- `메디큐브` approval-required context
- Forbidden external collection/sending implementation
- `.gitignore` protection patterns
- Sample files remain trackable

The guard uses local repository inspection only. It does not scrape, search, call APIs, automate browsers, enrich buyer data, check credit, send messages, or send quotations.

## 5. PASS / WARNING / FAIL Meaning

| Result | Meaning | Action |
| --- | --- | --- |
| PASS | Repository passes current privacy checks. | Continue with normal manual review before commit. |
| WARNING | Ambiguous issue requires human review but is not necessarily blocking. | Review the warning and decide whether a policy or validator adjustment is needed. |
| FAIL | Likely sensitive data exposure, unsafe filename/path, missing protection, or unsafe implementation. | Do not commit until resolved. |

Warnings should not be ignored. They are signals for human review.

## 6. Safe Response to Failures

When Privacy Guard fails:

- Do not auto-delete files.
- Do not auto-commit fixes.
- Identify whether the issue is actual sensitive data, unsafe filename/path, missing `.gitignore` protection, validator false positive, or documentation wording false positive.
- For actual sensitive data, remove it from tracked paths and use ignored/private storage.
- For unsafe filenames or paths, move the data only after a safe ignored/private storage plan is approved.
- For missing `.gitignore` protection, update `.gitignore` in a dedicated approved step.
- For validator false positives, fix only the validator after review.
- For ambiguous cases, require manual confirmation.

If real buyer/contact/commercial data is found in a tracked path, stop and review before staging or committing anything else.

## 7. Safe Test Strategy Without Creating Unsafe Files

This repository should avoid creating real or simulated unsafe files directly in tracked paths.

Recommended safe test approaches:

- Use `git check-ignore` with example paths instead of creating files.
- Use temporary directories outside the repository for destructive tests.
- If future fixture tests are needed, use clearly fake fixtures under a dedicated safe fixture path.
- Never create real buyer/contact/price/stock/expiry data as a test.
- Never create external-ready quotation samples with real commercial data.
- Never commit unsafe fixtures.

Example safe check without creating a file:

```powershell
git check-ignore -v data/private/buyers/buyers_real.csv
git check-ignore -v output/final/buyer_external_ready.pdf
```

These commands test ignore behavior using paths only. They do not create files.

## 8. Suggested Future Fixture Strategy

Future fixture strategy is proposed only. This step does not create fixtures.

Potential future fixture folder:

- `tests/fixtures/privacy_guard_safe/`

Potential future fixture files:

- `safe_placeholder_contacts.csv`
- `safe_placeholder_prices_sample.csv`
- `safe_forbidden_terms_documentation.md`

Rules for any future fixtures:

- Fixtures must be fictional.
- Fixtures must not include real emails or phones.
- Fixtures must not include real prices, stock, or expiry.
- Fixtures must test false-positive prevention safely.
- Unsafe fixture creation requires separate approval.
- Unsafe fixtures must never be committed.

## 9. Commit Safety Workflow

1. Run Privacy Guard:

   ```powershell
   python tests/validate_privacy_guard.py
   ```

2. Run relevant task validators.
3. Run:

   ```powershell
   git status --short
   ```

4. Review staged files manually.
5. Confirm no real/private data is staged.
6. Confirm output files are ignored or sample-safe.
7. Commit only source, docs, tests, automation, and sample-safe files.
8. Push only after human review.

## 10. Real Data Migration Workflow

Before migrating from sample to real operation:

1. Confirm repository privacy.
2. Confirm `.gitignore` protections.
3. Prepare ignored private folders only after policy approval.
4. Put real buyer/contact/price/stock/expiry data only in ignored/private paths.
5. Do not copy real data into `*_sample.csv` files.
6. Run Privacy Guard before and after migration.
7. Validate automation outputs remain internal-review only.
8. Do not externally send generated outputs automatically.

Real operating data should remain outside tracked sample paths.

## 11. Limitations

Privacy Guard is not a full data loss prevention system.

Limitations:

- It cannot guarantee all sensitive data is detected.
- It does not validate commercial accuracy.
- It does not verify buyer authenticity.
- It does not verify price, stock, expiry, supply, payment terms, or incoterms.
- It does not replace human review.
- It does not approve external use of proposal drafts, quotation drafts, reports, or content plans.

Human review remains required before any external use.

## 12. Recommended Next Step

After Step F:

- Step G should update `docs/automation_roadmap.md` and `docs/task_log.md` for Task 010 completion pending final review.
- Step H should perform the Task 010 final review.

Do not proceed to Task 011, Integrated Runner, dashboard work, scraping, live research, APIs, browser automation, buyer enrichment, credit checks, email sending, messaging automation, quotation sending, or external sending as part of Step F.
