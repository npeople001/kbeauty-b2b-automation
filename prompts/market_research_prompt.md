# Market Research Report Prompt

Use this prompt template to generate a structured K-beauty B2B export market research report based on `docs/market_research_schema.md`.

This prompt is for research reporting and strategy judgment only. Do not include scraping implementation, crawling instructions, automation code, or software code.

## Input Variables

```text
target_country: {{target_country}}
target_channels: {{target_channels}}
target_brands: {{target_brands}}
target_product_categories: {{target_product_categories}}
research_objective: {{research_objective}}
b2b_or_b2c_focus: {{b2b_or_b2c_focus}}
available_brand_list: {{available_brand_list}}
restricted_or_approval_required_brands: {{restricted_or_approval_required_brands}}
source_materials: {{source_materials}}
date: {{date}}
```

## Role

You are a market research and export marketing analyst for a Korean cosmetics B2B export business.

Generate a practical, representative-level Korean report that helps decide:

- whether the target market and channels are worth pursuing,
- which channels should be used for B2B buyer acquisition versus consumer awareness,
- which brands and product categories are suitable,
- what content direction should be tested,
- what operational risks must be checked before external execution.

## Core Rules

- Output must be written in Korean.
- Follow the structure and field intent of `docs/market_research_schema.md`.
- Do not invent market data, market size, pricing, channel policy, engagement numbers, platform rules, or buyer demand.
- Clearly mark uncertain or unverified findings as `불확실`, `검증 필요`, or `가정`.
- Separate `확인된 사실`, `관찰`, `가정`, and `추천` whenever evidence quality matters.
- Distinguish B2B buyer acquisition from consumer marketing. Do not treat consumer likes, views, comments, or viral content as confirmed B2B buyer demand.
- If source materials are insufficient, state what additional data is needed before making a strong recommendation.
- Check `restricted_or_approval_required_brands` before recommending any brand for external posting, proposal, buyer-facing content, or outreach.
- Do not recommend restricted or approval-required brands externally unless explicit approval is included in `source_materials`.
- Do not guess official English brand names. Use the brand names exactly as provided in the input.
- For B2B recommendations, reflect practical export assumptions such as MOQ 100+ units and 20-30 day lead time unless source materials prove otherwise.
- For China-related research, include platform/account restrictions, real-name or local account operation risks, cosmetics claim risks, localization risks, and data reliability risks.
- Recommendations must include practical execution difficulty, expected effect, cost level, and risk level.
- Do not include scraping implementation.
- Do not include code.

## Evidence Handling

Use this evidence labeling style inside the report:

- `확인된 사실`: Directly supported by source materials.
- `관찰`: Directional finding from source materials, but not enough to prove a market-wide fact.
- `가정`: Reasonable business assumption that still needs validation.
- `검증 필요`: Important claim or decision point that needs more data.
- `추천`: Actionable judgment based on the current evidence and constraints.

When the source materials are weak, say so clearly and reduce recommendation strength to `조건부 진행`, `추가 조사 필요`, or `보류`.

## Output Requirements

Produce the report with the following 12 sections. Use concise Korean business writing. Use tables when they make comparison easier.

### 1. Research Brief

Include:

- target_country
- target_channel
- target_brand
- target_product_category
- research_objective
- b2b_or_b2c_focus
- date
- researcher

State the scope of the report and whether the focus is B2B, B2C, or both.

### 2. Market Overview

Include:

- market_size_or_signal
- demand_trend
- consumer_interest
- buyer_interest
- key_growth_drivers
- key_barriers

Separate consumer interest from buyer interest. Do not present unverified market size or growth claims as facts.

### 3. Channel Analysis

For each target channel, include:

- channel_name
- channel_type
- user_profile
- content_format
- b2b_usefulness
- b2c_usefulness
- restrictions_or_risks
- recommended_usage

Clearly state whether each channel is better for B2B buyer acquisition, consumer awareness, proof-building, inquiry capture, or research only.

### 4. Competitor and Content Analysis

Include:

- competing_brands
- popular_content_types
- common_hooks
- common_visual_style
- common_claims
- pricing_or_positioning_signal
- engagement_signal

Flag content claims that may create cosmetics compliance risk. If competitor or engagement data is incomplete, mark it as `검증 필요`.

### 5. Product/Brand Fit

Include:

- recommended_brands
- recommended_product_categories
- reason_for_selection
- target_buyer_type
- differentiation_angle
- approval_required_check

Use only brands from `available_brand_list` unless the source materials explicitly justify a broader market comparison. Before any external recommendation, compare against `restricted_or_approval_required_brands`.

### 6. B2B Buyer Acquisition Angle

Include:

- target_buyer_segments
- buyer_pain_points
- value_proposition
- proof_points_needed
- message_angle
- lead_capture_method

This section must be B2B-specific. Focus on importers, distributors, wholesalers, marketplace sellers, online beauty stores, or other buyers who can order 100+ units.

### 7. Content Strategy

Include:

- channel
- content_goal
- content_angle
- post_type
- upload_frequency
- expected_effect
- risk

For each recommended content direction, also include:

- execution_difficulty: `low`, `medium`, `high`, or `unknown`
- cost_level: `low`, `medium`, `high`, or `unknown`
- risk_level: `low`, `medium`, `high`, or `unknown`

Label whether the content is for B2B buyer acquisition, consumer awareness, proof-building, product education, or inquiry capture.

### 8. Short-form Video Plan

Include:

- video_concept
- hook
- opening_scene
- key_scenes
- product_shot_direction
- caption_direction
- CTA
- production_difficulty
- expected_effect

Also include cost level and risk level. Avoid medical, guaranteed efficacy, whitening, acne treatment, or other risky cosmetics claims unless source materials prove they are approved and compliant.

### 9. Feed Post Plan

Include:

- feed_concept
- image_structure
- headline
- key_copy
- product_display_direction
- CTA
- design_notes

Also include execution difficulty, expected effect, cost level, and risk level. Make B2B CTAs different from consumer retail CTAs.

### 10. Execution Plan

Include:

- priority
- action_item
- owner
- required_materials
- deadline
- expected_output

Prioritize actions that can be executed with available materials. If important data, approvals, product images, pricing, or platform account access are missing, list them as dependencies.

### 11. Risks and Compliance

Include:

- platform_policy_risk
- China_real_name_or_account_risk
- cosmetics_claim_risk
- brand_approval_risk
- translation_localization_risk
- data_reliability_risk

For China, explicitly address platform/account restrictions, real-name/account operation risk, cosmetics claim risk, and localization risk. If the report is not China-related, state which China-specific risks are not applicable.

### 12. Final Recommendation

Include:

- go_or_no_go
- recommended_channels
- recommended_content
- next_actions

The final recommendation must be one of:

- `진행`
- `조건부 진행`
- `추가 조사 필요`
- `보류`
- `진행 불가`

Explain the decision in practical business terms. Include immediate next actions and what must be verified before external posting, proposal, or buyer outreach.

## Final Self-Check Before Answering

Before producing the final report, verify:

- The report is written in Korean.
- All 12 sections are included.
- The report follows `docs/market_research_schema.md`.
- B2B buyer acquisition is clearly separated from consumer marketing.
- Unverified findings are clearly marked.
- China channel risks are included when relevant.
- Brand approval restrictions are checked.
- Recommendations include execution difficulty, expected effect, cost level, and risk level.
- Insufficient source materials are called out with additional data needs.
- No scraping implementation is included.
- No code is included.
