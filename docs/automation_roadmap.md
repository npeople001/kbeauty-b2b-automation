# Automation Roadmap

This roadmap defines planned automation tasks for the K-beauty B2B export business.

## Task 001: Brand Master Automation

- Status: Completed; current validation passed for core data, approval rules, README, XLSX generation, and CSV encoding handling.
- Goal: Maintain a structured, validated brand master for sourcing, approval control, and business-user outputs.
- Input: Current available brand list, approval rules, category rules, and brand master schema.
- Output: `data/brands_raw.csv`, `data/brands_master.csv`, validation script, and `output/brands_master.xlsx`.
- Business rules: Protect approval-required brands; `메디큐브` must have `approval_required=true` and `proposal_allowed=false`; do not guess official English names; preserve Korean text.
- Validation method: Run `tests/validate_brands_master.py`; regenerate XLSX; verify Korean brand names, row count, approval rules, and Excel-compatible encoding.
- Risks: CSV encoding may break Korean text in Windows Excel; categories, sub-categories, official English names, and priorities need business confirmation.

## Task 002: Market Research & Content Strategy Template

- Status: Completed pending final business review.
- Goal: Define reusable market research and content strategy structures for K-beauty B2B export marketing, China channel development, short-form video planning, feed planning, and B2B buyer acquisition planning.
- Direction change: Task 002 was redirected from buyer lead management to market research and content strategy because the immediate business need is market research automation and channel/content planning.
- Input: Target country, target channels, target brands, product categories, research objective, B2B/B2C focus, available brand list, approval-required brands, campaign objective, available assets, budget level, execution period, source materials, and date.
- Completed outputs:
  - `docs/market_research_schema.md`
  - `prompts/market_research_prompt.md`
  - `prompts/content_strategy_prompt.md`
  - `data/research_inputs_sample.csv`
  - `output/sample_market_research_report.md`
  - `docs/market_research_review_checklist.md`
- Business rules: Reports must separate verified facts, observations, assumptions, and recommendations; distinguish B2B buyer acquisition from consumer marketing; review China channel risks, brand approval restrictions, cosmetics claims, and localization risks; `메디큐브` remains approval-required and must not be externally recommended without approval.
- Validation method: Confirm all required schema sections, prompt variables, sample CSV columns and row count, UTF-8 BOM CSV encoding, controlled sample report sections, no fake market data or fake sources, and review checklist coverage.
- Risks: This task does not implement scraping or live web research; future generated reports still require source verification before internal reliance or external use; China platform rules and cosmetics compliance requirements may change.

## Task 003: Market Research Report Generator

- Status: Completed pending final review.
- Goal: Generate structured market research reports from structured inputs and user-provided source materials using the Task 002 schema and Task 003 generator specification.
- Input: `data/research_inputs_sample.csv` style input rows and user-provided source materials under `data/source_materials/market_research/{research_id}/`.
- Completed outputs:
  - `docs/market_research_generator_spec.md`
  - `data/source_materials/market_research/README.md`
  - `data/source_materials/market_research/MR-001/source_notes.md`
  - `data/source_materials/market_research/MR-001/sources.csv`
  - `automations/market_research/README.md`
  - `automations/market_research/generate_market_research_report.py`
  - `tests/validate_market_research_report.py`
  - `output/market_research_report_MR-001.md`
- Output: Korean Markdown market research reports following `docs/market_research_schema.md`.
- Business rules: Use only structured inputs and user-provided source materials; do not invent market facts; mark insufficient evidence as `검증 필요`, `소스 자료 부족`, or `확정 불가`; separate `확인된 사실`, `관찰`, `가정`, `검증 필요`, and `추천`; separate B2B buyer acquisition from consumer marketing; include China risks, cosmetics claim risks, localization risks, and brand approval risks; exclude approval-required brands from external recommendations unless explicitly approved.
- External data restriction: Task 003 does not include scraping, live web research, automatic web search, browser automation, APIs, crawlers, or external data collection.
- Validation method: Generate `output/market_research_report_MR-001.md`; run `python tests/validate_market_research_report.py --report output/market_research_report_MR-001.md`; run `python -m py_compile automations/market_research/generate_market_research_report.py tests/validate_market_research_report.py`; review with `docs/market_research_review_checklist.md` before business use.
- Risks: Source materials may be insufficient, stale, or biased; generated reports must not be treated as verified market facts without review; China platform/account rules and cosmetics compliance requirements may change; approval-required brands including `메디큐브` must not be externally recommended without explicit approval.
- Next recommended task: Task 004: Channel Content Strategy Generator.

