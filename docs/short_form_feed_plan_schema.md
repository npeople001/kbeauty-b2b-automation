# Short-form Video & Feed Plan Output Schema

## Purpose

This schema defines the required output structure for short-form video production plans and feed post production plans generated in Task 005.

Task 005 outputs must support K-beauty B2B export marketing by converting existing local market research reports and channel content strategy reports into practical production plans, asset checklists, weekly schedules, and B2B inquiry conversion paths.

Task 005 outputs must not contain scraping results, live web research, automatic web search results, API-collected data, crawler output, browser automation output, or externally collected data unless the user manually provided those materials.

## Global Output Rules

- Output must be written in Korean.
- Internal normalized values may use English codes, but business-facing reports should display Korean-friendly labels where practical.
- B2B buyer acquisition content must be separated from consumer marketing content.
- Each content idea must have a clear CTA.
- B2B content must include inquiry trigger, contact path, follow-up message direction, and required sales materials.
- China plans must include Xiaohongshu, Douyin, and WeChat adaptations where relevant.
- China account/platform, localization, and cosmetics claim risks must be included where relevant.
- Approval-required brands must not be recommended for external posting, public content, buyer-facing proposals, advertising copy, video script, or feed copy unless explicitly approved.
- `메디큐브` must remain approval-required unless explicit approval is provided.
- The plan must not invent fake market facts, fake performance numbers, fake rankings, fake platform metrics, fake engagement rates, fake sales data, or fake sources.
- If source evidence is insufficient, the output must mark assumptions or verification-needed items clearly.
- Recommendations must be practical for a small K-beauty B2B export business.

## Allowed Values

| Field | Allowed values | Korean display guidance | Notes |
|---|---|---|---|
| `b2b_or_b2c_focus` | `b2b`, `b2c`, `both` | B2B, B2C, B2B/B2C 병행 | Required for each content idea. |
| `production_difficulty` | `low`, `medium`, `high`, `unknown` | 낮음, 중간, 높음, 확인 필요 | Estimate based on asset readiness, filming burden, localization, and approval needs. |
| `expected_effect` | `high`, `medium`, `low`, `unknown` | 높음, 중간, 낮음, 확인 필요 | Must describe practical planning value, not guaranteed views, sales, or inquiries. |
| `cost_level` | `low`, `medium`, `high`, `unknown` | 낮음, 중간, 높음, 확인 필요 | Reflect budget, production effort, and external resource needs. |
| `risk_level` | `low`, `medium`, `high`, `unknown` | 낮음, 중간, 높음, 확인 필요 | Include evidence, compliance, platform, localization, approval, and resource risks. |
| `go_or_no_go` | `go`, `go_with_caution`, `no_go` | 진행, 조건부 진행, 보류 | External use still requires claim, approval, and localization review. |
| `content_type` | `short_form_video`, `feed_post`, `carousel`, `story`, `live_clip`, `b2b_pitch_post`, `other` | 숏폼 영상, 피드 게시물, 캐러셀, 스토리, 라이브 클립, B2B 제안형 게시물, 기타 | Use the closest value; explain `other` in notes. |

## Evidence Handling

Task 005 outputs must preserve caution from the market research report and channel strategy report.

Use these evidence labels where useful:

- `확인된 사실`: directly supported by local structured input or manually provided source materials.
- `관찰`: based on manually provided observations.
- `가정`: planning assumption derived from limited materials.
- `검증 필요`: useful but not confirmed.
- `추천`: execution recommendation based on available inputs and stated limits.

If evidence is weak, use wording such as `검증 필요`, `소스 자료 부족`, or `확정 불가`.

## 1. Executive Summary

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `summary_conclusion` | Overall conclusion for the video/feed production plan. | Required | Korean short paragraph | `MR-001은 중국 채널용 B2B 문의 유도 콘텐츠를 우선 제작하되, 소스 자료 부족으로 외부 사용 전 검증이 필요합니다.` | Must mention whether the plan is internal-only, conditional, or ready for limited execution. |
| `priority_content` | First content items to produce. | Required | List of content IDs or concise Korean text | `V-001 B2B 제품군 체크 영상, F-001 공급 조건 안내 카드` | Choose practical content that can be produced with available assets. |
| `recommended_channels` | Channels recommended for the production plan. | Required | Comma-separated channel list or table | `WeChat, Xiaohongshu, Douyin` | For China, include Xiaohongshu, Douyin, and WeChat where relevant. |
| `expected_effect` | Practical expected effect of the plan. | Required | Allowed value plus Korean explanation | `medium: 문의 경로와 콘텐츠 제작 우선순위를 정리할 수 있으나 실제 성과는 검증 필요` | Do not promise sales, views, engagement, or buyer inquiries. |
| `key_risks` | Main risks before production or external use. | Required | Bullet list or concise Korean text | `브랜드 승인, 중국 계정 운영, 화장품 표현, 현지화, 제품 이미지 부족` | Include evidence limitation risk if source reports are weak. |

