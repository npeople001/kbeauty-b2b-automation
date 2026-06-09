# Channel Content Strategy Generator

This folder contains the local workflow for Task 004: Channel Content Strategy Generator.

## 1. Purpose

This automation generates a Korean channel-specific content strategy report from:

- an existing generated market research report
- structured research input data
- optional user-provided source materials
- the Task 004 content strategy schema

It is designed for K-beauty B2B export marketing. The output helps plan channel roles, short-form videos, feed posts, B2B buyer acquisition content, weekly uploads, execution priorities, and risk checks.

This automation does not perform scraping, live web research, automated web search, browser automation, API calls, crawling, requests to external services, or external data collection. It only reads local files already provided or generated inside the repository.

## 2. Input Requirements

Required inputs:

- Research input CSV path: `data/research_inputs_sample.csv` or future `data/research_inputs.csv`
- Research ID: for example, `MR-001`
- Existing market research report path: `output/market_research_report_{research_id}.md`
- Content strategy schema: `docs/channel_content_strategy_schema.md`

Optional inputs:

- Source material folder: `data/source_materials/market_research/{research_id}/`
- Source notes: `data/source_materials/market_research/{research_id}/source_notes.md`
- Source registry: `data/source_materials/market_research/{research_id}/sources.csv`

Related guidance:

- `docs/channel_content_strategy_generator_spec.md`
- `prompts/content_strategy_prompt.md`

CSV files intended for Excel or business users must be read with an encoding compatible with UTF-8 with BOM (`utf-8-sig`).

## 3. Output

Default output:

```text
output/channel_content_strategy_{research_id}.md
```

Example:

```text
output/channel_content_strategy_MR-001.md
```

The output is Korean Markdown.

The generated report must include all 9 required sections:

1. Strategy Summary
2. Channel Strategy
3. Short-form Video Strategy
4. Feed Post Strategy
5. B2B Buyer Acquisition Content
6. Weekly Upload Plan
7. Execution Priority
8. Risks and Compliance
9. Final Recommendation

## 4. Generation Command

Basic command:

```powershell
python automations/channel_content_strategy/generate_channel_content_strategy.py --research-id MR-001
```

Optional arguments:

```powershell
python automations/channel_content_strategy/generate_channel_content_strategy.py `
  --research-id MR-001 `
  --input data/research_inputs_sample.csv `
  --research-report-dir output `
  --source-root data/source_materials/market_research `
  --output-dir output
```

Supported optional arguments:

- `--input`: path to the research input CSV
- `--research-report-dir`: folder containing `market_research_report_{research_id}.md`
- `--source-root`: root folder for user-provided market research source materials
- `--output-dir`: output folder for the generated channel content strategy report

## 5. Validation Command

Run the validation script before using the generated report for internal planning, external proposals, or content execution.

```powershell
python tests/validate_channel_content_strategy.py --report output/channel_content_strategy_MR-001.md
```

The validation script checks structure, Korean text preservation, B2B/B2C separation, China channel risks, brand approval handling, fake source patterns, unsupported performance claims, and required strategy fields.

## 6. Standard Workflow

Step 1: Prepare or update the research input row.

- Confirm `research_id`, target country, target channels, target brands, product categories, campaign objective, budget level, and execution period.
- Do not alter business-critical data casually.

Step 2: Generate or verify the market research report.

- Required path: `output/market_research_report_{research_id}.md`
- The market research report should already mark weak evidence as `검증 필요`, `소스 자료 부족`, or `확정 불가`.

Step 3: Add or verify source materials if available.

- Use `data/source_materials/market_research/{research_id}/`.
- Add only user-provided source materials.
- Do not add guessed market facts, fake statistics, fake rankings, or fake sources.

Step 4: Generate the channel content strategy report.

```powershell
python automations/channel_content_strategy/generate_channel_content_strategy.py --research-id MR-001
```

Step 5: Run the validation script.

```powershell
python tests/validate_channel_content_strategy.py --report output/channel_content_strategy_MR-001.md
```

Step 6: Review the output manually before using it for execution.

- Use the generated report together with `docs/market_research_review_checklist.md`.
- Confirm source evidence, brand approval, cosmetics claims, localization, and execution resources.

Step 7: Use only internally unless external claims and brand permissions are verified.

- External posting, buyer-facing proposals, advertising copy, platform claims, market claims, and cosmetics claims require separate verification and approval.

## 7. Business Rules

- Separate B2B buyer acquisition from consumer marketing.
- For China, include Xiaohongshu, Douyin, and WeChat where relevant.
- Include a B2B inquiry/conversion path.
- Include short-form video strategy.
- Include feed post strategy.
- Include weekly upload plan.
- Include execution priority.
- Every recommendation should include execution difficulty, expected effect, cost level, and risk level.
- Respect approval-required brands.
- `메디큐브` must not be externally recommended unless explicitly approved.
- Buyer-facing materials should focus on practical B2B checks such as MOQ, delivery lead time, brand approval status, available product materials, and inquiry handling.

## 8. Evidence and Claim Rules

- Do not invent new market facts.
- Do not invent fake statistics, rankings, platform performance, engagement rates, sales data, or sources.
- If the market research report includes `검증 필요`, `소스 자료 부족`, or `확정 불가`, carry that caution into the content strategy.
- Strategy ideas may be recommendations, but factual claims must be grounded in the market research report or marked as assumptions.
- Consumer engagement signals must not be treated as confirmed B2B buyer demand unless verified source materials support that conclusion.
- Channel strategy may propose low-cost tests, but it must not promise views, sales, conversions, buyer inquiries, or platform performance.

## 9. PASS / PASS WITH CAUTION / FAIL Usage Rules

`FAIL`

- Do not use for execution.
- Do not use for external communication.
- Fix structure, evidence, compliance, approval, or fake-claim issues before reuse.

`PASS WITH CAUTION`

- Internal planning only.
- External use requires verification.
- Use this when the structure is useful but source evidence, brand approval, localization, compliance, or execution readiness remains incomplete.

`PASS`

- Usable as an internal planning draft.
- External claims and brand permissions still require verification.
- PASS does not approve public posting, buyer-facing claims, advertising copy, China platform operation, or cosmetics claims.

## 10. Known Limitations

- No live market data is collected.
- No automatic platform trend detection is performed.
- No automatic source verification is performed.
- Output quality depends on the quality of the market research report and source materials.
- China platform/account rules may change and must be verified before execution.
- Cosmetics claims must be reviewed before external use.
- Content execution still requires actual product images, videos, brand approval, and Chinese/local language review.
- The generated strategy is not a substitute for legal, regulatory, platform policy, brand approval, or localization review.