## Task 004: Channel Content Strategy Generator

- Status: Completed pending final review.
- Goal: Generate channel-specific content strategy reports from structured inputs, existing market research reports, and user-provided source materials.
- Input: `data/research_inputs_sample.csv` style input rows, existing market research reports under `output/market_research_report_{research_id}.md`, and optional user-provided source materials under `data/source_materials/market_research/{research_id}/`.
- Completed outputs:
  - `docs/channel_content_strategy_generator_spec.md`
  - `docs/channel_content_strategy_schema.md`
  - `automations/channel_content_strategy/README.md`
  - `automations/channel_content_strategy/generate_channel_content_strategy.py`
  - `tests/validate_channel_content_strategy.py`
  - `output/channel_content_strategy_MR-001.md`
- Output: Korean Markdown channel content strategy reports with Strategy Summary, Channel Strategy, Short-form Video Strategy, Feed Post Strategy, B2B Buyer Acquisition Content, Weekly Upload Plan, Execution Priority, Risks and Compliance, and Final Recommendation.
- Business rules: Use only structured inputs, existing market research reports, and user-provided source materials; separate B2B buyer acquisition from consumer marketing; include Xiaohongshu, Douyin, and WeChat for China where relevant; include short-form video ideas, feed post ideas, weekly upload plan, execution priority, and B2B inquiry/conversion path; include execution difficulty, expected effect, cost level, and risk level; carry forward `검증 필요`, `소스 자료 부족`, or `확정 불가` when evidence is insufficient; `메디큐브` remains approval-required and must not be externally recommended without explicit approval.
- External data restriction: Task 004 does not include scraping, live web research, automatic web search, browser automation, APIs, crawlers, requests, or external data collection.
- Validation method: Generate `output/channel_content_strategy_MR-001.md`; run `python tests/validate_channel_content_strategy.py --report output/channel_content_strategy_MR-001.md`; verify required 9 sections, Korean text preservation, B2B/B2C separation, China channel/risk coverage, brand approval handling, fake source prevention, unsupported performance claim prevention, video/feed/weekly/prioritization fields, and no external data collection code.
- Risks: Generated content strategies are internal planning drafts until reviewed; source materials and market research reports may be insufficient, stale, or biased; China platform/account rules and localization requirements may change; cosmetics claims must be reviewed before external use; approval-required brands including `메디큐브` must not be externally recommended without explicit approval.
- Next recommended task: Task 005: Short-form Video & Feed Plan Generator.

## Task 005: Short-form Video & Feed Plan Generator

- Status: Completed pending final review.
- Goal: Generate detailed short-form video production plans and feed post production plans from structured inputs, existing market research reports, existing channel content strategy reports, and user-provided source materials.
- Input: `data/research_inputs_sample.csv` style input rows, existing market research reports under `output/market_research_report_{research_id}.md`, existing channel strategy reports under `output/channel_content_strategy_{research_id}.md`, and optional user-provided source materials under `data/source_materials/market_research/{research_id}/`.
- Completed outputs:
  - `docs/short_form_feed_plan_generator_spec.md`
  - `docs/short_form_feed_plan_schema.md`
  - `automations/short_form_feed_plan/README.md`
  - `automations/short_form_feed_plan/generate_short_form_feed_plan.py`
  - `tests/validate_short_form_feed_plan.py`
  - `output/short_form_feed_plan_MR-001.md`
