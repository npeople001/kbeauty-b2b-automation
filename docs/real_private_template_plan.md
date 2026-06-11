# Real/Private Template Plan

## 1. Purpose

This plan defines future ignored private CSV template files for real/private operations.

It does not create those templates yet. It does not create `data/private/templates/`, create real data files, create CSV/XLSX templates, implement code, modify `.gitignore`, modify Privacy Guard, or enable real/private workflows.

The goal is to document what future private templates may look like only after Privacy Guard, `.gitignore`, manual approval gates, and sample-to-real separation rules are reviewed.

## 2. Scope

Planned future template categories:

- Real buyer master template
- Buyer contact template
- Buyer opportunity notes template
- Price input template
- Stock input template
- Expiry input template
- Quotation input template
- Approval record template
- Manual review record template

All templates described here are future examples only. They must not be used by current sample workflows.

## 3. Planned Template Paths

The following paths are planned examples only:

- `data/private/templates/buyers_master_real_template.csv`
- `data/private/templates/buyer_contacts_real_template.csv`
- `data/private/templates/buyer_opportunities_real_template.csv`
- `data/private/templates/price_inputs_real_template.csv`
- `data/private/templates/stock_inputs_real_template.csv`
- `data/private/templates/expiry_inputs_real_template.csv`
- `data/private/templates/quotation_inputs_real_template.csv`
- `data/private/templates/approval_records_real_template.csv`
- `data/private/templates/manual_review_records_real_template.csv`

Rules:

- Do not create these files in Step E.
- Do not create `data/private/templates/` in Step E.
- These future files must be ignored and must never be committed.
- These future files must not contain real data unless separately approved.
- These future files must pass Privacy Guard and manual review before use.

## 4. Template Field Plan

### 4.1 Real Buyer Master Template

Planned path: `data/private/templates/buyers_master_real_template.csv`

Required columns:

- `buyer_id`
- `buyer_legal_name`
- `country`
- `buyer_type`
- `sales_channel`
- `lead_status`
- `priority`
- `created_at`
- `updated_at`

Optional columns:

- `city`
- `platform`
- `website`
- `sns_url`
- `language`
- `interested_brands`
- `interested_categories`
- `estimated_order_qty`
- `moq_fit`
- `china_relevance`
- `payment_risk`
- `repeat_purchase_potential`
- `lead_source`
- `next_action`
- `notes`

Sensitive columns:

- `buyer_legal_name`
- `website`
- `sns_url`
- `notes`

Allowed values:

- `moq_fit`: `yes`, `no`, `unknown`
- `priority`: `high`, `medium`, `low`, `hold`
- `china_relevance`: `high`, `medium`, `low`, `unknown`
- `payment_risk`: `high`, `medium`, `low`, `unknown`

Validation notes:

- `buyer_id` must be unique.
- MOQ 100+ logic must be checked.
- Real buyer authenticity is not verified by automation.

Manual review notes:

- Buyer identity, contact permission, MOQ fit, and approval-required brand interest require human review.

Commit policy:

- Private buyer master templates and filled files must not be committed.

### 4.2 Buyer Contact Template

Planned path: `data/private/templates/buyer_contacts_real_template.csv`

Required columns:

- `buyer_id`
- `contact_name`
- `contact_channel`
- `contact_permission_status`
- `contact_privacy_level`
- `updated_at`

Optional columns:

- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `address`
- `preferred_language`
- `preferred_contact_method`
- `contact_notes`

Sensitive columns:

- `contact_name`
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `address`
- `contact_notes`

Allowed values:

- `contact_channel`: `email`, `wechat`, `whatsapp`, `phone`, `sns`, `platform`, `other`
- `contact_permission_status`: `confirmed`, `needs_review`, `unknown`, `do_not_contact`
- `contact_privacy_level`: `private`, `restricted`, `internal_only`

Validation notes:

- Contact fields must not appear in dashboards by default.
- Contact values must not be copied into committed sample files.

Manual review notes:

- Human review is required before using real contact data.
- No automatic outreach is allowed.

Commit policy:

- Contact templates and filled files must not be committed.

### 4.3 Buyer Opportunity Notes Template

Planned path: `data/private/templates/buyer_opportunities_real_template.csv`

Required columns:

- `opportunity_id`
- `buyer_id`
- `opportunity_status`
- `interested_categories`
- `next_action`
- `updated_at`

