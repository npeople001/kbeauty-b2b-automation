# Manual Approval Gate

## 1. Purpose

This approval gate prevents internal automation outputs from being treated as externally approved business actions.

Current automation may generate internal-review drafts, summaries, scores, reports, and dashboards. It must not approve external use. A human approval owner must review and approve before any external proposal, quotation, message, dashboard/report, or commercial communication is used outside internal review.

Validator, runner, dashboard, report, or quotation `PASS` means only that a defined internal validation check passed. It does not mean external approval, final commercial approval, buyer verification, creditworthiness, purchase certainty, or legal/commercial readiness.

## 2. Scope

This gate applies to:

- Real/private buyer data.
- Buyer contact usage.
- Proposal message drafts.
- Quotation drafts.
- Dashboard/report outputs.
- Approval-required brands.
- Medicube.
- Price, stock, expiry, MOQ, payment, shipping, tax, duties, and incoterms checks.
- Final quotation.
- External communication.

## 3. Core Principle

- Automation may prepare internal-review outputs.
- Automation must not approve external use.
- A human approval owner must review and approve before external proposal, quotation, or communication.
- PASS from validators, runners, dashboards, or reports does not mean external approval.
- Approval cannot be inferred from `score_total`, `priority_tier`, buyer interest, requested quantity, or dashboard status.

## 4. Approval Stages

Required stages:

1. Data readiness approval.
2. Brand approval gate.
3. Buyer/contact approval gate.
4. Price, stock, and expiry verification approval.
5. Proposal draft approval gate.
6. Quotation draft approval gate.
7. Final quotation gate.
8. External communication approval gate.
9. Dashboard/report approval gate.

Each stage should be completed by a responsible human owner before external use.

## 5. Data Readiness Approval

Checklist:

- [ ] Privacy Guard PASS.
- [ ] `git status --short` checked.
- [ ] No private files staged.
- [ ] No real data committed.
- [ ] Real/private files stored outside GitHub.
- [ ] Schema requirements met.
- [ ] Sensitive fields identified.
- [ ] Manual review owner assigned.
- [ ] `data/private/**`, `output/private/**`, and `output/final/**` not used by sample workflow.
- [ ] Real/private workflow approved separately before use.

Data readiness approval is required before real/private data is processed, reviewed, summarized, or used for any buyer-facing decision.

## 6. Brand Approval Gate

Checklist:

- [ ] `approval_required` checked.
- [ ] `approval_block` checked.
- [ ] `proposal_allowed` checked.
- [ ] `approval_status` checked.
- [ ] `approval_owner` recorded.
- [ ] `approval_date` recorded where applicable.
- [ ] `approval_notes` reviewed.
- [ ] Medicube approval recorded before external proposal.
- [ ] `approval_block=true` blocks external proposal unless explicit approved exception exists.

Rules:

- `priority_tier=A` cannot override `approval_block`.
- High `score_total` cannot override `approval_block`.
- Approval cannot be inferred from buyer score.
- Approval cannot be inferred from buyer interest.
- Approval cannot be inferred from order quantity.
- Approval records containing real owners, notes, buyer-specific scope, or commercial context must not be committed.

## 7. Buyer/Contact Approval Gate

Checklist:

- [ ] Buyer identity reviewed manually.
- [ ] Buyer contact source reviewed manually.
- [ ] `contact_email` not exposed in committed outputs.
- [ ] `contact_phone` not exposed in committed outputs.
- [ ] `wechat_id` not exposed in committed outputs.
- [ ] `whatsapp` not exposed in committed outputs.
- [ ] Contact method approved manually.
- [ ] No automatic outreach.
- [ ] No buyer authenticity inferred from `score_total`.
- [ ] No creditworthiness inferred from `score_total`.
- [ ] No credit check automation.

Rules:

- Contact data is privacy-sensitive.
- Real contact data must remain private or in approved secure storage.
- Any buyer outreach must be manual and separately approved.
- Buyer scoring is internal prioritization only.

## 8. Price, Stock, and Expiry Approval Gate

Checklist:

- [ ] `price_source` verified.
- [ ] `price_confirmed_at` recorded.
- [ ] `price_confirmed_by` recorded.
- [ ] `stock_source` verified.
- [ ] `stock_confirmed_at` recorded.
- [ ] `stock_confirmed_by` recorded.
- [ ] `expiry_source` verified.
- [ ] `expiry_confirmed_at` recorded.
- [ ] `expiry_confirmed_by` recorded.
- [ ] MOQ confirmed.
- [ ] Delivery lead time confirmed.
- [ ] Tax reviewed.
- [ ] Shipping reviewed.
- [ ] Duties reviewed.
- [ ] Incoterms reviewed.
- [ ] Payment terms reviewed.
- [ ] Unverified values block final quotation.

Rules:

- Price, stock, expiry, MOQ, delivery, tax, shipping, duties, incoterms, and payment terms require manual commercial review.
- Dashboard/report PASS does not mean commercial approval.
- Integrated Runner PASS does not mean commercial approval.

## 9. Proposal Draft Approval Gate

Checklist:

- [ ] Proposal message is internal draft.
- [ ] Brand approval checked.
- [ ] Buyer/contact approval checked.
- [ ] No external-ready/send-ready wording.
- [ ] No prohibited claims.
- [ ] No unapproved brand proposal.
- [ ] No automatic sending.
- [ ] Human approval recorded before external use.

Rules:

- Proposal drafts must not be externally sent from this repository.
- Cosmetic efficacy, medical, clinical, ranking, sales, certification, exclusivity, or commercial claims require verified source material and manual approval.
- Approval-required brands must be excluded unless explicit approval is recorded.

