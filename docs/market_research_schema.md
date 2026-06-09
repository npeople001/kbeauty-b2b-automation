# Market Research and Content Strategy Schema

This document defines the report structure for K-beauty B2B export market research and content strategy planning.

The schema will support later automation for market research summaries, channel strategy decisions, short-form video planning, feed post planning, and one organized strategy report. This document does not implement scraping, crawling, web research automation, prompt files, buyer outreach, or lead management.

## Business Rules

- Distinguish B2B buyer acquisition from consumer marketing in every recommendation.
- Do not assume unverified market data. Mark uncertain findings as `uncertain`, `needs_verification`, or `assumption`.
- Include source dates and report dates when available because market signals and platform rules can change.
- Include China channel risks for China-related channels, including account registration, real-name verification, local entity requirements, platform policy, and localization risk.
- Consider brand approval restrictions before external posting, proposal, or buyer-facing content.
- Approval-required brands must not be included in external proposal or posting recommendations unless explicit approval is recorded.
- Do not guess official English brand names.
- For B2B buyer acquisition, assume MOQ is generally 100+ units and delivery lead time is generally 20-30 days unless verified otherwise.
- Preserve Korean, English, and Chinese text with UTF-8 compatible encoding.

## Field Format Guide

| Format | Meaning |
| --- | --- |
| Text | UTF-8 text. May include Korean, English, or Chinese. |
| Date | ISO date: `YYYY-MM-DD`. |
| Enum | One of the listed values. Use `unknown` if not known. |
| List | Semicolon-separated values for CSV-style use, or bullet list in reports. |
| Evidence text | Short statement with source, date, and confidence when available. |
| Risk text | Risk description plus mitigation or verification need. |

## 1. Research Brief

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `target_country` | Country or region being researched. | Required | Text | `China` | Priority markets include China, Southeast Asia, Russia, and later global buyers. |
| `target_channel` | Main platform, channel, or channel group being evaluated. | Required | Text or List | `Xiaohongshu; Douyin; WeChat` | Use exact platform or channel names where possible. |
| `target_brand` | Brand or brand group being considered. | Optional | Text or List | `라곰; 토리든` | Do not guess official English names. Check approval restrictions before external recommendations. |
| `target_product_category` | Product category being researched. | Required | Text or List | `skincare; cleansing` | Use normalized categories where possible. |
| `research_objective` | Business reason for the research. | Required | Text | `Identify China channels for B2B buyer acquisition and content planning.` | Should connect to overseas marketing, China channel development, buyer acquisition, or profit growth. |
| `b2b_or_b2c_focus` | Whether the research is focused on buyer acquisition, consumer marketing, or both. | Required | Enum: `b2b`, `b2c`, `both`, `unknown` | `b2b` | B2B buyer acquisition must be separated from consumer awareness tactics. |
| `date` | Date the research report is prepared. | Required | Date | `2026-06-05` | Use the report creation date, not the source publication date. |
| `researcher` | Person, team, or automation process preparing the report. | Required | Text | `Npeople export team` | Use `unknown` only if the researcher is not identifiable. |

## 2. Market Overview

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `market_size_or_signal` | Evidence of market size, demand, platform activity, or commercial opportunity. | Required | Evidence text | `Multiple skincare posts observed; market size needs_verification.` | Do not invent numbers. Use `needs_verification` for unverified signals. |
| `demand_trend` | Direction of demand for the category or brand theme. | Required | Enum or Evidence text: `growing`, `stable`, `declining`, `uncertain`, plus evidence | `growing: hydration and barrier-care content appears frequent.` | Trend claims need evidence or uncertainty marking. |
| `consumer_interest` | Consumer-side interest signals. | Required | Evidence text | `Consumers appear interested in gentle skincare routines; uncertain.` | Consumer interest is not the same as buyer purchase intent. |
| `buyer_interest` | B2B buyer-side interest signals. | Required | Evidence text | `Distributor interest not confirmed; needs buyer-channel validation.` | Must be separated from consumer likes, views, or comments. |
| `key_growth_drivers` | Factors that may support market growth. | Optional | List | `K-beauty awareness; short-form video discovery; skincare routine content` | Mark assumptions clearly. |
| `key_barriers` | Factors that may block market entry or sales. | Required | List | `Platform account restrictions; claim compliance; local competition` | Include regulatory, language, channel, and brand approval barriers. |

