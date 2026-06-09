# Real Data Migration & Privacy Guard Specification

## 1. Scope

Task 010 defines the operating rules and guardrails needed before the automation foundation is used with real business data.

Task 010 does:

- Separate sample/fictitious data from future real operating data.
- Define how sensitive buyer, contact, price, stock, expiry, quotation, and approval data should be classified.
- Define privacy and business-data guard requirements before files are committed or used in internal workflows.
- Define future validation requirements for detecting accidental exposure of private or commercially sensitive data.
- Protect the existing Task 001-009 automation foundation before real business use.

Task 010 does not do:

- It does not create real buyer, contact, price, stock, expiry, supplier, or quotation files.
- It does not move existing files.
- It does not change `.gitignore` in Step A.
- It does not implement code in Step A.
- It does not change business automation logic from Task 001-009.
- It does not collect, scrape, enrich, verify, crawl, or search external data.
- It does not use APIs, browser automation, live web research, buyer enrichment, credit checks, email sending, messaging automation, or external sending.

Step A is specification-only. No real operating data should be stored, created, moved, deleted, or committed in this step.

## 2. Background

Tasks 001-009 completed the first-pass internal automation foundation for K-beauty B2B export operations:

- Brand master management
- Market research and content strategy templates
- Local market research report generation
- Channel content strategy generation
- Short-form video and feed planning
- Buyer lead templates
- Buyer scoring
- Internal-review proposal message drafts
- Internal-review quotation drafts

The current repository is suitable for sample-data workflows and internal-review automation testing. Real operation introduces additional risks:

- Real buyer contact data could be exposed in Git or generated outputs.
- Real price, stock, expiry, supply availability, and supplier terms could leak.
- Approval-required brands could be proposed externally without approval.
- Draft proposal messages or quotations could be mistaken for final external communication.
- Generated internal-review outputs could be shared externally without human review.
- Private business data could be accidentally committed to GitHub.

Task 010 should reduce these risks before any real buyer/contact/commercial data is introduced.

## 3. Data Classification

| Data class | Examples | May be committed to Git? | Storage recommendation | Validation requirement | Risk level |
| --- | --- | --- | --- | --- | --- |
| Public/source code safe | Python scripts, schemas, specs, README files, validation scripts, prompt templates | Yes | Normal tracked repository folders | Standard test and review | Low |
| Sample/fictitious data | `*_sample.csv`, placeholder buyer rows, `example.invalid` emails, fake phone numbers, fictional quotation inputs | Yes, if clearly fictional | Tracked sample files under `data/` or future `data/samples/` | Must pass sample privacy validation | Low to medium |
| Internal business data | Manually prepared operating spreadsheets, internal notes without personal contact details, non-public workflow records | Generally no, unless explicitly approved | Future ignored private folders | Manual review before use | Medium |
| Sensitive buyer/contact data | Real buyer names, contact emails, phone numbers, WeChat IDs, WhatsApp numbers, personal buyer notes | No | Future ignored private folders only | Privacy guard must block accidental commit | High |
| Sensitive commercial data | Real price lists, stock lists, expiry dates, supply availability, supplier terms, payment terms, incoterms | No | Future ignored private folders only | Commercial-data guard must block accidental commit | High |
| Generated internal-review output | Draft proposals, draft quotations, internal reports, internal XLSX review files | Usually no for real data; sample generated outputs may remain ignored | `output/` or future `output/private/` | Must include internal-review disclaimer | Medium to high |
| Generated external-ready output | Final buyer-facing proposals, final quotations, final messages | Currently not supported | Outside repository or approved secure storage only | Requires human approval process | High |

Generated external-ready output is not supported by the current automation foundation. All proposal, quotation, scoring, and report outputs remain internal-review drafts unless a later approved process explicitly changes this rule.

## 4. Sample Data Rules

Sample data must be fictional and safe to commit.

Required sample rules:

- Use fictional company names.
- Use placeholder emails such as `buyer001@example.invalid`.
- Use fake phone numbers such as `+00-0000-0000`.
- Use placeholder WeChat and WhatsApp values such as `placeholder_wechat_001`.
- Do not include real buyer names, real contact details, real supplier details, or real private notes.
- Sample price, stock, expiry, supply, and quotation values must be clearly treated as fictional or manually provided sample values.
- Sample outputs must retain internal-review disclaimers.
- Korean, English, and Chinese text must be preserved with UTF-8-compatible encoding.
- CSV files intended for Excel or business users must use UTF-8 with BOM (`utf-8-sig`).

Sample data may include approval-required brands only to test warning and blocking behavior. If `메디큐브` appears in sample data, it must remain treated as approval-required.

## 5. Real Data Rules

The following real data must not be committed to Git:

- Real buyer company contact details
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- Real buyer notes containing personal data
- Real price lists
- Real stock lists
- Real expiry lists
- Real supply availability records
- Real quotation inputs
- Real quotation outputs
- Final quotation files
- Private supplier terms
- Payment terms
- Contract terms
- Incoterms
- Confidential brand approval records

Real operating data should be stored only in ignored private folders or another approved secure storage location. The repository should not become the source of truth for private buyer/contact/commercial records unless a future privacy and access-control policy explicitly approves that use.

## 6. Recommended Folder Strategy

This section proposes a future folder strategy only. Step A must not create these folders.

Recommended future folders:

- `data/samples/`
- `data/private/`
- `data/private/buyers/`
- `data/private/pricing/`
- `data/private/stock/`
- `data/private/expiry/`
- `data/private/quotations/`
- `output/private/`
- `output/reports/`
- `output/generated/`

Recommended tracking behavior:

- `data/samples/`: trackable if files are fictional, validated, and safe.
- `data/private/**`: ignored; no real buyer/contact/commercial data should be committed.
- `output/private/**`: ignored; real generated internal-review outputs should not be committed.
- `output/reports/` and `output/generated/`: may remain ignored by default unless a future rule defines trackable sample outputs.
- Placeholder files should be used only when needed to preserve empty safe folders. Do not use placeholder files to justify committing private folders.

Task 010 should preserve existing sample workflows. It should not break current Task 001-009 sample CSV, XLSX generation, validation, or internal draft generation.

## 7. Recommended .gitignore Strategy

This section proposes future `.gitignore` rules only. Step A must not modify `.gitignore`.

Recommended future ignore patterns:

```gitignore
data/private/**
output/private/**
*_real.csv
*_private.csv
*_production.csv
*_contacts.csv
*_prices.csv
*_stock.csv
*_expiry.csv
*_quotation_final.*
*.xlsx
.env
*.key
*.pem
*token*
*credential*
local_config.*
```

Sample files should remain trackable when they are intentionally fictional and required for tests or documentation. Examples:

- `data/*_sample.csv`
- `data/source_materials/**` when contents are sample/user-provided placeholders
- `docs/**`
- `prompts/**`
- `automations/**`
- `tests/**`

If a file contains real buyer/contact/commercial data, its name should make that risk visible and it should be ignored or moved outside the repository.

## 8. Privacy Guard Requirements

A future privacy guard validator should check for:

- `contact_email`, `contact_phone`, `wechat_id`, and `whatsapp` appearing in files that should not expose contact data.
- Non-placeholder emails in sample files.
- Real-looking phone numbers in sample files.
- Sensitive file naming patterns such as `*_real.csv`, `*_private.csv`, `*_contacts.csv`, `*_prices.csv`, `*_stock.csv`, and `*_expiry.csv`.
- Real price, stock, expiry, or supply files staged for commit.
- Generated external-ready quotation files.
- Missing internal-review disclaimers in proposal, quotation, scoring, and report outputs.
- Approval-required brand misuse.
- `메디큐브` appearing as externally allowed, recommended, quoted, or buyer-facing without explicit approval.
- Draft proposal or quotation outputs that include contact email, phone, WeChat ID, or WhatsApp by default.

The privacy guard should not automatically delete or rewrite business data. It should report the issue, block unsafe validation, and require manual review.

## 9. Pre-commit / Manual Review Concept

Before committing real-operation work, the operator should:

1. Run `git status`.
2. Review staged and unstaged files.
3. Run the privacy validation script after it exists.
4. Confirm that only source code, documentation, schemas, tests, sample data, and safe placeholders are staged.
5. Confirm that private buyer/contact/commercial data is not staged.
6. Confirm that generated real-data outputs are not staged.
7. Confirm approval-required brand handling, especially for `메디큐브`.
8. Require manual confirmation for ambiguous files.

The guard process should not auto-delete files, auto-stage files, or auto-commit changes. It should support safer human review.

## 10. Real Operation Migration Checklist

Before using the automation foundation with real business data:

- Confirm the repository visibility and access policy are appropriate for business operations.
- Confirm `.gitignore` protects private folders and sensitive file patterns.
- Confirm a real-data folder exists only after it is ignored.
- Confirm sample data is clearly separated from real data.
- Confirm contact data is masked where needed.
- Confirm price, stock, expiry, supply availability, MOQ, and delivery lead time are manually verified before use.
- Confirm approval-required brands are reviewed before proposal, quotation, public content, or buyer-facing communication.
- Confirm `메디큐브` remains approval-required unless explicit approval is recorded.
- Confirm all generated outputs are treated as internal-review drafts.
- Confirm final external communication remains manual and separately approved.
- Confirm no automation sends emails, DMs, WeChat messages, WhatsApp messages, quotations, or platform posts.

## 11. Task 001-009 Impact

Task 010 should protect the existing automation foundation without breaking it.

- Brand Master Automation: approval rules remain business-critical and must not be changed casually.
- Market Research and Content Workflows: generated reports and strategies remain internal-review drafts unless source verification and external-use review are completed.
- Buyer Lead Template: real contact fields require privacy protection; sample placeholder data remains trackable.
- Buyer Scoring Automation: scores remain internal prioritization signals only and must not imply buyer authenticity, creditworthiness, payment ability, or purchase certainty.
- Proposal Message Generator: drafts remain internal-review only; approval-blocked rows must not generate buyer-facing proposal copy.
- Quotation Maker: quotation outputs remain internal-review drafts; price, stock, expiry, MOQ, delivery, and commercial terms must come from manually provided verified inputs.

Task 010 should not change Task 001-009 business logic unless a future approved step identifies a critical privacy or data-protection issue.

## 12. Completion Criteria

Task 010 is complete only when future steps satisfy all of the following:

- This specification exists.
- A real/sample data policy document exists.
- `.gitignore` strategy is reviewed and safely applied.
- A privacy guard validation script exists.
- Existing sample data passes privacy validation.
- Safe simulated unsafe fixtures are detected by the guard.
- README or operating guidance is updated.
- Roadmap and task log are updated.
- Final review passes.

## 13. Recommended Future Steps

Recommended Task 010 sequence:

- Step B: Create a real/sample data policy document.
- Step C: Update `.gitignore` safely after reviewing current tracked files.
- Step D: Create a privacy guard validation script.
- Step E: Add README operating guidance.
- Step F: Test the guard with safe simulated fixtures.
- Step G: Update roadmap and task log.
- Step H: Perform final review.

Do not implement an integrated runner, dashboard, external research intake workflow, scraping, live research, external messaging, or quotation sending as part of Task 010 unless explicitly approved in a later task.
