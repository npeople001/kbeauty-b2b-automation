# Approval Gate Baseline Review

## 1. Purpose

This document records the current approval-related fields and sample/internal-review behavior before any Approval Gate Validator implementation.

The purpose is to define the baseline for future `tests/validate_approval_gate.py` work without creating code, tests, real/private data, private folders, final folders, templates, or external workflows.

## 2. Scope

This baseline reviews:

- Brand approval fields.
- Buyer/sample scoring fields.
- Proposal draft fields.
- Quotation draft fields.
- Dashboard/report approval indicators.
- 메디큐브/Medicube handling.
- `approval_block` behavior.
- `proposal_allowed` behavior.
- Final quotation and external-ready wording status.

The reviewed files are sample/internal-review or ignored generated output files only.

## 3. Non-goals

Step B does not:

- Implement approval validation code.
- Create `tests/validate_approval_gate.py`.
- Create or modify real/private files.
- Approve external use.
- Create final quotation workflow.
- Send messages or quotations.
- Verify buyer authenticity or creditworthiness.
- Replace manual approval.

## 4. Current Files Reviewed

| File path | Exists? | Purpose | Approval-related fields observed | Proposal/quotation/final/external indicators observed | Notes |
|---|---:|---|---|---|---|
| `data/brands_master.csv` | yes | Brand reference and proposal eligibility control. | `approval_required`, `approval_note`, `proposal_allowed`, brand name fields. | 메디큐브 is `approval_required=true` and `proposal_allowed=false`. | Safe committed reference data. Future validator should allow this when it is clearly a brand reference. |
| `data/buyers_master_sample.csv` | yes | Sample buyer master data. | `approval_warning`, `proposal_brand_check`, `recommended_follow_up`, `next_action`. | BUYER-0004 includes 메디큐브 as buyer interest and is marked approval review needed. | Sample placeholder contacts only. Approval warning is internal-review context. |
| `data/buyers_scored_sample.csv` | yes | Sample scored buyer output. | `approval_block`, `priority_tier`, `score_total`, `recommended_next_action`, `risk_flags`. | BUYER-0004 has `approval_block=true` and `priority_tier=Hold`. | Confirms approval block overrides score and tier. |
| `data/proposal_messages_sample.csv` | yes | Internal-review proposal message drafts. | `approval_block`, `message_status`, `recommended_brands`, `excluded_brands`, `required_internal_review`, `next_action`. | BUYER-0004 is `blocked_approval_required`; 메디큐브 appears in `excluded_brands`. Internal-review and no automatic sending language is present. | Future validator should fail if blocked rows contain buyer-facing recommendation copy for approval-required brands. |
| `data/quotation_sample.csv` | yes | Internal-review quotation draft sample output. | `approval_block`, `quotation_status`, `required_internal_review`, `next_action`, brand/product fields. | QUOTE-0002 for 메디큐브 is `blocked_approval_required`; wording says not external quotation-ready. | Contains price/stock/expiry/MOQ sample values but remains internal-review only. |
| `data/brands_raw.csv` | yes | Raw brand sample/source file. | No normalized approval fields; note includes approval policy text for 메디큐브. | 메디큐브 note states director approval required before external posting/proposal. | Future validator should treat this as raw reference/policy context, not buyer-facing recommendation. |
| `data/buyers_raw.csv` | yes | Raw buyer input template. | No approval-specific normalized fields found in header. | No proposal/quotation/final/external output indicators found. | Empty/template-like raw file. |
| `output/internal_workflow_summary.md` | yes, ignored generated output | Integrated Runner local summary. | Shows `approval_block=true` in generation summaries and PASS statuses. | PASS appears for workflow stages, but it is a generated internal run summary. | Must not be committed unless explicitly approved. PASS must not be interpreted as approval. |
| `output/operations_dashboard.md` | yes, ignored generated output | Operations dashboard local generated output. | Surfaces `approval_block`, approval-required issue count, and 메디큐브 warning. | States dashboard/report PASS is not external approval and proposal/quotation outputs are drafts. | Must remain ignored generated output. Future validator may read it only if explicitly requested. |

## 5. Approval Field Inventory