## 3. Channel Analysis

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `channel_name` | Name of the channel being analyzed. | Required | Text | `Xiaohongshu` | Analyze one channel per row or subsection. |
| `channel_type` | Main channel role. | Required | Enum: `social`, `short_video`, `messaging`, `marketplace`, `wholesale_marketplace`, `b2b_platform`, `search`, `other`, `unknown` | `social` | 1688 may be wholesale marketplace; WeChat may be messaging/private commerce. |
| `user_profile` | Typical users or business participants on the channel. | Required | Evidence text | `Beauty consumers and content creators; B2B buyer presence needs_verification.` | Distinguish general platform users from importers, distributors, or wholesale buyers. |
| `content_format` | Common content formats on the channel. | Required | List | `short video; image feed; product comparison` | Use formats relevant to the channel. |
| `b2b_usefulness` | Usefulness for buyer discovery, relationship building, wholesale inquiry, or proof-building. | Required | Enum plus notes: `high`, `medium`, `low`, `unknown` | `medium: useful for brand signal, direct buyer capture uncertain.` | Do not treat consumer engagement as confirmed B2B usefulness. |
| `b2c_usefulness` | Usefulness for consumer awareness, demand creation, or retail conversion. | Required | Enum plus notes: `high`, `medium`, `low`, `unknown` | `high: suitable for skincare content discovery.` | B2C usefulness may support B2B proof but is not a buyer lead by itself. |
| `restrictions_or_risks` | Platform, account, policy, translation, compliance, or China-specific channel risks. | Required | Risk text | `China real-name/account requirements and cosmetics claim limits need review.` | China channel risks must be included for local platforms. |
| `recommended_usage` | How the business should use the channel. | Required | Text | `Use for consumer signal research and soft brand awareness; capture B2B inquiries through WeChat.` | State whether the channel is for research, content, buyer acquisition, proof-building, or inquiry capture. |

## 4. Competitor and Content Analysis

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `competing_brands` | Brands or products appearing in the same category or content space. | Required | List | `Local derma brands; Korean skincare competitors` | Do not present unverified competitor lists as complete. |
| `popular_content_types` | Content formats that appear to perform or recur often. | Required | List | `before-after routine; ingredient explanation; texture test` | Use observed signals or mark as assumption. |
| `common_hooks` | Opening lines, visual hooks, or ideas commonly used to attract attention. | Optional | List | `For sensitive skin; barrier routine; lightweight hydration` | Avoid medical, guaranteed, or unverified claims. |
| `common_visual_style` | Common look, composition, or editing style. | Optional | Text | `Clean shelf shots, close-up texture application, subtitle-heavy edits.` | Helpful for production planning. |
| `common_claims` | Claims commonly made in content or product positioning. | Required | List | `hydrating; calming; barrier support` | Flag claims that may need compliance review. |
| `pricing_or_positioning_signal` | Price tier or market positioning signal. | Optional | Evidence text | `Mid-price derma positioning appears common; uncertain.` | Do not infer exact pricing without verified data. |
| `engagement_signal` | Observed engagement or attention signal. | Optional | Evidence text | `High comment volume on routine videos; source/date needed.` | Views, likes, comments, and shares should be recorded with date if available. |

## 5. Product/Brand Fit

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `recommended_brands` | Brands that may fit the market or channel opportunity. | Required | List | `라곰; 토리든` | Check brand approval restrictions before external use. |
| `recommended_product_categories` | Product categories to prioritize. | Required | List | `hydration skincare; cleansing; sunscreen` | Must connect to market signals and buyer needs. |
| `reason_for_selection` | Why these brands or categories are selected. | Required | Evidence text | `Selected for gentle skincare positioning; buyer demand still needs_verification.` | Separate evidence from assumptions. |
| `target_buyer_type` | Buyer segment the product or brand may fit. | Required | List | `distributor; importer; online store; marketplace seller` | Buyer type is flexible if the buyer can order 100+ units. |
| `differentiation_angle` | Clear message that differentiates the brand or category. | Required | Text | `Korean routine-focused skincare with MOQ-friendly export support.` | Avoid unverified superiority claims. |
| `approval_required_check` | Approval status review before recommending external posting or proposal. | Required | Enum plus notes: `cleared`, `approval_required`, `not_allowed`, `unknown` | `cleared: no approval restriction found in current brand master.` | Approval-required brands must not be used externally without explicit approval. |

