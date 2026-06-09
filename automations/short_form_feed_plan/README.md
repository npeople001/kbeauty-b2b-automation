# Short-form Video & Feed Plan Generator

## Purpose

This automation generates short-form video and feed post production plans from existing internal reports and structured input data.

It is designed for K-beauty B2B export marketing. The output helps plan short-form video concepts, feed post concepts, channel-specific adaptations, weekly production tasks, required assets, B2B inquiry conversion paths, and compliance risks.

This automation does not perform scraping, live web research, automated web search, APIs, browser automation, crawlers, requests, or external data collection. It only reads local files already provided or generated inside this repository.

## Input Requirements

Required inputs:

- Research input CSV path: `data/research_inputs_sample.csv` or future `data/research_inputs.csv`
- Research ID: for example, `MR-001`
- Existing market research report: `output/market_research_report_{research_id}.md`
- Existing channel content strategy report: `output/channel_content_strategy_{research_id}.md`
- Short-form/feed schema: `docs/short_form_feed_plan_schema.md`

Optional inputs:

- Source material folder: `data/source_materials/market_research/{research_id}/`
- Source notes: `data/source_materials/market_research/{research_id}/source_notes.md`
- Source registry: `data/source_materials/market_research/{research_id}/sources.csv`

CSV files intended for Excel or business users should use `utf-8-sig`. Scripts should read business CSV files with an encoding compatible with `utf-8-sig`.

## Output

Default output:

```text
output/short_form_feed_plan_{research_id}.md
```

Example:

```text
output/short_form_feed_plan_MR-001.md
```

The output is Korean Markdown and must include all 9 required sections:

1. Executive Summary
2. Short-form Video Production Plan
3. Feed Post Production Plan
4. Channel-Specific Adaptation
5. Weekly Production Schedule
6. Asset Checklist
7. B2B Inquiry Conversion Plan
8. Risks and Compliance
9. Final Recommendation

## Generation Command

Basic command:

```powershell
python automations/short_form_feed_plan/generate_short_form_feed_plan.py --research-id MR-001
```

Optional arguments:

```powershell
python automations/short_form_feed_plan/generate_short_form_feed_plan.py `
  --research-id MR-001 `
  --input data/research_inputs_sample.csv `
  --market-report-dir output `
  --channel-strategy-dir output `
  --source-root data/source_materials/market_research `
  --output-dir output
```

## Validation Command

Run the validator before using a generated production plan:

```powershell
python tests/validate_short_form_feed_plan.py --report output/short_form_feed_plan_MR-001.md
```

The validation script checks section completeness, required video/feed fields, B2B/B2C separation, China channel/risk requirements, brand approval restrictions, insufficient evidence wording, unsupported performance claims, and required production planning fields.

## Standard Workflow

Step 1: Prepare or update the research input row.

Step 2: Generate or verify the market research report.

Step 3: Generate or verify the channel content strategy report.

Step 4: Add or verify user-provided source materials if available.

Step 5: Generate the short-form/feed production plan.

Step 6: Run the validation script.

Step 7: Review the output manually before production.

Step 8: Use the output only internally unless external claims, brand permissions, and local regulations are verified.

## Business Rules

- Separate B2B buyer acquisition content from consumer marketing content.
- For China, include Xiaohongshu, Douyin, and WeChat adaptations where relevant.
- Include short-form video production plans.
- Include feed post production plans.
- Include a weekly production schedule.
- Include an asset checklist.
- Include a B2B inquiry conversion plan.
- Every recommendation should include production difficulty, expected effect, cost level, and risk level.
- Respect approval-required brands.
- 메디큐브 must not be externally recommended unless explicitly approved.

## Evidence and Claim Rules

- Do not invent new market facts.
- Do not invent fake statistics, rankings, platform performance, engagement rates, sales data, conversion rates, guaranteed results, or sources.
- If the market research report or channel strategy report includes `검증 필요`, `소스 자료 부족`, or `확정 불가`, carry that caution into the video/feed plan.
- Production ideas may be recommendations, but factual claims must be grounded in the source reports or marked as assumptions.
- Do not imply verified performance unless verified evidence exists.
- Consumer-facing content ideas must not be treated as proof of B2B buyer demand.
- Buyer-facing claims must be supported by source reports, user-provided materials, or clearly marked as verification-needed.

## PASS / PASS WITH CAUTION / FAIL Usage Rules

- `FAIL`: Do not use for production, execution, external communication, or decision-making until fixed.
- `PASS WITH CAUTION`: Internal planning only; external use requires verification.
- `PASS`: Usable as an internal production planning draft, but external claims, brand permissions, and local regulations still require verification.

Even when a plan passes validation, external posting, buyer-facing proposals, advertising copy, video scripts, and feed copy still require manual review for claims, brand approval, localization, and platform rules.

## Known Limitations

- No live market data is collected.
- No automatic platform trend detection is performed.
- No automatic source verification is performed.
- No automatic creative performance prediction is performed.
- Output quality depends on the quality of the market research report, channel strategy report, and user-provided source materials.
- China platform/account rules may change and must be verified before execution.
- Cosmetics claims must be reviewed before external use.
- Content execution still requires actual product images, videos, brand approval, translation/localization review, and proof materials.