| Field | Current location if found | Current purpose | Future validator use | Sensitivity level | Allowed in sample? |
|---|---|---|---|---|---:|
| `approval_required` | `data/brands_master.csv`; policy docs. | Marks brands needing approval. | Block proposal/quotation context without approval. | business-critical | yes |
| `approval_block` | `data/buyers_scored_sample.csv`, `data/proposal_messages_sample.csv`, `data/quotation_sample.csv`, dashboard/report outputs. | Blocks unsafe external proposal/quotation handling. | Primary FAIL trigger unless approved or exception-approved. | business-critical | yes |
| `proposal_allowed` | `data/brands_master.csv`. | Controls whether a brand can be proposed. | FAIL when false in proposal context. | business-critical | yes |
| `approval_status` | Policy/planning docs only. | Planned explicit approval state. | Required for future approval records. | sensitive when real | yes as placeholder/policy |
| `approval_owner` | Policy/planning docs only. | Planned human approval owner. | Required for approved/exception-approved records. | private when real | yes as placeholder/policy |
| `approval_date` | Policy/planning docs only. | Planned approval timestamp/date. | Required for approved/exception-approved records. | private when real | yes as placeholder/policy |
| `approval_expiry` | Policy/planning docs only. | Planned approval validity end. | FAIL if expired. | sensitive when real | yes as placeholder/policy |
| `approval_notes` | Policy/planning docs only. | Planned approval context/exception notes. | Warning if notes exist without expiry or owner. | private/commercial when real | yes as placeholder/policy |
| `exception_reason` | Policy/planning docs only. | Planned exception explanation. | Required for exception-approved status. | sensitive when real | yes as placeholder/policy |
| `review_required_next` | Policy/planning docs only. | Planned next review signal. | WARNING/INFO routing. | low to medium | yes |
| `brand_name` | `data/quotation_sample.csv`; conceptually `brand_ko` in brand files. | Brand involved in quote/proposal context. | Identify approval-required brand usage. | business-critical | yes |
| `buyer_id` | Buyer, scoring, proposal, quotation files. | Links buyer-related outputs. | Connect blockers across buyer/scoring/proposal/quotation outputs. | internal identifier | yes |
| `related_output_file` | Policy/planning docs only. | Planned output reference. | FAIL if references `output/final/**` before final process exists. | medium | yes as placeholder/policy |
| `approval_type` | Policy/planning docs only. | Planned gate category. | Route brand/contact/proposal/quotation/final gates. | low to medium | yes |
| `priority_tier` | `data/buyers_scored_sample.csv`, `data/proposal_messages_sample.csv`, dashboard summaries. | Internal sales priority. | Must not override approval blockers. | internal business signal | yes |
| `score_total` | `data/buyers_scored_sample.csv`, dashboard summaries. | Internal sales-priority score. | Must not imply approval, buyer authenticity, creditworthiness, or purchase certainty. | internal business signal | yes |
| `next_action` | Buyer, proposal, quotation files. | Internal follow-up action. | Warning/INFO context for manual review needs. | internal operating note | yes |

## 6. Current Approval Assumptions

Current business assumptions:

- `approval_required` is allowed in sample/internal-review files.
- `approval_block` is allowed in sample/internal-review files.
- `proposal_allowed` is allowed in sample/internal-review files.
- `priority_tier` and `score_total` are internal prioritization only.
- `score_total` is not buyer authenticity, creditworthiness, or purchase probability.
- `approval_block` overrides `priority_tier` and `score_total`.
- PASS from Privacy Guard, dashboard, runner, proposal validation, or quotation validation is not external approval.
- Manual approval remains required before external use.

## 7. Medicube Baseline

메디큐브/Medicube appears in current reviewed files as:

- Brand reference: `data/brands_master.csv`, with `approval_required=true` and `proposal_allowed=false`.
- Raw brand reference/policy note: `data/brands_raw.csv`.
- Sample buyer interest: `data/buyers_master_sample.csv` for BUYER-0004.
- Scoring context: `data/buyers_scored_sample.csv`, with `approval_block=true` and `priority_tier=Hold`.
- Proposal context: `data/proposal_messages_sample.csv`, where BUYER-0004 is blocked and 메디큐브 is excluded, not recommended.
- Quotation context: `data/quotation_sample.csv`, where QUOTE-0002 is blocked approval-required and not external quotation-ready.
- Dashboard/report warning: `output/operations_dashboard.md`, where 메디큐브/Medicube appears as approval-required warning context.

Expected future validator behavior:

- Documentation or policy mention should pass.
- Brand reference may be allowed if marked approval-required.
- Proposal/quotation context without an approved approval record should fail in future implementation.
- `approval_block=true` should override `priority_tier` and `score_total`.
- 메디큐브/Medicube should not fail merely because it appears in blocked/excluded/internal-review policy context.

## 8. Proposal Baseline

Proposal sample/internal-review findings:

- `proposal_allowed` does not appear directly in `data/proposal_messages_sample.csv`, but is available in `data/brands_master.csv`.
- `approval_required` does not appear directly in proposal output, but approval-required brand handling appears through `approval_block`, `message_status`, `excluded_brands`, and `compliance_notes`.
- `approval_block` appears in proposal output.
- `external_ready` and `send_ready` normalized markers were not found in proposal output.
- Proposal messages clearly state internal-review draft language and no automatic sending.
- BUYER-0004 has `message_status=blocked_approval_required`, no recommended brands, and `excluded_brands=메디큐브`.

Expected baseline:

- No automatic sending.
- No external-ready approval.
- Internal-review only.

## 9. Quotation Baseline

