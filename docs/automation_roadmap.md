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
- Follow-up: Task 010 was later defined as Real Data Migration & Privacy Guard to prepare the repository for real operating data protection before real business use.

## Task 010: Real Data Migration & Privacy Guard

- Status: Completed pending final review.
- Goal: Separate sample data from future real operating data, protect sensitive buyer/contact/price/stock/expiry/quotation/private business data, and define Privacy Guard validation before real business use.
- Input: Existing Task 001-009 repository structure, sample data files, output handling rules, `.gitignore`, README operating guidance, and privacy guard policy documents.
- Completed outputs:
  - `docs/real_data_migration_privacy_guard_spec.md`
  - `docs/real_sample_data_policy.md`
  - `docs/privacy_guard_validation_workflow.md`
  - `.gitignore`
  - `README.md`
  - `tests/validate_privacy_guard.py`
- Output: Real/sample data policy, private-data ignore protections, Privacy Guard validation workflow, README operating guidance, and local privacy guard validator.
- Business rules: Task 010 protects real operating data before real business use. Real buyer/contact/price/stock/expiry/quotation data must not be committed to Git. `data/private/**`, `output/private/**`, `output/final/**`, and `local_config/**` are protected by `.gitignore`. Sensitive filename patterns such as `*_real.csv`, `*_private.csv`, `*_contacts.csv`, `*_prices.csv`, `*_stock.csv`, `*_expiry.csv`, and `*_quotation_final.*` are protected. Sample data must remain fictional and placeholder-based. `메디큐브` remains approval-required unless explicit approval is recorded. Task 001-009 outputs remain internal-review only.
- External data and sending restriction: Task 010 does not include scraping, live web research, automatic search, APIs, browser automation, crawlers, buyer enrichment, credit checks, external data collection, email sending, messaging automation, quotation sending, or external sending.
- Real data creation restriction: Task 010 does not create real data files or private folders.
- Validation method: Run `python tests/validate_privacy_guard.py`; confirm `.gitignore` protects private folders and sensitive filename patterns; confirm sample/source files remain trackable; confirm no real data files, private folders, scraping/live research/API/external data collection, or external sending automation were added.
- Risks: Privacy Guard is not a full DLP system. Human review is still required before commit. Real data may still be accidentally placed in the wrong path if operating discipline is weak. Commercial data freshness must still be verified manually. Approval-required brand misuse remains a business risk.
- Follow-up: Task 011 was later defined as Integrated Runner to orchestrate the existing sample buyer sales workflow after Task 010 privacy guardrails were in place.

## Task 011: Integrated Runner

- Status: Completed pending final review.
- Goal: Run the existing internal Task 006-010 buyer sales sample workflow through one controlled local runner while preserving all privacy, approval, validation, quotation, and internal-review restrictions.
- Input: Existing local sample files and generated sample dependencies for `buyer_sales_sample`, including `data/buyers_raw_sample.csv`, `data/buyers_master_sample.csv`, `data/brands_master.csv`, `data/quotation_inputs_sample.csv`, generated sample outputs, and existing generator/validator scripts.
- Completed outputs:
  - `docs/integrated_runner_spec.md`
  - `docs/integrated_runner_workflow.md`
  - `automations/run_internal_workflow.py`
  - `tests/validate_integrated_runner.py`
  - `output/internal_workflow_summary.md`
  - `README.md`
- Supported workflow: `buyer_sales_sample`.
- Execution stages:
  - Privacy Guard validation
  - buyer lead validation
  - buyer scoring generation
  - buyer score validation
  - proposal message generation
  - proposal message validation
  - quotation generation
  - quotation validation
  - final run summary
- Output: Controlled workflow run summary at `output/internal_workflow_summary.md`, plus generated sample outputs refreshed by existing generators where applicable.
- Business rules: Integrated Runner orchestrates existing local scripts only and does not replace existing generators or validators. Privacy Guard runs first, and Privacy Guard failure blocks downstream generation. The full workflow remains internal-review only. The runner uses sample/internal-review data only, does not use `data/private/` or `output/private/` paths, does not create real data files, and does not directly modify source input CSV files. Generated sample outputs may be refreshed by existing generators.
- External data and sending restriction: Task 011 does not include a real data workflow, `data/private/` usage, dashboard, scraping, live web research, automatic search, APIs, browser automation, crawlers, buyer enrichment, credit checks, email sending, messaging automation, quotation sending, external sending, or external data collection.
- Validation method: Run `python tests/validate_privacy_guard.py`; run `python tests/validate_integrated_runner.py`; run `python automations/run_internal_workflow.py --workflow buyer_sales_sample --dry-run`; run `python automations/run_internal_workflow.py --workflow buyer_sales_sample --output-summary output/internal_workflow_summary.md`; run `python tests/validate_integrated_runner.py --check-summary --summary output/internal_workflow_summary.md`; run `python -m py_compile automations/run_internal_workflow.py tests/validate_integrated_runner.py`.
- Risks: Runner executes multiple scripts, so failure cause must be read from the summary. Generated sample output files may change during full run. XLSX output can be affected by file locks. Summary `PASS` does not mean external-ready proposal or quotation. Real/private workflow is not supported yet. Human review is still required before external use. Future dashboard or real-data runner requires separate design.
- Follow-up: Task 012 was later defined as Operations Dashboard to summarize the local sample/internal-review workflow after Task 011 Integrated Runner was in place.

