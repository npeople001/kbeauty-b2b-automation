# Market Research Report Generator

This folder contains the local workflow for Task 003: Market Research Report Generator.

## 1. Purpose

This automation generates a Korean Markdown market research report from:

- Local structured CSV input
- User-provided source materials

It is designed for K-beauty B2B export marketing, especially market research, China channel planning, content direction, and B2B buyer acquisition planning.

This automation does not perform scraping, live web research, automated web search, browser automation, API calls, crawling, or external data collection. It only reads local files already provided by the user or business team.

## 2. Input Requirements

Required inputs:

- Research input CSV path: `data/research_inputs_sample.csv`
- Research ID: for example, `MR-001`
- Source materials folder path: `data/source_materials/market_research/{research_id}/`
- Source notes file: `data/source_materials/market_research/{research_id}/source_notes.md`
- Source registry file: `data/source_materials/market_research/{research_id}/sources.csv`

Default MR-001 example:

```text
data/research_inputs_sample.csv
data/source_materials/market_research/MR-001/source_notes.md
data/source_materials/market_research/MR-001/sources.csv
```

CSV files intended for Excel or business users must use UTF-8 with BOM, compatible with `utf-8-sig`.

## 3. Source Material Rules

Source materials must be user-provided only.

Allowed source materials include:

- Manually collected notes
- Copied platform observations
- User-provided links with descriptions
- Screenshots or exports manually provided by the user
- Internal notes
- Brand approval notes
- Product information provided by the business team

Source materials must not include guessed market facts.

The generator must not invent market size, rankings, sales data, platform statistics, view counts, engagement rates, regulatory facts, or fake source names.

If evidence is missing, weak, or insufficient, the generated report must clearly mark the affected findings as:

- `검증 필요`
- `소스 자료 부족`
- `확정 불가`

## 4. Generation Command

Basic command:

```powershell
python automations/market_research/generate_market_research_report.py --research-id MR-001
```

Optional arguments:

```powershell
python automations/market_research/generate_market_research_report.py `
  --research-id MR-001 `
  --input data/research_inputs_sample.csv `
  --source-root data/source_materials/market_research `
  --output-dir output
```

Default output:

```text
output/market_research_report_{research_id}.md
```

Example:

```text
output/market_research_report_MR-001.md
```

## 5. Validation Command

Run the validation script before using a generated report for internal reporting, external proposals, or content execution.

```powershell
python tests/validate_market_research_report.py --report output/market_research_report_MR-001.md
```

The validation script checks:

- Report file existence
- UTF-8 readability
- Korean text preservation
- All 12 required report sections
- Evidence labels
- Insufficient-evidence wording
- B2B/B2C separation
- China risks when relevant
- Brand approval restrictions
- Fake source patterns
- Unsupported statistics
- Recommendation fields for execution difficulty, expected effect, cost level, and risk level

## 6. Standard Workflow

Step 1: Add or update a research input row.

- Add a row to `data/research_inputs_sample.csv` or a future `data/research_inputs.csv`.
- Confirm `research_id`, target country, target channels, target brands, product categories, objective, budget, and execution period.

Step 2: Add user-provided source materials.

- Create or update `data/source_materials/market_research/{research_id}/`.
- Add `source_notes.md`.
- Add `sources.csv`.
- Do not add guessed facts.

Step 3: Generate the report.

```powershell
python automations/market_research/generate_market_research_report.py --research-id MR-001
```

Step 4: Run the validation script.

```powershell
python tests/validate_market_research_report.py --report output/market_research_report_MR-001.md
```

Step 5: Review the report manually using:

```text
docs/market_research_review_checklist.md
```

Step 6: Mark the report as one of:

- `PASS`
- `PASS WITH CAUTION`
- `FAIL`

Step 7: Use the report only internally unless external claims are verified.

- External proposals, public content, buyer-facing materials, market data claims, cosmetics claims, and channel policy claims require separate verification before use.

## 7. PASS / PASS WITH CAUTION / FAIL Usage Rules

`FAIL`

- Do not use externally.
- Do not use internally for business decisions until fixed.
- Fix evidence, compliance, brand approval, fake data, or execution-readiness problems first.

`PASS WITH CAUTION`

- Internal planning only.
- External use requires verification.
- Use this when the structure is useful but source evidence, approval, localization, compliance, or execution details remain unresolved.

`PASS`

- May be used as an internal planning document.
- External claims still require verification.
- Do not treat `PASS` as approval for public posting, external proposal, buyer-facing claims, or regulatory/cosmetics claims.

## 8. Business Rules

- Separate B2B buyer acquisition from consumer marketing.
- Consumer engagement is not the same as B2B buyer demand.
- Include China risks where relevant, including account operation, real-name/account restrictions, platform policy, localization, and channel operation risk.
- Include cosmetics claim and compliance risks.
- Avoid exaggerated efficacy, medical, drug-like, before/after, clinical, or functional claims unless verified and approved for the target country.
- Respect approval-required brands.
- `메디큐브` must not be externally recommended, posted, proposed to buyers, or used in public-facing content unless explicit approval is provided.
- Approval-required brands may be mentioned only as restricted or excluded items unless approval is recorded.

## 9. Known Limitations

- No live market data is collected.
- No automatic source verification is performed.
- Output quality depends on the quality and completeness of user-provided source materials.
- China platform rules may change and must be checked before execution.
- China account operation and real-name/account requirements must be verified before channel operation.
- Cosmetic claims must be reviewed before external use.
- The generated report is not a substitute for legal, regulatory, platform policy, or brand approval review.

## 10. Related Files

- `docs/market_research_generator_spec.md`
- `docs/market_research_schema.md`
- `docs/market_research_review_checklist.md`
- `data/source_materials/market_research/README.md`
- `automations/market_research/generate_market_research_report.py`
- `tests/validate_market_research_report.py`