Quotation sample/internal-review findings:

- `final_quotation`, `final_quote`, `approved_quotation`, and `commercially_approved` markers were not found as normalized status values in `data/quotation_sample.csv`.
- Quotation sample includes price, stock, expiry, MOQ, delivery lead time, tax/shipping/duties/incoterms notes, and internal-review compliance notes.
- Quotation rows are internal-review drafts.
- QUOTE-0002 for 메디큐브 is blocked approval-required.
- Missing price, stock, expiry, and MOQ issues appear as draft statuses requiring confirmation.
- No final quotation workflow exists.
- No automatic quotation sending exists.

Expected baseline:

- Final quotation remains out of scope.
- No final quotation workflow.
- No automatic quotation sending.

## 10. Dashboard and Report Baseline

Generated ignored outputs reviewed if present:

- `output/internal_workflow_summary.md`
- `output/operations_dashboard.md`

Findings:

- Integrated Runner summary shows PASS for workflow stages, including proposal and quotation validation.
- Operations dashboard surfaces approval blockers, approval-required issue counts, and 메디큐브/Medicube warning counts.
- Dashboard output states that proposal messages and quotation results are draft or internal-review outputs.
- Dashboard output states that `approval_block=true` overrides `priority_tier` and `score_total`.
- Dashboard output states that quotation PASS is not final commercial approval.
- No private contact fields such as `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp` were surfaced in the dashboard scan.
- Dashboard PASS could be misunderstood as approval if read without the disclaimer, so future validator should keep the disclaimer requirement visible.

These outputs are ignored local generated files and must not be committed unless explicitly approved.

## 11. Baseline Blocker Candidates

Future validator blocker candidates:

- `approval_block=true` without `approved` or `exception_approved`.
- `approval_required=true` with missing `approval_status`.
- `proposal_allowed=false` in proposal context.
- 메디큐브/Medicube proposal or quotation without approved approval record.
- Final quotation markers before final process exists.
- `external_ready` or `send_ready` wording without approval.
- Approved status missing `approval_owner`.
- Approved status missing `approval_date`.
- Expired `approval_expiry`.
- `related_output_file` references `output/final/**`.

## 12. Baseline Warning Candidates

Future warning candidates:

- `approval_required=true` in internal-review only file.
- Approval placeholders in sample files.
- Dashboard/report mentions approval blockers.
- Approval notes without expiry.
- Sample-safe approval status values.
- Manual review recommended but not yet blocking.

## 13. Baseline Allowed Candidates

Future allowed/INFO candidates:

- Documentation policy mentions.
- Sample placeholders.
- `approval_required` fields in sample-safe files.
- `approval_block` fields in sample-safe files.
- `proposal_allowed` fields in sample-safe files.
- 메디큐브/Medicube mention in policy docs.
- `score_total` and `priority_tier` internal-review fields.
- 메디큐브/Medicube appearing as blocked, excluded, approval-required, or internal-review only.

## 14. False-positive Risks

False-positive risks:

- Docs mention approval blockers as policy.
- Future validator file will contain deny-list strings.
- Sample files may include approval placeholders.
- Brand master may include approval-required brands.
- Dashboard/report may mention blockers without being external-ready.
- 메디큐브/Medicube may appear in policy docs and reference files.
- Internal-review quote rows may include commercial sample values that are not real operating values.

Mitigation:

- Treat docs and tests as policy/configuration contexts.
- Treat sample files as allowed when they are clearly placeholder or internal-review.
- Treat strict proposal/quotation/output contexts more aggressively only when wording looks buyer-facing, final, approved, external-ready, or send-ready.

## 15. Recommended Implementation Entry Criteria for Step C

Step C should start only when:

- This baseline review exists.
- Privacy Guard passes.
- Staged-only Privacy Guard passes.
- Privacy Guard self-test passes.
- No private/final folders exist.
- No real/private data exists.
- Only docs are changed in Step B.
- Approval validator implementation scope remains minimal.

## 16. Recommended Step C Scope

Step C should create a minimal:

- `tests/validate_approval_gate.py`

Only in Step C, not in Step B.

Step C should include:

- `argparse`.
- `--self-test`.
- Python standard library only.
- No real/private file creation.
- Synthetic checks only at first.
- PASS/WARNING/FAIL output.
- No integration with external sending.
- No real/private workflow.

## 17. Completion Criteria

Step B passes when:

- `docs/approval_gate_baseline_review.md` exists.
- Baseline approval fields are reviewed.
- Sample/internal-review files are documented.
- Future blocker/warning/allowed candidates are identified.
- No code is implemented.
- No tests are created.
- `tests/validate_privacy_guard.py` is not modified.
- `.gitignore` is not modified.
- No real/private/final folders are created.
- No CSV/XLSX templates are created.
- Privacy Guard passes.
- Staged-only Privacy Guard passes.
- Privacy Guard self-test passes.