Optional columns:

- `interested_brands`
- `estimated_order_qty`
- `target_price_note`
- `buyer_requirement_note`
- `internal_sales_note`
- `risk_note`
- `owner`
- `deadline`

Sensitive columns:

- `target_price_note`
- `buyer_requirement_note`
- `internal_sales_note`
- `risk_note`

Allowed values:

- `opportunity_status`: `new`, `reviewing`, `needs_info`, `proposal_draft`, `quotation_draft`, `hold`, `closed`

Validation notes:

- Approval-required brand interest must not become an automatic external recommendation.
- `approval_block` must override opportunity priority.

Manual review notes:

- Buyer need, MOQ fit, and brand approval readiness require manual review.

Commit policy:

- Opportunity templates and filled files must not be committed.

### 4.4 Price Input Template

Planned path: `data/private/templates/price_inputs_real_template.csv`

Required columns:

- `price_record_id`
- `brand_name`
- `product_name`
- `sku_or_option`
- `unit_price`
- `currency`
- `price_source`
- `price_confirmed_at`
- `price_confirmed_by`
- `verification_status`

Optional columns:

- `price_valid_until`
- `min_order_qty`
- `discount_note`
- `supplier_details`
- `distributor_details`
- `internal_margin`
- `payment_terms`
- `incoterms`
- `notes`

Sensitive columns:

- `unit_price`
- `supplier_details`
- `distributor_details`
- `internal_margin`
- `payment_terms`
- `incoterms`
- `discount_note`

Allowed values:

- `verification_status`: `pass`, `review_needed`, `fail`, `verified`, `needs_review`, `unverified`, `expired`

Validation notes:

- `unit_price` must be numeric when used.
- `currency` must exist when price exists.
- Unverified price must block final quotation.

Manual review notes:

- Price, source, validity, margin, tax, shipping, duties, payment terms, and incoterms require manual review.

Commit policy:

- Price templates and filled files must not be committed.

### 4.5 Stock Input Template

Planned path: `data/private/templates/stock_inputs_real_template.csv`

Required columns:

- `stock_record_id`
- `brand_name`
- `product_name`
- `sku_or_option`
- `stock_status`
- `stock_source`
- `stock_confirmed_at`
- `stock_confirmed_by`
- `verification_status`

Optional columns:

- `available_qty`
- `reserved_qty`
- `warehouse_note`
- `supply_status`
- `supplier_details`
- `notes`

Sensitive columns:

- `available_qty`
- `reserved_qty`
- `warehouse_note`
- `supplier_details`

Allowed values:

- `stock_status`: `in_stock`, `limited`, `out_of_stock`, `unknown`
- `supply_status`: `available`, `limited`, `unavailable`, `unknown`
- `verification_status`: `pass`, `review_needed`, `fail`, `verified`, `needs_review`, `unverified`, `expired`

Validation notes:

- Stock status must be explicit.
- Available quantity must be numeric if used.
- Unverified stock must block final quotation.

Manual review notes:

- Stock and supply availability must be rechecked before external quotation.

Commit policy:

- Stock templates and filled files must not be committed.

### 4.6 Expiry Input Template

Planned path: `data/private/templates/expiry_inputs_real_template.csv`

Required columns:

- `expiry_record_id`
- `brand_name`
- `product_name`
- `sku_or_option`
- `expiry_date`
- `expiry_source`
- `expiry_confirmed_at`
- `expiry_confirmed_by`
- `verification_status`

Optional columns:

- `lot_or_batch_note`
- `shelf_life_note`
- `buyer_expiry_requirement`
- `notes`

Sensitive columns:

- `expiry_date`
- `lot_or_batch_note`
- `buyer_expiry_requirement`

Allowed values:

- `verification_status`: `pass`, `review_needed`, `fail`, `verified`, `needs_review`, `unverified`, `expired`

Validation notes:

- `expiry_date` should use `YYYY-MM-DD` when real values are approved.
- Unverified expiry must block final quotation.

Manual review notes:

- Expiry and shelf-life suitability must be checked before external quotation.

Commit policy:

- Expiry templates and filled files must not be committed.

### 4.7 Quotation Input Template

Planned path: `data/private/templates/quotation_inputs_real_template.csv`

Required columns:

- `quotation_request_id`
- `buyer_id`
- `brand_name`
- `product_name`
- `sku_or_option`
- `requested_qty`
- `currency`
- `quotation_stage`
- `required_internal_review`
- `updated_at`

Optional columns:

- `unit_price`
- `moq`
- `delivery_lead_time`
- `price_record_id`
- `stock_record_id`
- `expiry_record_id`
- `payment_terms`
- `shipping_terms`
- `tax_note`
- `duties_note`
- `incoterms`
- `buyer_note`
- `internal_margin`
- `compliance_notes`

Sensitive columns:

- `unit_price`
- `payment_terms`
- `shipping_terms`
- `tax_note`
- `duties_note`
- `incoterms`
- `buyer_note`
- `internal_margin`

Allowed values:

- `quotation_stage`: `draft`, `internal_review`, `blocked`, `needs_confirmation`
- `required_internal_review`: `true`, `false`

Validation notes:

- `requested_qty` must be numeric.
- `approval_block=true` must block buyer-facing quotation.
- Unverified price, stock, or expiry must block final quotation.

Manual review notes:

- Price, stock, expiry, MOQ, delivery, tax, shipping, duties, payment terms, and incoterms require human approval.

Commit policy:

- Quotation templates and filled files must not be committed.

### 4.8 Approval Record Template

Planned path: `data/private/templates/approval_records_real_template.csv`

Required columns:

- `approval_record_id`
- `brand_name`
- `approval_required`
- `approval_block`
- `proposal_allowed`
- `approval_status`
- `approval_owner`
- `approval_date`
- `brand_risk_level`
- `updated_at`

Optional columns:

- `buyer_id`
- `product_name`
- `approval_scope`
- `approval_expiry_date`
- `approval_notes`
- `evidence_reference`

Sensitive columns:

- `approval_owner`
- `approval_notes`
- `evidence_reference`

Allowed values:

- `approval_required`: `true`, `false`
- `approval_block`: `true`, `false`
- `proposal_allowed`: `true`, `false`
- `approval_status`: `approved`, `rejected`, `needs_review`, `expired`, `not_requested`
- `brand_risk_level`: `high`, `medium`, `low`, `unknown`

Validation notes:

- Medicube must default to `approval_required=true`.
- `approval_block=true` must block external proposal.
- Approval status must be explicit, not inferred.
- High `priority_tier` or `score_total` must not override `approval_block`.

Manual review notes:

- Approval owner must verify approval status before external use.

Commit policy:

- Approval templates and filled files must not be committed.

### 4.9 Manual Review Record Template

Planned path: `data/private/templates/manual_review_records_real_template.csv`

Required columns:

- `review_id`
- `related_record_type`
- `related_record_id`
- `review_status`
- `review_owner`
- `reviewed_at`
- `required_next_action`

Optional columns:

- `buyer_id`
- `brand_name`
- `review_area`
- `review_notes`
- `blocking_issue`
- `resolved_at`

Sensitive columns:

- `review_owner`
- `review_notes`
- `blocking_issue`

Allowed values:

- `related_record_type`: `buyer`, `contact`, `opportunity`, `price`, `stock`, `expiry`, `quotation`, `approval`
- `review_status`: `pass`, `pass_with_caution`, `fail`, `blocked`, `needs_review`
- `review_area`: `privacy`, `brand_approval`, `commercial`, `claim`, `localization`, `quotation`, `buyer_contact`, `other`

Validation notes:

- Blocking review records must prevent external use.
- Manual review does not replace brand approval, commercial verification, or privacy review.

Manual review notes:

- Review notes must stay internal and should not appear in dashboards by default.

Commit policy:

- Manual review templates and filled files must not be committed.

## 5. Placeholder Policy

Future templates should use synthetic placeholders only.

Never use:

- Real buyer names.
- Real contact info.
- Real prices.
- Real stock values.
- Real expiry dates.
- Real supplier/distributor terms.
- Final quotation terms.

Recommended placeholder patterns:

- `BUYER_EXAMPLE_001`
- `CONTACT_NAME_EXAMPLE`
- `example@example.invalid`
- `+00-0000-0000`
- `WECHAT_EXAMPLE`
- `WHATSAPP_EXAMPLE`
- `PRICE_PLACEHOLDER`
- `STOCK_PLACEHOLDER`
- `EXPIRY_YYYY_MM_DD`
- `APPROVAL_REQUIRED_PLACEHOLDER`