## 2. Short-form Video Production Plan

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `video_id` | Unique ID for the video plan. | Required | `V-001`, `V-002` | `V-001` | Must be stable enough to reference in schedule and conversion plan. |
| `video_title` | Working title of the video. | Required | Korean title | `중국 바이어용 K-뷰티 제품군 체크 영상` | Avoid unsupported market or performance claims in title. |
| `target_channel` | Channel where the video will be used. | Required | Channel name | `Douyin` | Use input/report channels; for China consider Xiaohongshu, Douyin, and WeChat where relevant. |
| `objective` | Business objective of the video. | Required | Korean sentence | `B2B 바이어가 문의 전 확인해야 할 제품군과 공급 조건을 정리합니다.` | Must distinguish inquiry conversion, consumer awareness, or both. |
| `target_viewer` | Intended viewer. | Required | Korean phrase | `중국 수입상, 도매상, 소싱 담당자` | Do not claim precise audience demographics without evidence. |
| `b2b_or_b2c_focus` | Whether the video supports B2B, B2C, or both. | Required | Allowed value | `b2b` | B2B content must include inquiry and follow-up logic. |
| `hook` | Opening copy or attention point. | Required | Korean copy line | `K-뷰티 공급 문의 전 먼저 확인할 3가지` | Avoid medical, guaranteed efficacy, ranking, or popularity claims. |
| `opening_scene` | First visual scene. | Required | Korean scene direction | `승인 가능 브랜드 제품 이미지를 정면 배치하고 제품군명을 표시` | Must be feasible with available assets. |
| `scene_by_scene_plan` | Detailed scene sequence. | Required | Numbered list or semicolon-separated sequence | `1. 제품군 소개; 2. MOQ/납기 안내; 3. 승인 필요 브랜드 제외; 4. 문의 CTA` | Required for production-ready planning. |
| `product_shot_direction` | How products should appear in video shots. | Required | Korean direction | `아누아, 토리든, VT 등 승인 가능한 브랜드만 노출하고 메디큐브는 제외` | Must respect brand approval rules. |
| `script_direction` | Script message and tone. | Required | Korean sentence | `소비자 효능 주장보다 공급 가능성, MOQ, 문의 절차 중심으로 작성` | No unsupported cosmetics claims. |
| `caption_direction` | Caption copy direction. | Required | Korean sentence | `검증 필요 항목은 확정 표현을 피하고 문의 유도 문구로 정리` | Include localization caution where relevant. |
| `subtitle_direction` | Subtitle and localization direction. | Required | Korean sentence | `중국어 자막은 현지 표현 검토 후 사용` | Required for China or multilingual execution. |
| `CTA` | Call to action. | Required | Korean CTA | `MOQ와 공급 가능 브랜드 문의` | B2B CTA must differ from consumer purchase CTA. |
| `required_assets` | Assets needed to produce the video. | Required | List | `제품 이미지, 제품 영상, 승인 가능 브랜드 목록, 중국어 검수 카피` | Mark missing assets clearly. |
| `production_difficulty` | Estimated production difficulty. | Required | Allowed value | `medium` | Use allowed values only. |
| `expected_effect` | Practical expected effect. | Required | Allowed value plus Korean explanation | `medium: 문의 전환 경로를 설명하는 내부 테스트 콘텐츠로 활용 가능` | Do not claim views, sales, or conversion rates. |
| `cost_level` | Estimated cost level. | Required | Allowed value | `low` | Reflect available assets and budget. |
| `risk_level` | Overall risk level. | Required | Allowed value | `medium` | Include approval, localization, platform, evidence, and claim risks. |
| `compliance_notes` | Compliance and approval notes. | Required | Korean sentence or list | `화장품 효능 표현과 메디큐브 노출은 외부 사용 전 검토 필요` | Must mention restricted brands or claim risks where relevant. |

