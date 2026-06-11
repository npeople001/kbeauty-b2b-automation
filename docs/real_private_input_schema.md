# Real/Private Input Schema

## 1. Purpose

This document defines the planned schema for future real/private operating input files.

It is preparation only. It does not create real data files, approve real data usage, create private folders, create CSV/XLSX templates, implement code, or enable real workflows.

The goal is to define how future real buyer, contact, price, stock, expiry, quotation, approval, and manual review inputs should be structured before any real/private operation is approved.

## 2. Scope

Planned real/private input categories:

- Real buyer master
- Real buyer contact
- Real buyer opportunity notes
- Real price inputs
- Real stock inputs
- Real expiry inputs
- Real quotation inputs
- Real approval records
- Real manual review records

These categories are for future design only. Current sample workflows must continue to use sample files and must not read private paths.

## 3. Planned File Paths

The following paths are examples only. They are not created in this step.

| Planned file | Purpose | Commit policy |
| --- | --- | --- |
| `data/private/buyers_master_real.csv` | Future real buyer master records. | Must not be committed to GitHub. |
| `data/private/buyer_contacts_real.csv` | Future real buyer contact records. | Must not be committed to GitHub. |
| `data/private/buyer_opportunities_real.csv` | Future real buyer opportunity and sales notes. | Must not be committed to GitHub. |
| `data/private/price_inputs_real.csv` | Future real price and commercial price source inputs. | Must not be committed to GitHub. |
| `data/private/stock_inputs_real.csv` | Future real stock and supply availability inputs. | Must not be committed to GitHub. |
| `data/private/expiry_inputs_real.csv` | Future real expiry and shelf-life inputs. | Must not be committed to GitHub. |
| `data/private/quotation_inputs_real.csv` | Future real quotation request inputs. | Must not be committed to GitHub. |
| `data/private/approval_records_real.csv` | Future real approval records. | Must not be committed to GitHub. |
| `data/private/manual_review_records_real.csv` | Future real manual review records. | Must not be committed to GitHub. |

Rules:

- These files must not be created in Step B.
- These files must not be committed to GitHub.
- These files require Privacy Guard validation and separate approval before use.
- These files must remain outside sample workflows unless a future approved real workflow is designed.

## 4. Field-Level Schema

### 4.1 Real Buyer Master

Planned file: `data/private/buyers_master_real.csv`

Required fields:

- `buyer_id`
- `buyer_legal_name`
- `country`
- `buyer_type`
- `sales_channel`
- `lead_status`
- `priority`
- `created_at`
- `updated_at`

Optional fields:

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

Sensitive fields:

- `buyer_legal_name`
- `website` if private or buyer-specific
- `sns_url` if tied to a real buyer/contact
- `notes` if it contains private business context

Validation rules:

- `buyer_id` must be unique.
- `buyer_legal_name` must not be blank for real operation.
- `estimated_order_qty >= 100` should map to `moq_fit=yes`.
- `estimated_order_qty` from 1 to 99 should map to `moq_fit=no`.
- Blank, unknown, 0, or non-numeric `estimated_order_qty` should map to `moq_fit=unknown`.
- `lead_status` and `priority` must use controlled values defined by the buyer lead schema or a future approved real schema.
- Real buyer authenticity is not verified by this repository.

Allowed values where applicable:

- `moq_fit`: `yes`, `no`, `unknown`
- `china_relevance`: `high`, `medium`, `low`, `unknown`
- `payment_risk`: `high`, `medium`, `low`, `unknown`
- `repeat_purchase_potential`: `high`, `medium`, `low`, `unknown`
- `priority`: `high`, `medium`, `low`, `hold`

Manual review requirements:

- Confirm buyer identity and contact permission outside automation.
- Confirm MOQ fit before external proposal.
- Confirm approval-required brand restrictions before proposal or quotation.
- Confirm payment risk is a manual indicator only, not credit verification.

Commit policy:

- Real buyer master files must not be committed.

### 4.2 Real Buyer Contact

Planned file: `data/private/buyer_contacts_real.csv`

Required fields:

- `buyer_id`
- `contact_name`
- `contact_channel`
- `contact_permission_status`
- `contact_privacy_level`
- `updated_at`

Optional fields:

- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `address`
- `preferred_language`
- `preferred_contact_method`
- `contact_notes`

Sensitive fields:

- `contact_name`
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `address`
- `contact_notes`

Validation rules:

- `buyer_id` must match a real buyer master record.
- At least one contact method may be present for operation, but contact details must not be printed to dashboards by default.
- Contact fields must not be written to public, sample, or external-ready outputs.
- Contact permission should be reviewed before external communication.

Allowed values where applicable:

- `contact_channel`: `email`, `wechat`, `whatsapp`, `phone`, `sns`, `platform`, `other`
- `contact_permission_status`: `confirmed`, `needs_review`, `unknown`, `do_not_contact`
- `contact_privacy_level`: `private`, `restricted`, `internal_only`

Manual review requirements:

- Confirm permission to contact.
- Mask or exclude contact details from dashboard and summary outputs.
- Review local privacy obligations before sharing internally.

Commit policy:

- Real buyer contact files must not be committed.

### 4.3 Real Buyer Opportunity Notes

Planned file: `data/private/buyer_opportunities_real.csv`

Required fields:

- `opportunity_id`
- `buyer_id`
- `opportunity_status`
- `interested_categories`
- `next_action`
- `updated_at`

Optional fields:

- `interested_brands`
- `estimated_order_qty`
- `target_price_note`
- `buyer_requirement_note`
- `internal_sales_note`
- `risk_note`
- `owner`
- `deadline`

Sensitive fields:

- `target_price_note`
- `buyer_requirement_note`
- `internal_sales_note`
- `risk_note`

Validation rules:

- `buyer_id` must match a real buyer master record.
- Approval-required brand interest must not become an automatic recommendation.
- MOQ and approval readiness must be reviewed separately.
- Opportunity priority must not override `approval_block`.

Allowed values where applicable:

- `opportunity_status`: `new`, `reviewing`, `needs_info`, `proposal_draft`, `quotation_draft`, `hold`, `closed`

Manual review requirements:

- Confirm buyer need, MOQ fit, and brand approval status before proposal.
- Keep subjective notes internal.

Commit policy:

- Real buyer opportunity files must not be committed.

### 4.4 Real Price Inputs

Planned file: `data/private/price_inputs_real.csv`

Required fields:

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

Optional fields:

- `price_valid_until`
- `min_order_qty`
- `discount_note`
- `supplier_details`
- `distributor_details`
- `internal_margin`
- `payment_terms`
- `incoterms`
- `notes`

Sensitive fields:

- `unit_price`
- `real negotiated price`
- `supplier_details`
- `distributor_details`
- `internal_margin`
- `payment_terms`
- `incoterms`
- `discount_note`

Validation rules:

- `unit_price` must be numeric when used for draft calculation.
- `currency` must be present when `unit_price` is present.
- `verification_status` must be `verified` before final quotation review.
- Missing or stale price data must block final quotation.

Allowed values where applicable:

- `verification_status`: `verified`, `needs_review`, `unverified`, `expired`

Manual review requirements:

- Confirm price, currency, validity period, supplier/distributor source, and margin before external use.
- Confirm tax, shipping, duties, insurance, discounts, payment terms, and incoterms separately.

Commit policy:

- Real price files must not be committed.

### 4.5 Real Stock Inputs

Planned file: `data/private/stock_inputs_real.csv`

Required fields:

- `stock_record_id`
- `brand_name`
- `product_name`
- `sku_or_option`
- `stock_status`
- `stock_source`
- `stock_confirmed_at`
- `stock_confirmed_by`
- `verification_status`

Optional fields:

- `available_qty`
- `reserved_qty`
- `warehouse_note`
- `supply_status`
- `supplier_details`
- `notes`

Sensitive fields:

- `real stock quantity`
- `available_qty`
- `reserved_qty`
- `warehouse_note`
- `supplier_details`

Validation rules:

- `stock_status` must be present.
- `available_qty` must be numeric if present.
- `verification_status` must be `verified` before final quotation review.
- Missing or unverified stock must block final quotation.

Allowed values where applicable:

- `stock_status`: `in_stock`, `limited`, `out_of_stock`, `unknown`
- `supply_status`: `available`, `limited`, `unavailable`, `unknown`
- `verification_status`: `verified`, `needs_review`, `unverified`, `expired`

Manual review requirements:

- Reconfirm stock before quotation.
- Confirm available quantity, reserved quantity, and supply availability manually.

Commit policy:

- Real stock files must not be committed.

### 4.6 Real Expiry Inputs

Planned file: `data/private/expiry_inputs_real.csv`

Required fields:

- `expiry_record_id`
- `brand_name`
- `product_name`
- `sku_or_option`
- `expiry_date`
- `expiry_source`
- `expiry_confirmed_at`
- `expiry_confirmed_by`
- `verification_status`

Optional fields:

- `lot_or_batch_note`
- `shelf_life_note`
- `buyer_expiry_requirement`
- `notes`

Sensitive fields:

- `real expiry date`
- `lot_or_batch_note`
- `buyer_expiry_requirement`

Validation rules:

- `expiry_date` must use `YYYY-MM-DD` when present.
- `verification_status` must be `verified` before final quotation review.
- Missing, stale, or unsuitable expiry information must block final quotation.

Allowed values where applicable:

- `verification_status`: `verified`, `needs_review`, `unverified`, `expired`

Manual review requirements:

- Confirm expiry and shelf-life suitability before quotation.
- Confirm buyer-specific expiry requirements manually.

Commit policy:

- Real expiry files must not be committed.

### 4.7 Real Quotation Inputs

Planned file: `data/private/quotation_inputs_real.csv`

Required fields:

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

Optional fields:

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

Sensitive fields:

- `unit_price`
- `payment_terms`
- `shipping_terms`
- `tax_note`
- `duties_note`
- `incoterms`
- `buyer_note`
- `internal_margin`
- `final quotation terms`

Validation rules:

- `buyer_id` must match a real buyer master record.
- `requested_qty` must be numeric.
- MOQ review must be complete before external quotation preparation.
- Unverified price, stock, or expiry must block final quotation.
- `approval_block=true` must block buyer-facing quotation.
- Total amount may be calculated only from verified numeric `requested_qty` and `unit_price`.

Allowed values where applicable:

- `quotation_stage`: `draft`, `internal_review`, `blocked`, `needs_confirmation`
- `required_internal_review`: `true`, `false`

Manual review requirements:

- Confirm price, stock, expiry, MOQ, delivery, tax, shipping, duties, payment terms, and incoterms.
- Confirm brand approval before buyer-facing quotation.

Commit policy:

- Real quotation input files must not be committed.

### 4.8 Real Approval Records

Planned file: `data/private/approval_records_real.csv`

Required fields:

- `approval_record_id`
- `brand_name`
- `approval_required`
- `proposal_allowed`
- `approval_block`
- `approval_status`
- `approval_owner`
- `approval_date`
- `brand_risk_level`
- `updated_at`

Optional fields:

- `buyer_id`
- `product_name`
- `approval_scope`
- `approval_expiry_date`
- `approval_notes`
- `evidence_reference`

Sensitive fields:

- `approval_owner`
- `approval_notes`
- `evidence_reference`
- confidential approval context

Validation rules:

- `approval_required=true` or `proposal_allowed=false` should set `approval_block=true` unless explicit approval is recorded.
- `approval_block=true` overrides `priority_tier`, `score_total`, buyer interest, and requested quantity.
- `approval_status` must be manually verified before external proposal.
- Medicube remains approval-required unless explicit approval is recorded.
- `approval_allowed` or equivalent approval-cleared status must be manually verified before external proposal.

