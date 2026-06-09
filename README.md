# K-Beauty B2B Automation

Automation tools and structured data for a K-beauty B2B export business.

## Project Purpose

This repository supports sourcing Korean cosmetics and health product brands through domestic distributors and selling them to overseas buyers. The automation focus is to keep brand data structured, safe for proposal workflows, and usable by business users.

## Folder Structure

```text
automations/
  brand_master/
    generate_brands_master_xlsx.py
data/
  brands_raw.csv
  brands_master.csv
docs/
  brand_master_schema.md
output/
  brands_master.xlsx
tests/
  validate_brands_master.py
```

## Business Context

The business sources Korean brands domestically and sells to overseas buyers. Priority markets are China, Southeast Asia, Russia, and later global buyers. Buyer type is flexible when the buyer can order 100+ units.

Important operating rules:

- MOQ is generally 100+ units.
- Delivery lead time is generally 20-30 days.
- Korean, English, and Chinese text must be handled with UTF-8.

## Brand Master Automation

The brand master automation converts the raw available brand list into a structured master CSV and business-user XLSX output.

- `data/brands_raw.csv` stores the raw brand list with category and source note.
- `data/brands_master.csv` stores normalized brand records and approval controls.
- `output/brands_master.xlsx` is the business-user spreadsheet output.
- `docs/brand_master_schema.md` defines required columns, defaults, and allowed values.

## Validate Brand Data

Run the validation script before using the brand master for proposals or XLSX generation:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" tests\validate_brands_master.py
```

The validation checks required files, required columns, row counts, approval rules, Korean text preservation, blank brand names, and priority values.

## Generate XLSX Output

Run the XLSX generation script:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" automations\brand_master\generate_brands_master_xlsx.py
```

The script reads `data/brands_master.csv` and creates `output/brands_master.xlsx`. It validates required columns before generation, preserves Korean text, freezes the header row, adjusts column widths, and highlights approval inspection columns.

## Business Rules

- `메디큐브` requires director approval before external posting/proposal.
- Approval-required brands must not be `proposal_allowed` by default.
- Approval-required brands can only be included in external proposal outputs after explicit approval.
- Unknown official English brand names should not be guessed.
- Priority values should use `high`, `medium`, `low`, or `unknown`.

## Real Data & Privacy Guard

Tasks 001-009 are the first-pass internal automation foundation for brand master, market/content planning, buyer lead templates, buyer scoring, internal-review proposal drafts, and internal-review quotation drafts.

The current sample files are safe, fictitious test data. Real buyer, contact, price, stock, expiry, supplier, quotation, and approval-sensitive data must not be committed to Git. Task 010 adds policy and guardrails for real operation, but the system remains internal-review only.

### Before Using Real Data

- Confirm repository privacy and access control.
- Confirm `.gitignore` protects private folders and sensitive filename patterns.
- Do not place real data in tracked sample files.
- Use ignored/private paths for real operating data only after policy is applied.
- Do not commit buyer contact data.
- Do not commit real price, stock, expiry, or supplier terms.
- Do not commit final quotations or external-ready documents.
- Run Privacy Guard validation before commit.
- Manually review `git status` before commit.
- Keep external communication manual and separately approved.

### Privacy Guard Command

Run the Privacy Guard before committing or before introducing real operating data:

```powershell
python tests/validate_privacy_guard.py
```

Optional modes:

```powershell
python tests/validate_privacy_guard.py --root .
python tests/validate_privacy_guard.py --mode working-tree
python tests/validate_privacy_guard.py --staged-only
```

The validation checks:

- Sensitive file names and paths.
- Real/private/contact/price/stock/expiry/final quotation patterns.
- Sample contact placeholder safety.
- `메디큐브` approval-required context.
- Forbidden external collection or sending implementation.
- Required `.gitignore` protections.
- Sample files remain trackable.

### Safe Sample Data Rules

- Sample data must be fictional.
- Sample emails should use `example.invalid`.
- Sample phone numbers must be placeholders.
- Sample WeChat and WhatsApp values must be placeholders.
- Sample price, stock, and expiry values must be marked as fictional/manual sample values.
- Sample proposal and quotation outputs must remain internal-review drafts.

### Real Data Rules

The following must not be committed:

- Real buyer contact details.
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- Real buyer notes with private business context.
- Real supplier price lists.
- Real stock lists.
- Real expiry lists.
- Real supply availability.
- Real quotation inputs.
- Real quotation outputs.
- Final quotations.
- Supplier payment terms.
- Private contract terms.
- Incoterms.
- Confidential brand approval records.
- Credentials, tokens, or local config.

### External Automation Restrictions

This repository does not currently implement:

- Scraping.
- Live web research.
- Automatic search.
- APIs.
- Browser automation.
- Crawlers.
- Buyer enrichment.
- Credit checks.
- Email sending.
- Messaging automation.
- Quotation sending.
- External sending.

### Operating Principle

Internal-review outputs are not final external documents. Proposal drafts and quotation drafts require human review before external use.

Price, stock, expiry, MOQ, delivery, tax, shipping, duties, payment terms, and incoterms must be manually verified.

Approval-required brands such as `메디큐브` must not be externally proposed, quoted, or used in public content without explicit approval.

### Commit Safety Workflow

1. Update sample/source files only.
2. Keep real data outside tracked paths.
3. Run:

   ```powershell
   python tests/validate_privacy_guard.py
   ```

4. Run:

   ```powershell
   git status --short
   ```

5. Review staged files manually.
6. Commit only source, docs, tests, automation, and sample-safe files.
7. Do not commit ignored/private files or final external documents.
