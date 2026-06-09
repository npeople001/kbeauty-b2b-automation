# Channel Content Strategy Output Schema

## Purpose

This schema defines the required output structure for channel-specific content strategy reports generated in Task 004.

The report must support K-beauty B2B export marketing by turning a local market research report and structured input row into practical channel strategy, short-form video ideas, feed post ideas, B2B buyer acquisition content, weekly execution planning, and risk review.

Task 004 outputs must not contain scraping results, live web research, automatic web search results, API-collected data, crawler output, or externally collected data unless the user manually provided those materials.

## Global Output Rules

- Output must be written in Korean.
- Internal normalized values may use English codes, but business-facing reports should display Korean-friendly labels.
- B2B buyer acquisition must be separated from consumer marketing.
- China strategies must include Xiaohongshu, Douyin, and WeChat where relevant.
- China account operation, real-name/account, platform policy, localization, and cosmetics claim risks must be included where relevant.
- Approval-required brands must not be recommended for external posting, public content, buyer-facing proposals, or advertising copy unless explicitly approved.
- `메디큐브` must remain approval-required unless explicit approval is provided.
- The strategy must not invent fake market facts, fake statistics, fake rankings, fake platform performance, fake engagement rates, fake sales data, or fake sources.
- If source evidence is insufficient, the output must mark assumptions or verification-needed items clearly.
- Recommendations must be practical for a small K-beauty B2B export business.

## Allowed Values

| Field | Allowed values | Korean display guidance | Notes |
|---|---|---|---|
| `execution_difficulty` | `low`, `medium`, `high`, `unknown` | 낮음, 중간, 높음, 확인 필요 | Use for channel and execution actions. |
| `production_difficulty` | `low`, `medium`, `high`, `unknown` | 낮음, 중간, 높음, 확인 필요 | Use for short-form video production burden. |
| `expected_effect` | `high`, `medium`, `low`, `unknown` | 높음, 중간, 낮음, 확인 필요 | Do not imply guaranteed performance. |
| `cost_level` | `low`, `medium`, `high`, `unknown` | 낮음, 중간, 높음, 확인 필요 | Estimate based on input budget and required assets. |
| `risk_level` | `low`, `medium`, `high`, `unknown` | 낮음, 중간, 높음, 확인 필요 | Include compliance, approval, resource, and evidence risks. |
| `go_or_no_go` | `go`, `go_with_caution`, `no_go` | 진행, 조건부 진행, 진행 보류 | External use still requires claim verification. |

## Evidence Handling

Reports should preserve caution from the market research report.

Use these Korean evidence labels where useful:

- `확인된 사실`: directly supported by local structured input or user-provided source materials.
- `관찰`: based on manually provided observations.
- `가정`: planning assumption derived from limited materials.
- `검증 필요`: potentially useful but not confirmed.
- `추천`: strategy recommendation based on available inputs and stated limits.

If evidence is weak, use wording such as `검증 필요`, `소스 자료 부족`, or `확정 불가`.

## 1. Strategy Summary

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `summary_conclusion` | Overall conclusion of the content strategy. | Required | Korean sentence or short paragraph | `중국 대상 초기 전략은 소비자 반응 관찰과 B2B 문의 유도 경로를 분리한 조건부 진행이 적절함.` | Must mention uncertainty if source evidence is limited. |
| `recommended_channels` | Channels recommended for initial execution. | Required | Comma-separated channel names or table list | `Xiaohongshu, Douyin, WeChat` | For China, include these channels where relevant to the input. |
| `recommended_brands_or_categories` | Brands or product categories suitable for content planning. | Required | Brand/category list | `아누아, 토리든, VT / toner, serum, sunscreen` | Exclude approval-required brands from external recommendations unless approved. |
| `first_content_direction` | First content direction to execute. | Required | Korean sentence | `제품 효능 단정보다 B2B 공급 가능성과 문의 경로를 강조하는 테스트 콘텐츠` | Must be practical for a small B2B exporter. |
| `expected_effect` | Expected practical effect of the strategy. | Required | Allowed value plus Korean explanation | `medium: 초기 문의 경로와 콘텐츠 반응 확인 가능` | Must not promise sales, views, or engagement. |
| `key_risks` | Main risks that could affect execution. | Required | Bullet list or concise text | `중국 계정 운영, 실명 인증, 화장품 표현, 브랜드 승인, 현지화 리스크` | Include China risks when target country is China. |