## 6. B2B Buyer Acquisition Angle

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `target_buyer_segments` | B2B buyer groups to approach or attract. | Required | List | `China distributors; importers; online beauty sellers` | Must be distinct from consumer audience segments. |
| `buyer_pain_points` | Problems or needs the buyer may have. | Required | List | `Need reliable Korean sourcing; need MOQ clarity; need marketable content assets` | Mark assumptions if not verified by buyer interviews or data. |
| `value_proposition` | Business value offered to buyers. | Required | Text | `Access to Korean cosmetics brands with MOQ 100+ and 20-30 day lead time guidance.` | Include realistic operating constraints. |
| `proof_points_needed` | Evidence needed to convince buyers. | Required | List | `brand list; pricing availability; product photos; compliance documents; content performance signals` | Do not claim proof that has not been collected. |
| `message_angle` | Buyer-facing angle for outreach or inquiry capture. | Required | Text | `K-beauty sourcing partner for China distributors seeking MOQ-friendly skincare.` | Must exclude approval-required brands unless approved. |
| `lead_capture_method` | How B2B inquiries or buyer contacts should be collected. | Required | Text | `WeChat inquiry form, LinkedIn message, B2B platform contact form, or manual CRM entry.` | This schema plans the method only; it does not implement buyer lead management. |

## 7. Content Strategy

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `channel` | Channel where content will be posted or tested. | Required | Text | `Douyin` | Use one row per channel strategy. |
| `content_goal` | Purpose of the content. | Required | Enum: `consumer_awareness`, `buyer_acquisition`, `proof_building`, `product_education`, `inquiry_capture`, `other` | `proof_building` | Connect content goal to B2B or B2C focus. |
| `content_angle` | Strategic angle for the content. | Required | Text | `Show product texture and routine fit for China skincare audiences.` | Avoid unsupported product claims. |
| `post_type` | Type of post. | Required | Enum or Text: `short_video`, `feed_image`, `carousel`, `live`, `article`, `message_post`, `other` | `short_video` | Use channel-native formats. |
| `upload_frequency` | Planned cadence. | Optional | Text | `3 posts per week for 4 weeks` | Should be realistic for available production resources. |
| `expected_effect` | Expected outcome of the content. | Required | Text | `Build consumer signal that can support buyer discussions.` | Mark as expected, not guaranteed. |
| `risk` | Content execution risk. | Required | Risk text | `Claim compliance and translation localization need review.` | Include platform and brand approval risks where relevant. |

## 8. Short-form Video Plan

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `video_concept` | Main concept of the short-form video. | Required | Text | `Three-step Korean hydration routine for humid weather.` | Should match channel and audience. |
| `hook` | First phrase or visual that captures attention. | Required | Text | `Light hydration without a heavy finish.` | Avoid medical, guaranteed, or unverified claims. |
| `opening_scene` | First visual scene. | Required | Text | `Close-up texture shot on clean background.` | Keep production realistic. |
| `key_scenes` | Main sequence of scenes. | Required | List | `texture test; application; routine lineup; final shelf shot` | Use semicolon-separated values for CSV-style use. |
| `product_shot_direction` | How products should be shown. | Required | Text | `Show packaging, texture, and application without overclaiming efficacy.` | Check brand approval before external posting. |
| `caption_direction` | Caption or subtitle style and language direction. | Required | Text | `Chinese subtitles with concise benefit wording and compliance review.` | Localization risk must be considered. |
| `CTA` | Call to action. | Required | Text | `For wholesale inquiry, contact us on WeChat.` | B2B CTA should be separated from consumer retail CTA. |
| `production_difficulty` | Difficulty level for production. | Required | Enum: `low`, `medium`, `high`, `unknown` | `medium` | Consider models, filming, editing, product samples, and translation. |
| `expected_effect` | Expected business or marketing effect. | Required | Text | `Create reusable product proof content for buyer discussions.` | Do not guarantee performance. |

