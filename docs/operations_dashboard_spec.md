# Operations Dashboard Specification

## 1. Scope

Task 012 defines an internal Operations Dashboard for the K-beauty B2B automation workflow.

Task 012 does:

- Summarize the current local sample/internal-review workflow status.
- Read existing local sample files and internal-review outputs from Task 006-011.
- Show buyer pipeline status, scoring status, proposal status, quotation status, approval risks, and next-action summaries.
- Make approval blocks, review-needed cases, and commercial confirmation gaps easy to see.
- Keep all dashboard outputs internal-review only.

Task 012 does not do:

- It does not implement scraping, live web research, automatic web search, APIs, browser automation, crawlers, buyer enrichment, credit checks, external data collection, email sending, messaging automation, quotation sending, or external sending.
- It does not send emails, DMs, WeChat messages, WhatsApp messages, quotations, or any external communication.
- It does not verify buyer authenticity, creditworthiness, payment ability, purchase probability, price accuracy, stock accuracy, expiry accuracy, or final commercial approval.
- It does not create real data files.
- It does not create `data/private/`, `output/private/`, or `output/final/` folders.
- It does not use real/private data paths in v1.
- It does not modify source CSV files.
- It does not weaken Privacy Guard, approval-block, quotation, or internal-review controls.

The dashboard is internal-review only. Dashboard `PASS`, Integrated Runner `PASS`, or validation `PASS` means the local sample workflow structure and validation checks passed. It does not mean external-ready proposal, external-ready quotation, buyer verification, credit verification, purchase certainty, or commercial approval.

Dashboard v1 should use local sample/internal-review files only. Real/private workflows require separate design, Privacy Guard review, and explicit approval.

## 2. Background

Task 001-009 created the first-pass internal automation foundation:

- Brand Master Automation
- Market Research & Content Strategy Template
- Market Research Report Generator
- Channel Content Strategy Generator
- Short-form Video & Feed Plan Generator
- Buyer Lead Template
- Buyer Scoring Automation
- Proposal Message Generator
- Quotation Maker

Task 010 added Real Data Migration & Privacy Guard to separate sample data from future real operating data and protect buyer/contact/price/stock/expiry/quotation/private business data.

Task 011 added the Integrated Runner to execute the local `buyer_sales_sample` workflow in a controlled order.

Task 012 should summarize operational status for business review. It must not weaken privacy controls, approval-required brand restrictions, quotation safeguards, or internal-review disclaimers.

## 3. Recommended Dashboard Type

Recommended v1 output:

- `output/operations_dashboard.md`

Optional future outputs:

- `output/operations_dashboard.xlsx`
- `data/operations_dashboard_summary.csv`

Markdown should be the v1 priority because it is simple, auditable, and lower risk than a multi-sheet business workbook. XLSX may be added later if business review requires filters, sheets, conditional formatting, or manager-facing spreadsheet review.

`output/*` files are generated outputs and should follow existing output ignore rules. Generated dashboard outputs must remain internal-review only unless a future task explicitly changes the policy after review.

## 3.1 v1 Output Decision

Task 012 v1 uses Markdown only.

- Primary v1 output: `output/operations_dashboard.md`
- Deferred output: `output/operations_dashboard.xlsx`
- Deferred output: `data/operations_dashboard_summary.csv`

XLSX or CSV dashboard summary outputs require separate approval and validation design before they are enabled.

The Markdown-only v1 decision reduces:

- File lock risk from spreadsheet applications.
- Validation complexity.
- Privacy exposure risk.
- Accidental external-use risk.

Current dashboard validation may produce a non-blocking warning when the `brands` row count is not directly printed in the dashboard body. This warning does not block v1 if brand risk and approval information are still summarized. A future version may add an explicit brands row count if operationally useful. Do not modify generator output solely to remove this warning.

## 4. Input Files

Dashboard v1 should read:

- `output/internal_workflow_summary.md`
- `data/buyers_master_sample.csv`
- `data/buyers_scored_sample.csv`
- `data/proposal_messages_sample.csv`
- `data/quotation_sample.csv`
- `data/brands_master.csv`

Dashboard v1 must not use:

- `data/private/**`
- `output/private/**`
- `output/final/**`
- real buyer/contact data
- real price/stock/expiry data
- real quotation/final commercial documents
- private approval records
- credentials, tokens, local config, or private notes

CSV inputs should be read with `utf-8-sig` compatibility. Markdown inputs and outputs should use UTF-8.

## 5. Output Files

Recommended v1 output:

- `output/operations_dashboard.md`

Optional future outputs:

- `output/operations_dashboard.xlsx`
- `data/operations_dashboard_summary.csv`

Dashboard output rules:

