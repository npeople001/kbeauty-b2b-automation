# Real/Private Validation Checklist

## 1. Purpose

This checklist must be used before introducing, processing, reviewing, or externally using any future real/private operating data.

It is documentation only. It does not create validator code, real data files, private folders, CSV/XLSX templates, external communication, scraping, APIs, browser automation, buyer enrichment, credit checks, or external data collection.

The checklist is intended to protect buyer/contact data, price data, stock data, expiry data, quotation data, supplier terms, approval records, and private business decisions before the repository is used beyond sample/internal-review workflows.

## 2. Scope

This checklist covers:

- Pre-data introduction checks
- File/folder checks
- Git/GitHub safety checks
- Privacy Guard checks
- Schema checks
- Buyer contact checks
- Price, stock, and expiry verification checks
- Approval-required brand checks
- Proposal and quotation checks
- Dashboard/report checks
- External communication checks
- Final approval checks

All items should be treated as required before any real/private workflow is approved.

## 3. Pre-Data Introduction Checklist

Complete these checks before any future real/private data is introduced:

- [ ] Confirm Task 010 Privacy Guard is passing.
- [ ] Confirm repository `git status --short` is clean or contains only reviewed safe changes.
- [ ] Confirm `.gitignore` covers planned real/private paths and sensitive filename patterns.
- [ ] Confirm no real data is currently committed.
- [ ] Confirm `data/private/**`, `output/private/**`, and `output/final/**` are not tracked.
- [ ] Confirm the operator understands that real/private files must not be pushed to GitHub.
- [ ] Confirm a manual approval owner is defined.
- [ ] Confirm backup/storage policy is defined outside GitHub.
- [ ] Confirm sample workflows remain sample/internal-review only.
- [ ] Confirm real workflow support has separate approval before use.

Stop if any item fails.

## 4. File and Folder Checklist

Planned future paths:

- `data/private/**`
- `output/private/**`
- `output/final/**`

Required checks:

- [ ] Confirm these folders are not tracked.
- [ ] Confirm these folders are not created until approved.
- [ ] Confirm files inside these folders are never committed.
- [ ] Confirm `output/final/**` remains blocked until a separate final quotation process exists.
- [ ] Confirm sample workflows do not read from private or final paths.
- [ ] Confirm generated sample outputs do not write to private or final paths.

Policy:

- `data/private/**` is for future real input data only after approval.
- `output/private/**` is for future real-data internal-review outputs only after approval.
- `output/final/**` is outside the current automation scope.

## 5. Git/GitHub Safety Checklist

Run these commands before and after any future real/private workflow test:

```powershell
git status --short
git diff --name-only
git ls-files --others --exclude-standard
git check-ignore -v data/private/<example_file>
git check-ignore -v output/private/<example_file>
git check-ignore -v output/final/<example_file>
```

Required checks:

- [ ] Confirm no private files are staged.
- [ ] Confirm no private files are tracked.
- [ ] Confirm no real buyer/contact files are staged.
- [ ] Confirm no real price/stock/expiry files are staged.
- [ ] Confirm no final quotation files are staged.
- [ ] Confirm no external-ready proposal or quotation files are staged.

Rules:

- Do not use `git add -f` on private/final paths.
- Do not commit real buyer/contact/price/stock/expiry/final quotation files.
- Stop immediately if private files appear as staged or tracked.
- Do not commit if file purpose is ambiguous.

## 6. Privacy Guard Checklist

Run Privacy Guard before and after any real/private workflow test:

```powershell
python tests/validate_privacy_guard.py
```

Required checks:

- [ ] Confirm Privacy Guard PASS before proceeding.
- [ ] Confirm Privacy Guard PASS after any workflow test.
- [ ] Treat Privacy Guard failure as blocking for commit and workflow execution.
- [ ] Review any warning before commit.
- [ ] Confirm private path detection is treated as blocking.

Future Privacy Guard should detect:

- Private paths such as `data/private/**`, `output/private/**`, and `output/final/**`
- Buyer contact columns
- Real price, stock, and expiry files
- Final quotation files
- External-ready wording
- External sending logic
- Scraping, API, browser automation, buyer enrichment, or credit-check logic

