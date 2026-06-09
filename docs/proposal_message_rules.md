# Proposal Message Rules and Templates

## 1. Scope

This document defines the message selection rules, safety rules, brand approval handling, and template guidance for Task 008: Proposal Message Generator.

Proposal messages are internal-review drafts only. They are not approved external messages, sent messages, quotations, or final buyer-facing proposals.

Task 008 does not:

- send external messages
- automate email, DM, WeChat, WhatsApp, or platform communication
- collect buyer data externally
- enrich buyer data externally
- verify buyer authenticity
- verify payment ability or creditworthiness
- scrape, crawl, search, or perform live web research
- use APIs, browser automation, requests, crawlers, buyer enrichment, credit checks, or external data collection

The generator must only use local buyer lead data, local buyer scoring results, local brand approval rules, and manually provided business context.

## 2. Input Interpretation Rules

| Input field | How to use it | Safety rule |
|---|---|---|
| `country` | Use for internal context, China workflow caution, and localization review needs. | Do not infer market facts or buyer quality from country alone. |
| `language` | Select draft language: Chinese, Korean, or English. | Unsupported or unknown languages should default to English and require localization review. |
| `interested_brands` | Starting point for possible brand discussion. | Must be filtered through brand approval rules before recommendation. |
| `interested_categories` | Use for category-level message direction when brand recommendation is limited or unsafe. | Do not make unsupported product efficacy claims. |
| `estimated_order_qty` | Use to decide whether MOQ confirmation is needed. | Treat as manually provided estimate, not confirmed purchase volume. |
| `moq_fit` | Use for message status and next action. | `no` or `unknown` should prevent strong proposal language. |
| `lead_status` | Use to choose message type, such as first contact or follow-up. | Do not imply buyer engagement beyond local input data. |
| `priority_tier` | Use as internal follow-up priority. | Never mention score or tier in buyer-facing message body. |
| `approval_block` | Controls whether buyer-facing proposal copy is allowed. | `true` must block buyer-facing proposal copy. |
| `risk_flags` | Use to populate compliance notes and internal review needs. | Risk flags are cautions, not external verification results. |
| `proposal_brand_check` | Controls brand approval readiness. | `approval_required_review` must block external brand proposal copy. |
| `payment_risk` | Use to require payment risk review when high or uncertain. | Payment risk is manually entered and is not credit verification. |
| `recommended_next_action` | Use as source guidance for internal next action. | Next action must not trigger external sending automatically. |

## 3. Brand Recommendation Rules

- Recommend only brands where `proposal_allowed=true` and `approval_required=false`.
- Exclude brands where `approval_required=true` or `proposal_allowed=false`.
- `메디큐브` must be excluded unless explicit approval is recorded.
- If buyer `interested_brands` includes approval-required brands, place those brands in `excluded_brands` and `compliance_notes`.
- Never let `priority_tier=A`, high `score_total`, or strong commercial fit override `approval_block`.
- Do not invent brand availability, official English brand names, stock status, distribution rights, or proposal eligibility.
- If the safe brand list is unclear, use category-level discussion only.

## 4. Blocked Row Rules

If `approval_block=true` or `proposal_brand_check=approval_required_review`:

- `message_status` must be `blocked_approval_required`.
- `message_type` must be `approval_review_required`.
- `message_body` must not contain buyer-facing proposal copy.
- `message_body` should contain internal approval guidance only.
- `recommended_brands` should be blank, unless clearly approved alternatives are available and safe.
- `excluded_brands` must include the blocked brand.
- `required_internal_review` must be `true`.
- `next_action` must require internal approval review before any external action.

Blocked rows may still be commercially interesting, but the output must not make the restricted brand externally proposal-ready.

## 5. MOQ and Delivery Wording Rules

- MOQ is generally 100+ units.
- Delivery lead time is generally 20-30 days.
- These terms must be phrased as general business terms, not guaranteed final terms.
- If `moq_fit=no`, do not push a proposal. The internal next action should confirm whether the buyer can increase quantity or combine categories to meet MOQ 100+.
- If `moq_fit=unknown`, `message_status` should be `needs_moq_confirmation` unless another stronger block applies.
- Do not state that estimated quantity is a confirmed order.
- Do not promise final delivery timing, product availability, or shipping conditions without verified business confirmation.

## 6. Payment Risk Rules

- `payment_risk` is manually entered and is not credit verification.
- If `payment_risk=high`, `message_status` should be `needs_payment_risk_review`.
- Do not imply payment ability, financial reliability, or creditworthiness was verified.
- Include internal caution in `compliance_notes` when payment risk is `high`, `medium`, `unknown`, or blank.
- High payment risk may require safer payment terms or management review before external communication.

