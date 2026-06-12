# Approval Gate Validator Plan

## 1. Purpose

Task 015 plans a future Approval Gate Validator for K-beauty B2B internal automation outputs.

The future validator should check whether approval-related blockers are present before proposal drafts, quotation drafts, dashboards, reports, or other internal-review outputs continue through the internal workflow.

The future validator is a guardrail only:

- It does not approve external use.
- It does not send messages.
- It does not create final quotations.
- It does not verify buyer authenticity.
- It does not verify buyer creditworthiness.
- It only checks approval-related conditions and reports PASS, WARNING, or FAIL.

The validator should help prevent internal-review outputs from being mistaken for approved external proposals, final quotations, or send-ready communications.

## 2. Scope

The future Approval Gate Validator should check approval gate conditions for:

- Brands.
- Approval-required brands.
- 메디큐브/Medicube.
- Buyer/contact approval.
- Proposal draft approval.
- Quotation draft approval.
- Final quotation blockers.
- External communication blockers.
- Dashboard/report warning conditions.

It should operate only on local files and should remain aligned with the current internal-review workflow.

## 3. Non-goals

Task 015 and the future validator must not:

- Create real/private data.
- Create private/final folders.
- Create private templates.
- Enable real/private workflow.
- Approve final quotation.
- Send emails, DMs, WeChat messages, WhatsApp messages, or quotations.
- Scrape, crawl, call APIs, enrich buyers, or credit-check buyers.
- Replace human approval.
- Override manual approval rules.

The validator may block unsafe states, but it must never grant business approval.

## 4. Planned Validator Name and Location

Recommended future validator:

- `tests/validate_approval_gate.py`

This file must not be created in Task 015 Step A.

Implementation should happen only in a later step after this plan is reviewed and approved.

## 5. Input Categories

The future validator may inspect these categories:

- Sample/internal-review files.
- Future private approval records.
- Future proposal drafts.
- Future quotation drafts.
- Future dashboard/report outputs.
- Brand master/reference files.

Planned private paths may be referenced as examples only:

- `data/private/approval_records_real.csv`
- `data/private/manual_review_records_real.csv`
- `data/private/quotation_inputs_real.csv`
- `output/private/proposal_messages_real.*`
- `output/private/quotation_drafts_real.*`
- `output/private/operations_dashboard_real.md`

These paths must not be created in Task 015 Step A.

## 6. Approval Fields

The future validator should understand these approval-related fields:

- `approval_required`
- `approval_block`
- `proposal_allowed`
- `approval_status`
- `approval_owner`
- `approval_date`
- `approval_expiry`
- `approval_notes`
- `exception_reason`
- `review_required_next`
- `brand_name`
- `buyer_id`
- `related_output_file`
- `approval_type`

These fields may appear in brand records, future private approval records, future manual review records, proposal draft metadata, quotation draft metadata, dashboard summaries, or report summaries.

## 7. Allowed Approval Status Values

Allowed future approval status values:

- `not_required`
- `required`
- `pending`
- `approved`
- `rejected`
- `expired`
- `exception_approved`
- `review_needed`

Approval status must be explicit. It must not be inferred from buyer score, priority tier, order quantity, buyer interest, dashboard status, or validator PASS.

## 8. Blocking Conditions

Future FAIL conditions should include:

- `approval_block=true` and `approval_status` is not `approved` or `exception_approved`.
- `approval_required=true` and `approval_status` is missing.
- `approval_required=true` and `approval_status` is `pending`, `rejected`, `expired`, or `review_needed`.
- `proposal_allowed=false` for a proposal draft.
- 메디큐브/Medicube appears in proposal or quotation context without an approved approval record.
- `final quotation`, `final_quotation`, `final_quote`, `approved_quotation`, or `commercially_approved` wording appears before a final quotation gate exists.
- External communication, `send-ready`, or `external-ready` wording appears before approval.
- `approval_owner` is missing for `approved` or `exception_approved` records.
- `approval_date` is missing for `approved` or `exception_approved` records.
- `approval_expiry` is expired.
- `related_output_file` references `output/final/**` before a final quotation process exists.

FAIL should stop commit preparation or workflow promotion until reviewed and corrected.

## 9. Warning Conditions

Future WARNING conditions should include:

- `approval_required=true` but the file is clearly internal-review draft only.
- `approval_status=not_required` but the brand appears in a sensitive or high-risk category.
- Approval record has notes but no expiry.
- Dashboard/report mentions approval blockers.
- Sample data has approval placeholders.
- `approval_owner` uses placeholder value.
- Manual review is recommended but not blocking yet.

WARNING should not approve external use. It should signal that human review is still required.

## 10. Info Conditions

Future INFO conditions should include:

- `approval_required=false` and `proposal_allowed=true` in sample-safe data.
- `approval_status=not_required` in sample-safe data.
- `approval_block=false` in sample/internal-review context.
- Documentation mentions approval gate as policy.

INFO should be used for safe context reporting only.

## 11. Medicube-specific Rule

메디큐브/Medicube remains approval-required.

Rules:

