# Operations Dashboard Schema and Metrics Definition

## 1. Purpose

This document fixes the Operations Dashboard output schema before implementation.

It defines the exact dashboard sections, output structure, metric names, input sources, calculation rules, validation expectations, privacy exclusion rules, approval-block display rules, proposal/quotation safety rules, and internal-review wording required for the Task 012 Operations Dashboard.

This document is schema/documentation only. It does not implement code, create dashboard outputs, create automation folders, modify existing automation logic, or use real/private data.

## 2. Dashboard Version

| Field | Value |
| --- | --- |
| version | `v1` |
| primary output | `output/operations_dashboard.md` |
| format | UTF-8 Markdown |
| scope | sample/internal-review only |
| data paths | local sample/internal-review files only |
| private path support | not supported in v1 |
| external action support | not supported |

Dashboard v1 is an internal operational summary. It must not be interpreted as an external-ready proposal, quotation, buyer verification report, credit decision, purchase probability estimate, or final commercial approval.

## 3. Input Sources

| input file | purpose | required/optional | key fields used | privacy notes |
| --- | --- | --- | --- | --- |
| `output/internal_workflow_summary.md` | Integrated Runner latest run status and stage result summary. | Required | workflow name, result, stage names, stage statuses, output paths, internal-review and no-external-sending wording. | Generated internal-review output only. Must not be treated as business approval. |
| `data/buyers_master_sample.csv` | Buyer pipeline and lead status summary. | Required | `buyer_id`, `company_name`, `country`, `lead_status`, `moq_fit`, `approval_warning`, `proposal_brand_check`, `next_action`. | Source includes contact columns, but dashboard must not output `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp`. |
| `data/buyers_scored_sample.csv` | Internal buyer scoring and approval-block summary. | Required | `buyer_id`, `score_total`, `priority_tier`, `risk_flags`, `approval_block`, `recommended_next_action`. | `score_total` is internal priority only, not buyer verification or purchase probability. |
| `data/proposal_messages_sample.csv` | Proposal draft status summary. | Required | `message_id`, `buyer_id`, `message_status`, `approval_block`, `excluded_brands`, `required_internal_review`, `next_action`. | Full message body should not be printed in v1. Drafts are internal-review only. |
| `data/quotation_sample.csv` | Quotation status, approval block, MOQ, price, stock, expiry, and review status summary. | Required | `quotation_id`, `buyer_id`, `quotation_status`, `approval_block`, `brand_name`, `moq_check`, `stock_status`, `expiry_date`, `required_internal_review`, `next_action`. | Do not present quotation data as final commercial approval. Aggregate price/stock fields unless later approved. |
| `data/brands_master.csv` | Brand approval and proposal eligibility reference. | Required | `brand_ko`, `brand_en`, `approval_required`, `proposal_allowed`, `approval_note`. | Brand approval rules are business-critical. Do not change them in dashboard generation. |

All CSV inputs should be read with `utf-8-sig` compatibility. Markdown inputs should be read as UTF-8.

## 4. Forbidden Inputs

Dashboard v1 must not read from or depend on:

- `data/private/**`
- `output/private/**`
- `output/final/**`
- `local_config/**`
- real buyer/contact files
- real price files
- real stock files
- real expiry files
- real quotation/final commercial files
- externally collected buyer data
- externally enriched buyer data
- credit check data
- scraped, crawled, API-collected, or live web research data

If future implementation receives a private path by CLI argument or configuration, it must fail clearly. Private/real workflows require a separate task, Privacy Guard review, and explicit approval.

## 5. Output Schema

The v1 Markdown dashboard must use this exact section order:

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

## 5.1 Deferred Output Schemas

XLSX and CSV summary schemas are not active in Task 012 v1.

- `output/operations_dashboard.xlsx` is deferred.
- `data/operations_dashboard_summary.csv` is deferred.
- Future XLSX support must be designed and validated in a separate step.
- Future CSV dashboard summary support must be designed and validated in a separate step.

Future XLSX/CSV support must preserve:

- Contact field exclusion.
- `approval_block` visibility.
- `硫붾뵒?먮툕`/Medicube approval-required warning.
- Internal-review-only disclaimer.
- No final quotation language.
- No external sending language.
- No private path usage.

