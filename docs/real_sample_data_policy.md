# Real and Sample Data Policy

## 1. Purpose

This policy defines how sample data and real business data must be separated before the Task 001-009 automation foundation is used with real buyer, contact, price, stock, expiry, quotation, or approval-sensitive data.

Tasks 001-009 are currently designed for sample data, local files, and internal-review automation. They are useful for testing workflows, validating schemas, generating internal drafts, and reviewing business logic.

Real business operation introduces privacy and confidentiality risks:

- Real buyer and contact information can expose personal or business-sensitive data.
- Real price, stock, expiry, supply, and supplier terms can expose commercial information.
- Real quotation drafts can be mistaken for final commercial offers.
- Approval-sensitive brand decisions can expose confidential business rules.
- Private data can be accidentally staged, committed, or pushed to GitHub.

The purpose of this policy is to make the safe path obvious before real operating data is introduced.

## 2. Definitions

| Term | Definition |
| --- | --- |
| Sample data | Data created for testing, documentation, validation, or workflow demonstration. It must be safe to commit. |
| Fictional data | Non-real data that does not identify actual buyers, contacts, suppliers, prices, stock, expiry, contracts, or private business terms. |
| Real operating data | Data used for actual business operation, including real buyers, contacts, prices, stock, expiry, quotation inputs, quotation outputs, supplier terms, and approval records. |
| Sensitive buyer/contact data | Real buyer names, company contact details, contact emails, phone numbers, WeChat IDs, WhatsApp numbers, SNS links tied to real people, and private buyer notes. |
| Sensitive commercial data | Real supplier prices, price lists, stock lists, inventory, expiry dates, supply availability, payment terms, contract terms, incoterms, and quotation values. |
| Generated internal-review output | Reports, proposal drafts, scoring outputs, quotation drafts, XLSX workbooks, or Markdown summaries generated for internal review only. |
| Final external business document | A final buyer-facing proposal, quotation, message, contract, product list, or other external commercial document. This is outside the current automation scope. |
| Approval-sensitive brand data | Brand approval status, proposal eligibility, confidential approval records, and business decisions for approval-required brands. |

## 3. Sample Data Policy

Sample data may be committed only when all of the following are true:

- It is fictional.
- It uses placeholder contacts only.
- It uses safe placeholder domains such as `example.invalid`.
- It does not contain real buyer or contact details.
- It does not contain real supplier price, stock, expiry, supply, or payment information.
- It includes internal-review disclaimers where relevant.
- It is suitable for public code review or internal repository sharing.
- It preserves Korean, English, and Chinese text correctly.
- CSV files intended for Excel or business users use UTF-8 with BOM (`utf-8-sig`).

Safe sample contact examples:

- `buyer001@example.invalid`
- `+00-0000-0000`
- `placeholder_wechat_001`
- `placeholder_whatsapp_001`

Sample data may include approval-required brands only for testing warning, exclusion, and approval-block behavior.

## 4. Real Data Policy

Real data must not be committed to Git.

Real data includes:

- Real buyer company contact details
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- Real buyer notes with personal or private business context
- Real supplier price lists
- Real stock lists
- Real expiry lists
- Real supply availability
- Real quotation inputs
- Real quotation outputs
- Final quotations
- Supplier payment terms
- Private contract terms
- Incoterms
- Confidential brand approval records
- Private sourcing information

Real operating data should be stored only in ignored private folders or in another approved secure storage location. The repository should not contain real buyer/contact/commercial data unless a future data-protection process explicitly approves that workflow.

## 5. File Naming Policy

Safe trackable sample naming conventions:

- `*_sample.csv`
- `sample_*.csv`
- `docs/*.md`
- `prompts/*.md`
- `tests/*.py`
- `automations/*.py`
- `README.md`

High-risk names that should generally be ignored or manually reviewed:

- `*_real.csv`
- `*_private.csv`
- `*_production.csv`
- `*_contacts.csv`
- `*_buyers_real.csv`
- `*_prices.csv`
- `*_price_list.csv`
- `*_stock.csv`
- `*_inventory.csv`
- `*_expiry.csv`
- `*_quotation_final.*`
- `*_supplier_terms.*`
- `*_contract_terms.*`
- `*_payment_terms.*`
- `*_incoterms.*`

File names should make risk visible. A file that contains real operating data should not be named like a sample file.