## 7. Schema Checklist

For each future real/private file category, confirm:

- [ ] Required fields exist.
- [ ] Sensitive fields are marked.
- [ ] Allowed values are respected.
- [ ] Approval fields are present where relevant.
- [ ] Verification fields are present where relevant.
- [ ] Manual review fields are present.
- [ ] Missing required fields block workflow.
- [ ] Commit policy is clear and private by default.

Categories to check:

- [ ] Real buyer master
- [ ] Buyer contact
- [ ] Opportunity notes
- [ ] Price inputs
- [ ] Stock inputs
- [ ] Expiry inputs
- [ ] Quotation inputs
- [ ] Approval records
- [ ] Manual review records

Missing or malformed required fields should block real/private workflow execution.

## 8. Buyer Contact Checklist

Required checks:

- [ ] `contact_email` must not appear in dashboards by default.
- [ ] `contact_phone` must not appear in dashboards by default.
- [ ] `wechat_id` must not appear in dashboards by default.
- [ ] `whatsapp` must not appear in dashboards by default.
- [ ] Contact data must not appear in committed files.
- [ ] Contact data must not appear in sample workflow outputs.
- [ ] Contact data must not be externally messaged automatically.
- [ ] Manual contact use requires human review.
- [ ] Contact permission status must be reviewed before outreach.
- [ ] Real contact data must remain local/private or in approved secure storage.

Any contact exposure in committed output is blocking.

## 9. Price, Stock, and Expiry Checklist

Required price checks:

- [ ] `price_source` exists.
- [ ] `price_confirmed_at` exists.
- [ ] `price_confirmed_by` exists.
- [ ] Price currency is present when price is present.
- [ ] Price freshness is reviewed manually.

Required stock checks:

- [ ] `stock_source` exists.
- [ ] `stock_confirmed_at` exists.
- [ ] `stock_confirmed_by` exists.
- [ ] Stock status is reviewed manually.
- [ ] Available quantity is reviewed manually if used.

Required expiry checks:

- [ ] `expiry_source` exists.
- [ ] `expiry_confirmed_at` exists.
- [ ] `expiry_confirmed_by` exists.
- [ ] Expiry date format is reviewed.
- [ ] Shelf-life suitability is reviewed manually.

Verification checks:

- [ ] `verification_status` is `pass`, `review_needed`, `fail`, or an approved equivalent.
- [ ] Unverified price blocks final quotation.
- [ ] Unverified stock blocks final quotation.
- [ ] Unverified expiry blocks final quotation.
- [ ] Dashboard/report PASS does not count as commercial approval.

## 10. Approval-Required Brand Checklist

Required checks:

- [ ] `approval_required` is checked.
- [ ] `approval_block` is checked.
- [ ] `proposal_allowed` is checked.
- [ ] `approval_status` is checked.
- [ ] `approval_owner` is checked.
- [ ] 메디큐브/Medicube remains approval-required unless explicit approval is recorded.
- [ ] `approval_block=true` overrides `priority_tier` and `score_total`.
- [ ] Approval cannot be inferred from high buyer score.
- [ ] Approval cannot be inferred from high order quantity.
- [ ] Approval cannot be inferred from buyer interest.
- [ ] Approval-required brands are not proposed externally without explicit approval.

Blocking rule:

- If `approval_block=true` and no explicit approval exists, external proposal, pitch, quotation, public content, and ad copy must not proceed.

## 11. Proposal and Quotation Checklist

Required checks:

- [ ] Proposal messages are draft/internal-review only.
- [ ] Quotation outputs are draft/internal-review only.
- [ ] PASS does not mean final commercial approval.
- [ ] Price requires manual review.
- [ ] Stock requires manual review.
- [ ] Expiry requires manual review.
- [ ] MOQ requires manual review.
- [ ] Delivery lead time requires manual review.
- [ ] Tax requires manual review.
- [ ] Shipping requires manual review.
- [ ] Duties require manual review.
- [ ] Payment terms require manual review.
- [ ] Incoterms require manual review.
- [ ] `output/final/**` is not used.
- [ ] No external-ready/final quotation language appears.
- [ ] No automatic sending is implemented.