Future XLSX/CSV validators must be created before those outputs are enabled. The v1 Markdown validator may produce a non-blocking warning when the `brands` row count is not directly printed in the dashboard body. This warning does not block v1 when brand risk and approval information are still summarized. A future version may add explicit brands row count if operationally useful. Do not modify generator output solely to remove this warning.

### 1. Executive Summary

| Schema item | Requirement |
| --- | --- |
| section purpose | Give a short internal operational overview of the latest sample workflow status. |
| required metrics | `integrated_runner_result`, `total_buyers`, `buyer_count_by_approval_block`, `required_internal_review_count`, `key_risk_count`. |
| required wording | Must state: internal-review only; no external sending; not final commercial approval. |
| source files | `output/internal_workflow_summary.md`, all summary CSV inputs. |
| validation checks | Section exists; required metric labels appear; internal-review disclaimer appears. |
| privacy restrictions | Do not print contact fields or private notes. |

### 2. Integrated Runner Status

| Schema item | Requirement |
| --- | --- |
| section purpose | Show whether the local `buyer_sales_sample` workflow passed, warned, or failed. |
| required metrics | `integrated_runner_result`, `integrated_runner_stage_count`. |
| required wording | Runner `PASS` does not mean external-ready proposal, external-ready quotation, buyer verification, or commercial approval. |
| source files | `output/internal_workflow_summary.md`. |
| validation checks | Runner result appears; stage count appears; no external sending implication appears. |
| privacy restrictions | Do not print private paths or command output containing sensitive data. |

### 3. Buyer Pipeline Summary

| Schema item | Requirement |
| --- | --- |
| section purpose | Summarize buyer lead pipeline status from sample buyer master data. |
| required metrics | `total_buyers`, `buyer_count_by_lead_status`, `moq_issue_count`. |
| required wording | Buyer records are sample/internal-review records; buyer authenticity is not verified. |
| source files | `data/buyers_master_sample.csv`. |
| validation checks | Row count matches buyer master CSV; lead status counts appear. |
| privacy restrictions | Do not print `contact_email`, `contact_phone`, `wechat_id`, `whatsapp`, or contact-like values. |

### 4. Buyer Priority Summary

| Schema item | Requirement |
| --- | --- |
| section purpose | Summarize internal sales priority tiers and scoring status. |
| required metrics | `buyer_count_by_priority_tier`, `buyer_count_by_approval_block`. |
| required wording | `score_total` is not buyer authenticity, creditworthiness, payment ability, or purchase probability. |
| source files | `data/buyers_scored_sample.csv`. |
| validation checks | Priority tier counts appear; `score_total` disclaimer appears. |
| privacy restrictions | Scored output should not expose unnecessary contact information. |

### 5. Approval & Brand Risk Summary

| Schema item | Requirement |
| --- | --- |
| section purpose | Make approval-blocked and approval-required brand issues visible. |
| required metrics | `buyer_count_by_approval_block`, `approval_required_brand_issue_count`, `medicube_blocked_or_review_needed_count`. |
| required wording | `approval_block` has priority over `priority_tier` and `score_total`; `메디큐브`/Medicube remains approval-required unless explicit approval is recorded. |
| source files | `data/buyers_master_sample.csv`, `data/buyers_scored_sample.csv`, `data/proposal_messages_sample.csv`, `data/quotation_sample.csv`, `data/brands_master.csv`. |
| validation checks | Approval block summary appears; `메디큐브`/Medicube warning appears. |
| privacy restrictions | Do not expose confidential approval records beyond sample-safe status summary. |

### 6. Proposal Message Summary

| Schema item | Requirement |
| --- | --- |
| section purpose | Summarize proposal draft statuses without printing outbound-ready message bodies. |
| required metrics | `proposal_count_by_message_status`, `required_internal_review_count`, `approval_required_brand_issue_count`. |
| required wording | Proposal messages are draft/internal-review outputs and must not be sent externally without human review. |
| source files | `data/proposal_messages_sample.csv`. |
| validation checks | Message status counts appear; draft/internal-review wording appears. |
| privacy restrictions | Do not print full message bodies, contact fields, send instructions, or buyer contact data. |

### 7. Quotation Summary

| Schema item | Requirement |
| --- | --- |
| section purpose | Summarize quotation draft statuses and review-needed conditions. |
| required metrics | `quotation_count_by_quotation_status`, `required_internal_review_count`, `buyer_count_by_approval_block`. |
| required wording | Quotation outputs are internal-review drafts and are not final commercial offers. |
| source files | `data/quotation_sample.csv`. |
| validation checks | Quotation status counts appear; final commercial approval disclaimer appears. |
| privacy restrictions | Do not include contact fields; aggregate sensitive commercial indicators where possible. |