## Task 012: Operations Dashboard

- Status: Completed pending final review.
- Goal: Summarize the local sample/internal-review buyer sales workflow status in a Markdown-only internal operations dashboard.
- Input: Existing Task 006-011 local sample/internal-review outputs, including `output/internal_workflow_summary.md`, `data/buyers_master_sample.csv`, `data/buyers_scored_sample.csv`, `data/proposal_messages_sample.csv`, `data/quotation_sample.csv`, and `data/brands_master.csv`.
- Completed outputs:
  - `docs/operations_dashboard_spec.md`
  - `docs/operations_dashboard_schema.md`
  - `automations/operations_dashboard/README.md`
  - `automations/operations_dashboard/generate_operations_dashboard.py`
  - `tests/validate_operations_dashboard.py`
  - `output/operations_dashboard.md`
  - `README.md`
- Primary output: `output/operations_dashboard.md`.
- Deferred outputs:
  - `output/operations_dashboard.xlsx`
  - `data/operations_dashboard_summary.csv`
- Output decision: Task 012 v1 is Markdown-only. XLSX dashboard output and CSV dashboard summary output are deferred until separately approved and validated.
- Dashboard summaries:
  - Integrated Runner status
  - buyer pipeline
  - buyer priority
  - approval and brand risk
  - proposal message status
  - quotation status
  - MOQ / price / stock / expiry issues
  - next actions
  - internal review items
  - risks and warnings
- Business rules: Dashboard is internal-review only and uses local sample/internal-review data only. It does not use `data/private`, `output/private`, or `output/final` paths. It must not display `contact_email`, `contact_phone`, `wechat_id`, `whatsapp`, `phone`, `email`, `private_note`, `real_contact`, `real_price`, `real_stock`, or `real_expiry`. `score_total` is only an internal prioritization signal. `approval_block` overrides `priority_tier` and `score_total`. `硫붾뵒?먮툕`/Medicube remains approval-required before external proposal. Proposal messages and quotations remain internal drafts. `PASS` does not mean final commercial approval.
- External data and sending restriction: Task 012 does not include a real data workflow, `data/private` usage, `output/private` usage, `output/final` usage, XLSX dashboard v1, CSV dashboard summary v1, scraping, live web research, automatic search, APIs, browser automation, crawlers, buyer enrichment, credit checks, email sending, messaging automation, quotation sending, external sending, or external data collection.
- Validation method: Run `python tests/validate_privacy_guard.py`; run `python tests/validate_operations_dashboard.py --skip-dashboard`; run `python automations/operations_dashboard/generate_operations_dashboard.py --output output/operations_dashboard.md`; run `python tests/validate_operations_dashboard.py --dashboard output/operations_dashboard.md`; run `python -m py_compile automations/operations_dashboard/generate_operations_dashboard.py tests/validate_operations_dashboard.py`. Current dashboard validation passes with a non-blocking warning that the `brands` row count is not directly printed in the dashboard body; v1 passes because brand risk and approval warnings are summarized.
- Risks: `output/operations_dashboard.md` is ignored generated output and may not be committed. Dashboard `PASS` can be misread as external-ready approval. Quotation `PASS` can be misread as final commercial approval. Approval-blocked and `硫붾뵒?먮툕` warning cases require manual review. Dashboard does not validate real buyer authenticity, creditworthiness, live price, stock, expiry, tax, shipping, duties, payment terms, or incoterms. Markdown-only v1 lacks spreadsheet filtering. Future XLSX/CSV outputs need separate privacy and validation design. Real/private workflow is not supported.
- Future work: Task 013 remains future discussion only. Do not define or start Task 013 in Task 012.

## Task 013: Real/private Operations Transition Preparation

- Status: Completed pending final review.
- Goal: Prepare planning documentation for a future real/private operating transition while keeping real buyer/contact/price/stock/expiry/final quotation data out of GitHub and preserving the current sample/internal-review workflow.
- Input: Existing Task 010 privacy guard policy, Task 011 Integrated Runner design, Task 012 Operations Dashboard design, and current sample/internal-review data handling rules.
- Completed outputs:
  - `docs/real_private_operations_transition_spec.md`
  - `docs/real_private_input_schema.md`
  - `docs/real_private_validation_checklist.md`
  - `docs/privacy_guard_enhancement_spec.md`
  - `docs/real_private_template_plan.md`
  - `docs/sample_to_real_mapping.md`
  - `docs/manual_approval_gate.md`