- 메디큐브/Medicube must not be proposed externally without explicit approval.
- `approval_block=true` overrides `score_total`, `priority_tier`, buyer interest, and requested quantity.
- The future validator should fail if 메디큐브/Medicube is found in proposal or quotation context without an approved approval record.
- The future validator should not fail merely because documentation mentions 메디큐브/Medicube policy.
- The future validator should allow policy statements that clearly say 메디큐브/Medicube is blocked, excluded, approval-required, or internal-review only.

## 12. Proposal Gate Rules

Proposal drafts are internal-review only.

Rules:

- `proposal_allowed=false` blocks proposal use.
- `approval_required=true` requires `approved` or `exception_approved` before external use.
- `approval_block=true` blocks buyer-facing proposal copy unless an approved exception exists.
- External-ready or send-ready wording should fail unless external communication approval exists.
- No automatic sending is allowed.
- Proposal draft PASS does not mean send-ready approval.

## 13. Quotation Gate Rules

Quotation drafts are internal-review only.

Rules:

- Final quotation remains out of scope.
- `final_quotation`, `final_quote`, `approved_quotation`, and `commercially_approved` markers are blockers unless a future final quotation process exists.
- Price, stock, expiry, MOQ, payment, shipping, tax, duties, and incoterms must be verified separately.
- `approval_block=true` blocks external-ready quotation.
- PASS does not mean final commercial approval.

The future validator should not calculate commercial values, approve prices, or convert quotation drafts into final quotations.

## 14. Dashboard and Report Rules

Dashboards and reports are internal-review only.

Rules:

- Dashboard PASS does not mean approval.
- Report PASS does not mean approval.
- Dashboard/report outputs may surface blockers and warnings.
- Dashboard/report outputs must not expose private contact or commercial terms.
- `output/private` dashboard outputs remain planned only and must not be committed.
- `output/final` remains blocked until a separate approved final process exists.

## 15. File Sensitivity and False-positive Rules

The future validator must avoid false positives while still blocking unsafe outputs.

Rules:

- `docs/*.md` can mention approval rules as policy.
- `tests/*.py` can contain validator patterns.
- Sample/internal-review files can contain placeholders.
- Strict proposal, quotation, and generated output files should be checked more aggressively in future implementation.
- No failure should occur from documentation-only policy references.
- Policy wording such as "must not be externally proposed" should not be treated as an unsafe recommendation.
- Actual proposal/quotation language that appears buyer-facing, external-ready, send-ready, final, or commercially approved should be treated as higher risk.

## 16. Planned Synthetic Tests

Future implementation should use synthetic tests without creating real/private files.

Planned synthetic cases:

- Synthetic brand row with `approval_block=true` should FAIL.
- Synthetic 메디큐브/Medicube proposal context without approval should FAIL.
- Synthetic `proposal_allowed=false` should FAIL.
- Synthetic approved record missing `approval_owner` should FAIL.
- Synthetic expired approval should FAIL.
- Synthetic documentation mention should PASS.
- Synthetic sample placeholder should PASS.
- Synthetic internal-review warning should WARNING.

Synthetic tests should run in memory or in safe temporary paths. They must not create `data/private`, `data/private/templates`, `output/private`, or `output/final`.

## 17. Validation Commands for Future Implementation

Future implementation should use:

```powershell
python tests/validate_privacy_guard.py
python tests/validate_privacy_guard.py --mode staged-only
python tests/validate_privacy_guard.py --self-test
python tests/validate_approval_gate.py
python tests/validate_approval_gate.py --self-test
python -m py_compile tests/validate_approval_gate.py
python tests/validate_integrated_runner.py --check-summary --summary output/internal_workflow_summary.md
python tests/validate_operations_dashboard.py --skip-dashboard
```

`tests/validate_approval_gate.py` does not exist yet and must not be created in this planning step.

## 18. Recommended Implementation Sequence

Recommended future Task 015 sequence:

- Step A: Approval gate validator plan document.
- Step B: Baseline approval fields and sample data review.
- Step C: Create minimal `tests/validate_approval_gate.py` skeleton with self-test only.
- Step D: Implement brand approval blocker.
- Step E: Implement Medicube-specific approval blocker.
- Step F: Implement proposal/quotation approval blockers.
- Step G: Implement warning/info output and false-positive handling.
- Step H: Regression validation and README update.
- Step I: Roadmap/task log update and final review.

Do not implement the validator until Step A is reviewed.

## 19. Completion Criteria for Task 015 Planning

Task 015 Step A passes when:

- `docs/approval_gate_validator_plan.md` exists.
- No code is implemented.
- No tests are created.
- `tests/validate_privacy_guard.py` is not modified.
- `.gitignore` is not modified.
- No real data files are created.
- No `data/private`, `data/private/templates`, `output/private`, or `output/final` folders are created.
- No CSV/XLSX templates are created.
- Existing automation logic is not modified.
- Privacy Guard passes.
- Staged-only Privacy Guard passes.
- Privacy Guard self-test passes.

## 20. Recommended Next Step

Recommended next step:

- Task 015 Step B: baseline approval fields and sample data review.

Do not implement `tests/validate_approval_gate.py` until Step A plan is reviewed and Step B confirms the baseline fields and sample data contexts.