## 7. Buyer Score Usage Rules

- `score_total` and `priority_tier` are internal follow-up signals only.
- Do not mention `score_total` in buyer-facing `message_body`.
- Do not state that a buyer is verified, qualified, financially reliable, creditworthy, or likely to purchase based only on score.
- High score may influence internal `next_action`, but must not override approval, MOQ, payment, privacy, claim, or localization restrictions.
- `priority_tier=Hold` should normally produce internal guidance, low-pressure nurture, MOQ confirmation, payment review, or approval review direction.

## 8. Claim and Compliance Rules

The generator must not invent or include unsupported:

- price
- stock
- inventory
- expiry date
- official certification
- exclusive distribution rights
- clinical claims
- dermatological claims
- medical claims
- before/after claims
- guaranteed results
- sales rankings
- platform performance metrics
- sales volume
- engagement rates

Cosmetic efficacy, functional, clinical, dermatology, medical, or before/after claims must be omitted unless manually provided and verified. If such claims are needed later, mark them for internal compliance review before external use.

## 9. Privacy Rules

- Do not include `contact_email`, `contact_phone`, `wechat_id`, or `whatsapp` in output by default.
- Do not expose buyer contact information in public or external-facing outputs.
- Real buyer contact data is internal-use only.
- Future sending workflows require separate explicit approval and separate implementation.
- Contact completeness may guide internal readiness, but must not be described as buyer quality or buyer verification.

## 10. Language Rules

Language selection:

| Buyer language | Draft language |
|---|---|
| `Chinese` | Chinese draft |
| `Korean` | Korean draft |
| `English` | English draft |
| `unknown`, `other`, or unsupported language | English draft by default |

All outputs must include Korean internal review notes.

Style rules:

- Use conservative, professional B2B wholesale/export tone.
- Avoid exaggerated claims.
- Avoid pressure-selling.
- Avoid unsupported urgency.
- Use localization review for Chinese or any non-Korean context before external use.
- Do not guess official localized brand names.

## 11. Message Templates

### A. `first_contact`

| Item | Guidance |
|---|---|
| When to use | Buyer is usually `A` or `B` tier, `approval_block=false`, and MOQ appears fit or confirmable. |
| Required conditions | No approval block; safe brands or safe categories exist; message remains internal-review draft. |
| Prohibited content | Price, stock, guaranteed availability, official certification, exclusive rights, unsupported claims, buyer score. |
| Example subject/opening | `Internal review draft: K-beauty category supply introduction` |
| Example body outline | Internal-review disclaimer; brief company/category introduction; mention safe brand/category discussion; ask to confirm interested categories and order quantity; note general MOQ 100+ and delivery lead time 20-30 days as subject to confirmation. |
| Required compliance notes | Internal review only; price/stock not verified; brand approval check required before sending; localization review if non-Korean. |

### B. `follow_up`

| Item | Guidance |
|---|---|
| When to use | `lead_status` is `contacted`, `replied`, or `qualified`, and `approval_block=false`. |
| Required conditions | Existing local input shows follow-up context; no blocked brand proposal. |
| Prohibited content | Claims that the buyer is verified, price promises, stock promises, unsupported urgency. |
| Example subject/opening | `Following up on K-beauty product category interest` |
| Example body outline | Internal-review disclaimer; refer cautiously to prior category interest from local records; ask for preferred product category, target quantity, and next discussion point; keep brand mentions limited to approved brands. |
| Required compliance notes | Confirm source context; verify MOQ; verify brand approval; review localization before external use. |

### C. `quotation_intro`

| Item | Guidance |
|---|---|
| When to use | MOQ appears fit, `approval_block=false`, and internal team is ready to review quotation preparation. |
| Required conditions | `moq_fit=yes`; no approval-required brand in recommendation; no high payment risk block. |
| Prohibited content | Actual price, final stock, expiry date, final delivery term, final quotation, exclusive rights, guaranteed availability unless verified. |
| Example subject/opening | `Quotation preparation review for approved K-beauty items` |
| Example body outline | Internal-review disclaimer; explain that quotation can be prepared after confirming product, quantity, availability, and business terms; mention MOQ/delivery only as general terms subject to final confirmation. |
| Required compliance notes | Price/stock/expiry not verified; final terms require manual confirmation; approval-required brands excluded unless approved. |

### D. `product_category_intro`

