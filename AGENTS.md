# AGENTS.md

This repository builds automation tools for a K-beauty B2B export business.

## Required Workflow

For every non-trivial task, future agents must:

1. Understand the business goal before changing code.
2. Inspect only the relevant parts of the codebase.
3. Summarize current codebase findings.
4. Propose a step-by-step implementation plan.
5. Review whether the plan is complete, minimal, safe, and testable.
6. Identify missing steps, risks, and dependencies.
7. Implement one step at a time.
8. After each step, run relevant validation.
9. Do not proceed to the next step if validation fails.
10. Report changes, validation results, remaining risks, and the next step.

## Token Efficiency Rules

- Do not read the whole codebase unless necessary.
- Inspect folder structure and dependency manifests first.
- Use targeted search before opening large files.
- Prefer dependency graph, call graph, code-review-graph, grep, or symbol search when available.
- Use RTK or equivalent output compression when available.
- Avoid pasting full logs or full files.
- Summarize command outputs and failures.
- Read only relevant functions, classes, and modules.

## Business Rules

- Source Korean cosmetics brands through domestic distributors and sell them to overseas buyers.
- MOQ is generally 100 units or more.
- Delivery lead time is generally 20-30 days.
- Priority markets are China, Southeast Asia, Russia, and later global buyers.
- Primary goals are overseas marketing, China buyer channel development, and profit growth.
- Buyer type is flexible if the buyer can order 100+ units.
- Some brands require approval before external proposal.
- Approval-required brands must not be included in external proposal outputs unless explicitly approved.
- Korean, English, and Chinese text must be supported with UTF-8 encoding.
- All CSV files intended for Excel or business users must be written with UTF-8 with BOM, using utf-8-sig.
- Scripts must read CSV files using an encoding compatible with utf-8-sig.
- XLSX is preferred for business-facing outputs when Korean, English, or Chinese text is included.
- When generating XLSX files, if the target output file is locked or cannot be overwritten, create a timestamped fallback output file.
- Do not modify source CSV files to resolve output permission issues.
- Clearly report the actual output path generated.
- Korean brand names must be validated after CSV/XLSX generation.
- Do not report encoding-related tasks as complete until Korean text is verified.
- Business master data must not be changed casually.
- Brand names, approval rules, MOQ, delivery lead time, buyer rules, and proposal eligibility are business-critical data.
- If a task requires changing business data, first explain the reason and request confirmation.
- Scripts may transform data into outputs, but must not silently alter source data.
- Never guess official English brand names.
- Never change approval_required or proposal_allowed rules without explicit instruction.
- Always preserve row count unless the task explicitly asks to add or remove records.

## Available Brands

- 라곰
- k-secret
- 메디큐브: requires director approval before external posting/proposal
- vt
- 에이프릴스킨
- 토리든
- 바이오던스
- 쥬스투클렌즈
- 리쥬란
- 바이브랩
- 테라로직
- GIK
- 올리브영PB 제품
- 3CE
- 뷰티드라마
- 아비브
- 스킨1004
- 345크림/닥터엘시아
- 넘버즈인
- NEEDLY
- 토코보
- 디오디너리
- 가히
- 라운드랩
- 앰플엔
- 에스네이처
- 쏘내추럴
- 그레이멜린
- 아누아
- 아렌시아
- 아토팜
- 클라뷰
- 리브이셀
- 아로셀
- 마미케어
- 아로마티카
- 조선미녀
- 셀리맥스
- 낫씨백
- 네이처리퍼블릭
- 더마픽스
- 웰라쥬
- 미미박스
- CLIO
- 벨라
- 결콜라겐
- 락토핏
- 비타민마을
- 뉴트리디데이
- 네추럴라이즈