## 6. Folder Policy

This policy proposes future folder usage only. Step B does not create folders.

Trackable folders:

- `docs/`
- `prompts/`
- `automations/`
- `tests/`
- `data/` sample files only
- `data/source_materials/` sample files or user-provided non-sensitive placeholders only

Ignored/private future folders:

- `data/private/`
- `data/private/buyers/`
- `data/private/contacts/`
- `data/private/pricing/`
- `data/private/stock/`
- `data/private/expiry/`
- `data/private/quotations/`
- `output/private/`
- `output/final/`
- `local_config/`

Private folders must be ignored before real data is placed there. Do not create private folders and then add real data before `.gitignore` has been reviewed and updated.

## 7. Data Category Table

| Data category | Examples | Commit allowed? | Recommended storage | Required review | Risk level |
| --- | --- | --- | --- | --- | --- |
| Source code | Automation scripts, validation scripts, XLSX generators | Yes | `automations/`, `tests/` | Code review and validation | Low |
| Documentation | Specs, schemas, README files, policies, prompt templates | Yes | `docs/`, `prompts/` | Business rule review | Low |
| Sample CSV | `buyers_raw_sample.csv`, `quotation_inputs_sample.csv`, `research_inputs_sample.csv` | Yes, if fictional | `data/` or future `data/samples/` | Sample privacy check | Low |
| Generated sample CSV | `buyers_scored_sample.csv`, `proposal_messages_sample.csv`, `quotation_sample.csv` | Yes, if needed for tests and fictional | `data/` sample paths | Output validation and privacy check | Low to medium |
| Generated internal-review output | Draft Markdown reports, XLSX review files, internal quotation drafts | Usually no for real data; sample outputs may remain ignored | `output/` or future `output/private/` | Internal-review disclaimer check | Medium |
| Real buyer/contact data | Real buyer email, phone, WeChat, WhatsApp, personal notes | No | Future ignored private folder or secure external storage | Privacy review | High |
| Real price/stock/expiry data | Supplier price list, stock list, expiry list, supply availability | No | Future ignored private folder or secure external storage | Commercial review | High |
| Real quotation/final commercial documents | Final quotations, buyer-facing commercial offers, external proposal files | No | Outside repository or approved secure storage | Human approval | High |
| Approval-sensitive brand records | Confidential approval decisions, blocked/proposal-limited brand records | Usually no if confidential | Future ignored private folder or secure approval system | Director/business approval | High |
| Credentials/tokens/config | API keys, passwords, tokens, local config files, `.env` | No | Local ignored files or secret manager | Security review | High |

## 8. Task-Specific Policy

### Task 001 Brand Master

- Sample/trackable: brand master schema, validation scripts, sample-safe brand master files, and policy-level approval flags.
- Private when real data is used: confidential approval records, director approval notes, supplier-specific brand permissions, and private sourcing rules.
- Before external use: confirm `approval_required` and `proposal_allowed` values, especially approval-required brands.

### Task 002-005 Market and Content Workflows

- Sample/trackable: schemas, prompt templates, sample research inputs, controlled sample reports, and sample planning outputs.
- Private when real data is used: real campaign notes, confidential channel strategy, private screenshots, real platform exports, and buyer-specific content strategy.
- Before external use: verify sources, claims, brand approvals, cosmetics wording, localization, and China platform/account risks.

### Task 006 Buyer Lead Template

- Sample/trackable: fictional buyer sample CSV files with placeholder contacts.
- Private when real data is used: real buyer company contacts, contact person details, real WeChat/WhatsApp IDs, buyer notes, and lead status history.
- Before external use: confirm contact permission, privacy handling, MOQ fit, lead qualification, and approval-required brand restrictions.

### Task 007 Buyer Scoring

- Sample/trackable: scoring schema, scoring rules, sample scored buyer CSV, and validation scripts.
- Private when real data is used: scored outputs derived from real buyers, real next actions, payment-risk notes, and internal prioritization decisions.
- Before external use: do not treat score as buyer authenticity, creditworthiness, payment ability, or purchase probability.

### Task 008 Proposal Message Generator

- Sample/trackable: message schemas, rules, sample proposal CSV, and internal-review sample Markdown.
- Private when real data is used: real buyer-specific proposal drafts and real message outputs.
- Before external use: confirm brand approval, MOQ, price/stock/expiry, claims, translation/localization, contact permission, and manual send approval.