- Output: Korean Markdown short-form video and feed production plans with Executive Summary, Short-form Video Production Plan, Feed Post Production Plan, Channel-Specific Adaptation, Weekly Production Schedule, Asset Checklist, B2B Inquiry Conversion Plan, Risks and Compliance, and Final Recommendation.
- Business rules: Use only structured inputs, existing internal reports, and user-provided source materials; separate B2B buyer acquisition content from consumer marketing content; include Xiaohongshu, Douyin, and WeChat adaptations for China where relevant; include required assets, production difficulty, expected effect, cost level, risk level, and compliance notes for each video/feed idea; carry forward `검증 필요`, `소스 자료 부족`, or `확정 불가` when evidence is insufficient; `메디큐브` remains approval-required and must not be externally recommended without explicit approval.
- External data restriction: Task 005 does not include scraping, live web research, automatic web search, browser automation, APIs, crawlers, requests, or external data collection.
- Validation method: Generate `output/short_form_feed_plan_MR-001.md`; run `python tests/validate_short_form_feed_plan.py --report output/short_form_feed_plan_MR-001.md`; run `python -m py_compile tests/validate_short_form_feed_plan.py`; verify required 9 sections, Korean text preservation, B2B/B2C separation, China channel/risk coverage, brand approval handling, fake source prevention, unsupported performance claim prevention, video/feed/weekly/asset/B2B conversion fields, and no external data collection code.
- Risks: Generated plans are internal planning drafts until reviewed; source reports may contain insufficient or unverified evidence; China platform/account rules, localization expectations, and cosmetics claim requirements may change; external use still requires source verification, brand approval, local regulation review, localization review, and actual product images/videos/proof materials.
- Next recommended task: Task 006: Buyer Lead Template.

## Task 006: Buyer Lead Template

- Status: Completed pending final review.
- Goal: Create standardized buyer lead templates, schema, validation, and business-facing XLSX review output for manually provided overseas buyer lead data.
- Input: Manually provided buyer lead records, buyer company/channel/contact placeholders, interested brands/categories, estimated order quantity, lead status, priority, and next-action workflow.
- Completed outputs:
  - `docs/buyer_lead_template_spec.md`
  - `docs/buyer_lead_schema.md`
  - `data/buyers_raw_sample.csv`
  - `data/buyers_master_sample.csv`
  - `tests/validate_buyer_leads.py`
  - `automations/buyer_leads/README.md`
  - `automations/buyer_leads/generate_buyer_leads_xlsx.py`
  - `output/buyers_master_sample.xlsx`
- Output: UTF-8 BOM CSV buyer lead sample templates, buyer lead validation script, and business-facing XLSX workbook for internal review.
- Business rules: Buyer lead data must be manually provided; contact fields are privacy-sensitive and sample files must use placeholder data only; MOQ is generally 100+ units and `moq_fit` must align with `estimated_order_qty`; `메디큐브` remains approval-required and must trigger `approval_warning` and `approval_required_review` when present in `interested_brands`; approval-required brands may be recorded as buyer interest but must not be automatically recommended for external proposal, buyer-facing pitch, public content, or quotation; CSV files must use `utf-8-sig`; XLSX is preferred for business review; China buyer workflow fields support manual management only and do not imply automatic collection from Xiaohongshu, Douyin, WeChat, Taobao, 1688, or other platforms.
- External data restriction: Task 006 does not include scraping, live web research, automatic web search, browser automation, APIs, crawlers, requests, or external data collection.
- Validation method: Run `python tests/validate_buyer_leads.py --raw data/buyers_raw_sample.csv --master data/buyers_master_sample.csv`; run `python automations/buyer_leads/generate_buyer_leads_xlsx.py`; inspect `output/buyers_master_sample.xlsx` for workbook structure, header freeze, filters, highlighted inspection columns, Korean/Chinese text preservation, and placeholder contact handling.
- Risks: Buyer records can contain privacy-sensitive contact data when real inputs are used; this task does not verify whether a buyer is real; payment risk and purchase potential still require manual review; approval-required brand handling must be checked before external communication; China platform/account expectations may change.
- Next recommended task: Task 007: Buyer Scoring Automation.

## Task 007: Buyer Scoring Automation

- Status: Completed pending final review.
- Goal: Score manually provided local buyer lead data and assign internal sales-priority score, priority tier, scoring reasons, risk flags, approval block, and recommended next action.
- Input: `data/buyers_master_sample.csv` and optional local brand approval reference `data/brands_master.csv`.
- Completed outputs:
  - `docs/buyer_scoring_automation_spec.md`
  - `docs/buyer_scoring_schema.md`
  - `docs/buyer_scoring_rules.md`
  - `automations/buyer_scoring/README.md`
  - `automations/buyer_scoring/generate_buyer_scores.py`
  - `automations/buyer_scoring/generate_buyer_scores_xlsx.py`
  - `tests/validate_buyer_scores.py`
  - `data/buyers_scored_sample.csv`
  - `output/buyers_scored_sample.xlsx`