| Item | Guidance |
|---|---|
| When to use | Buyer has category interest, but brand recommendation is limited, unsafe, or not yet approved. |
| Required conditions | Category interest exists; no unsupported claims; restricted brands excluded. |
| Prohibited content | Restricted brand recommendation, medical/clinical/functional claims, fake rankings, fake platform performance. |
| Example subject/opening | `K-beauty skincare category discussion draft` |
| Example body outline | Internal-review disclaimer; discuss categories such as skincare, toner, serum, sunscreen, or derma in broad business terms; ask buyer to confirm target category, quantity, and market channel. |
| Required compliance notes | Category-level discussion only; brand approval check required before brand proposal; cosmetic claims require review. |

### E. `approval_review_required`

| Item | Guidance |
|---|---|
| When to use | `approval_block=true` or `proposal_brand_check=approval_required_review`. |
| Required conditions | Blocked brand appears or approval restriction is active. |
| Prohibited content | Buyer-facing proposal copy, quotation copy, public content, ad copy, or external pitch for the blocked brand. |
| Example subject/opening | `Internal approval review required before proposal` |
| Example body outline | Internal guidance only; identify excluded brand; state that external proposal, buyer-facing pitch, quotation, public content, or ad copy must not proceed before explicit approval; suggest approved alternatives only if safely available. |
| Required compliance notes | Approval-required brand detected; internal review required; no external sending; 메디큐브 excluded unless explicit approval is recorded. |

### F. `low_priority_nurture`

| Item | Guidance |
|---|---|
| When to use | Buyer is `C` or `Hold` without approval block, or immediate proposal is not appropriate. |
| Required conditions | No approval block for the suggested content; message stays low-pressure and internal. |
| Prohibited content | Aggressive proposal, quotation pressure, unsupported urgency, score disclosure, guaranteed terms. |
| Example subject/opening | `Internal draft: light follow-up for future K-beauty category discussion` |
| Example body outline | Internal-review disclaimer; ask one or two clarifying questions about category, quantity, or channel; keep tone gentle and non-committal. |
| Required compliance notes | Internal planning only; MOQ/payment/source limitations should be reviewed before stronger proposal. |

## 12. Recommended Brand Selection Logic

1. Start from `interested_brands`.
2. Check each brand against local brand approval reference, such as `data/brands_master.csv`.
3. Remove brands where `approval_required=true` or `proposal_allowed=false`.
4. Always remove `메디큐브` unless explicit approval is recorded.
5. Put removed approval-required or proposal-blocked brands into `excluded_brands`.
6. If no safe brand remains, recommend category-level discussion only.
7. Do not substitute unrelated brands without a clear internal reason.
8. If suggesting alternatives, mark them as internal suggestions only.
9. Do not invent brand availability or official English brand names.

## 13. Required Internal Review Rules

`required_internal_review` must be `true` when:

- `approval_block=true`
- `message_status` is not `draft_ready_for_internal_review`
- buyer language is Chinese
- buyer language is unsupported and localization-sensitive
- `payment_risk` is `high` or `unknown`
- `moq_fit` is `no` or `unknown`
- `compliance_notes` mention claim verification
- `compliance_notes` mention price, stock, inventory, expiry, or availability verification
- `compliance_notes` mention approval verification
- `recommended_brands` is blank because of restrictions
- output may be used beyond internal planning

Even when `required_internal_review=false` in a future output, external sending still requires human review and approval outside Task 008.

## 14. Output Safety Rules

Every generated output must include:

- `내부 검토용 초안`
- compliance notes
- next action
- required internal review status
- a statement that no automatic sending is performed

Generated output must not imply:

- an email was sent
- a WeChat or WhatsApp message was sent
- an external proposal was approved
- buyer data was externally verified
- price, stock, certification, or claims were verified

## 15. Validation Requirements

Future generated messages must be validated for:

- required fields from `docs/proposal_message_schema.md`
- allowed `message_status` values
- allowed `message_type` values
- blocked rows have no buyer-facing proposal copy
- `메디큐브` is not in `recommended_brands` without explicit approval
- approval-required or proposal-blocked brands are excluded
- no fake price, stock, certification, exclusive rights, medical claims, clinical claims, functional claims, rankings, platform performance claims, engagement claims, or sales claims
- no unnecessary personal contact data
- internal review disclaimer is present
- no email sending, messaging automation, or external sending workflow is implied
- no scraping, live web research, automatic web search, APIs, browser automation, crawlers, buyer enrichment, credit checks, or external data collection is implied
- Korean, English, and Chinese text is preserved
- MOQ and delivery lead time are framed as general business terms only
- buyer score is not described as buyer authenticity, creditworthiness, payment ability, or purchase probability

## Step C Scope

This rules and templates document does not create or modify code, CSV files, Markdown output files, XLSX files, generated reports, email sending workflows, messaging automation, scraping workflows, live web research workflows, automatic web search, APIs, browser automation, crawlers, buyer enrichment, credit checks, or external data collection.
