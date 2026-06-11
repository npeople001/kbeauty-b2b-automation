# Sample-to-Real Mapping

## 1. Purpose

This document defines future migration logic from current sample/internal-review concepts to future real/private operating structures.

It does not enable real workflows. It does not create real data, private folders, mapping code, CSV/XLSX templates, final quotation workflows, external communication, scraping, APIs, browser automation, buyer enrichment, credit checks, or external data collection.

The goal is to make the boundary between committed sample files and future ignored real/private files explicit before any real operation is approved.

## 2. Scope

This mapping covers:

- Buyer master
- Buyer contacts
- Buyer scoring
- Opportunity notes
- Proposal messages
- Quotation inputs
- Quotation outputs
- Approval records
- Manual review records
- Dashboard/report summaries

All future real/private paths in this document are planned references only. They are not created by this step.

## 3. Non-Goals

This document does not:

- Introduce real data.
- Enable real workflow.
- Create private folders.
- Enable final quotation process.
- Automate external communication.
- Verify buyer authenticity.
- Verify buyer credit.
- Verify live market information.
- Verify price, stock, expiry, supplier terms, payment terms, tax, duties, shipping, or incoterms.
- Change existing sample automation logic.

## 4. Mapping Table

| Current sample/internal-review file | Current purpose | Future real/private counterpart | Mapping type | Fields that can map directly | Fields requiring manual review | Fields that must remain private | Commit policy | Validation requirement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `data/buyers_master_sample.csv` | Sample buyer lead master for validation and workflow testing. | `data/private/buyers_master_real.csv`; `data/private/buyer_contacts_real.csv`; `data/private/buyer_opportunities_real.csv` | Conceptual field mapping; real data stored separately. | `buyer_id`, `country`, `buyer_type`, `sales_channel`, `platform`, `language`, `interested_categories`, `estimated_order_qty`, `moq_fit`, `lead_status`, `priority`, `next_action` | `company_name`, `interested_brands`, `payment_risk`, `repeat_purchase_potential`, `lead_source`, `notes`, `approval_warning`, `proposal_brand_check` | `contact_name`, `contact_email`, `contact_phone`, `wechat_id`, `whatsapp`, real legal name, private buyer notes | Sample file may be committed only with fictional data; real counterparts must never be committed. | Privacy Guard, schema validation, MOQ validation, contact exclusion, approval gate validation. |
| `data/buyers_scored_sample.csv` | Internal sample buyer scoring output. | Future real scored output derived from `data/private/buyers_master_real.csv`, plus `data/private/manual_review_records_real.csv` | Derived internal prioritization mapping. | `buyer_id`, `score_total`, `priority_tier`, `risk_flags`, `approval_block`, `recommended_next_action`, `scoring_version`, `scored_at` | `scoring_summary`, `positive_factors`, `negative_factors`, score weights, risk interpretation | Any real buyer identity, contact detail, payment-risk notes, private scoring rationale | Sample scored output may be committed if fictional; real scored output must remain private. | Score validation, approval block validation, privacy/contact exclusion, overclaim prevention. |
| `data/proposal_messages_sample.csv` | Internal-review draft proposal messages from sample buyer/scoring data. | Future private proposal draft output under `output/private/`; approval link to `data/private/approval_records_real.csv` | Draft message mapping only. | `message_id`, `buyer_id`, `country`, `language`, `priority_tier`, `approval_block`, `message_status`, `message_type`, `excluded_brands`, `required_internal_review`, `next_action` | `company_name`, `subject_or_opening`, `message_body`, `recommended_brands`, `compliance_notes` | Real contact details, buyer-specific sensitive context, private approval notes, real commercial terms | Sample CSV may be committed if fictional; real proposal drafts must not be committed. | Proposal validation, approval gate validation, no external sending, contact exclusion, claim/commercial term review. |
| `data/quotation_sample.csv` | Internal-review sample quotation draft output. | `data/private/quotation_inputs_real.csv`; `data/private/price_inputs_real.csv`; `data/private/stock_inputs_real.csv`; `data/private/expiry_inputs_real.csv`; private draft output under `output/private/`; `output/final/` remains blocked | Draft quotation mapping only. | `quotation_id`, `buyer_id`, `country`, `quotation_status`, `approval_block`, `brand_name`, `product_name`, `product_category`, `sku_or_option`, `requested_qty`, `moq`, `moq_check`, `currency`, `required_internal_review`, `next_action` | `unit_price`, `total_amount`, `stock_status`, `available_qty`, `expiry_date`, `delivery_lead_time`, `price_valid_until`, `supply_status`, `compliance_notes` | Negotiated price, stock quantity, expiry date, supplier/distributor terms, payment terms, incoterms, internal margin, final quotation terms | Sample quotation output may be committed if fictional/test-required; real quotation files must not be committed. | Quotation validation, commercial verification, final quotation gate, approval gate, contact exclusion. |
| `data/brands_master.csv` | Committed reference for brand approval flags and proposal eligibility. | `data/private/approval_records_real.csv` for confidential or buyer-specific approvals | Reference plus private approval extension. | `brand_ko`, `brand_en`, `category`, `sub_category`, `approval_required`, `proposal_allowed` | `approval_note`, `china_priority`, `global_priority`, approval exceptions | Real approval owner, approval notes, buyer-specific approval, confidential approval evidence | Committed only if sample-safe/reference-safe; confidential approval records must remain private. | Brand master validation, approval gate validation, Medicube approval-required rule. |
| `output/internal_workflow_summary.md` | Ignored generated summary of sample Integrated Runner execution. | `output/private/real_workflow_summary.md` | Summary mapping; future real summary private only. | Stage names, PASS/WARNING/FAIL structure, internal-review disclaimers | Any real workflow result interpretation, real issue details | Real buyer names, contact details, commercial terms, private paths, approval notes | Sample generated output generally ignored; real workflow summary must never be committed. | Privacy Guard, private path validation, internal-review disclaimer validation. |
| `output/operations_dashboard.md` | Ignored Markdown dashboard for sample/internal-review workflow. | `output/private/operations_dashboard_real.md` | Dashboard concept mapping; future real dashboard private only. | Metric names, section structure, approval block summary, risk summary structure | Real metric interpretation, buyer-specific next actions, commercial issue details | Contact fields, real price/stock/expiry details, internal margin, private approval notes | Sample generated output generally ignored; real dashboard must never be committed. | Dashboard validation, contact exclusion, commercial detail aggregation, approval warning validation. |
| No current sample file | Future opportunity notes. | `data/private/buyer_opportunities_real.csv` | New private real structure only. | `buyer_id`, opportunity status categories, next-action concept | Real opportunity status, buyer requirement, category/brand interest, timing | Buyer-specific requirements, target price, private sales notes | Must never be committed. | Schema validation, privacy review, approval review. |
| No current sample file | Future manual review records. | `data/private/manual_review_records_real.csv` | New private real structure only. | Review status concept, review area concept | Reviewer decision, blocking issue, resolution status | Reviewer name, private review notes, approval/commercial context | Must never be committed. | Manual review gate validation, privacy review, final approval gate validation. |