## 3. Feed Post Production Plan

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `feed_id` | Unique ID for the feed post plan. | Required | `F-001`, `F-002` | `F-001` | Must be stable enough to reference in schedule and conversion plan. |
| `feed_title` | Working title of the feed post. | Required | Korean title | `B2B 공급 조건 안내 카드` | Keep title practical and claim-safe. |
| `target_channel` | Channel where the feed will be used. | Required | Channel name | `Xiaohongshu` | Use input/report channels where possible. |
| `objective` | Business objective of the feed post. | Required | Korean sentence | `바이어가 제품군, MOQ, 문의 경로를 빠르게 확인하도록 합니다.` | Separate consumer awareness from B2B conversion. |
| `image_structure` | Overall visual layout. | Required | Korean layout description | `표지 1장, 제품군 1장, MOQ/납기 1장, 문의 CTA 1장` | Must be specific enough for design. |
| `slide_by_slide_plan` | Detailed slide sequence. | Required | Numbered slide list | `1. 표지; 2. 제품군; 3. 공급 조건; 4. 문의 경로` | Required for carousel/feed production. |
| `headline` | Main headline copy. | Required | Korean headline | `K-뷰티 B2B 공급 문의 전 확인할 항목` | Avoid fake market popularity claims. |
| `key_copy` | Main copy direction. | Required | Korean copy or copy guide | `시장 수치 대신 공급 가능성, 승인 여부, 문의 절차를 중심으로 작성` | Must mark assumptions clearly. |
| `product_display_direction` | Product and brand visual display guidance. | Required | Korean direction | `승인 가능한 브랜드 이미지만 사용하고 메디큐브는 승인 전 제외` | Must respect brand approval restrictions. |
| `proof_points` | Evidence or proof needed for the post. | Required | List | `브랜드 승인 자료, 제품 이미지, MOQ/납기 확인 자료, 표현 검토 자료` | If unavailable, mark as `검증 필요` or `소스 자료 부족`. |
| `CTA` | Call to action. | Required | Korean CTA | `카탈로그와 공급 가능 여부 문의` | B2B feed CTA should connect to contact path. |
| `design_notes` | Design and localization guidance. | Required | Korean notes | `중국어 문구는 현지화 검토 후 사용하고 과장 효능 표현 금지` | Include platform and localization caution. |
| `required_assets` | Assets needed to create the feed post. | Required | List | `제품 이미지, 로고 사용 승인, 제품 정보, 중국어 검수 카피` | Mark missing assets clearly. |
| `production_difficulty` | Estimated production difficulty. | Required | Allowed value | `low` | Use allowed values only. |
| `expected_effect` | Practical expected effect. | Required | Allowed value plus Korean explanation | `medium: 문의 전 설명 자료로 활용 가능하나 실제 성과는 검증 필요` | Do not claim engagement or inquiry results. |
| `cost_level` | Estimated cost level. | Required | Allowed value | `low` | Reflect design and localization needs. |
| `risk_level` | Overall risk level. | Required | Allowed value | `medium` | Include evidence, claim, approval, platform, and localization risks. |
| `compliance_notes` | Compliance and approval notes. | Required | Korean sentence or list | `효능 표현, 전후 이미지, 승인 필요 브랜드 노출은 금지 또는 검토 필요` | Must be explicit before external use. |

## 4. Channel-Specific Adaptation

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `xiaohongshu_adaptation` | How to adapt content for Xiaohongshu. | Required when China is target country; optional otherwise | Korean paragraph or bullet list | `정보형 카드와 짧은 제품군 설명 중심. 소비자 반응은 관찰용이며 바이어 수요로 단정하지 않음.` | Include platform and localization caution. |
| `douyin_adaptation` | How to adapt content for Douyin. | Required when China is target country; optional otherwise | Korean paragraph or bullet list | `15-30초 숏폼으로 제품군과 문의 CTA를 간결하게 구성.` | Do not imply guaranteed views or performance. |
| `wechat_adaptation` | How to adapt content for WeChat. | Required when China is target country; optional otherwise | Korean paragraph or bullet list | `B2B 문의 접수, 후속 자료 전달, MOQ/납기 확인 경로로 사용.` | WeChat or suitable contact path should support B2B conversion. |
| `tiktok_instagram_adaptation` | How to adapt content for TikTok or Instagram if relevant. | Optional | Korean paragraph or `해당 없음` | `MR-001은 중국 중심이므로 TikTok/Instagram은 해당 없음.` | Include only when channels are relevant to input. |
| `b2b_buyer_facing_adaptation` | Adaptation for buyer-facing communication. | Required | Korean paragraph or bullet list | `공급 가능성, 승인 가능 브랜드, MOQ, 납기, 문의 경로 중심으로 조정.` | Must include B2B CTA and proof needs. |
| `consumer_facing_adaptation` | Adaptation for consumer-facing content. | Required | Korean paragraph or bullet list | `소비자 반응 관찰용으로 활용하되 도매 수요로 단정하지 않음.` | Must stay separate from buyer conversion claims. |

