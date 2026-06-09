# Short-form Video & Feed Plan Generator Specification

## Purpose

This document defines how Task 005: Short-form Video & Feed Plan Generator will convert existing local market research and channel content strategy outputs into detailed, production-ready short-form video plans and feed post plans for K-beauty B2B export marketing.

The generator must help a small B2B export business decide what content to produce first, what assets are required, how each content item supports B2B buyer inquiry conversion, and what risks must be reviewed before external use.

## 1. Scope

### What Task 005 Does

- Reads local structured research input data for a selected `research_id`.
- Reads the existing market research report for the same `research_id`.
- Reads the existing channel content strategy report for the same `research_id`.
- Optionally reads user-provided local source materials, product notes, brand approval notes, product images/videos descriptions, copy notes, or sales materials if manually provided.
- Converts the existing strategy into detailed short-form video production plans, feed post production plans, channel-specific adaptations, weekly production schedules, asset checklists, B2B inquiry conversion plans, and risk notes.
- Produces a Korean Markdown planning document for internal planning and review.
- Carries forward evidence limitations from source reports and clearly marks uncertain or insufficiently supported items.
- Respects brand approval restrictions, especially approval-required brands such as `메디큐브`.

### What Task 005 Does Not Do

- Does not perform scraping.
- Does not perform live web research.
- Does not perform automated web search.
- Does not call APIs.
- Does not use browser automation.
- Does not use `requests`.
- Does not use crawlers.
- Does not perform external data collection.
- Does not verify live platform trends, rankings, views, engagement rates, market size, sales volume, regulation, or account policy changes.
- Does not create final external advertising copy that can be used without business, brand, translation, and compliance review.
- Does not modify Task 001 brand master files or business-critical source data.

Task 005 only uses local structured inputs, existing local reports, and user-provided source materials.

## 2. Input Files

### Required Inputs

| Input | Required | Format | Notes |
|---|---|---|---|
| `data/research_inputs_sample.csv` or future `data/research_inputs.csv` | Required | CSV, `utf-8-sig` for Excel/business compatibility | Must include `research_id` and the structured research fields used by previous tasks. Scripts must read it with an encoding compatible with `utf-8-sig`. |
| `output/market_research_report_{research_id}.md` | Required | Markdown, UTF-8 | Existing Task 003 market research report. The generator must not treat unverified findings as verified facts. |
| `output/channel_content_strategy_{research_id}.md` | Required | Markdown, UTF-8 | Existing Task 004 channel strategy report. This is the primary strategy source for video/feed production planning. |

### Optional Inputs

| Input | Required | Format | Notes |
|---|---|---|---|
| `data/source_materials/market_research/{research_id}/source_notes.md` | Optional | Markdown, UTF-8 | User-provided notes only. Missing notes must not block generation, but evidence must be marked as limited. |
| `data/source_materials/market_research/{research_id}/sources.csv` | Optional | CSV, `utf-8-sig` | User-provided source list only. Missing or unverified sources must be carried forward as evidence limitations. |
| User-provided product images | Optional | Manual file references or notes | The generator may reference them only if manually provided. It must not inspect or fetch external product images. |
| User-provided product videos | Optional | Manual file references or notes | Use only as available production assets. |
| User-provided copy notes | Optional | Markdown, text, CSV, or notes | Must not be treated as verified market facts unless explicitly supported. |
| User-provided brand approval notes | Optional | Markdown, text, CSV, or notes | Required before approval-required brands can be recommended externally. |
| User-provided sales materials | Optional | Markdown, text, CSV, XLSX, or notes | May support B2B inquiry conversion planning if manually provided. |

## 3. Output Files

### Recommended Output

| Output | Format | Language | Notes |
|---|---|---|---|
| `output/short_form_feed_plan_{research_id}.md` | Markdown, UTF-8 | Korean | Primary Task 005 output. Must include all required sections listed in this specification. |

### Optional Future Outputs

