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