Allowed values where applicable:

- `approval_required`: `true`, `false`
- `proposal_allowed`: `true`, `false`
- `approval_block`: `true`, `false`
- `approval_status`: `approved`, `rejected`, `needs_review`, `expired`, `not_requested`
- `brand_risk_level`: `high`, `medium`, `low`, `unknown`

Manual review requirements:

- Director or approved business owner must verify approval status.
- Approval scope and expiry must be checked before external use.
- Approval records may be confidential and must not be committed.

Commit policy:

- Real approval record files must not be committed.

### 4.9 Real Manual Review Records

Planned file: `data/private/manual_review_records_real.csv`

Required fields:

- `review_id`
- `related_record_type`
- `related_record_id`
- `review_status`
- `review_owner`
- `reviewed_at`
- `required_next_action`

Optional fields:

- `buyer_id`
- `brand_name`
- `review_area`
- `review_notes`
- `blocking_issue`
- `resolved_at`

Sensitive fields:

- `review_owner`
- `review_notes`
- `blocking_issue`
- buyer-specific or commercial review context

Validation rules:

- Blocking review records must prevent external use.
- Review status must be clear before proposal or quotation leaves internal review.
- Manual review does not replace brand approval, commercial verification, or privacy review.

Allowed values where applicable:

- `related_record_type`: `buyer`, `contact`, `opportunity`, `price`, `stock`, `expiry`, `quotation`, `approval`
- `review_status`: `pass`, `pass_with_caution`, `fail`, `blocked`, `needs_review`
- `review_area`: `privacy`, `brand_approval`, `commercial`, `claim`, `localization`, `quotation`, `buyer_contact`, `other`

Manual review requirements:

- Record who reviewed, when reviewed, and what remains blocked.
- Do not expose sensitive review notes in dashboards by default.

Commit policy:

- Real manual review files must not be committed.

## 5. Sensitive Fields

The following fields or data types are sensitive and must be handled as private when real:

- Buyer legal name
- Contact name
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- Address
- Real negotiated price
- Real stock quantity
- Real expiry date
- Payment terms
- Incoterms
- Supplier details
- Distributor details
- Internal margin
- Final quotation terms

Sensitive fields must not be printed to dashboard outputs by default, committed to GitHub, or included in sample files unless clearly fictional placeholders are used.

## 6. Never-Commit Fields and Files

Files containing the following real data types must never be committed:

- Real buyer contacts
- Real prices
- Real stock
- Real expiry
- Real payment terms
- Real incoterms
- Final quotation
- Supplier private terms
- Distributor private terms
- Internal margin
- External-ready proposal or quotation

If a file might contain real/private business data, treat it as private until manually cleared. Do not rely on filename alone as proof of safety.

## 7. Sample-to-Real Separation

Sample files may be committed only when they are fictional, placeholder-based, and safe for repository review.

Real/private files must remain local/private and must not be committed. Sample workflows must not read private paths. Real workflows must not be enabled by default.

Real workflow support requires:

- Separate approval.
- Privacy Guard validation.
- Explicit sample-to-real mapping.
- Manual approval gates.
- Confirmation that no private paths are staged.
- Confirmation that generated private outputs are ignored.

Current sample workflows should continue to read sample-safe paths such as `data/*_sample.csv` and generated internal-review outputs.

## 8. Approval-Required Brand Handling

Required approval fields:

- `approval_required`
- `approval_block`
- `proposal_allowed`
- `approval_status`
- `approval_owner`
- `approval_date`
- `approval_notes`
- `brand_risk_level`

Rules:

- Medicube remains approval-required unless explicit approval is recorded.
- Approval-required brands may be recorded as buyer interest, but they must not be used in buyer-facing proposal, pitch, quotation, public content, or ad copy without explicit approval.
- `approval_block=true` overrides `priority_tier` and `score_total`.
- High score, A-tier priority, MOQ fit, or large requested quantity must not override approval restrictions.
- Approval-cleared status must be manually verified before external proposal.
- Approval records may contain confidential business context and must not be committed.

## 9. Price, Stock, and Expiry Verification

Required verification fields:

- `price_source`
- `price_confirmed_at`
- `price_confirmed_by`
- `stock_source`
- `stock_confirmed_at`
- `stock_confirmed_by`
- `expiry_source`
- `expiry_confirmed_at`
- `expiry_confirmed_by`
- `verification_status`

Rules:

- Unverified price must block final quotation.
- Unverified stock must block final quotation.
- Unverified expiry must block final quotation.
- Dashboard or report `PASS` does not mean commercial approval.
- Integrated Runner `PASS` does not mean price, stock, expiry, supplier terms, or buyer-specific conditions are approved.
- Verification timestamps should be reviewed for freshness before external use.

## 10. Final Quotation Restrictions

Quotation stages:

- Draft quotation: generated or prepared for internal review only.
- Internal-review quotation: reviewed internally but not approved for external sending.
- Final quotation: buyer-facing commercial document; out of current scope.

Rules:

- Final quotation files are out of scope for the current repository workflow.
- `output/final/` remains blocked.
- Final quotation requires manual approval and a separate process.
- No automatic sending is allowed.
- Quotation validation `PASS` means structural/safety validation only, not final commercial approval.
- Final quotation must not proceed when price, stock, expiry, approval, MOQ, payment, shipping, tax, duties, or incoterms are unverified.

## 11. Validation Requirements

Future validators must check:

- No private files are staged.
- No real/private path is read by sample workflow.
- Required fields exist.
- Sensitive fields are not printed to dashboard by default.
- `approval_block` is respected.
- Medicube approval-required rule is respected.
- Unverified price, stock, or expiry blocks final quotation.
- Final quotation files are not generated.
- No external sending logic exists.
- Contact fields are excluded from internal summary outputs by default.
- Real/private filenames are ignored and not force-added.

Validation must use local repository inspection only. It must not scrape, search, call APIs, automate browsers, enrich buyer data, run credit checks, send messages, send quotations, or collect external data.

## 12. Privacy Guard Strengthening Candidates

Recommended future Privacy Guard checks:

- Detect `data/private/**`.
- Detect `output/private/**`.
- Detect `output/final/**`.
- Detect buyer contact columns.
- Detect real price, stock, and expiry files.
- Detect final quotation terms.
- Detect external-ready wording.
- Detect accidental force-add risk.
- Detect private path usage in sample workflow commands.
- Detect dashboards that expose contact fields by default.

These checks should report clear PASS/WARNING/FAIL results and should never delete, move, rewrite, stage, commit, or push files automatically.

## 13. Recommended Future Steps

- Step C: Real/private validation checklist document.
- Step D: Privacy Guard enhancement specification.
- Step E: Optional ignored template plan, without real data.
- Step F: Sample-to-real mapping document.
- Step G: Manual approval gate document.
- Step H: Roadmap/task log update.
- Step I: Final review.

## 14. Completion Criteria

Step B is complete only when:

- `docs/real_private_input_schema.md` exists.
- No real/private files were created.
- No private/final folders were created.
- No CSV/XLSX templates were created.
- No code was implemented.
- `.gitignore` was not modified.
- Existing automation logic was not modified.
- Privacy Guard still passes.

## 15. Remaining Risks

- This schema does not provide technical enforcement by itself.
- Privacy Guard is not a full DLP system.
- Human review is still required before real operation.
- Real data may be accidentally placed in tracked paths if operating discipline is weak.
- Commercial values can become stale quickly.
- Approval-required brand misuse remains a business-critical risk.
- External communication and final quotation processes remain outside the current scope.