| Output | Format | Notes |
|---|---|---|
| `output/short_form_video_plan_{research_id}.xlsx` | XLSX | Business-facing video plan table. If implemented later, Korean text must be verified after generation. |
| `output/feed_post_plan_{research_id}.xlsx` | XLSX | Business-facing feed post plan table. |
| `output/weekly_production_schedule_{research_id}.xlsx` | XLSX | Business-facing schedule table. |

If XLSX outputs are added later and a target file is locked, the automation must create a timestamped fallback file and report the actual output path. This is not part of Step A.

## 4. Required Output Sections

The generated plan must include the following 9 sections in Korean.

### 1) Executive Summary

Required fields:

- 핵심 결론
- 우선 제작 콘텐츠
- 추천 채널
- 기대 효과
- 주요 리스크

Notes:

- State whether the plan is mainly for B2B buyer acquisition, consumer-facing content, or both.
- If source reports contain insufficient evidence, the summary must mention that the plan is an internal planning draft.

### 2) Short-form Video Production Plan

For each video, include:

- `video_id`
- `video_title`
- `target_channel`
- `objective`
- `target_viewer`
- `b2b_or_b2c_focus`
- `hook`
- `opening_scene`
- `scene_by_scene_plan`
- `product_shot_direction`
- `script_direction`
- `caption_direction`
- `subtitle_direction`
- `CTA`
- `required_assets`
- `production_difficulty`
- `expected_effect`
- `cost_level`
- `risk_level`
- `compliance_notes`

Notes:

- `hook`, `script_direction`, `caption_direction`, and `subtitle_direction` must avoid medical, drug-like, guaranteed efficacy, before/after, whitening, acne treatment, or unsupported functional claims unless verified approval and compliance evidence is provided.
- B2B videos must use inquiry-oriented CTAs, not consumer retail purchase CTAs.
- Consumer-facing videos must not be treated as proof of wholesale buyer demand.

### 3) Feed Post Production Plan

For each feed post, include:

- `feed_id`
- `feed_title`
- `target_channel`
- `objective`
- `image_structure`
- `slide_by_slide_plan`
- `headline`
- `key_copy`
- `product_display_direction`
- `proof_points`
- `CTA`
- `design_notes`
- `required_assets`
- `production_difficulty`
- `expected_effect`
- `cost_level`
- `risk_level`
- `compliance_notes`

Notes:

- `proof_points` must distinguish available proof from missing proof.
- If proof materials are missing, mark them as `검증 필요`, `소스 자료 부족`, or `확정 불가`.
- Feed copy must not imply market popularity, ranking, sales performance, views, engagement, or buyer demand unless verified in the source reports.

### 4) Channel-Specific Adaptation

Include:

- Xiaohongshu adaptation
- Douyin adaptation
- WeChat adaptation
- TikTok/Instagram adaptation if relevant
- B2B buyer-facing adaptation
- Consumer-facing adaptation

Notes:

- For China, Xiaohongshu, Douyin, and WeChat must be considered where relevant to the input.
- Channel roles should be adapted from the channel content strategy report.
- WeChat or another suitable inquiry path should be included for B2B conversion where relevant.
- Platform-specific copy, visual, and CTA differences must be practical and cautious.

### 5) Weekly Production Schedule

Include:

- `week`
- `content_id`
- `channel`
- `content_type`
- `topic`
- `production_task`
- `required_materials`
- `owner`
- `expected_output`

Notes:

- The schedule must fit the `execution_period`, `budget_level`, and `available_assets` from the research input row.
- Asset preparation, approval checks, and localization review may be scheduled before posting tasks.
- The schedule must not promise views, engagement, sales, or inquiry volume.

### 6) Asset Checklist

Include:

- product images
- product videos
- texture shots
- package shots
- before/after restrictions
- brand approval materials
- translation/localization materials
- proof documents if needed

Notes:

- Each asset should be marked as available, missing, or verification needed where possible.
- Before/after content must be restricted unless explicitly approved and compliant.
- Brand approval materials are required before any approval-required brand can appear externally.

### 7) B2B Inquiry Conversion Plan

Include:

- `content_id`
- `buyer_segment`
- `inquiry_trigger`
- `CTA`
- `landing_or_contact_path`
- `follow_up_message_direction`
- `required_sales_materials`

Notes:

- Buyer segments should reflect B2B export logic, including importers, distributors, wholesalers, online beauty stores, marketplace sellers, sourcing agents, and other buyers able to order 100+ units.
- Follow-up direction must include checks for quantity, country, buyer type, target brand, approval restrictions, MOQ, and delivery lead time where relevant.
- Buyer-facing claims must be supported or marked as verification needed.

### 8) Risks and Compliance

Include:

- `cosmetics_claim_risk`
- `brand_approval_risk`
- `China_account_or_platform_risk`
- `localization_risk`
- `production_resource_risk`
- `evidence_limitation_risk`

Notes:

- For China, include account operation, real-name/account operation, platform policy, localization, and cosmetics expression risks.
- Include brand approval risk for all approval-required brands, especially `메디큐브`.
- Include evidence limitation risk when source reports contain `검증 필요`, `소스 자료 부족`, or `확정 불가`.

### 9) Final Recommendation

Include:

- `go_or_no_go`
- `first_video_to_make`
- `first_feed_to_make`
- `next_actions`

Allowed `go_or_no_go` values:

- `go`
- `go_with_caution`
- `no_go`

Notes:

- Use `go_with_caution` when the plan is usable internally but source evidence, assets, localization, or approvals are incomplete.
- Use `no_go` if approval restrictions, missing assets, or compliance risks make external use unsafe.
- `next_actions` must include approval checks, asset preparation, localization review, inquiry path setup, and validation before external use where relevant.

## 5. Evidence and Claim Rules

- The generator must not invent new market facts.
- The generator must not invent fake statistics, rankings, platform performance, engagement rates, sales data, views, conversion rates, buyer demand, market size, regulatory facts, or sources.
- If the market research report or channel content strategy report says `검증 필요`, `소스 자료 부족`, or `확정 불가`, the video/feed plan must carry that caution forward.
- Strategy ideas may be generated as recommendations, but factual claims must be grounded in existing reports or marked as assumptions.
- Production ideas must not imply verified performance unless verified evidence exists.
- The generator must distinguish:
  - `확인된 사실`: directly supported by structured inputs or provided source materials.
  - `관찰`: based on manually provided observations.
  - `가정`: planning assumption derived from limited materials.
  - `검증 필요`: useful but not confirmed.
  - `추천`: execution recommendation based on available inputs and stated limitations.
- If source reports are mostly insufficient, the output must reduce recommendation strength and clearly state what additional materials are needed.
- Do not cite nonexistent sources.
- Do not use placeholder URLs as evidence unless clearly marked as placeholders.

## 6. Brand Approval Rules

- `restricted_or_approval_required_brands` must be respected.
- `메디큐브` must remain approval-required unless explicit approval is provided.
- Approval-required brands must not be recommended for:
  - external posting
  - public content
  - buyer-facing proposal
  - advertising copy
  - video script
  - feed copy
  - product shots
  - headline copy
  - CTA copy
  - sales follow-up materials
  unless explicitly approved.
- Approval-required brands may be mentioned only as restricted, excluded, blocked, or approval-required items.
- If explicit approval is provided later, the generator must still label the approval source or note and preserve that approval context.
- The generator must not alter brand master data, approval flags, or proposal eligibility rules.

## 7. B2B/B2C Separation Rules

- Each video and feed idea must specify `b2b_or_b2c_focus`.
- B2B content must include:
  - buyer segment
  - inquiry trigger
  - B2B CTA
  - landing or contact path
  - follow-up message direction
  - required sales materials