## 9. Feed Post Plan

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `feed_concept` | Main idea for a feed post or carousel. | Required | Text | `Korean skincare routine lineup for distributors.` | Can be B2B-facing or consumer-facing, but must be labeled. |
| `image_structure` | Visual layout or image sequence. | Required | Text or List | `cover; product lineup; category benefit; inquiry CTA` | Useful for carousel and image feed production. |
| `headline` | Main headline text. | Required | Text | `K-beauty skincare sourcing for China buyers` | Avoid unsupported claims. |
| `key_copy` | Main supporting copy. | Required | Text | `MOQ 100+ units, 20-30 day delivery lead time guidance, approved brands only.` | Include business constraints when B2B-facing. |
| `product_display_direction` | How products should appear in feed visuals. | Required | Text | `Clear packaging image with Korean brand name visible.` | Validate brand approval before posting externally. |
| `CTA` | Call to action for the feed post. | Required | Text | `Send inquiry for wholesale availability.` | Use B2B CTA for buyer acquisition posts. |
| `design_notes` | Production notes for design, language, or localization. | Optional | Text | `Use Korean product image, Chinese headline, and English internal notes.` | Preserve multilingual text with UTF-8. |

## 10. Execution Plan

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `priority` | Execution priority. | Required | Enum: `high`, `medium`, `low`, `unknown` | `high` | Use priority to sequence limited resources. |
| `action_item` | Specific action to perform. | Required | Text | `Prepare Xiaohongshu feed post draft for approved skincare brands.` | Should be actionable and scoped. |
| `owner` | Person or team responsible. | Required | Text | `Marketing team` | Use `unknown` if not assigned yet. |
| `required_materials` | Materials needed to execute the action. | Required | List | `product photos; approved brand list; Chinese copy review` | Include approval or compliance documents when needed. |
| `deadline` | Target completion date. | Optional | Date or Text | `2026-06-12` | Use `TBD` only when no date is assigned. |
| `expected_output` | Deliverable expected from the action. | Required | Text | `One feed post draft and one short-form video outline.` | Keep outputs concrete. |

## 11. Risks and Compliance

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `platform_policy_risk` | Risk from platform posting, account, commerce, or ad policies. | Required | Risk text | `Douyin product promotion policy needs_verification before posting.` | Must be reviewed per channel. |
| `China_real_name_or_account_risk` | China-specific account registration, real-name, business verification, or local operation risk. | Required for China channels; optional otherwise | Risk text | `WeChat official account or Douyin account operation may require local verification.` | Required when target country or channel is China-related. |
| `cosmetics_claim_risk` | Risk from product efficacy, ingredient, medical, or regulatory claims. | Required | Risk text | `Avoid whitening, acne treatment, or medical-style claims unless verified and compliant.` | Review claims before external posting. |
| `brand_approval_risk` | Risk of using approval-required brands without permission. | Required | Risk text | `메디큐브 requires director approval before external posting/proposal.` | Approval-required brands must be excluded unless explicitly approved. |
| `translation_localization_risk` | Risk from mistranslation, tone mismatch, or local market wording. | Required | Risk text | `Chinese captions require localization review before posting.` | Especially important for China, Southeast Asia, and Russia. |
| `data_reliability_risk` | Risk that research data is stale, unverified, biased, or incomplete. | Required | Risk text | `Observed platform content is directional only; source/date and sample size need verification.` | Mark uncertain findings clearly. |

## 12. Final Recommendation

| Field | Meaning | Required or optional | Format | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `go_or_no_go` | Final recommendation to proceed, pause, or reject. | Required | Enum plus reason: `go`, `no_go`, `conditional_go`, `needs_more_research` | `conditional_go: proceed with Xiaohongshu content testing after approval check.` | Must reflect risks and evidence quality. |
| `recommended_channels` | Channels recommended for the next stage. | Required | List | `Xiaohongshu for consumer signal; WeChat for B2B inquiry capture` | State channel purpose, not only channel name. |
| `recommended_content` | Content themes, formats, or assets to produce. | Required | List | `short-form texture tests; B2B sourcing feed post; buyer inquiry CTA` | Separate B2B buyer acquisition from consumer awareness content. |
| `next_actions` | Immediate next steps after the report. | Required | List | `Confirm approved brands; collect product images; draft Chinese captions; verify platform policy` | Should not include scraping or web research automation implementation in this step. |

## Report-Level Validation Checklist

- All 12 required sections are present.
- Each requested field includes meaning, required status, format, example, and notes.
- B2B buyer acquisition is distinguished from consumer marketing.
- Unverified market data is marked as uncertain or needing verification.
- China channel risks are included when China-related channels are discussed.
- Brand approval restrictions are checked before external posting or proposal recommendations.
- The report does not include scraping, crawling, or web research automation logic.
- No prompt files, task log updates, or roadmap updates are required for this step.