### Task 009 Quotation Maker

- Sample/trackable: quotation schema, rules, sample quotation inputs, sample quotation CSV, and validation scripts.
- Private when real data is used: real quotation inputs, real prices, real stock, real expiry, real supplier terms, and final quotation files.
- Before external use: verify price, stock, expiry, MOQ, delivery lead time, tax, shipping, duties, payment terms, incoterms, approval status, and human approval.

## 9. Approval-Required Brand Policy

`메디큐브` remains approval-required unless explicit approval is recorded.

Rules:

- Brands with `approval_required=true` must not be externally proposed, quoted, or used in public content without approval.
- Brands with `proposal_allowed=false` must not be externally proposed, quoted, or used in public content without approval.
- Real approval records may be sensitive and should not be committed if confidential.
- Sample approval states may be committed only when they are fictional, policy-level, or required to test validation behavior.
- A high buyer score, high priority tier, or strong sales opportunity must not override approval restrictions.

## 10. Generated Output Policy

Generated output files are internal-review only unless explicitly reviewed and approved.

Rules:

- Generated proposal, message, quotation, scoring, and report outputs using real data must not be committed.
- Generated sample outputs may remain ignored unless the project explicitly tracks them for tests.
- Final external documents are outside the current automation scope.
- Final external documents must require manual review and approval.
- Output files should include internal-review disclaimers where relevant.
- Generated outputs should not expose `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp` by default.

## 11. Privacy Review Checklist

Before adding, staging, committing, or sharing files, check:

- Does the file contain real buyer contact data?
- Does it contain real email, phone, WeChat, WhatsApp, or personal identifiers?
- Does it contain real price, stock, expiry, supplier terms, payment terms, or incoterms?
- Does it contain approval-sensitive brand decisions?
- Does it contain final quotation or external-ready proposal content?
- Does it contain credentials, API keys, tokens, local config, or private notes?
- Does it include internal-review disclaimers where needed?
- Is it clearly sample and fictional?
- Could the file name make someone think it is safe when it actually contains real data?
- Is the file staged intentionally?

If the answer is unclear, treat the file as sensitive and require manual confirmation.

## 12. Git Policy

Git rules:

- Do not commit real buyer/contact/commercial data.
- Do not commit credentials, tokens, local config, or private notes.
- Do not commit generated real outputs.
- Stage files intentionally.
- Review `git status` before commit.
- Run future privacy guard validation before commit.
- Ambiguous files require manual confirmation.
- Do not auto-delete suspicious files.
- Do not auto-commit or auto-push when privacy status is unclear.

The safe default is to commit source code, documentation, schemas, tests, and fictional samples only.

## 13. Future .gitignore Recommendations

This section lists recommended future ignore patterns only. This policy does not modify `.gitignore`.

Recommended future patterns:

```gitignore
data/private/**
output/private/**
output/final/**
local_config/**
*_real.csv
*_private.csv
*_production.csv
*_contacts.csv
*_prices.csv
*_price_list.csv
*_stock.csv
*_inventory.csv
*_expiry.csv
*_quotation_final.*
*_supplier_terms.*
*_contract_terms.*
*_payment_terms.*
*_incoterms.*
.env
*.key
*_token*
*_credentials*
```

Before applying these rules, confirm they do not accidentally hide sample files required for tests.

## 14. Migration Checklist

Before moving from sample operation to real operation:

- Confirm repository privacy and access control.
- Update `.gitignore`.
- Create ignored private folders.
- Prepare real data templates outside tracked sample paths.
- Run privacy guard validation.
- Confirm approval-required brand policy.
- Confirm price, stock, expiry, supply, and MOQ verification process.
- Confirm external communication remains manual.
- Confirm final quotation review process.
- Confirm no real data is staged.
- Confirm generated real outputs are ignored or stored outside the repository.
- Confirm real buyer contact data is masked or restricted when needed.

## 15. Completion Criteria

This policy is ready when:

- Sample vs real data rules are clear.
- Real data commit restrictions are clear.
- File naming and folder policy are clear.
- Task 001-009 impact is explained.
- Privacy checklist exists.
- Future `.gitignore` strategy is documented.
- Migration checklist exists.
- No actual real data is created.
- No private folders are created in this step.
- Existing automation logic remains unchanged.