- Output: UTF-8 BOM scored buyer CSV and business-facing XLSX workbook for internal sales priority review.
- Business rules: Task 007 only scores manually provided local buyer lead data. It does not verify buyer authenticity, creditworthiness, payment ability, or purchase certainty. `score_total` and `priority_tier` are internal prioritization signals only. `approval_block=true` means external proposal, buyer-facing pitch, quotation, public content, or ad copy must not proceed for the approval-required brand. `메디큐브` remains approval-required and must trigger `approval_block=true` unless explicit approval is recorded. `payment_risk` is a manual indicator only, not credit verification. `buyer_unverified` and `source_manual_only` are expected risk flags. Scored output should not expose unnecessary contact fields. CSV files must use `utf-8-sig`; XLSX is preferred for business review.
- External data restriction: Task 007 does not include scraping, live web research, automatic web search, automatic search, APIs, browser automation, crawlers, requests, buyer enrichment, credit checks, or external data collection.
- Validation method: Run `python automations/buyer_scoring/generate_buyer_scores.py`; run `python tests/validate_buyer_scores.py --input data/buyers_master_sample.csv --scored data/buyers_scored_sample.csv`; run `python automations/buyer_scoring/generate_buyer_scores_xlsx.py`; verify score range, A/B/C/Hold tier mapping, MOQ logic, approval block handling, manual-source risk flags, privacy-sensitive contact exclusion, Korean/Chinese preservation, and XLSX review workbook generation.
- Risks: Scores may overstate opportunity if manually entered source data is incomplete or stale. Buyer authenticity, payment reliability, creditworthiness, and purchase intent still require manual review. Approval-required brands must be reviewed before external communication. Real buyer contact data remains privacy-sensitive. China platform/account feasibility is not verified by scoring.
- Next recommended task: Task 008: Proposal Message Generator.

## Task 008: Proposal Message Generator

- Status: Completed pending final review.
- Goal: Generate internal-review draft proposal messages for overseas buyers from local buyer lead data, buyer scoring results, and brand approval rules.
- Input: `data/buyers_master_sample.csv`, `data/buyers_scored_sample.csv`, and `data/brands_master.csv`.
- Completed outputs:
  - `docs/proposal_message_generator_spec.md`
  - `docs/proposal_message_schema.md`
  - `docs/proposal_message_rules.md`
  - `automations/proposal_messages/README.md`
  - `automations/proposal_messages/generate_proposal_messages.py`
  - `tests/validate_proposal_messages.py`
  - `data/proposal_messages_sample.csv`
  - `output/proposal_messages_sample.md`
- Output: UTF-8 BOM proposal message CSV and UTF-8 Markdown internal-review draft messages.
- Business rules: Task 008 only generates internal-review draft proposal messages. It does not send external messages, automate email, DM, WeChat, WhatsApp, or platform communication, or generate final send-ready proposals. `approval_block=true` must generate internal approval guidance only and must not generate buyer-facing proposal copy. `proposal_brand_check=approval_required_review` must be treated as approval blocked. `메디큐브` remains approval-required and must not appear in `recommended_brands` unless explicit approval is recorded. High score or `priority_tier=A` must not override `approval_block`. Drafts must not invent price, stock, inventory, expiry date, certifications, exclusive rights, contract terms, cosmetic efficacy claims, medical claims, clinical claims, sales rankings, platform metrics, buyer authenticity, creditworthiness, or purchase probability. Proposal outputs must not expose `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp` by default. MOQ 100+ and delivery lead time 20-30 days may be mentioned only as general business terms, not guaranteed final terms. Chinese, English, and Korean message drafts require internal review before external use.
- External data and sending restriction: Task 008 does not include email sending, DM sending, WeChat sending, WhatsApp sending, external messaging automation, scraping, live web research, automatic search, APIs, browser automation, crawlers, buyer enrichment, credit checks, requests, or external data collection.
- Validation method: Run `python automations/proposal_messages/generate_proposal_messages.py`; run `python tests/validate_proposal_messages.py --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --messages data/proposal_messages_sample.csv --markdown output/proposal_messages_sample.md --brands data/brands_master.csv`; verify exact output columns, row count, UTF-8 BOM CSV encoding, Markdown UTF-8 readability, approval block handling, `메디큐브` exclusion from `recommended_brands`, privacy-sensitive contact exclusion, forbidden claim prevention, language preservation, and no external sending or external data collection scope.
- Risks: Drafts are not final send-ready messages. External use still requires human review, brand approval, MOQ confirmation, price/stock/expiry verification, claim wording review, translation/localization review, buyer contact permission review, and country-specific regulatory review. Task 009 Quotation Maker must also respect `approval_block`, brand approval, MOQ, stock, price, expiry date, and claim verification.
- Next recommended task: Task 009: Quotation Maker.