## 10. Quotation Draft Approval Gate

Checklist:

- [ ] Quotation is internal draft.
- [ ] Price verified.
- [ ] Stock verified.
- [ ] Expiry verified.
- [ ] MOQ verified.
- [ ] Payment reviewed.
- [ ] Shipping reviewed.
- [ ] Tax reviewed.
- [ ] Duties reviewed.
- [ ] Incoterms reviewed.
- [ ] Approval-required brands cleared.
- [ ] No final quotation wording unless final approval exists.
- [ ] Quotation validation PASS understood as structural/safety validation only.
- [ ] Human approval recorded before external use.

Rules:

- Quotation validation PASS does not mean final commercial approval.
- Draft quotation outputs must not be treated as final commercial offers.
- Missing or unverified commercial terms block external use.

## 11. Final Quotation Gate

`output/final/**` remains blocked until a separate final quotation process exists.

Final quotation is out of current automation scope. It requires separate manual approval, confirmed commercial terms, and a separate process. Final quotation must not be automatically sent.

Checklist:

- [ ] Final quotation owner assigned.
- [ ] Commercial terms approved.
- [ ] Brand approval approved.
- [ ] Buyer/contact approval approved.
- [ ] Legal/commercial review completed if required.
- [ ] External communication approval completed.
- [ ] Final quotation storage process approved outside normal tracked repository paths.
- [ ] No automatic sending.

## 12. External Communication Approval Gate

This gate applies to:

- Email.
- DM.
- WeChat.
- WhatsApp.
- Quotation sending.
- Buyer outreach.
- Proposal sending.

Rules:

- No automatic sending.
- No external sending from this repository.
- Human must approve message content.
- Human must approve recipient.
- Human must approve attachment/output.
- Human must verify no private/internal-only data is included.
- External communication process must be separate from current automation.

Any email, DM, WeChat, WhatsApp, quotation, buyer outreach, or proposal sending requires a separately approved manual process.

## 13. Dashboard/Report Approval Gate

Checklist:

- [ ] Dashboard/report is internal-review only.
- [ ] No contact fields exposed.
- [ ] No real price details exposed by default.
- [ ] No real stock details exposed by default.
- [ ] No real expiry details exposed by default.
- [ ] `approval_block` warnings reviewed.
- [ ] Medicube warnings reviewed.
- [ ] Dashboard PASS understood as not external approval.
- [ ] `score_total` understood as not buyer authenticity.
- [ ] `score_total` understood as not creditworthiness.
- [ ] `score_total` understood as not purchase probability.
- [ ] Dashboard/report is not externally sent.

Rules:

- Dashboards and reports summarize internal workflow status only.
- Private dashboard/report outputs must never be committed.
- Dashboard PASS does not approve proposals, quotations, or external communication.

## 14. Blocking Conditions

External use is blocked if any condition applies:

- Privacy Guard failure.
- Private file staged/tracked.
- `data/private/**`, `output/private/**`, or `output/final/**` path involved without approved process.
- `approval_block=true` without approved exception.
- Medicube proposed without approval.
- Unverified price.
- Unverified stock.
- Unverified expiry.
- Unconfirmed MOQ.
- Unconfirmed payment terms.
- Unconfirmed shipping.
- Unconfirmed tax.
- Unconfirmed duties.
- Unconfirmed incoterms.
- Proposal draft not manually approved.
- Quotation draft not manually approved.
- Final quotation process missing.
- External sending automation detected.
- Scraping logic detected.
- API collection logic detected.
- Buyer enrichment logic detected.
- Credit-check logic detected.

Blocking conditions require manual resolution and review before work continues.

## 15. Approval Record Fields

Future approval records should include:

- `approval_id`
- `approval_type`
- `related_buyer_id`
- `related_brand`
- `related_output_file`
- `approval_required`
- `approval_block`
- `approval_status`
- `approval_owner`
- `approval_date`
- `approval_notes`
- `approval_expiry`
- `exception_reason`
- `review_required_next`

Approval records containing real buyer, brand, owner, commercial, or exception notes must remain private and must not be committed.

## 16. Approval Status Values

Allowed values:

- `not_required`
- `required`
- `pending`
- `approved`
- `rejected`
- `expired`
- `exception_approved`
- `review_needed`

Approval status must be explicit. It must not be inferred automatically.

## 17. Separation From Automation

- Current automation can generate draft/internal-review outputs only.
- Approval is a manual business decision.
- Approval records are future private records.
- Approval records containing real buyer, brand, or commercial notes must not be committed.
- No approval should be inferred automatically.
- Validators can block unsafe states, but they cannot grant external approval.
- Runners and dashboards can summarize status, but they cannot grant external approval.

## 18. Recommended Future Validators

Future candidates only:

- `validate_manual_approval_gate.py`
- `validate_real_approval_records.py`
- `validate_external_use_blockers.py`
- `validate_final_quotation_gate.py`

These validators are not implemented in Step G.

Future validators must use local files only, avoid external sending/collection, and report PASS/WARNING/FAIL without modifying, deleting, staging, committing, or pushing files.

## 19. Completion Criteria

Step G passes when:

- `docs/manual_approval_gate.md` exists.
- Approval stages and blocking conditions are documented.
- No code is implemented.
- No approval workflow code is created.
- No real/private/final folders are created.
- No CSV/XLSX templates are created.
- `.gitignore` is not modified.
- `tests/validate_privacy_guard.py` is not modified.
- Existing automation logic is not modified.
- Privacy Guard still passes.

## 20. Recommended Next Steps

- Step H: Roadmap/task log update.
- Step I: Final review.

Do not proceed to Step H until Step G is reviewed and Privacy Guard passes.