Placeholders must clearly signal that they are not real business data.

## 6. Ignore Policy

Future template paths must be covered by `.gitignore` before creation:

- `data/private/**`
- `output/private/**`
- `output/final/**`

Rules:

- `git check-ignore` must confirm template paths are ignored.
- Do not use `git add -f` for private templates.
- If templates appear in `git status` as untracked, stop immediately.
- If templates are staged, unstage immediately and investigate.
- Private templates should never be committed, even when they contain placeholders.

## 7. Privacy Guard Requirements

Before future templates are created, Privacy Guard should be able to:

- Detect private path staging/tracking.
- Detect real contact fields.
- Detect real price, stock, and expiry fields.
- Detect final quotation markers.
- Distinguish safe placeholder templates from real data where possible.
- Warn if private folders exist locally.
- Fail if private files are staged or tracked.

Privacy Guard should report clear PASS/WARNING/FAIL results and should not delete, move, rewrite, stage, commit, or push files automatically.

## 8. Sample vs Private Template Separation

Sample files:

- Remain committed under `data/` when fictional and test-required.
- Must not include real contact, price, stock, or expiry data.
- Must support sample/internal-review workflows only.

Private templates:

- Must stay under `data/private/templates/`.
- Must be ignored.
- Must not be used by sample workflows.
- Must not enable real/private workflow by default.
- Must require separate approval before creation and use.

Real/private workflow support remains disabled by default.

## 9. Approval-Required Brand Template Rules

Future approval template should include:

- `brand_name`
- `approval_required`
- `approval_block`
- `proposal_allowed`
- `approval_status`
- `approval_owner`
- `approval_date`
- `approval_notes`
- `brand_risk_level`

Rules:

- Medicube must default to `approval_required=true`.
- `approval_block=true` must block external proposal.
- `approval_status` must be explicit, not inferred.
- High `priority_tier` or `score_total` must not override `approval_block`.
- Buyer interest must not override approval restrictions.

## 10. Verification Template Rules

Future price, stock, and expiry templates should include:

- `source`
- `confirmed_at`
- `confirmed_by`
- `verification_status`
- `review_notes`

Rules:

- Unverified price must block final quotation.
- Unverified stock must block final quotation.
- Unverified expiry must block final quotation.
- `verification_status` must be explicit.
- Dashboard/report PASS must not be treated as commercial approval.
- Integrated Runner PASS must not be treated as commercial approval.

## 11. Final Quotation Template Restrictions

No final quotation template should be created in v1.

Rules:

- `output/final/**` remains blocked.
- Final quotation process requires separate approval.
- Automatic quotation sending remains prohibited.
- Final quotation output must not be generated by current automation.
- Draft/internal-review quotation templates must not be presented as final commercial offers.

## 12. Future Creation Checklist

Before creating ignored templates later:

- [ ] `.gitignore` reviewed.
- [ ] Privacy Guard enhanced.
- [ ] `git check-ignore` confirmed.
- [ ] Template fields approved.
- [ ] Placeholder-only policy confirmed.
- [ ] No real data included.
- [ ] Manual approval owner assigned.
- [ ] Commit policy confirmed.
- [ ] Sample workflows confirmed unchanged.
- [ ] Private/final folders approved before creation.

Stop if any item fails.

## 13. Future Validation Commands

Expected commands:

```powershell
python tests/validate_privacy_guard.py
git status --short
git check-ignore -v data/private/templates/buyers_master_real_template.csv
git check-ignore -v output/private/example.md
git check-ignore -v output/final/example.pdf
```

These commands should be used before and after future private template creation. The `git check-ignore` commands test path protection without creating files.

## 14. Completion Criteria

Step E passes when:

- `docs/real_private_template_plan.md` exists.
- No actual templates are created.
- No private/final folders are created.
- No code is implemented.
- `.gitignore` is not modified.
- `tests/validate_privacy_guard.py` is not modified.
- Existing automation logic is not modified.
- Privacy Guard still passes.

## 15. Recommended Next Steps

- Step F: Sample-to-real mapping document.
- Step G: Manual approval gate document.
- Step H: Roadmap/task log update.
- Step I: Final review.

Do not proceed to Step F until Step E is reviewed and Privacy Guard passes.
