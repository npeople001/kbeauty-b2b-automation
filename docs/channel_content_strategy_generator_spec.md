# Channel Content Strategy Generator Specification

## 1. Scope

### What Task 004 Does

Task 004 defines and later implements a local Channel Content Strategy Generator for K-beauty B2B export marketing.

The generator will convert:

- structured research input data
- an existing generated market research report
- user-provided source materials, when available
- existing schema and prompt guidance

into a Korean channel-specific content strategy report.

The output is intended to help plan channel strategy, short-form videos, feed posts, B2B buyer acquisition content, weekly uploads, execution priorities, and risk review.

### What Task 004 Does Not Do

Task 004 does not perform:

- scraping
- live web research
- automated web search
- API calls
- browser automation
- requests to external services
- crawling
- external data collection

The generator must only use local input files, generated local market research reports, and user-provided source materials.

Task 004 does not verify live platform rules, live market statistics, rankings, engagement rates, sales data, or regulatory facts. If these details are not present in the provided materials, they must be marked as `검증 필요`, `소스 자료 부족`, or `확정 불가`.

## 2. Input Files

### Required Inputs

- `data/research_inputs_sample.csv` or future `data/research_inputs.csv`
- `output/market_research_report_{research_id}.md`
- `prompts/content_strategy_prompt.md`
- `docs/market_research_schema.md`

### Source Material Inputs

Use these files when available:

- `data/source_materials/market_research/{research_id}/source_notes.md`
- `data/source_materials/market_research/{research_id}/sources.csv`

### CSV Requirements

Business-facing CSV inputs must use UTF-8 with BOM (`utf-8-sig`) for Excel compatibility.

The generator must read CSV files using an encoding compatible with `utf-8-sig` and must preserve Korean, English, and Chinese text.

### Key Input Fields

The strategy generator should use these fields from the research input row:

- `research_id`
- `target_country`
- `target_channels`
- `target_brands`
- `target_product_categories`
- `research_objective`
- `b2b_or_b2c_focus`
- `available_brand_list`
- `restricted_or_approval_required_brands`
- `campaign_objective`
- `available_assets`
- `budget_level`
- `execution_period`
- `source_materials`
- `date`
- `notes`

## 3. Output Files

### Recommended Output

- `output/channel_content_strategy_{research_id}.md`

### Optional Future Outputs

- `output/channel_content_strategy_{research_id}.xlsx`
- `output/weekly_upload_plan_{research_id}.xlsx`
- `output/video_feed_plan_{research_id}.xlsx`

### Output Rules

- Output language must be Korean.
- Markdown output must be written as UTF-8.
- XLSX outputs, if implemented later, must preserve Korean, English, and Chinese text.
- The output must be suitable for internal planning and representative-level reporting.
- External claims still require source verification before use.

## 4. Required Output Sections

The generated channel content strategy must include all 9 sections below.

### 1. Strategy Summary

Required fields:

- 핵심 결론
- 추천 채널
- 추천 브랜드/제품군
- 가장 우선 실행할 콘텐츠 방향
- 기대 효과
- 주요 리스크

### 2. Channel Strategy

For each channel, include:

- `channel_name`
- `channel_role`
- `target_audience`
- `b2b_use_case`
- `b2c_use_case`
- `recommended_content_type`
- `posting_frequency`
- `lead_capture_method`
- `execution_difficulty`
- `expected_effect`
- `cost_level`
- `risk_level`

### 3. Short-form Video Strategy

For each video idea, include:

- `video_title`
- `objective`
- `target_viewer`
- `hook`
- `opening_scene`
- `key_scenes`
- `product_display_direction`
- `script_direction`
- `caption_direction`
- `CTA`
- `required_assets`
- `production_difficulty`
- `expected_effect`
- `risk`

### 4. Feed Post Strategy

For each feed idea, include:

- `feed_title`
- `objective`
- `image_structure`
- `headline`
- `key_copy`
- `product_display_direction`
- `proof_points`
- `CTA`
- `design_notes`
- `expected_effect`
- `risk`

### 5. B2B Buyer Acquisition Content

Required fields:

- `target_buyer_segment`
- `buyer_pain_point`
- `message_angle`
- `proof_needed`
- `recommended_post_type`
- `inquiry_conversion_path`
- `follow_up_action`

### 6. Weekly Upload Plan

Required fields:

- `week`
- `channel`
- `content_type`
- `topic`
- `format`
- `purpose`
- `required_materials`
- `expected_output`

### 7. Execution Priority

Required fields:

- `priority`
- `action_item`
- `reason`
- `difficulty`
- `expected_effect`
- `cost_level`
- `risk_level`

### 8. Risks and Compliance

Required fields:

- `platform_policy_risk`
- `China_account_or_real_name_risk`
- `cosmetics_claim_risk`
- `brand_approval_risk`
- `localization_risk`
- `resource_risk`

### 9. Final Recommendation

Required fields:

- `go_or_no_go`
- `first_channel_to_start`
- `first_content_to_create`
- `next_actions`