### 8. MOQ / Price / Stock / Expiry Issues

| Schema item | Requirement |
| --- | --- |
| section purpose | Highlight commercial confirmation gaps before external use. |
| required metrics | `moq_issue_count`, `price_confirmation_needed_count`, `stock_confirmation_needed_count`, `expiry_confirmation_needed_count`. |
| required wording | Price, stock, expiry, MOQ, delivery, tax, shipping, duties, payment terms, and incoterms require manual verification before external use. |
| source files | `data/buyers_master_sample.csv`, `data/quotation_sample.csv`. |
| validation checks | MOQ, price, stock, and expiry issue metrics appear. |
| privacy restrictions | Show counts/status summaries; avoid exposing real commercial data in future workflows. |

### 9. Next Action Summary

| Schema item | Requirement |
| --- | --- |
| section purpose | Summarize internal follow-up actions. |
| required metrics | `next_action_summary`. |
| required wording | Next actions are internal operational guidance only, not external send instructions. |
| source files | `data/buyers_master_sample.csv`, `data/buyers_scored_sample.csv`, `data/proposal_messages_sample.csv`, `data/quotation_sample.csv`. |
| validation checks | Next-action summary appears; no contact values appear. |
| privacy restrictions | Do not include contact details, private notes, or direct send instructions. |

### 10. Internal Review Required Items

| Schema item | Requirement |
| --- | --- |
| section purpose | List or count items requiring human review before use. |
| required metrics | `required_internal_review_count`, `approval_required_brand_issue_count`, `price_confirmation_needed_count`, `stock_confirmation_needed_count`, `expiry_confirmation_needed_count`. |
| required wording | Human review is required before external proposal, message, quotation, or commercial use. |
| source files | `data/proposal_messages_sample.csv`, `data/quotation_sample.csv`, `data/buyers_scored_sample.csv`, `data/buyers_master_sample.csv`. |
| validation checks | Internal review count appears; human review wording appears. |
| privacy restrictions | Review items may use IDs and status summaries but must not expose contact fields. |

### 11. Key Risks and Warnings

| Schema item | Requirement |
| --- | --- |
| section purpose | Summarize visible operational and compliance risks. |
| required metrics | `key_risk_count`, approval risk count, MOQ/commercial confirmation counts. |
| required wording | Dashboard `PASS` and summary `PASS` do not remove manual review duties. |
| source files | All dashboard inputs. |
| validation checks | Risk section exists; HIGH/MEDIUM/LOW risk levels appear where relevant. |
| privacy restrictions | If private/real data is detected in a future validator, dashboard generation should fail rather than summarize it. |

### 12. Final Operational Recommendation

| Schema item | Requirement |
| --- | --- |
| section purpose | Provide a concise internal next step based on visible workflow status and risk summary. |
| required metrics | `integrated_runner_result`, `key_risk_count`, `required_internal_review_count`, approval risk metrics. |
| required wording | Recommendation is internal only; do not externally send or treat as final approval. |
| source files | All dashboard inputs. |
| validation checks | Final recommendation appears; no external-ready wording appears. |
| privacy restrictions | Do not include contact fields, private notes, or private paths. |

## 6. Metric Dictionary

