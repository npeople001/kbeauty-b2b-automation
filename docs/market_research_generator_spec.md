# Market Research Report Generator Specification

This document defines how the Task 003 Market Research Report Generator will use structured research input data and user-provided source materials to generate a market research report for K-beauty B2B export marketing.

This is a specification only. It does not implement code, create source material folders, create reports, call APIs, browse websites, scrape data, or collect external data.

## 1. Scope

### What Task 003 Does

- Reads structured market research input rows from a CSV file.
- Reads user-provided source materials for the selected `research_id`.
- Generates a Korean market research report following `docs/market_research_schema.md`.
- Marks unsupported or insufficiently supported findings as `검증 필요`.
- Separates verified facts, observations, assumptions, and recommendations.
- Applies brand approval restrictions before external-facing recommendations.
- Produces a report suitable for internal review before any external use.

### What Task 003 Does Not Do

- Task 003 does not perform scraping.
- Task 003 does not perform live web research.
- Task 003 does not perform automated web search.
- Task 003 does not perform browser automation.
- Task 003 does not use `requests`, crawling tools, search APIs, or external data collection.
- Task 003 does not invent market facts, platform statistics, sales data, rankings, source names, or regulatory facts.
- Task 003 does not change Task 001 brand master data.
- Task 003 does not approve restricted brands.
- Task 003 does not create buyer lead management or outreach automation.

## 2. Input Files

### Current Sample Input

- `data/research_inputs_sample.csv`

### Future Input Pattern

- `data/research_inputs.csv`

### Required Columns

The generator must require these columns:

| Column | Meaning |
| --- | --- |
| `research_id` | Unique research input ID used for source material lookup and output naming. |
| `target_country` | Target market or region. |
| `target_channels` | Channels to review, such as Xiaohongshu, Douyin, WeChat, TikTok, Instagram, Shopee, Telegram, or VK. |
| `target_brands` | Brands being considered for the research. |
| `target_product_categories` | Product categories being researched. |
| `research_objective` | Business reason for the report. |
| `b2b_or_b2c_focus` | One of `b2b`, `b2c`, `both`, or `unknown`. |
| `available_brand_list` | Reference to available brands or approved available brand list. |
| `restricted_or_approval_required_brands` | Brands requiring approval or exclusion from external recommendations. |
| `campaign_objective` | Marketing or buyer acquisition objective. |
| `budget_level` | Expected budget level: `low`, `medium`, `high`, or `unknown`. |
| `execution_period` | Intended planning period, such as `4 weeks`. |
| `source_materials` | Source material reference, path, summary, or blank if not yet provided. |
| `date` | Report date in `YYYY-MM-DD` format. |

### Optional Columns

These columns are optional but recommended:

| Column | Meaning |
| --- | --- |
| `available_assets` | Product photos, product information, approved brand materials, translations, or other execution assets. |
| `notes` | Internal notes, missing source material reminders, or special cautions. |
| `researcher` | Person, team, or process preparing the report. |
| `approved_brands_for_external_use` | Explicitly approved brands for external proposals or public content. |
| `approval_notes` | Notes explaining approval source, approver, approval date, or limitations. |

### Encoding Requirement

- CSV files intended for Excel or business users must be written with UTF-8 with BOM, compatible with `utf-8-sig`.
- Scripts must read CSV files using `utf-8-sig` or an encoding compatible with UTF-8 BOM.
- Korean, English, and Chinese text must be preserved.

## 3. Source Materials

### Source Material Requirement

Source materials must be provided by the user. The generator must only use the structured input row and user-provided source materials.

If source materials are missing or insufficient, the report must state that clearly and mark affected findings as `검증 필요`, `소스 자료 미제공`, or `확정 불가`.

### Recommended Folder Pattern

```text
data/source_materials/market_research/{research_id}/
```

Example:

```text
data/source_materials/market_research/MR-001/
```

### Allowed Source Material Types

- `source_notes.md`
- `sources.csv`
- Copied research notes
- Manually collected platform observations
- User-provided links with descriptions
- Screenshots or exports only if manually provided by the user
- Product information sheets provided by the user
- Brand approval notes provided by the user
- Manually prepared competitor notes

### Disallowed Source Material Behavior

- Scraping
- Live web search
- Automatic crawling
- Browser automation
- API calls to collect new market data
- Guessing data not present in the source materials
- Creating nonexistent source names
- Treating user-provided links as verified facts without user-provided notes or extracted content

## 4. Output Files

### Recommended Output Pattern

```text
output/market_research_report_{research_id}.md
```

Example:

```text
output/market_research_report_MR-001.md
```

### Optional Future Outputs

```text
output/market_research_report_{research_id}.xlsx
output/content_strategy_{research_id}.xlsx
```

### Output Requirements