- Dashboard output is internal-review only.
- Dashboard output must not include `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp`.
- Dashboard output must not expose real buyer contact details.
- Dashboard output must not include private notes containing personal or confidential business data.
- Dashboard output must not imply final commercial approval.
- Dashboard output must not be treated as buyer authenticity, creditworthiness, payment ability, or purchase probability verification.
- Dashboard output must not be treated as permission to send proposals, messages, quotations, or external communications.

## 6. Dashboard Sections

Dashboard v1 must include these required sections:

1. Executive Summary
2. Integrated Runner Status
3. Buyer Pipeline Summary
4. Buyer Priority Summary
5. Approval & Brand Risk Summary
6. Proposal Message Summary
7. Quotation Summary
8. MOQ / Price / Stock / Expiry Issues
9. Next Action Summary
10. Internal Review Required Items
11. Key Risks and Warnings
12. Final Operational Recommendation

Each section must include or inherit an internal-review-only disclaimer. The dashboard should make it clear that generated proposal messages and quotation outputs remain drafts requiring human review before external use.

## 7. Core Metrics

Dashboard v1 should define and report these metrics:

- `integrated_runner_result`
- `integrated_runner_stage_count`
- `total_buyers`
- `buyer_count_by_priority_tier`
- `buyer_count_by_approval_block`
- `buyer_count_by_lead_status`
- `proposal_count_by_message_status`
- `quotation_count_by_quotation_status`
- `moq_issue_count`
- `price_confirmation_needed_count`
- `stock_confirmation_needed_count`
- `expiry_confirmation_needed_count`
- `approval_required_brand_issue_count`
- `medicube_blocked_or_review_needed_count`
- `required_internal_review_count`
- `next_action_summary`
- `key_risk_count`

Metrics should be descriptive summaries for internal operations. They must not be presented as external performance claims, buyer verification results, credit decisions, or final business approvals.

## 8. Calculation Rules

Calculation rules:

- `integrated_runner_result` comes from `output/internal_workflow_summary.md`.
- `integrated_runner_stage_count` comes from the Stage Results table in `output/internal_workflow_summary.md`.
- `total_buyers` comes from row count in `data/buyers_master_sample.csv`.
- `buyer_count_by_priority_tier` comes from `priority_tier` in `data/buyers_scored_sample.csv`.
- `buyer_count_by_approval_block` comes from `approval_block` in `data/buyers_scored_sample.csv` and may also reference quotation-level `approval_block` when explaining quotation risks.
- `buyer_count_by_lead_status` comes from `lead_status` in `data/buyers_master_sample.csv`.
- `proposal_count_by_message_status` comes from `message_status` in `data/proposal_messages_sample.csv`.
- `quotation_count_by_quotation_status` comes from `quotation_status` in `data/quotation_sample.csv`.
- `moq_issue_count` should include buyer rows where `moq_fit` is `no` or `unknown` and quotation rows where `moq_check` is `fail` or `unknown`.
- `price_confirmation_needed_count` comes from quotation rows where `quotation_status=needs_price_confirmation` or compliance/next-action text clearly requires price confirmation.
- `stock_confirmation_needed_count` comes from quotation rows where `quotation_status=needs_stock_confirmation` or compliance/next-action text clearly requires stock confirmation.
- `expiry_confirmation_needed_count` comes from quotation rows where `quotation_status=needs_expiry_confirmation` or compliance/next-action text clearly requires expiry confirmation.
- `approval_required_brand_issue_count` should include rows where `approval_block=true`, `approval_warning` is populated, `proposal_brand_check=approval_required_review`, `approval_required=true`, or `proposal_allowed=false` is relevant to a buyer/proposal/quotation row.
- `medicube_blocked_or_review_needed_count` should include rows where `메디큐브` is blocked, excluded, approval-required, or review-needed.
- `required_internal_review_count` should include proposal and quotation rows where `required_internal_review=true`, plus approval-blocked buyer rows where applicable.
- `next_action_summary` should aggregate or list internal next actions without exposing contact data.
- `key_risk_count` should summarize distinct visible risk categories, such as approval block, MOQ issue, price confirmation, stock confirmation, expiry confirmation, privacy caution, and internal-review requirement.

`score_total` must never be interpreted as buyer authenticity, creditworthiness, payment ability, or purchase probability. It is only an internal sales-priority signal.

## 9. Privacy and Contact Exclusion Rules

Dashboard output must not include:

- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- real buyer contact details
- private notes containing personal data
- private notes containing confidential business data
- credentials, tokens, or local config values

Dashboard v1 must not read from private paths by default. It must not accept `data/private/**`, `output/private/**`, `output/final/**`, or `local_config/**` as input paths unless a future real-data workflow is separately designed and approved.

The dashboard may use `buyer_id`, `company_name`, `country`, `lead_status`, `priority_tier`, `approval_block`, `message_status`, `quotation_status`, and `next_action` style summary fields when needed, but it should avoid unnecessary buyer-level detail in the first v1 summary.

## 10. Approval and Brand Safety Rules