## 2. Channel Strategy

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `channel_name` | Name of the channel. | Required | Text | `Xiaohongshu` | Use exact channel names from input/report where possible. |
| `channel_role` | Main strategic role of the channel. | Required | Korean phrase | `소비자 반응 관찰 및 B2B 문의 유도 보조 채널` | Separate awareness, proof-building, inquiry capture, and buyer acquisition roles. |
| `target_audience` | Intended audience on the channel. | Required | Korean phrase | `중국 소비자 및 K-뷰티 소싱 관심 바이어` | Avoid claiming exact user demographics without evidence. |
| `b2b_use_case` | How the channel supports buyer acquisition. | Required | Korean sentence | `도매 문의 가능성을 확인하고 WeChat 문의로 전환` | Must be distinct from consumer marketing. |
| `b2c_use_case` | How the channel supports consumer-facing content. | Required | Korean sentence | `제품군별 반응 관찰용 콘텐츠 테스트` | Do not confuse likes/views with buyer demand. |
| `recommended_content_type` | Content types recommended for the channel. | Required | List or phrase | `짧은 영상, 제품 비교 피드, 문의 유도 카드` | Must align with available assets and budget. |
| `posting_frequency` | Suggested upload frequency. | Required | Text with period | `주 1-2회 테스트` | Use cautious wording if resource capacity is unclear. |
| `lead_capture_method` | Method for capturing buyer inquiries. | Required | Korean sentence | `프로필/캡션에서 WeChat 또는 이메일 문의로 연결` | Must include a realistic inquiry path. |
| `execution_difficulty` | Estimated execution difficulty. | Required | Allowed value | `medium` | Use allowed values only. |
| `expected_effect` | Expected practical effect. | Required | Allowed value plus Korean explanation | `medium: 초기 반응과 문의 가능성 확인` | No unsupported performance claims. |
| `cost_level` | Estimated cost level. | Required | Allowed value | `low` | Reflect available budget and assets. |
| `risk_level` | Overall risk level. | Required | Allowed value | `medium` | Consider platform, evidence, localization, brand approval, and compliance risks. |

## 3. Short-form Video Strategy

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `video_title` | Working title of the video idea. | Required | Korean title | `중국 바이어용 K-뷰티 제품군 체크 영상` | Must be specific enough to produce. |
| `objective` | Business objective of the video. | Required | Korean sentence | `B2B 문의 전환 가능성을 테스트` | Separate B2B objective from B2C awareness. |
| `target_viewer` | Intended viewer. | Required | Korean phrase | `중국 도매 바이어 및 소싱 담당자` | Do not overstate audience presence without evidence. |
| `hook` | First attention-grabbing line or idea. | Required | Korean copy | `중국 바이어가 K-뷰티 제품을 볼 때 먼저 확인할 조건` | Avoid medical or exaggerated cosmetic claims. |
| `opening_scene` | First visual scene. | Required | Korean scene direction | `제품 3종을 정면 배치하고 카테고리명을 표시` | Must be feasible with available assets. |
| `key_scenes` | Main scenes in sequence. | Required | Numbered list or semicolon-separated text | `제품군 소개; MOQ/납기 안내; 문의 CTA` | Keep scenes practical for short-form production. |
| `product_display_direction` | How products should appear visually. | Required | Korean direction | `승인 가능한 브랜드만 노출하고 메디큐브는 제외` | Must respect brand approval restrictions. |
| `script_direction` | Script tone and message direction. | Required | Korean sentence | `효능 단정보다 공급 조건과 문의 절차 중심` | Avoid unsupported performance claims. |
| `caption_direction` | Caption style and wording direction. | Required | Korean sentence | `검증 필요 항목은 단정하지 않고 문의 유도 중심으로 작성` | Include localization caution for China. |
| `CTA` | Call to action. | Required | Korean CTA | `MOQ와 공급 가능 브랜드 문의` | B2B CTA must differ from consumer purchase CTA. |
| `required_assets` | Materials needed to produce the video. | Required | List | `제품 이미지, 승인 가능 브랜드 리스트, 중국어 검수 카피` | Mark missing materials clearly. |
| `production_difficulty` | Estimated production difficulty. | Required | Allowed value | `low` | Use allowed values only. |
| `expected_effect` | Expected practical effect. | Required | Allowed value plus Korean explanation | `medium: 문의 경로 테스트 가능` | Do not claim views or conversion rates without evidence. |
| `risk` | Key risk for the video idea. | Required | Korean sentence | `중국 화장품 표현 및 브랜드 승인 검토 필요` | Include claim and approval risks. |

