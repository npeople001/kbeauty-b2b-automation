# Operations Dashboard

## Purpose

The Operations Dashboard will summarize the local sample/internal-review buyer sales workflow for the K-beauty B2B automation project.

It will read existing Task 006-011 outputs and reduce manual review friction by collecting workflow status, buyer priority, approval blocks, proposal draft status, quotation draft status, commercial confirmation gaps, and next-action summaries into one internal review document.

The dashboard is not an external communication tool. It is not a buyer verification tool, credit check tool, purchase probability tool, or final quotation approval tool.

## Current Status

Task 012 has a Markdown generator and validator for v1.

- Generator: `automations/operations_dashboard/generate_operations_dashboard.py`
- Validator: `tests/validate_operations_dashboard.py`
- v1 target output is `output/operations_dashboard.md`.

XLSX and dashboard summary CSV outputs are not active in v1.

## Planned Input Files

Dashboard v1 is planned to read these local sample/internal-review files only:

- `output/internal_workflow_summary.md`
- `data/buyers_master_sample.csv`
- `data/buyers_scored_sample.csv`
- `data/proposal_messages_sample.csv`
- `data/quotation_sample.csv`
- `data/brands_master.csv`

Rules:

- Use sample/internal-review files only.
- Do not use `data/private/**`.
- Do not use `output/private/**`.
- Do not use `output/final/**`.
- Do not use real buyer/contact data.
- Do not use real price, stock, expiry, quotation, or private commercial data.

## Planned Output Files

v1 output:

- `output/operations_dashboard.md`

Optional future outputs:

- `output/operations_dashboard.xlsx`
- `data/operations_dashboard_summary.csv`

XLSX is not part of v1 unless separately approved. `output/*` follows the existing generated-output policy. Dashboard output remains internal-review only.

## v1 Output Policy

Use `output/operations_dashboard.md` only for v1.

- Do not expect `output/operations_dashboard.xlsx`.
- Do not expect `data/operations_dashboard_summary.csv`.
- If a reviewer needs spreadsheet filtering later, XLSX must be designed and validated in a separate step.
- Markdown dashboard output remains internal-review only and should not be externally sent.
- Markdown-only v1 reduces file lock risk, validation complexity, privacy exposure risk, and accidental external-use risk.

Current dashboard validation may show a non-blocking warning when the `brands` row count is not directly printed in the dashboard body. This warning does not block v1 if brand risk and approval information are still summarized. A future version may add explicit brands row count if operationally useful. Do not modify generator output solely to remove this warning.

## Planned Commands

Generation command:

```powershell
python automations/operations_dashboard/generate_operations_dashboard.py
```

Validation command:

```powershell
python tests/validate_operations_dashboard.py --dashboard output/operations_dashboard.md
```

Existing safety command:

```powershell
python tests/validate_privacy_guard.py
```

The generator writes Markdown only in v1. It does not create XLSX or CSV dashboard summary outputs.

## Recommended Future Workflow

1. Run Privacy Guard.
2. Run Integrated Runner if updated buyer/proposal/quotation data is needed.
3. Generate operations dashboard.
4. Validate operations dashboard.
5. Review dashboard manually.
6. Do not externally send dashboard outputs.

The dashboard should be used as an internal operating summary only. It should not be treated as approval to send proposals, messages, or quotations.

## Dashboard Sections

The dashboard must include these required sections:

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

Each section must include or inherit an internal-review-only disclaimer.

## Privacy Rules

Dashboard output must not print these field names or values:

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

Contact-related columns may exist in source files, but v1 dashboard must not print them.

## Approval and Brand Rules

- `approval_block=true` must be clearly visible.
- `메디큐브`/Medicube must remain approval-required unless explicit approval is recorded.
- `approval_required=true` must be shown as review-required.
- `proposal_allowed=false` must be shown as blocked/not allowed for external proposal.
- `priority_tier=A` or high `score_total` must not override `approval_block`.
- `score_total` is an internal prioritization signal only, not buyer authenticity, creditworthiness, payment ability, or purchase probability.

Brand opportunity and brand approval readiness must be kept separate.

## Proposal and Quotation Rules

- Proposal messages are internal drafts.
- Quotations are internal drafts.
- `PASS` does not mean final commercial approval.
- Integrated Runner `PASS` does not mean proposals or quotations are ready to send.
- Price, stock, expiry, MOQ, delivery, tax, shipping, duties, payment terms, and incoterms require manual review before external use.
- Dashboard must not include send-ready or final quotation language.

## External Automation Restrictions

The dashboard must not implement:

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

The dashboard must not send emails, DMs, WeChat messages, WhatsApp messages, quotations, or any external communication.

## Operator Checklist

Before generating:

- Privacy Guard passes.
- Integrated Runner summary exists if needed.
- Sample CSV files exist.
- No real/private data is staged.
- No `output/private` or `output/final` path is used.

After generating:

- Dashboard is reviewed manually.
- `approval_block` and `메디큐브`/Medicube warnings are checked.
- Proposal/quotation disclaimers are checked.
- Dashboard is not externally sent.
- Privacy Guard is run before commit.

## Known Limitations

- v1 is Markdown only.
- v1 uses sample/internal-review data only.
- No real/private workflow support.
- No external sending.
- No buyer verification.
- No credit check.
- No live market verification.
- No final quotation approval.
- No dashboard XLSX unless separately approved.

## Future Step References

- Step D should create `generate_operations_dashboard.py`.
- Step E should generate `output/operations_dashboard.md`.
- Step F should create `tests/validate_operations_dashboard.py`.
- Step G should decide whether XLSX is needed later.
- Step H should update root README.
- Step I should update roadmap/task log.
- Step J should perform final review.

Do not proceed to Step D until Step C is reviewed and accepted.