Approval and brand rules:

- `approval_block=true` must be highly visible.
- `메디큐브` must remain approval-required unless explicit approval exists.
- Brands with `approval_required=true` or `proposal_allowed=false` must be shown as blocked or review-required, not external-ready.
- A high score or `priority_tier=A` must not override `approval_block`.
- Dashboard must clearly separate opportunity priority from approval readiness.
- Approval-required brands may be shown as risk/review items, but must not be presented as approved external proposal, buyer-facing pitch, public content, ad copy, or quotation items.
- Any approval-blocked row should lead to internal review guidance, not external communication guidance.

The dashboard should highlight approval-required brand issues in the Approval & Brand Risk Summary and in Final Operational Recommendation.

## 11. Proposal and Quotation Safety Rules

Proposal and quotation rules:

- Proposal message outputs remain internal-review drafts.
- Quotation outputs remain internal-review drafts.
- `quotation_status=PASS` or validation `PASS` does not mean final commercial approval.
- Integrated Runner `PASS` does not mean proposals or quotations are ready to send.
- Price, stock, expiry, MOQ, delivery lead time, tax, shipping, duties, payment terms, incoterms, supplier terms, and final commercial terms must be manually verified before external use.
- The dashboard must include caution text for proposal and quotation review.
- Dashboard output must not include external-ready, send-ready, final quotation, or final commercial approval language.
- Dashboard output must not invent or imply price, stock, expiry, supply availability, exclusive rights, certifications, claims, buyer authenticity, creditworthiness, or purchase probability.

## 12. External Automation Restrictions

Dashboard implementation must not include:

- scraping
- live web research
- automatic search
- APIs
- browser automation
- crawlers
- buyer enrichment
- credit checks
- email sending
- messaging automation
- quotation sending
- external sending
- platform posting
- external communication workflow

Future implementation should use local files only. It must not import or use networking, browser automation, email, messaging, crawler, or external API libraries.

## 13. Validation Requirements

Future dashboard validation should check:

- Required dashboard sections exist.
- Integrated Runner status appears.
- Buyer, proposal, and quotation metrics appear.
- `approval_block` summary appears.
- `메디큐브` approval-required warning appears.
- Internal-review disclaimer appears.
- No contact fields appear.
- No private paths appear.
- No external-ready, send-ready, or final quotation language appears.
- No forbidden external automation implementation exists.
- UTF-8/Korean text is preserved.
- Generated dashboard reflects sample CSV row counts.
- Privacy Guard still passes.
- Dashboard does not imply buyer verification, credit verification, purchase probability, external proposal approval, quotation sending, or final commercial approval.

Recommended future validation commands:

```powershell
python tests/validate_privacy_guard.py
python automations/operations_dashboard/generate_operations_dashboard.py
python tests/validate_operations_dashboard.py --dashboard output/operations_dashboard.md
python -m py_compile automations/operations_dashboard/generate_operations_dashboard.py tests/validate_operations_dashboard.py
```

These commands are future implementation targets. Step A does not create scripts or dashboard output files.

## 14. Recommended Implementation Strategy

Future implementation should use:

- Python standard library only
- `csv` for CSV inputs
- `pathlib` for paths
- `collections.Counter` for counts
- UTF-8 Markdown output
- explicit input path validation
- explicit private path rejection
- simple deterministic Markdown rendering
- no pandas required for v1
- no XLSX in v1 unless separately approved

Future generator behavior should:

- Read source CSV files using `utf-8-sig`.
- Read Markdown files using UTF-8.
- Write Markdown using UTF-8.
- Never modify source CSV files.
- Never create real/private paths.
- Never create external-ready outputs.
- Fail clearly if required input files are missing.
- Mark dashboard as internal-review only.
- Keep approval-block and `메디큐브` warnings visible.

## 15. Completion Criteria

Task 012 should be considered complete only when:

- Specification exists.
- Schema/metrics document exists.
- Generator exists.
- `output/operations_dashboard.md` is generated.
- Validation script exists and passes.
- Privacy Guard still passes.
- README guidance is updated.
- Roadmap and task log are updated.
- Final review passes.

Task 012 is not complete if it only creates a visual output without validation, privacy checks, approval-block visibility, and internal-review disclaimers.

## 16. Recommended Future Steps

Recommended Task 012 sequence:

- Step B: Create `docs/operations_dashboard_schema.md`.
- Step C: Create `automations/operations_dashboard/README.md`.
- Step D: Create `automations/operations_dashboard/generate_operations_dashboard.py`.
- Step E: Generate `output/operations_dashboard.md`.
- Step F: Create `tests/validate_operations_dashboard.py`.
- Step G: Decide whether XLSX is needed later.
- Step H: Update README.
- Step I: Update roadmap/task log.
- Step J: Perform final review.

Do not proceed to Step B until Step A is reviewed and accepted.