## 4. Feed Post Strategy

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `feed_title` | Working title of the feed post idea. | Required | Korean title | `B2B 제품 제안 카드` | Must be specific enough to design. |
| `objective` | Business objective of the feed post. | Required | Korean sentence | `바이어 문의 전 상품군 이해를 돕기 위함` | Separate from consumer retail conversion. |
| `image_structure` | Layout structure of the feed image. | Required | Korean layout description | `1장 표지, 2장 제품군, 3장 MOQ/납기, 4장 문의 CTA` | Keep feasible for small team design. |
| `headline` | Main headline text. | Required | Korean headline | `중국 바이어용 K-뷰티 제품 검토 자료` | Avoid unsupported market claims. |
| `key_copy` | Main body copy direction. | Required | Korean copy or copy guide | `시장 수치보다 공급 가능 조건과 검증 필요 항목 중심` | Mark assumptions clearly. |
| `product_display_direction` | Product visual display guidance. | Required | Korean direction | `승인 가능한 브랜드와 제품군만 표시` | Do not display restricted brands externally. |
| `proof_points` | Evidence or proof needed for the post. | Required | List | `브랜드 승인 여부, 제품 이미지, 공급 가능 수량, 표현 검수 자료` | If unavailable, mark as `필요 자료` or `검증 필요`. |
| `CTA` | Call to action. | Required | Korean CTA | `카탈로그 및 공급 가능 여부 문의` | Use B2B inquiry-oriented CTA where relevant. |
| `design_notes` | Design and localization notes. | Required | Korean notes | `중국어 표현은 게시 전 현지화 검수 필요` | Include platform and localization caution. |
| `expected_effect` | Expected practical effect. | Required | Allowed value plus Korean explanation | `medium: 문의 전환용 설명 자료로 활용 가능` | No unsupported engagement claims. |
| `risk` | Key risk for the feed post. | Required | Korean sentence | `화장품 표현, 브랜드 승인, 중국 플랫폼 정책 검토 필요` | Include compliance risks. |

## 5. B2B Buyer Acquisition Content

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `target_buyer_segment` | Buyer segment targeted by the content. | Required | Korean phrase | `100개 이상 주문 가능한 도매상, 수입상, 소싱 담당자` | Must reflect B2B export buyer logic. |
| `buyer_pain_point` | Buyer problem or concern to address. | Required | Korean sentence | `승인 가능 브랜드, MOQ, 납기, 공급 안정성 확인 필요` | Use assumptions cautiously if not evidenced. |
| `message_angle` | Message angle for buyer acquisition. | Required | Korean sentence | `소비자 반응보다 공급 조건과 문의 절차를 명확히 제시` | Must not become consumer retail copy. |
| `proof_needed` | Proof materials needed before buyer-facing use. | Required | List | `브랜드 승인 기록, 공급 가능 수량, 제품 이미지, 표현 검수 자료` | Mark missing proof as `검증 필요`. |
| `recommended_post_type` | Best content format for buyer acquisition. | Required | Korean phrase | `B2B 문의 유도 피드 또는 짧은 체크리스트 영상` | Must be practical for available assets. |
| `inquiry_conversion_path` | Path from content exposure to buyer inquiry. | Required | Korean process | `콘텐츠 노출 -> 프로필 확인 -> WeChat/이메일 문의 -> MOQ/브랜드 승인 확인` | Must be explicit and operational. |
| `follow_up_action` | Action after inquiry is captured. | Required | Korean sentence | `구매 수량, 국가, 브랜드 승인 가능 여부 확인 후 자료 발송` | Restricted brands must be excluded unless approved. |

## 6. Weekly Upload Plan

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `week` | Execution week. | Required | `Week 1`, `1주차`, or date range | `1주차` | Align with execution period. |
| `channel` | Channel for the upload or task. | Required | Channel name | `Xiaohongshu` | Use input/report channels. |
| `content_type` | Type of content or preparation task. | Required | Korean phrase | `피드 포스트`, `짧은 영상`, `자산 준비` | Asset preparation may come before posting. |
| `topic` | Topic of the content. | Required | Korean phrase | `B2B 공급 조건 안내` | Avoid fake market claims. |
| `format` | Output format. | Required | Korean phrase | `4장 카드뉴스`, `15초 영상` | Keep feasible for small team production. |
| `purpose` | Purpose of the upload. | Required | Korean sentence | `문의 유도 경로를 테스트` | Separate B2B and B2C purpose. |
| `required_materials` | Materials needed. | Required | List | `제품 이미지, 승인 가능 브랜드 리스트, 중국어 검수 카피` | Mark missing materials. |
| `expected_output` | Concrete output expected from the task. | Required | Korean phrase | `게시용 초안 1건` | Do not promise performance results. |