## 5. Evidence and Claim Rules

The generator must not invent new market facts.

Disallowed unsupported claims include:

- market size
- rankings
- sales data
- platform performance claims
- view counts
- engagement rates
- conversion rates
- regulatory facts
- source names or citations not present in provided materials

If the market research report or source materials mark a point as `검증 필요`, `소스 자료 부족`, or `확정 불가`, the content strategy must preserve that caution.

The strategy may make practical recommendations, but factual claims must be grounded in the provided report or source materials. If grounding is insufficient, the item must be marked as an assumption or verification-needed item.

Recommended evidence handling:

- `확인된 사실`: Use only when the fact is directly supported by provided source materials.
- `관찰`: Use for manually provided platform or content observations.
- `가정`: Use for planning assumptions made from limited materials.
- `검증 필요`: Use when a point may be useful but cannot be confirmed from provided materials.
- `추천`: Use for strategy decisions derived from available inputs, with limits and risks stated.

The report must separate verified facts, observations, assumptions, verification-needed items, and recommendations.

## 6. Brand Approval Rules

The generator must respect `restricted_or_approval_required_brands`.

`메디큐브` must be treated as approval-required unless explicit approval is provided in the input or source materials.

Approval-required brands must not be recommended for:

- external posting
- public-facing content
- buyer-facing proposals
- paid ads
- public short-form videos
- public feed posts
- public sales copy

unless explicit approval is provided.

The report may mention approval-required brands only as restricted, excluded, or approval-required items.

If approval status is unclear, the brand must be treated as restricted until confirmed.

## 7. China-Specific Rules

When `target_country` is China, the strategy must include China-specific channel and operating risks.

Relevant channels should include Xiaohongshu, Douyin, and WeChat when they are present in the input or market research report.

The strategy must consider:

- account operation risk
- real-name/account risk
- platform policy risk
- localization risk
- cosmetics claim risk
- brand approval risk
- resource risk

For China-focused strategies, the report should distinguish:

- consumer-facing discovery content on channels such as Xiaohongshu or Douyin
- B2B buyer acquisition content and inquiry handling through WeChat or another appropriate business contact path

The inquiry conversion path must be explicit and practical, for example:

- consumer-facing content leads to profile inquiry
- profile or caption directs interested buyers to WeChat or another approved contact channel
- inquiry is qualified by buyer type, MOQ fit, target product, country, and expected order timing
- follow-up materials are sent only for brands approved for external proposal

Any China platform/account, real-name, or cosmetics compliance point that is not confirmed by provided materials must be marked as `검증 필요`.

## 8. Practicality Rules

Every recommendation must include:

- execution difficulty
- expected effect
- cost level
- risk level

Where applicable, recommendations must also include:

- required materials
- owner or responsible role
- production difficulty
- content format
- CTA
- inquiry conversion path
- follow-up action

Recommendations should be practical for a small K-beauty B2B export business with limited budget and limited production resources.

The strategy should prioritize actions that can be executed with available product images, short clips, internal notes, manually collected observations, and approved brand information.

The generator must avoid plans that depend on unapproved brand claims, unsupported performance expectations, or large production budgets unless the input explicitly supports them.

## 9. Validation Requirements

Generated channel content strategy outputs must be validated before use.

Validation must check:

- all 9 required sections exist
- Korean text is preserved
- B2B buyer acquisition and consumer marketing are separated
- China risks are included when target country is China
- brand approval rules are respected
- approval-required brands are not recommended externally without explicit approval
- no fake data, fake statistics, fake source names, fake rankings, fake platform performance claims, or unsupported engagement claims are included
- insufficient evidence from the market research report is carried over as `검증 필요`, `소스 자료 부족`, or `확정 불가`
- each channel strategy includes role, audience, B2B use case, B2C use case, content type, posting frequency, lead capture method, execution difficulty, expected effect, cost level, and risk level
- short-form video ideas include hook, opening scene, key scenes, product display direction, script direction, caption direction, CTA, required assets, production difficulty, expected effect, and risk
- feed post ideas include image structure, headline, key copy, product display direction, proof points, CTA, design notes, expected effect, and risk
- weekly upload plan exists and includes required materials and expected output
- execution priority exists and includes reason, difficulty, expected effect, cost level, and risk level
- risks and compliance section includes platform policy, China account or real-name, cosmetics claim, brand approval, localization, and resource risks

Validation should return PASS only when the strategy is internally usable and does not overstate unsupported claims.

## 10. Completion Criteria

Task 004 is complete only when all of the following are done:

- `docs/channel_content_strategy_generator_spec.md` exists
- a channel strategy output schema exists
- a generator exists
- a Korean sample strategy report is generated for MR-001
- a validation script exists and passes for the generated strategy report
- workflow documentation is updated
- `docs/automation_roadmap.md` is updated
- `docs/task_log.md` is updated
- final review passes

Task 004 completion must not include scraping, live web research, automated web search, API calls, browser automation, crawling, or external data collection.