## 5. Weekly Production Schedule

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `week` | Production week or date range. | Required | `Week 1`, `1주차`, or date range | `1주차` | Align with `execution_period`. |
| `content_id` | ID of the related video/feed/content item. | Required | `V-001`, `F-001`, or prep task ID | `V-001` | Must match a video/feed ID or clearly mark preparation task. |
| `channel` | Channel for production or publication. | Required | Channel name or `내부 준비` | `Douyin` | Use input/report channels. |
| `content_type` | Type of content or task. | Required | Allowed value | `short_form_video` | Use `other` only with explanation. |
| `topic` | Content topic. | Required | Korean phrase | `B2B 공급 조건 체크` | Avoid fake market claims. |
| `production_task` | Concrete production task. | Required | Korean action sentence | `제품 이미지 정리 후 15초 영상 초안 제작` | Must be actionable. |
| `required_materials` | Materials needed for the task. | Required | List | `제품 이미지, 승인 가능 브랜드 목록, 중국어 자막 초안` | Mark missing materials clearly. |
| `owner` | Person or role responsible. | Required | Role or person name | `담당자` | May be generic if owner is not assigned yet. |
| `expected_output` | Concrete output of the task. | Required | Korean phrase | `영상 초안 1건` | Do not promise performance results. |

## 6. Asset Checklist

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `product_images` | Product photos needed for video/feed production. | Required | Available/missing/check-needed list | `아누아 제품 이미지: 확인 필요` | Must not fetch external images automatically. |
| `product_videos` | Product video clips needed for short-form production. | Required | Available/missing/check-needed list | `제품 사용감 영상: 소스 자료 부족` | Mark missing clips before production. |
| `texture_shots` | Texture or detail shots needed. | Required | Available/missing/check-needed list | `토너 제형 컷: 검증 필요` | Avoid before/after or efficacy implication unless approved. |
| `package_shots` | Packaging and product package shots needed. | Required | Available/missing/check-needed list | `패키지 정면 컷: 필요` | Use approval-safe brand/product visuals only. |
| `before_after_restrictions` | Restrictions on before/after images or similar claims. | Required | Korean risk note | `전후 이미지는 승인 및 규제 확인 전 사용 금지` | Required for cosmetics claim safety. |
| `brand_approval_materials` | Brand approval records and usage permission materials. | Required | Available/missing/check-needed list | `메디큐브: 승인 전 외부 노출 금지` | Approval-required brands cannot appear externally without explicit approval. |
| `translation_localization_materials` | Translation and localization materials. | Required | Available/missing/check-needed list | `중국어 카피 검수 자료: 확인 필요` | Required for China or non-Korean execution. |
| `proof_documents_if_needed` | Proof documents needed to support claims or supply terms. | Required | List | `MOQ/납기 확인 자료, 브랜드 승인 자료, 표현 검토 자료` | If unavailable, mark as `검증 필요`. |

## 7. B2B Inquiry Conversion Plan

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `content_id` | Related content ID. | Required | `V-001`, `F-001`, etc. | `F-001` | Must match a planned video/feed item. |
| `buyer_segment` | Buyer segment targeted by the content. | Required | Korean phrase | `100개 이상 주문 가능한 중국 도매상 또는 수입상` | Must reflect B2B export buyer logic. |
| `inquiry_trigger` | What prompts the buyer to inquire. | Required | Korean sentence | `공급 가능 브랜드와 MOQ를 확인하고 싶을 때 문의하도록 유도` | Do not rely on consumer likes or views as buyer demand. |
| `CTA` | B2B call to action. | Required | Korean CTA | `MOQ와 공급 가능 브랜드 문의` | Must connect to contact path. |
| `landing_or_contact_path` | Where inquiries should go. | Required | Contact path or Korean process | `WeChat 또는 이메일 문의 -> 담당자 확인 -> 자료 발송` | For China, WeChat or suitable inquiry path should be considered. |
| `follow_up_message_direction` | Direction for follow-up after inquiry. | Required | Korean sentence | `국가, 예상 수량, 관심 브랜드, 승인 가능 여부, MOQ/납기를 확인하는 메시지` | Must exclude restricted brands unless approved. |
| `required_sales_materials` | Sales materials needed for follow-up. | Required | List | `승인 가능 브랜드 목록, 제품 이미지, 카탈로그, MOQ/납기 안내` | Mark missing materials as `소스 자료 부족` or `검증 필요`. |