## 7. Execution Priority

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `priority` | Priority order. | Required | Number or label | `1` | Highest priority should reduce risk or enable execution. |
| `action_item` | Action to execute. | Required | Korean sentence | `브랜드 승인 가능 목록 확인` | Must be actionable. |
| `reason` | Why the action matters. | Required | Korean sentence | `승인 제한 브랜드의 외부 노출을 막기 위해 필요` | Connect to business or risk control. |
| `difficulty` | Estimated action difficulty. | Required | Allowed value | `low` | Use same allowed values as execution difficulty. |
| `expected_effect` | Expected practical effect. | Required | Allowed value plus Korean explanation | `high: 외부 게시 리스크 감소` | No guaranteed sales or engagement claims. |
| `cost_level` | Estimated cost level. | Required | Allowed value | `low` | Reflect budget and resource assumptions. |
| `risk_level` | Risk if or while executing. | Required | Allowed value | `medium` | Include approval, resource, compliance, and evidence risk. |

## 8. Risks and Compliance

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `platform_policy_risk` | Platform policy or operation risk. | Required | Korean sentence | `중국 플랫폼 정책 및 게시 가능 표현 검토 필요` | Include platform-specific caution when relevant. |
| `China_account_or_real_name_risk` | China account operation and real-name/account risk. | Required when China is target country; optional otherwise | Korean sentence | `계정 운영 주체와 실명/인증 조건 확인 필요` | Mark as `검증 필요` if not confirmed. |
| `cosmetics_claim_risk` | Risk from cosmetic efficacy or regulated claims. | Required | Korean sentence | `미백, 여드름, 치료, 임상 표현은 검증 전 사용 금지` | Avoid medical/drug-like claims. |
| `brand_approval_risk` | Risk from using approval-required brands. | Required | Korean sentence | `메디큐브는 승인 전 외부 게시/제안에서 제외` | Respect `restricted_or_approval_required_brands`. |
| `localization_risk` | Translation and local market wording risk. | Required | Korean sentence | `중국어 카피는 현지화 검수 필요` | Include where China or non-Korean channels are used. |
| `resource_risk` | Internal resource and production capacity risk. | Required | Korean sentence | `저예산 4주 실행 기준으로 촬영/디자인 리소스 부족 가능` | Keep practical for small B2B exporter. |

## 9. Final Recommendation

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `go_or_no_go` | Final execution decision. | Required | Allowed value | `go_with_caution` | Use `no_go` if evidence, approval, or compliance risk is too high. |
| `first_channel_to_start` | First channel to start with. | Required | Channel name | `WeChat` | Explain whether it is for inquiry capture, proof-building, or content testing. |
| `first_content_to_create` | First content item to create. | Required | Korean phrase | `B2B 공급 조건 안내 피드 초안` | Must be executable with available materials. |
| `next_actions` | Next actions in order. | Required | Numbered list | `1. 승인 가능 브랜드 확인 2. 제품 이미지 정리 3. 중국어 카피 검수` | Include approval, evidence, asset, and inquiry path setup tasks. |

## Validation Requirements

Generated strategy outputs must be validated for:

- all 9 required sections exist
- required fields appear in each section
- Korean text is preserved
- B2B and B2C are separated
- China risks are included when target country is China
- `메디큐브` is not externally recommended unless explicitly approved
- execution difficulty, expected effect, cost level, and risk level are included
- video ideas include hook, opening scene, key scenes, CTA, required assets, production difficulty, expected effect, and risk
- feed ideas include image structure, headline, key copy, proof points, CTA, design notes, expected effect, and risk
- weekly upload plan exists
- no fake performance claims or unsupported market facts are included

## Business-Facing Label Guidance

| Internal code | Korean display |
|---|---|
| `low` | 낮음 |
| `medium` | 중간 |
| `high` | 높음 |
| `unknown` | 확인 필요 |
| `go` | 진행 |
| `go_with_caution` | 조건부 진행 |
| `no_go` | 진행 보류 |