- Output: Documentation-only real/private transition plan covering transition scope, future real/private input schema, validation checklist, Privacy Guard enhancement requirements, ignored private template plan, sample-to-real mapping, and manual approval gate.
- Business rules: Task 013 is planning/documentation only. No real/private data was introduced. No private/final folders were created. No CSV/XLSX private templates were created. `.gitignore` was not modified. Privacy Guard remains the first safety gate. Real/private workflow is not enabled. Sample workflow and real/private workflow must remain separated. Future real/private files must stay local/private and must not be committed. `data/private/**`, `output/private/**`, and `output/final/**` are planned restricted paths only. `output/final/**` remains blocked until a separate final quotation process exists. Medicube remains approval-required. `approval_block` overrides `priority_tier` and `score_total`. `score_total` is not buyer authenticity, creditworthiness, or purchase probability. Price, stock, expiry, MOQ, payment, shipping, tax, duties, and incoterms require manual verification. Proposal and quotation outputs remain internal-review drafts unless manually approved. PASS from validators, runners, reports, or dashboards does not mean external approval.
- External data and sending restriction: Task 013 does not include real workflow code, final quotation workflow, external sending workflow, scraping, live web research, automatic search, APIs, browser automation, crawlers, buyer enrichment, credit checks, external data collection, email sending, messaging automation, quotation sending, or external sending.
- Real data creation restriction: Task 013 does not create real data files, `data/private/`, `output/private/`, `output/final/`, CSV templates, or XLSX templates.
- Validation method: Run `python tests/validate_privacy_guard.py`; confirm PASS with `warnings=0` and `failures=0`; confirm no real/private/final folders, templates, code changes, `.gitignore` changes, or Privacy Guard code changes were introduced.
- Risks: Real/private operations are not implemented yet. Future private folders must be ignored and verified before creation. Future Privacy Guard enhancement is still specification only. Future templates are planned but not created. Real buyer/contact/price/stock/expiry/final quotation data must never be committed. Manual approval gates must be enforced before external use. Final quotation process remains out of scope. Human review remains mandatory.
- Follow-up: Task 014 was later defined as Privacy Guard Enhancement Implementation after Task 013 final review.

## Task 014: Privacy Guard Enhancement Implementation

- Status: Completed pending final review.
- Goal: Strengthen Privacy Guard before any future real/private operation by improving restricted path detection, sensitive filename detection, strict content marker detection, false-positive prevention, output severity clarity, and synthetic validation.
- Input: Existing Privacy Guard validator, Task 013 real/private transition documents, `.gitignore` protections, current sample/internal-review files, and current generated output handling rules.
- Completed outputs:
  - `docs/privacy_guard_enhancement_implementation_plan.md`
  - `docs/privacy_guard_baseline_test_matrix.md`
  - `tests/validate_privacy_guard.py`
  - `README.md`
  - `docs/automation_roadmap.md`
  - `docs/task_log.md`
- Implemented components:
  - path-based restricted path blocker
  - sensitive filename blocker
  - strict data/output content marker checker
  - false-positive prevention for docs, validator code, and sample/internal-review placeholders
  - severity/output cleanup with PASS/WARNING/FAIL source labels
  - `--self-test` synthetic validation mode
- Business rules: Task 014 strengthens guardrails before real/private operations. It does not enable real/private workflow, final quotation workflow, external sending workflow, or any automatic data collection. Real/private data remains prohibited from Git. `data/private/`, `output/private/`, and `output/final/` remain restricted. Strict non-sample data/output files remain blocked for sensitive contact, commercial, final quotation, and external-ready markers. Sample/internal-review files remain allowed when placeholder-safe. Documentation and validator deny-lists may mention prohibited terms as policy or configuration.
- Task 014 did not create:
  - real data
  - `data/private/`
  - `output/private/`
  - `output/final/`
  - private CSV/XLSX templates
  - real/private workflow
  - final quotation workflow
  - external sending workflow
- External data and sending restriction: Task 014 does not include scraping, live web research, automatic search, APIs, browser automation, crawlers, buyer enrichment, credit checks, external data collection, email sending, messaging automation, quotation sending, or external sending.
- Validation method: Run `python -m py_compile tests/validate_privacy_guard.py`; run `python tests/validate_privacy_guard.py`; run `python tests/validate_privacy_guard.py --mode staged-only`; run `python tests/validate_privacy_guard.py --self-test`; run Integrated Runner and Operations Dashboard regression checks.
- Known validation note: `python tests/validate_privacy_guard.py` passes with one non-blocking warning because `output/operations_dashboard.md` exists locally as ignored generated output. This file was not regenerated by Task 014 Step H and should not be force-added unless explicitly approved.
- Risks: Privacy Guard is still a guardrail, not a complete DLP system. Ignored files can exist locally and require human discipline. A user could still try to force-add ignored private files, though staged/tracked blockers should detect them. Future real/private workflow, future final quotation process, and external sending remain out of scope until separately planned and approved.
- Future work: Task 015 remains future discussion only. Do not define or start Task 015 before Task 014 final review and commit/push.