- B2C content must not be confused with wholesale buyer conversion strategy.
- Consumer reaction testing must not be treated as verified buyer demand.
- Buyer-facing content must avoid unsupported product, market, ranking, sales, or compliance claims.
- Buyer-facing content must identify required proof materials when claims or supply terms are used.

## 8. China-Specific Rules

When `target_country` is China, the plan must include:

- Xiaohongshu, Douyin, and WeChat adaptations where relevant.
- Account/platform risk.
- Real-name/account operation risk.
- Localization risk.
- Cosmetics claim risk.
- WeChat or another suitable inquiry conversion path.
- Channel-specific content format differences.
- Caution that China platform/account rules may change and must be verified before execution.
- Caution that Chinese copy and cosmetics expressions require localization and compliance review before posting.

China-specific content must not imply that the company can operate an account, run ads, or publish content externally unless the required account, real-name, platform, approval, and localization conditions are confirmed.

## 9. Practicality Rules

Every video/feed recommendation must include:

- required assets
- production difficulty
- expected effect
- cost level
- risk level
- compliance notes

Allowed planning values:

| Field | Allowed values | Notes |
|---|---|---|
| `production_difficulty` | `low`, `medium`, `high`, `unknown` | Estimate based on assets, filming burden, localization, and approval needs. |
| `expected_effect` | `high`, `medium`, `low`, `unknown` | Must describe practical planning value, not guaranteed performance. |
| `cost_level` | `low`, `medium`, `high`, `unknown` | Reflect budget and asset availability. |
| `risk_level` | `low`, `medium`, `high`, `unknown` | Include compliance, approval, localization, evidence, and resource risks. |

The plan must be practical for a small K-beauty B2B export business with limited production resources. Prefer low-cost, reusable, approval-safe content before complex campaigns.

## 10. Validation Requirements

The generated plan must be checked for:

- All 9 required sections exist.
- Korean text is preserved.
- B2B and B2C are separated.
- China channel adaptations are included where relevant.
- Brand approval rules are respected.
- `메디큐브` is not externally recommended unless explicitly approved.
- No fake performance claims or unsupported market facts are included.
- No fake statistics, rankings, platform performance claims, engagement rates, sales data, views, conversion rates, market size, or fake sources are included.
- Insufficient evidence is carried over from the source reports.
- Video plans include hook, opening scene, scene-by-scene plan, CTA, required assets, difficulty, expected effect, cost level, and risk level.
- Feed plans include image structure, slide-by-slide plan, headline, key copy, proof points, CTA, design notes, required assets, difficulty, expected effect, cost level, and risk level.
- Asset checklist exists.
- B2B inquiry conversion plan exists.
- Weekly production schedule exists.
- China account, real-name/account operation, platform policy, localization, and cosmetics expression risks are included when target country is China.
- Output is suitable as an internal planning draft, not as unreviewed external content.

## 11. Failure and Caution Behavior

- If required input CSV is missing, the future generator should fail clearly.
- If `research_id` is missing, the future generator should fail clearly.
- If the market research report is missing, the future generator should fail clearly because Task 005 depends on Task 003 output.
- If the channel content strategy report is missing, the future generator should fail clearly because Task 005 depends on Task 004 output.
- If optional source materials are missing, the future generator may still generate the plan but must mark evidence as limited.
- If source reports contain insufficient evidence, the future generator must carry forward `검증 필요`, `소스 자료 부족`, or `확정 불가`.
- If approval-required brands appear in input, the future generator must exclude them from external recommendations unless explicit approval is provided.

## 12. Completion Criteria

Task 005 is complete only when:

- Specification exists.
- Output schema exists.
- Generator exists.
- Sample short-form/feed plan is generated for `MR-001`.
- Validation script exists and passes.
- Workflow documentation is updated.
- Task log and roadmap are updated.
- Final review passes.

Step A is complete when this specification exists and no code, generated report, scraping, live research, API use, browser automation, crawler, request-based collection, or external data collection has been added.
