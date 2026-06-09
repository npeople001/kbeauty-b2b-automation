# Proposal Message Generator Specification

## 1. Scope

### What Task 008 Does

Task 008 defines a local Proposal Message Generator for the K-beauty B2B export business.

The generator will use local, manually provided buyer lead data, buyer scoring results, and local brand approval rules to create internal-review draft proposal messages for overseas buyers.

The intended users are internal sales or business operators who need cautious message drafts before deciding whether to contact a buyer.

Task 008 only generates internal-review draft proposal messages. Generated messages are not final external communications.

### What Task 008 Does Not Do

Task 008 must not:

- send emails
- send DMs
- send WeChat messages
- send WhatsApp messages
- send any external communication
- implement email sending
- implement messaging automation
- scrape buyer data
- perform live web research
- perform automatic web search
- call APIs
- use browser automation
- crawl websites or platforms
- use requests or external network collection
- enrich buyer profiles from external sources
- verify whether a buyer is real
- run credit checks
- verify payment ability
- verify purchase probability
- collect buyer data from external sources

Task 008 must only read local files and generate internal draft outputs for review.

The generated draft must clearly state that it is for internal review only and must not be sent externally without human review.

## 2. Input Files

### Required Inputs

| File | Purpose | Encoding |
| --- | --- | --- |
| `data/buyers_master_sample.csv` | Local buyer master sample file created from manually provided buyer data. | `utf-8-sig` |
| `data/buyers_scored_sample.csv` | Local buyer scoring output with internal priority, risk flags, and approval block fields. | `utf-8-sig` |
| `data/brands_master.csv` | Local brand approval reference for `approval_required` and `proposal_allowed` rules. | `utf-8-sig` |

### Optional Future Inputs

| File or Material | Purpose | Rule |
| --- | --- | --- |
| `data/buyers_master.csv` | Future real buyer master input. | Internal-use only. |
| `data/buyers_scored.csv` | Future real scored buyer input. | Internal-use only. |
| manually provided product notes | Product/category context for message drafts. | Must be manually provided and verified. |
| manually provided stock/price/MOQ notes | Optional business terms for future drafts. | Must not be invented. |
| manually approved brand list | Explicit approval reference for restricted brands. | Must be provided before recommending approval-required brands externally. |

Optional future inputs must remain local and manually provided. They must not trigger scraping, live research, automatic search, APIs, enrichment, or external collection.

## 3. Output Files

### Recommended Output

| File | Purpose | Encoding |
| --- | --- | --- |
| `output/proposal_messages_sample.md` | Internal-review Markdown draft messages for sample buyer leads. | UTF-8 |

### Optional Future Outputs

| File | Purpose | Encoding |
| --- | --- | --- |
| `data/proposal_messages_sample.csv` | Structured proposal message output for validation or spreadsheet review. | `utf-8-sig` |
| `output/proposal_messages_sample.xlsx` | Business-facing workbook for internal review. | XLSX |

Generated outputs are internal drafts only. They must not be treated as sent messages, approved proposals, quotations, or final buyer-facing copy.

## 4. Recommended Output Fields