`output/final/` is referenced only as a blocked future final quotation area. It must not be used by current workflows.

## 5. Field Classification

### Public-safe sample fields

Examples:

- `buyer_id`
- `country`
- `buyer_type`
- `sales_channel`
- `platform`
- `language`
- `interested_categories`
- `moq_fit`
- `lead_status`
- `priority`

These fields may appear in committed sample files when values are fictional or sample-safe.

### Internal-review fields

Examples:

- `priority_tier`
- `score_total`
- `next_action`
- `risk_flags`
- `message_status`
- `quotation_status`
- `required_internal_review`

These fields support internal planning only. They must not be treated as external approval, buyer verification, creditworthiness, payment ability, or purchase probability.

### Sensitive private fields

Examples:

- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `legal_name`
- `buyer_legal_name`
- `negotiated_price`
- `stock_quantity`
- `expiry_date`
- `supplier_details`
- `distributor_details`
- `internal_margin`

These fields must remain private when real and must not be printed to dashboards or committed outputs by default.

### Approval gate fields

Examples:

- `approval_required`
- `approval_block`
- `proposal_allowed`
- `approval_status`
- `approval_owner`
- `approval_date`
- `approval_notes`
- `brand_risk_level`

These fields control whether a brand can be proposed, quoted, or used externally.

### Verification fields

Examples:

- `price_confirmed_at`
- `price_confirmed_by`
- `stock_confirmed_at`
- `stock_confirmed_by`
- `expiry_confirmed_at`
- `expiry_confirmed_by`
- `verification_status`

These fields must be explicit before real commercial use.

### Final quotation fields

Examples:

- `final_price`
- `incoterms`
- `payment_terms`
- `final_validity_date`
- `final_quote_number`

Final quotation fields are outside the current workflow. They require a separate approved final quotation process.

## 6. Mapping Principles