## 8. Risks and Compliance

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `cosmetics_claim_risk` | Risk from cosmetic efficacy or regulated claims. | Required | Korean sentence or bullet list | `미백, 여드름 치료, 전후 비교, 기능성 단정 표현은 검증 전 사용 금지` | Avoid medical/drug-like claims. |
| `brand_approval_risk` | Risk from using approval-required brands. | Required | Korean sentence or bullet list | `메디큐브는 명시 승인 전 외부 게시, 영상 스크립트, 피드 카피에서 제외` | Must respect `restricted_or_approval_required_brands`. |
| `China_account_or_platform_risk` | China account, platform, and operation risk. | Required when China is target country; optional otherwise | Korean sentence or bullet list | `중국 계정 운영 주체, 실명/계정 조건, 플랫폼 정책 확인 필요` | Include Xiaohongshu, Douyin, WeChat where relevant. |
| `localization_risk` | Translation and local expression risk. | Required | Korean sentence or bullet list | `중국어 카피는 현지화 검토 전 외부 사용 금지` | Required for China or multilingual content. |
| `production_resource_risk` | Risk from missing assets, time, budget, or people. | Required | Korean sentence or bullet list | `제품 이미지와 영상 소스 부족으로 제작 범위 축소 필요 가능` | Keep recommendations practical for small team. |
| `evidence_limitation_risk` | Risk from insufficient or unverified source evidence. | Required | Korean sentence or bullet list | `소스 자료 부족으로 시장 반응, 채널 성과, 바이어 수요는 확정 불가` | Must carry over caution from source reports. |

## 9. Final Recommendation

| Field | Meaning | Required | Format | Example | Notes |
|---|---|---|---|---|---|
| `go_or_no_go` | Final production decision. | Required | Allowed value | `go_with_caution` | Use `no_go` if external use is unsafe due to approvals, assets, or compliance. |
| `first_video_to_make` | First video to produce. | Required | Video ID plus title | `V-001: B2B 제품군 체크 영상` | Must be practical with available assets. |
| `first_feed_to_make` | First feed post to produce. | Required | Feed ID plus title | `F-001: B2B 공급 조건 안내 카드` | Must be useful for inquiry conversion or proof-building. |
| `next_actions` | Next actions before production or external use. | Required | Numbered Korean list | `1. 승인 가능 브랜드 확인 2. 제품 이미지 정리 3. 중국어 카피 검수 4. 문의 경로 설정` | Include approval, asset, evidence, localization, and validation tasks. |

## Validation Requirements

Generated Task 005 outputs must be validated for:

- All 9 required sections exist.
- Required fields appear in each section.
- Korean text is preserved.
- B2B and B2C are separated.
- China channel adaptations are included when target country is China.
- `메디큐브` is not externally recommended unless explicitly approved.
- Production difficulty, expected effect, cost level, and risk level are included.
- Each video idea includes hook, opening scene, scene-by-scene plan, product shot direction, CTA, required assets, compliance notes, and risk.
- Each feed idea includes image structure, slide-by-slide plan, headline, key copy, proof points, CTA, design notes, required assets, compliance notes, and risk.
- Weekly production schedule exists.
- Asset checklist exists.
- B2B inquiry conversion plan exists.
- No fake performance claims or unsupported market facts are included.
- Insufficient evidence is carried over from source reports.
- Approval-required brands are excluded from public-facing and buyer-facing content unless explicitly approved.
- China account/platform, localization, and cosmetics expression risks are included where relevant.

## External Use Warning

Task 005 outputs are internal planning drafts unless all required evidence, brand approvals, localization checks, and cosmetics claim reviews are complete.

Reports marked `go_with_caution` may be used for internal planning, but external posting, buyer-facing proposals, advertising copy, video scripts, and feed copy still require verification and approval.