| Field | Meaning | Required | Format | Example | Notes |
| --- | --- | ---: | --- | --- | --- |
| `message_id` | Stable ID for the generated draft message. | Required | Text, recommended `MSG-0001`. | `MSG-0001` | Must be unique within the output. |
| `buyer_id` | Buyer ID from input buyer master/scored files. | Required | Existing buyer ID. | `BUYER-0001` | Must match local input data. |
| `company_name` | Buyer company name from local buyer master data. | Required | UTF-8 text. | `Shanghai Sample Beauty Trade` | Must not be invented. |
| `country` | Buyer country from local buyer master data. | Required | UTF-8 text. | `China` | Used for language and market context only. |
| `language` | Draft message language. | Required | Controlled text. | `Chinese` | Based on buyer `language` field. |
| `priority_tier` | Internal priority tier from buyer scoring output. | Required | `A`, `B`, `C`, `Hold` | `A` | Must not be described as purchase probability. |
| `approval_block` | Whether approval rules block buyer-facing proposal readiness. | Required | `true` or `false` | `true` | If `true`, do not generate buyer-facing proposal copy. |
| `message_status` | Status of the draft message. | Required | Allowed value. | `draft_ready_for_internal_review` | See Message Status Rules. |
| `message_type` | Type of message draft or internal guidance. | Required | Allowed value. | `first_contact` | See Message Type Rules. |
| `subject_or_opening` | Subject line or opening phrase for the draft. | Required | UTF-8 text. | `K-beauty supply proposal for internal review` | Must be conservative. |
| `message_body` | Draft message body or internal guidance. | Required | UTF-8 text. | `This is an internal-review draft...` | Must not include unsupported claims. |
| `recommended_brands` | Brands allowed to appear in draft recommendation. | Required | Semicolon-separated UTF-8 text or blank. | `아누아; 토리든` | Only brands with `proposal_allowed=true` unless explicit approval exists. |
| `excluded_brands` | Brands excluded due to approval or proposal rules. | Required | Semicolon-separated UTF-8 text or blank. | `메디큐브` | Approval-required brands should appear here when blocked. |
| `compliance_notes` | Internal compliance and evidence notes. | Required | UTF-8 text. | `가격, 재고, 효능 표현은 검증 필요.` | Must include review needs. |
| `required_internal_review` | Internal review needed before external use. | Required | Semicolon-separated text. | `brand_approval; localization_review` | Must include relevant checks. |
| `next_action` | Practical internal next action. | Required | UTF-8 text. | `Confirm MOQ and prepare approved brand list.` | Must not trigger sending. |
| `generated_at` | Date generated. | Required | ISO date `YYYY-MM-DD`. | `2026-06-08` | Local generation date. |

## 5. Message Status Rules

Allowed `message_status` values:

- `draft_ready_for_internal_review`
- `blocked_approval_required`
- `needs_more_buyer_info`
- `needs_moq_confirmation`
- `needs_payment_risk_review`

Rules:

- `approval_block=true` must result in `blocked_approval_required` or internal approval guidance only.
- `moq_fit=no` or `moq_fit=unknown` should result in `needs_moq_confirmation` unless the output is only an internal follow-up note.
- `payment_risk=high` should result in `needs_payment_risk_review`.
- Missing buyer information should result in `needs_more_buyer_info`.
- `draft_ready_for_internal_review` does not mean the message is approved to send.
- All statuses remain internal workflow labels only.

## 6. Message Type Rules

Allowed `message_type` values:

- `first_contact`
- `follow_up`
- `quotation_intro`
- `product_category_intro`
- `approval_review_required`
- `low_priority_nurture`

Rules:

- `approval_block=true` must use `approval_review_required`.
- Low-priority or `Hold` buyers should not receive aggressive proposal drafts.
- `quotation_intro` must not include invented price, stock, expiry date, certification, exclusive rights, contract terms, or guaranteed availability.
- `first_contact` and `follow_up` must remain conservative and should mention that the draft requires internal review.
- `product_category_intro` may describe broad categories, but must not make cosmetic efficacy, medical, clinical, dermatological, or functional claims unless provided and verified.

## 7. Brand Approval Rules

The generator must use `data/brands_master.csv` as the approval reference where available.

Rules:

- Brands where `proposal_allowed=false` must not be recommended externally.
- Brands where `approval_required=true` must not be recommended externally unless explicit approval is recorded.
- `메디큐브` must remain approval-required unless explicit approval is provided.
- If `interested_brands` includes `메디큐브`, it may appear only in `excluded_brands` or internal approval notes unless explicit approval exists.
- `approval_block=true` must prevent buyer-facing proposal copy.
- A high buyer score must not override `approval_block`.
- Official English brand names must not be guessed when `brand_en` is blank.
- Approval-required brands may be recorded as buyer interest, but must not be presented as proposal-ready.

## 8. Message Generation Rules

All messages are drafts for internal review only.

Rules:

- Do not send messages externally.
- Do not include unnecessary personal contact data.
- Do not include price, stock, inventory, expiry date, official certification, exclusivity, contract terms, or guaranteed availability unless provided and verified.
- Do not make cosmetic efficacy, medical, clinical, dermatological, or functional claims unless provided and verified.
- Do not claim buyer-specific fit as fact if based only on scoring.
- Do not claim that buyer scoring proves authenticity, creditworthiness, payment ability, or purchase probability.
- Use conservative, professional B2B language.
- Mention MOQ 100+ and delivery lead time 20-30 days only as general business terms.
- Include review notes where verification is needed.
- Include an internal review disclaimer in every generated output.
- If evidence is insufficient, the draft must say that verification is needed.

## 9. Language Rules

Language selection should use the buyer master `language` field.

Rules:

- If buyer language is `Chinese`, generate Chinese draft text.
- If buyer language is `Korean`, generate Korean draft text.
- If buyer language is `English`, `unknown`, `other`, or any unsupported value, generate English draft text by default.
- For languages such as `Russian`, `Vietnamese`, or `Thai`, generate English draft text by default until reviewed local-language templates exist.
- All outputs must include Korean internal review notes.
- Chinese, English, and Korean drafts must remain conservative and avoid unsupported claims.
- Localization and translation review should be listed in `required_internal_review` when the draft is not in Korean.

## 10. Privacy and Contact Rules

Buyer contact fields are privacy-sensitive.

Contact fields include:

- `contact_name`
- `contact_email`
- `contact_phone`
- `wechat_id`
- `whatsapp`
- `website`
- `sns_url`

Rules:

- Proposal outputs should not include `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp` by default.
- Real buyer contact data should remain internal-use only.
- Do not expose personal contact data in public or external outputs.
- Any future sending workflow must require separate explicit approval and must be outside Task 008.
- Contact completeness may guide internal readiness, but must not be described as buyer quality.

## 11. MOQ and Delivery Rules

Business terms:

- MOQ is generally 100+ units.
- Delivery lead time is generally 20-30 days.

Rules:

- These terms must be phrased as general conditions, not guaranteed final terms.
- If `moq_fit=no`, the message should request quantity increase, category bundling, or MOQ confirmation rather than pushing a proposal.
- If `moq_fit=unknown`, the message should request estimated order quantity confirmation before proposal.
- Delivery lead time must not be framed as guaranteed for all products or all orders.
- Future price, stock, product availability, and shipping conditions require manual verification.

## 12. Risk and Compliance Rules

The generator must flag:

- approval-required brand risk
- MOQ uncertainty
- payment risk
- `buyer_unverified` limitation
- `source_manual_only` limitation
- cosmetics claim risk
- localization or translation review need
- price and stock verification need
- brand approval review need
- privacy/contact review need when real buyer data is used

Risk flags should appear in `compliance_notes` or `required_internal_review` where relevant.

## 13. Validation Requirements

Generated proposal messages must be validated for:

- required output fields
- `buyer_id` matching input data
- row/message count matching the intended buyer input set
- allowed `message_status` values
- allowed `message_type` values
- `approval_block=true` rows do not contain buyer-facing proposal body
- `메디큐브` is not in `recommended_brands` unless explicit approval exists
- `proposal_allowed=false` brands are not recommended
- approval-required brands appear only in `excluded_brands` or internal approval notes unless explicit approval exists
- no fake price, stock, inventory, expiry date, certification, exclusive rights, contract terms, or efficacy claims
- no email sending or messaging automation code
- no scraping, live web research, automatic web search, APIs, browser automation, crawlers, buyer enrichment, credit checks, or external data collection code
- no unnecessary contact data exposure
- Korean, English, and Chinese text preservation
- internal review disclaimer present
- MOQ and delivery terms are phrased as general conditions
- buyer scoring is not described as buyer authenticity, creditworthiness, payment ability, or purchase probability

## 14. Completion Criteria

Task 008 is complete only when:

- specification exists
- proposal message schema exists
- proposal message rules/template document exists
- generator exists
- sample proposal messages are generated
- validation script exists and passes
- README/workflow documentation exists
- roadmap and task log are updated
- final review passes

Task 008 is not complete if it sends messages externally, adds email/messaging automation, performs external data collection, recommends approval-required brands without explicit approval, or generates unsupported price, stock, certification, exclusivity, or cosmetic claim content.