- Sample files must remain synthetic or internal-review safe.
- Real/private files must remain local/private and ignored.
- Sample workflow must not read `data/private/**` paths.
- Real workflow must not be enabled by default.
- Real data must not be backfilled into sample files.
- Dashboard/report outputs must not expose private contact or commercial terms by default.
- `output/final/**` remains blocked until a separate final quotation process exists.
- Privacy Guard must pass before and after any approved real/private workflow test.
- Mapping is conceptual until a future approved implementation exists.

## 7. Buyer Mapping Rules

- Sample `buyer_id` may map to a future private `buyer_id`.
- Real legal name and contact fields must live only in private files.
- Buyer scoring may use anonymized `buyer_id`, but must not expose contact details.
- `score_total` remains internal prioritization only.
- `score_total` is not buyer authenticity, creditworthiness, payment ability, or purchase probability.
- Buyer contact use requires manual review.
- Real buyer notes must not be committed.
- Payment risk remains a manual indicator unless a separate approved process changes it.

## 8. Brand and Approval Mapping Rules

- `data/brands_master.csv` may remain committed reference data if sample-safe and business-approved.
- `approval_required` and `approval_block` must be respected in real workflow.
- Medicube remains approval-required unless an explicit approval record exists.
- `approval_status` must be explicit.
- High `priority_tier` or `score_total` cannot override `approval_block`.
- Approval cannot be inferred from buyer interest, large order quantity, or high score.
- Approval records must remain private if they include real owners, notes, buyer-specific approvals, or commercial terms.

## 9. Proposal Mapping Rules

- Sample proposal messages remain internal drafts.
- Real proposal messages must not be automatically sent.
- Real proposal drafts must exclude contact fields by default.
- `proposal_allowed=false` blocks external proposal.
- Approval-required brands require recorded approval before external proposal.
- Outbound-ready language must be avoided unless separately approved.
- Proposal message PASS does not mean send-ready approval.
- Real proposal drafts must remain private and must not be committed.

## 10. Quotation Mapping Rules

- Sample quotation outputs remain internal drafts.
- Real quotation inputs require verified price, stock, expiry, MOQ, payment, shipping, tax, duties, and incoterms.
- Unverified commercial terms block final quotation.
- `output/final/**` remains blocked.
- Quotation validation PASS does not mean final commercial approval.
- Final quotation process requires separate approval and separate workflow.
- Real quotation drafts must not include contact fields by default.
- Real quotation outputs must remain private and must not be committed.

## 11. Dashboard and Report Mapping Rules

- Sample Operations Dashboard uses `output/operations_dashboard.md`.
- Future real dashboard, if allowed, should be `output/private/operations_dashboard_real.md`.
- Real dashboard must not expose contact fields by default.
- Real dashboard must not expose detailed commercial terms by default.
- Dashboard PASS does not mean external approval.
- Dashboard PASS does not mean final commercial approval.
- Private dashboard outputs must never be committed.
- Dashboard summaries should aggregate risks and counts instead of printing sensitive row-level data.

## 12. Validation Mapping

Future validator candidates:

- `validate_real_private_paths.py`
- `validate_real_private_schema.py`
- `validate_sample_to_real_mapping.py`
- `validate_real_approval_gate.py`
- `validate_final_quotation_gate.py`

These are future candidates only. They are not implemented in Step F.

Future validation should check:

- Private paths are ignored and not staged.
- Sample workflows do not read private paths.
- Required real/private schema fields exist.
- Contact fields are excluded from dashboards by default.
- Approval gate fields block unsafe external use.
- Unverified price, stock, and expiry block final quotation.
- Final quotation outputs are not generated by unapproved workflows.
- External sending logic is absent.

## 13. Migration Readiness Checklist

Before any future sample-to-real migration:

- [ ] Privacy Guard enhanced.
- [ ] `.gitignore` confirmed.
- [ ] Private paths ignored.
- [ ] Private templates approved.
- [ ] Schema approved.
- [ ] Approval gate defined.
- [ ] Manual review owner defined.
- [ ] No real data committed.
- [ ] No external sending implemented.
- [ ] `output/final/**` still blocked.
- [ ] Sample workflow still passes.
- [ ] Integrated Runner still uses sample paths only.
- [ ] Operations Dashboard still excludes private data by default.

Stop if any item fails.

## 14. Completion Criteria

Step F passes when:

- `docs/sample_to_real_mapping.md` exists.
- Mapping principles are documented.
- No code is implemented.
- No real/private/final folders are created.
- No CSV/XLSX templates are created.
- `.gitignore` is not modified.
- Existing automation logic is not modified.
- Privacy Guard still passes.

## 15. Recommended Next Steps

- Step G: Manual approval gate document.
- Step H: Roadmap/task log update.
- Step I: Final review.

Do not proceed to Step G until Step F is reviewed and Privacy Guard passes.