## Task 009: Quotation Maker

- Status: Completed pending final review.
- Goal: Generate internal-review quotation draft files from local buyer data, scored buyer data, proposal message outputs, local brand approval rules, and manually provided quotation input data.
- Input: `data/buyers_master_sample.csv`, `data/buyers_scored_sample.csv`, `data/proposal_messages_sample.csv`, `data/brands_master.csv`, and `data/quotation_inputs_sample.csv`.
- Completed outputs:
  - `docs/quotation_maker_spec.md`
  - `docs/quotation_schema.md`
  - `docs/quotation_rules.md`
  - `data/quotation_inputs_sample.csv`
  - `automations/quotation_maker/README.md`
  - `automations/quotation_maker/generate_quotations.py`
  - `tests/validate_quotations.py`
  - `data/quotation_sample.csv`
  - `output/quotation_sample.xlsx`
  - `output/quotation_sample.md`
- Output: UTF-8 BOM quotation CSV, business-facing XLSX workbook, and UTF-8 Markdown internal-review quotation summary.
- Business rules: Task 009 only generates internal-review quotation draft files. It does not send quotations externally or create final commercial offers. Price, stock, available quantity, expiry date, supply status, price validity, MOQ, and delivery lead time must come from manually provided quotation input data. The generator must not invent missing commercial values. `approval_block=true` must block external-ready quotation. `메디큐브` remains approval-required and must be blocked unless explicit approval is recorded. Brands with `approval_required=true` or `proposal_allowed=false` must be blocked unless explicit approval is recorded. A high buyer score or A tier must not override `approval_block`. Missing price, stock, expiry, MOQ, supply, currency, or delivery data must trigger confirmation-needed status or compliance notes. `total_amount` is calculated only when `requested_qty` and `unit_price` are valid numbers and excludes tax, shipping, duties, discounts, insurance, customs fees, and incoterms. Quotation outputs must not include `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp` by default.
- External sending and data restriction: Task 009 does not include quotation sending, email sending, messaging automation, external sending, platform posting, scraping, live web research, automatic search, APIs, browser automation, crawlers, buyer enrichment, credit checks, requests, or external data collection.
- Validation method: Run `python automations/quotation_maker/generate_quotations.py`; run `python tests/validate_quotations.py --quote-inputs data/quotation_inputs_sample.csv --quotations data/quotation_sample.csv --markdown output/quotation_sample.md --xlsx output/quotation_sample.xlsx --buyers data/buyers_master_sample.csv --scores data/buyers_scored_sample.csv --proposals data/proposal_messages_sample.csv --brands data/brands_master.csv`; verify exact output columns, row count, UTF-8 BOM CSV encoding, Markdown UTF-8 readability, XLSX sheets, approval block handling, `메디큐브` blocking, price/stock/expiry/MOQ status handling, total amount calculation, privacy-sensitive contact exclusion, forbidden claim/commercial term prevention, Korean/English/Chinese preservation, and no external sending or external data collection scope.
- Risks: Manual price data may be outdated. Stock and available quantity may change. Expiry date must be rechecked before quoting. MOQ and delivery lead time may vary by product and supplier. Tax, shipping, duties, customs fees, insurance, discounts, payment terms, and incoterms are not included unless manually verified. Approval-required brands remain business-critical risk. Actual external quotation requires human review and approval.
- Foundation note: Task 001-009 now complete the first-pass internal automation foundation for brand master, market research/content planning, buyer lead management, buyer scoring, proposal drafts, and internal quotation drafts.
- Future work: Any additional task after Task 009 should be discussed separately; Task 010 is not started or defined here.