| metric_name | description | source_file | source_column_or_source_rule | calculation_rule | expected_output_type | safety_note |
| --- | --- | --- | --- | --- | --- | --- |
| `integrated_runner_result` | Latest Integrated Runner overall status. | `output/internal_workflow_summary.md` | `result:` line. | Parse `result` value such as `PASS`, `WARNING`, or `FAIL`. | string | `PASS` is operational validation only, not commercial approval. |
| `integrated_runner_stage_count` | Number of runner stages shown in Stage Results. | `output/internal_workflow_summary.md` | Stage Results table rows. | Count stage rows excluding table header/separator. | integer | Stage count does not prove business readiness. |
| `total_buyers` | Total buyer records in sample buyer master. | `data/buyers_master_sample.csv` | row count. | Count data rows. | integer | Sample/internal-review buyer count only. |
| `buyer_count_by_priority_tier` | Buyer count by internal priority tier. | `data/buyers_scored_sample.csv` | `priority_tier`. | Count each tier with `Counter`. | mapping | Priority tier is internal follow-up priority only. |
| `buyer_count_by_approval_block` | Buyer count by approval block. | `data/buyers_scored_sample.csv`; optionally `data/quotation_sample.csv`. | `approval_block`. | Count true/false values in scored buyers; quote-level blocks may be summarized separately. | mapping | Approval block overrides score and priority. |
| `buyer_count_by_lead_status` | Buyer count by lead status. | `data/buyers_master_sample.csv` | `lead_status`. | Count each lead status value. | mapping | Does not verify buyer authenticity. |
| `proposal_count_by_message_status` | Proposal draft count by status. | `data/proposal_messages_sample.csv` | `message_status`. | Count each message status. | mapping | Draft status is not send permission. |
| `quotation_count_by_quotation_status` | Quotation draft count by status. | `data/quotation_sample.csv` | `quotation_status`. | Count each quotation status. | mapping | Quotation status is not final commercial approval. |
| `moq_issue_count` | Count of MOQ mismatch or unknown cases. | `data/buyers_master_sample.csv`; `data/quotation_sample.csv`. | `moq_fit`, `moq_check`. | Count buyer rows with `moq_fit` in `no`, `unknown`; count quotation rows with `moq_check` in `fail`, `unknown`. | integer | MOQ must be manually confirmed before external quote. |
| `price_confirmation_needed_count` | Count of price confirmation-needed quote rows. | `data/quotation_sample.csv` | `quotation_status`, `compliance_notes`, `next_action`. | Count rows where status or review text indicates price confirmation required. | integer | Do not expose real price details in dashboard v1. |
| `stock_confirmation_needed_count` | Count of stock confirmation-needed quote rows. | `data/quotation_sample.csv` | `quotation_status`, `stock_status`, `compliance_notes`, `next_action`. | Count rows where status or review text indicates stock confirmation required. | integer | Stock must be manually verified. |
| `expiry_confirmation_needed_count` | Count of expiry confirmation-needed quote rows. | `data/quotation_sample.csv` | `quotation_status`, `expiry_date`, `compliance_notes`, `next_action`. | Count rows where status or review text indicates expiry confirmation required. | integer | Expiry must be manually verified. |
| `approval_required_brand_issue_count` | Count of approval-required or proposal-blocked issues. | All CSV inputs; `data/brands_master.csv`. | `approval_required`, `proposal_allowed`, `approval_block`, `approval_warning`, `proposal_brand_check`, `excluded_brands`, `brand_name`. | Count rows with approval-required, proposal-blocked, approval-blocked, excluded, or review-required status. | integer | Approval-required brands must not be shown as external-ready. |
| `medicube_blocked_or_review_needed_count` | Count of `메디큐브`/Medicube blocked, excluded, or review-needed cases. | All CSV inputs; `data/brands_master.csv`. | brand text fields and approval fields. | Count rows involving `메디큐브`, mojibake equivalent `硫붾뵒?먮툕`, or `Medicube` where approval is required, blocked, excluded, or review-needed. | integer | `메디큐브` remains approval-required unless explicit approval exists. |
| `required_internal_review_count` | Count of rows requiring human/internal review. | `data/proposal_messages_sample.csv`; `data/quotation_sample.csv`; scored/master buyer files where applicable. | `required_internal_review`, `approval_block`, warning/review statuses. | Count rows with `required_internal_review=true`, approval block, warning status, quotation issue, or proposal review status. | integer | Internal review is required before external use. |
| `next_action_summary` | Summary of internal next actions. | buyer, scored, proposal, quotation CSVs. | `next_action`, `recommended_next_action`. | Aggregate or list non-contact next actions by source/status. | mapping or bullet list | Must not include contact data or send instructions. |
| `key_risk_count` | Count of visible risk categories. | All dashboard inputs. | derived risk categories. | Count distinct HIGH/MEDIUM/LOW risk categories visible in current data. | integer | Risk count is operational guidance, not compliance clearance. |

## 7. Calculation Rules

Future implementation must follow these rules:

- `total_buyers` comes from `data/buyers_master_sample.csv` row count.
- `priority_tier` counts come from `data/buyers_scored_sample.csv`.
- `approval_block` counts come from `data/buyers_scored_sample.csv` and quotation outputs if applicable.
- `lead_status` counts come from `data/buyers_master_sample.csv`.
- `message_status` counts come from `data/proposal_messages_sample.csv`.
- `quotation_status` counts come from `data/quotation_sample.csv`.
- `moq_issue_count` comes from `moq_fit=no/unknown` or `moq_check=fail/unknown` where available.
- `price_confirmation_needed_count` comes from `quotation_status` or validation/status text indicating price confirmation required.
- `stock_confirmation_needed_count` comes from `quotation_status`, `stock_status`, or validation/status text indicating stock confirmation required.
- `expiry_confirmation_needed_count` comes from `quotation_status`, `expiry_date`, or validation/status text indicating expiry confirmation required.
- `approval_required_brand_issue_count` comes from `approval_required`, `proposal_allowed=false`, `approval_block=true`, `approval_warning`, `proposal_brand_check=approval_required_review`, `excluded_brands`, or equivalent brand safety fields.
- `medicube_blocked_or_review_needed_count` comes from rows involving `메디큐브`, mojibake equivalent `硫붾뵒?먮툕`, or `Medicube` where approval is required, blocked, excluded, or review-needed.
- `required_internal_review_count` comes from `required_internal_review=true`, approval block, warning statuses, quotation issues, or proposal review status.
- `next_action_summary` comes from internal `next_action` and `recommended_next_action` fields only, without contact data.
- `key_risk_count` comes from visible warning/risk categories, not from external data.

If exact column names differ in current or future sample CSVs, future implementation must map safely to existing columns and fail validation if required fields are absent. It must not silently skip required metrics.

## 8. Required Wording Rules

Dashboard output must include wording with these meanings:

- Internal-review only.
- External sending is prohibited / not included.
- Not final commercial approval.
- Proposal/quotation outputs are draft or internal-review outputs.
- `score_total` is not buyer authenticity, creditworthiness, payment ability, or purchase probability.
- `approval_block` takes priority over `priority_tier` and `score_total`.
- `메디큐브`/Medicube is approval-required and must not be externally proposed, quoted, posted, or used in buyer-facing outputs without explicit approval.

Recommended Korean wording examples:

- `이 대시보드는 내부검토용입니다.`
- `외부 발송, 메시징 자동화, 견적 발송은 포함되지 않습니다.`
- `PASS는 최종 상업 승인 또는 외부 발송 가능 상태를 의미하지 않습니다.`
- `제안/견적 출력물은 draft 또는 internal-review output입니다.`
- `score_total은 바이어 실제성, 신용도, 결제능력, 구매확률 검증이 아닙니다.`
- `approval_block은 priority_tier 및 score_total보다 우선합니다.`
- `메디큐브는 승인필요 브랜드이며 명시적 승인 전 외부 제안/견적/공개 콘텐츠에 사용할 수 없습니다.`

## 9. Forbidden Wording

Dashboard output must not include wording that implies:

- `external-ready`
- `send-ready`
- `final quotation`
- `approved quotation`
- `verified buyer`
- `credit-approved buyer`
- `purchase probability`
- `automatic sending`
- `buyer authenticity verification`
- `commercially approved price`
- `live market verified`

Future validator should flag these phrases and equivalent Korean meanings when they imply external readiness, final approval, verified buyer status, or live/external verification.

## 10. Privacy Exclusion Schema

Dashboard must not output these field names or values:

- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `phone`
- `email`
- `private_note`
- `real_contact`
- `real_price`
- `real_stock`
- `real_expiry`

Contact-related columns may exist in source files, but v1 dashboard must not print them. Dashboard v1 may count rows or summarize statuses without exposing contact data.

## 11. Approval and Brand Risk Display Schema

Approval and brand risk display rules:

- `approval_block=true` must appear in a visible warning table or bullet list.
- `메디큐브`/Medicube cases must appear in Approval & Brand Risk Summary.
- `approval_required=true` must be shown as review-required.
- `proposal_allowed=false` must be shown as blocked/not allowed for external proposal.
- `priority_tier=A` must not override `approval_block`.
- Brand opportunity and brand approval readiness must be separate.
- Approval-required brands may be recorded as buyer interest or risk flags, but must not be shown as approved external recommendation.

Recommended display columns for a future warning table:

- risk_type
- count
- related_source
- internal_review_needed
- caution_note

Do not include private approval records or confidential approval notes in dashboard v1.

## 12. Proposal Message Schema

Proposal message dashboard rules:

- Summarize `message_status` counts only.
- Show review-needed counts.
- Mention proposal messages are internal drafts.
- Do not print full outbound-ready messages unless a later task explicitly approves it.
- Do not include contact fields.
- Do not include send instructions.
- Do not imply any proposal was sent or is ready to send.
- Approval-blocked proposal rows should be shown as internal review guidance only.

Recommended v1 proposal summary fields:

- message_status
- count
- approval_block_count
- internal_review_required_count
- caution_note

## 13. Quotation Schema

Quotation dashboard rules:

- Summarize `quotation_status` counts.
- Summarize MOQ, price, stock, and expiry checks.
- Do not present quotation output as final.
- Include manual verification disclaimer.
- Do not include external sending instructions.
- If price or stock fields exist, show only aggregated counts unless later approved.
- Do not imply tax, shipping, duties, payment terms, incoterms, discounts, or final supplier terms are included unless manually verified.

Recommended v1 quotation summary fields:

- quotation_status
- count
- approval_block_count
- moq_issue_count
- price_confirmation_needed_count
- stock_confirmation_needed_count
- expiry_confirmation_needed_count
- internal_review_required_count
- caution_note

## 14. Risk Levels

Dashboard v1 should use these risk levels:

| risk_level | meaning | action |
| --- | --- | --- |
| HIGH | A blocking or business-critical risk exists. | Do not use externally; require internal review or fix. |
| MEDIUM | A review-needed or operational caution exists. | Internal use only; verify before external use. |
| LOW | Informational or routine internal-review reminder. | Monitor and review as needed. |

Required HIGH risks:

- `approval_block` present
- `메디큐브`/Medicube approval required
- private/real data detected
- contact data exposure risk
- external-ready wording detected

Required MEDIUM risks:

- generated sample outputs changed
- XLSX lock risk
- price confirmation needed
- stock confirmation needed
- expiry confirmation needed
- summary `PASS` misinterpretation risk

The dashboard may include LOW risks for routine manual review reminders, such as sample-only scope, internal-review output reminders, or source freshness reminders.

## 15. Validation Expectations

Future validator must check:

- All required sections exist.
- All required metric labels exist.
- Internal-review disclaimer exists.
- No forbidden contact fields appear.
- No private paths appear.
- No external-ready/final quotation language appears.
- `approval_block` summary exists.
- `메디큐브`/Medicube approval-required warning exists.
- Proposal draft/internal-review wording exists.
- Quotation draft/internal-review wording exists.
- `score_total` disclaimer exists.
- Output is UTF-8 readable.
- Dashboard row/count summaries are consistent with sample CSV inputs.
- No forbidden automation imports or implementation patterns exist in future generator.

Future validator should also check that dashboard output does not imply:

- buyer verification
- credit approval
- purchase probability
- external message sending
- quotation sending
- final commercial approval
- live market verification

## 16. Recommended Generator Behavior

Future generator should:

- Use Python standard library only.
- Use `csv` module.
- Use `pathlib`.
- Use `collections.Counter`.
- Write UTF-8 Markdown.
- Read CSV inputs with `utf-8-sig`.
- Fail clearly if required input files are missing.
- Fail clearly if required columns are missing.
- Do not silently ignore privacy-risk fields.
- Do not read private paths by default.
- Do not create XLSX in v1.
- Do not modify source CSV files.
- Do not create real data files.
- Do not create private folders.
- Do not import or use networking, browser automation, email, messaging, crawler, scraping, API, buyer enrichment, or credit-check libraries.

Future generator should produce deterministic output so validation can compare row counts, section labels, and metric labels reliably.

## 17. Completion Criteria for Step B

Step B passes when:

- `docs/operations_dashboard_schema.md` exists.
- It defines sections, metrics, calculation rules, privacy rules, approval rules, proposal/quotation rules, forbidden wording, and validation expectations.
- No code is implemented.
- No dashboard output is created.
- No `automations/operations_dashboard/` folder is created.
- No existing automation logic is modified.
- No source CSV files are modified.
- No generated output files are modified.
- No real data files are created.
- No private folders are created.
- No external sending or external data collection automation is added.

## 18. Recommended Next Step

After Step B is reviewed and accepted, proceed to Step C only:

- Create `automations/operations_dashboard/README.md`.

Do not create the generator, dashboard output, validation script, XLSX output, private folders, real data files, or any external automation in Step C unless explicitly requested by a later instruction.