Quotation validation PASS means structure and safety checks passed. It does not mean final commercial terms are approved.

## 12. Dashboard and Report Checklist

Required checks:

- [ ] Dashboards must not expose contact fields.
- [ ] Dashboards must not expose real price details by default.
- [ ] Dashboards must not expose real stock details by default.
- [ ] Dashboards must not expose real expiry details by default.
- [ ] Dashboards must show `approval_block` clearly.
- [ ] Dashboards must show 메디큐브/Medicube approval-required warnings.
- [ ] Dashboards must show internal-review-only disclaimers.
- [ ] Dashboard PASS does not mean external approval.
- [ ] Report PASS does not mean external approval.
- [ ] `score_total` is not buyer authenticity.
- [ ] `score_total` is not creditworthiness.
- [ ] `score_total` is not purchase probability.

Reports and dashboards are operating summaries only unless a separate approved external-use process exists.

## 13. External Communication Checklist

Confirm the repository still has no:

- [ ] Email sending
- [ ] DM sending
- [ ] WeChat sending
- [ ] WhatsApp sending
- [ ] Quotation sending
- [ ] External sending
- [ ] Automatic buyer outreach
- [ ] Scraping
- [ ] Live research
- [ ] API data collection
- [ ] Browser automation
- [ ] Buyer enrichment
- [ ] Credit checks

Any external communication requires separate manual approval and a separate process outside the current automation scope.

## 14. Final Approval Checklist

Before any external use, confirm:

- [ ] Real/private data checked.
- [ ] `approval_block=false` or approved exception recorded.
- [ ] 메디큐브/Medicube or other approval-required brand approval recorded when relevant.
- [ ] Price verified.
- [ ] Stock verified.
- [ ] Expiry verified.
- [ ] MOQ verified.
- [ ] Delivery, tax, shipping, duties, payment terms, and incoterms reviewed.
- [ ] Quotation manually approved.
- [ ] Proposal manually approved.
- [ ] External communication manually approved.
- [ ] Privacy Guard PASS.
- [ ] Git status checked.
- [ ] No private files staged.
- [ ] No final quotation generated by unapproved automation.

No external use should proceed until all relevant manual gates pass.

## 15. Blocking Conditions

Stop the workflow if any of these conditions occur:

- Privacy Guard failure.
- Private path staged.
- Real data tracked.
- Contact fields exposed in committed output.
- Unverified price used for final quotation.
- Unverified stock used for final quotation.
- Unverified expiry used for final quotation.
- `approval_block=true` without explicit approval.
- 메디큐브/Medicube proposed without approval.
- `output/final/**` generated without approved process.
- External sending logic detected.
- Scraping logic detected.
- API collection logic detected.
- Buyer enrichment logic detected.
- Credit-check logic detected.
- Dashboard or report presents PASS as external approval.
- Quotation draft is presented as final commercial offer.

Blocking issues must be resolved manually and reviewed before work continues.

## 16. Recommended Future Automation

Future automation may convert some checklist items into validators, but only after separate approval.

Potential future validators:

- `validate_real_private_paths.py`
- `validate_real_private_schema.py`
- `validate_real_private_approval_gate.py`
- `validate_final_quotation_gate.py`

Future validators must:

- Use local files only.
- Avoid real/private test fixtures unless approved.
- Avoid external data collection.
- Avoid external sending.
- Report PASS/WARNING/FAIL clearly.
- Never delete, move, rewrite, stage, commit, or push files automatically.

## 17. Completion Criteria

Step C passes when:

- `docs/real_private_validation_checklist.md` exists.
- Checklist covers manual and automated validation requirements.
- No code is implemented.
- No validator code is created.
- No real/private/final folders are created.
- No CSV/XLSX templates are created.
- `.gitignore` is not modified.
- Existing automation logic is not modified.
- Privacy Guard still passes.

## 18. Remaining Risks

- A checklist is not technical enforcement.
- Privacy Guard is not a full DLP system.
- Human review remains required.
- Real data can still be misplaced if operating discipline is weak.
- Commercial data may become stale between confirmation and external use.
- Approval-required brand misuse remains business-critical.
- External communication remains outside current scope.