- Output language must be Korean.
- Output must follow `docs/market_research_schema.md`.
- Output must include all 12 required report sections.
- Output must clearly mark missing or insufficient evidence.
- Output must not include fake statistics, fake rankings, fake sales data, fake source names, or unsupported regulatory claims.
- Output must clearly report the actual output path generated.
- If future XLSX output is added and the target file is locked, the generator must create a timestamped fallback output file rather than modifying source files.

## 5. Evidence Labels

| Label | Meaning | When to use it | Example | Risk if misused |
| --- | --- | --- | --- | --- |
| `확인된 사실` | A statement directly supported by user-provided source materials. | Use only when the source material explicitly supports the statement. | `source_notes.md에 Xiaohongshu 콘텐츠 관찰 기록이 있음.` | If used without evidence, the report may overstate reliability and mislead business decisions. |
| `관찰` | A directional note found in source materials but not enough to prove a market-wide fact. | Use for manually observed patterns, repeated examples, or limited source notes. | `제공된 관찰 메모에서 텍스처 영상이 반복적으로 언급됨.` | If treated as fact, limited observations may become false market conclusions. |
| `가정` | A reasonable business assumption based on input context but not verified by source materials. | Use when planning needs a working assumption and evidence is incomplete. | `저예산 4주 테스트에서는 피드 2개와 숏폼 2개 제작을 가정.` | If not labeled, assumptions may be mistaken for verified strategy. |
| `검증 필요` | A claim, risk, or recommendation cannot be confirmed from available materials. | Use when source materials are missing, incomplete, stale, or not specific enough. | `중국 플랫폼 계정 운영 조건은 검증 필요.` | If omitted, the report may appear more certain than the evidence allows. |
| `추천` | A practical action proposed after considering inputs, evidence, assumptions, and risks. | Use for next actions, channel priorities, content directions, or execution plans. | `WeChat 문의 경로를 먼저 준비하는 것을 추천.` | If disconnected from evidence and risks, recommendations may become unsafe or impractical. |

## 6. Fake Data Prevention Rules

- Do not invent market size, rankings, sales data, platform statistics, views, engagement rates, regulatory facts, or source names.
- Do not cite nonexistent sources.
- Do not treat source names, URLs, screenshots, or copied notes as verified unless the user-provided material contains the relevant claim.
- If source materials are insufficient, mark the relevant item as `검증 필요`.
- Separate facts, observations, assumptions, and recommendations.
- If no source materials are provided, the report may still be generated as a structure test, but all market claims must be marked as `검증 필요`, `가정`, `소스 자료 미제공`, or `확정 불가`.
- Numbers may be included only when they appear in user-provided source materials and the report identifies them as source-provided.
- Channel policy and regulatory statements must be framed as review items unless verified source materials are provided.

## 7. Brand Approval Rules

- `restricted_or_approval_required_brands` must be respected.
- `메디큐브` must be treated as approval-required unless explicit approval is provided.
- Approval-required brands must not be recommended for external posting, buyer-facing proposals, public content, external content strategy, or outreach unless explicitly approved.
- The report may mention approval-required brands only as restricted or excluded items.
- Explicit approval must be provided in source materials or an approval-related input field before an approval-required brand can be included externally.
- The generator must not change `approval_required`, `proposal_allowed`, or other Task 001 brand master rules.
- If approval status is unknown, mark the brand approval status as `검증 필요` and avoid external recommendation.

## 8. Required Report Sections

Generated reports must include these 12 sections:

1. Research Brief
2. Market Overview
3. Channel Analysis
4. Competitor and Content Analysis
5. Product/Brand Fit
6. B2B Buyer Acquisition Angle
7. Content Strategy
8. Short-form Video Plan
9. Feed Post Plan
10. Execution Plan
11. Risks and Compliance
12. Final Recommendation

## 9. Validation Requirements

The generated report must be checked for:

- All 12 sections exist.
- Korean text is preserved.
- No fake statistics or fake sources are present.
- Unverified findings are marked.
- Facts, observations, assumptions, and recommendations are separated.
- B2B and B2C are separated.
- China risks are included where relevant.
- Cosmetics claim risks are included.
- Brand approval rules are respected.
- `메디큐브` is not externally recommended unless explicit approval is provided.
- Execution difficulty, expected effect, cost level, and risk level are included.
- The report review checklist in `docs/market_research_review_checklist.md` can be applied.
- The report does not include scraping, live web research, automated web search, browser automation, API calls, or external data collection.

## 10. Completion Criteria

Task 003 is complete only when:

- This specification exists.
- A source material template exists.
- A generator or structured workflow exists.
- A sample report is generated from sample input and sample source materials.
- Validation passes.
- Korean text is verified after generation.
- Brand approval restrictions are verified after generation.
- The generated report is reviewed with `docs/market_research_review_checklist.md`.
- The actual output path is reported.
- Task log and roadmap are updated.

Task 003 is not complete if the report contains unsupported market data, fake sources, unmarked assumptions, approval-required brand recommendations without approval, or unreviewed China/cosmetics/localization risks.
