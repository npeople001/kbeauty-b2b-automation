"""Generate a local market research report from structured inputs.

This script reads only local CSV and Markdown files. It does not perform
scraping, live web research, browser automation, API calls, or external data
collection.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_REPORT_SECTIONS = [
    "Research Brief",
    "Market Overview",
    "Channel Analysis",
    "Competitor and Content Analysis",
    "Product/Brand Fit",
    "B2B Buyer Acquisition Angle",
    "Content Strategy",
    "Short-form Video Plan",
    "Feed Post Plan",
    "Execution Plan",
    "Risks and Compliance",
    "Final Recommendation",
]

REQUIRED_INPUT_COLUMNS = [
    "research_id",
    "target_country",
    "target_channels",
    "target_brands",
    "target_product_categories",
    "research_objective",
    "b2b_or_b2c_focus",
    "available_brand_list",
    "restricted_or_approval_required_brands",
    "campaign_objective",
    "available_assets",
    "budget_level",
    "execution_period",
    "source_materials",
    "date",
    "notes",
]

SOURCE_COLUMNS = [
    "source_id",
    "research_id",
    "source_type",
    "source_title",
    "source_description",
    "provided_by",
    "date_collected",
    "reliability_level",
    "verification_status",
    "notes",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def read_business_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        fail(f"input CSV not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            fail(f"input CSV has no header row: {path}")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def validate_input_columns(rows: list[dict[str, str]], path: Path) -> None:
    if not rows:
        fail(f"input CSV has no data rows: {path}")

    missing = [column for column in REQUIRED_INPUT_COLUMNS if column not in rows[0]]
    if missing:
        fail(f"input CSV missing required columns: {', '.join(missing)}")


def select_research_row(rows: list[dict[str, str]], research_id: str) -> dict[str, str]:
    for row in rows:
        if row.get("research_id") == research_id:
            return row
    fail(f"research_id not found in input CSV: {research_id}")


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def read_source_notes(path: Path, warnings: list[str]) -> str:
    if not path.exists():
        warnings.append("source_notes.md 없음: 소스 자료 부족")
        return ""

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        warnings.append("source_notes.md 비어 있음: 소스 자료 부족")
    return text


def read_sources_csv(path: Path, research_id: str, warnings: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        warnings.append("sources.csv 없음: 소스 자료 부족")
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            warnings.append("sources.csv 헤더 없음: 소스 자료 부족")
            return []
        missing_columns = [column for column in SOURCE_COLUMNS if column not in reader.fieldnames]
        if missing_columns:
            warnings.append(f"sources.csv 필수 컬럼 누락: {', '.join(missing_columns)}")
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]

    filtered_rows = [row for row in rows if row.get("research_id") == research_id]
    if not filtered_rows:
        warnings.append("sources.csv에 해당 research_id 자료 없음: 소스 자료 부족")
    return filtered_rows


def load_source_materials(source_root: Path, research_id: str) -> dict[str, object]:
    warnings: list[str] = []
    source_dir = source_root / research_id

    if not source_dir.exists():
        warnings.append(f"소스 폴더 없음: {source_dir}")
        return {
            "source_dir": source_dir,
            "source_notes": "",
            "sources": [],
            "warnings": warnings,
            "is_sufficient": False,
        }

    source_notes = read_source_notes(source_dir / "source_notes.md", warnings)
    sources = read_sources_csv(source_dir / "sources.csv", research_id, warnings)

    if not source_notes and not sources:
        warnings.append("사용 가능한 소스 자료 없음: 소스 자료 부족")

    needs_review_count = sum(1 for source in sources if source.get("verification_status") == "needs_review")
    unverified_count = sum(1 for source in sources if source.get("verification_status") == "unverified")
    verified_count = sum(1 for source in sources if source.get("verification_status") == "verified")

    placeholder_signals = ["placeholder", "가정", "검증 필요", "소스 자료", "controlled sample"]
    has_placeholder_signal = any(signal in source_notes.lower() for signal in placeholder_signals)
    is_sufficient = bool(source_notes and sources and verified_count > 0 and not warnings and not has_placeholder_signal)

    if sources and verified_count == 0:
        warnings.append("verified 상태의 소스 없음: 확정 불가")
    if needs_review_count or unverified_count:
        warnings.append("검토 필요 또는 미검증 소스 포함: 검증 필요")
    if has_placeholder_signal:
        warnings.append("소스 노트에 가정/검증 필요 표시가 있어 확정 자료로 사용할 수 없음")

    return {
        "source_dir": source_dir,
        "source_notes": source_notes,
        "sources": sources,
        "warnings": warnings,
        "is_sufficient": is_sufficient,
    }


def is_china_target(target_country: str) -> bool:
    normalized = target_country.strip().lower()
    return "china" in normalized or "중국" in normalized


def normalize_restricted_brands(row: dict[str, str]) -> list[str]:
    restricted = split_values(row.get("restricted_or_approval_required_brands", ""))
    if "메디큐브" not in restricted:
        restricted.append("메디큐브")
    return restricted


def markdown_list(items: list[str], fallback: str = "검증 필요") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def source_summary_table(sources: list[dict[str, str]]) -> str:
    if not sources:
        return "| source_id | source_type | verification_status | notes |\n|---|---|---|---|\n| 검증 필요 | 소스 자료 부족 | 확정 불가 | sources.csv 자료 없음 또는 비어 있음 |"

    lines = ["| source_id | source_type | verification_status | notes |", "|---|---|---|---|"]
    for source in sources:
        note_summary = "사용자 제공 소스 메타데이터 있음"
        if source.get("verification_status") != "verified":
            note_summary = "사용자 제공 소스이나 검증 필요"
        lines.append(
            "| {source_id} | {source_type} | {verification_status} | {notes} |".format(
                source_id=source.get("source_id") or "확정 불가",
                source_type=source.get("source_type") or "확정 불가",
                verification_status=source.get("verification_status") or "검증 필요",
                notes=note_summary,
            )
        )
    return "\n".join(lines)


def recommendation_level_text(budget_level: str) -> str:
    if budget_level.lower() == "low":
        return "소규모 테스트 중심"
    if budget_level.lower() == "medium":
        return "제한적 확장 테스트"
    if budget_level.lower() == "high":
        return "확장 운영 가능"
    return "예산 수준 검증 필요"


def build_channel_rows(channels: list[str], china_target: bool) -> str:
    if not channels:
        return "| channel_name | channel_type | user_profile | b2b_usefulness | b2c_usefulness | restrictions_or_risks | recommended_usage |\n|---|---|---|---|---|---|---|\n| 검증 필요 | 검증 필요 | 소스 자료 부족 | 확정 불가 | 확정 불가 | 검증 필요 | 소스 자료 확보 후 판단 |"

    rows = ["| channel_name | channel_type | user_profile | b2b_usefulness | b2c_usefulness | restrictions_or_risks | recommended_usage |", "|---|---|---|---|---|---|---|"]
    for channel in channels:
        if china_target:
            risk = "플랫폼 정책, 계정 운영, 실명/인증, 현지화 리스크 검토 필요"
        else:
            risk = "플랫폼 정책 및 현지화 리스크 검토 필요"
        rows.append(
            f"| {channel} | 검증 필요 | 소스 자료 기반 확인 필요 | 바이어 신뢰 형성/문의 유도 가능성은 검증 필요 | 소비자 반응 관찰 가능성은 검증 필요 | {risk} | 검증된 자료 확보 전에는 낮은 비용의 테스트 운영 권장 |"
        )
    return "\n".join(rows)


def build_recommendation_rows(channels: list[str], products: list[str], budget_level: str) -> str:
    if not channels:
        channels = ["검증 필요"]
    topic = ", ".join(products[:2]) if products else "제품군 검증 필요"
    rows = ["| channel | content_goal | content_angle | post_type | upload_frequency | execution_difficulty | expected_effect | cost_level | risk_level | risk |", "|---|---|---|---|---|---|---|---|---|---|"]
    for channel in channels:
        rows.append(
            f"| {channel} | 바이어 문의 유도와 소비자 반응 관찰 분리 | {topic} 중심의 제품 이해 콘텐츠 | 숏폼/피드 테스트 | 주 1-2회 가정, 실제 운영 가능성 검증 필요 | 낮음-중간 | 초기 반응 확인 가능, 확정 효과는 검증 필요 | {recommendation_level_text(budget_level)} | 중간 | 소스 자료 부족 시 성과 예측 확정 불가 |"
        )
    return "\n".join(rows)


def build_report(row: dict[str, str], source_materials: dict[str, object]) -> str:
    research_id = row["research_id"]
    target_country = row.get("target_country", "")
    channels = split_values(row.get("target_channels", ""))
    brands = split_values(row.get("target_brands", ""))
    products = split_values(row.get("target_product_categories", ""))
    restricted_brands = normalize_restricted_brands(row)
    recommended_brands = [brand for brand in brands if brand not in restricted_brands]
    china_target = is_china_target(target_country)
    warnings = source_materials["warnings"]
    sources = source_materials["sources"]
    is_sufficient = bool(source_materials["is_sufficient"])
    evidence_status = "제한적 사용 가능" if is_sufficient else "검증 필요 / 소스 자료 부족 / 확정 불가"
    go_or_no_go = "조건부 진행" if is_sufficient else "주의 조건부 진행: 내부 검토용 샘플 생성만 가능"

    china_risk_line = (
        "중국 대상이므로 플랫폼 정책, 계정 운영, 실명/인증, 현지화, 화장품 표현 리스크를 반드시 검토해야 합니다."
        if china_target
        else "대상 국가별 플랫폼 정책, 현지화, 화장품 표현 리스크 검토가 필요합니다."
    )

    warning_lines = "\n".join(f"- {warning}" for warning in warnings) if warnings else "- 현재 로컬 소스 기준 추가 경고 없음"

    return f"""# 시장조사 보고서 - {research_id}

> 이 보고서는 로컬 구조화 입력값과 사용자 제공 소스 자료만 사용해 생성되었습니다. 스크래핑, 라이브 웹리서치, 자동 웹검색, API 호출, 외부 데이터 수집은 수행하지 않았습니다.

## 증거 상태 요약

- 확인된 사실: 입력 CSV의 연구 조건, 사용자가 제공한 소스 파일 존재 여부
- 관찰: `source_notes.md`와 `sources.csv`에 사용자가 기록한 관찰 내용
- 가정: 제공 자료가 부족한 영역에서 내부 검토를 위해 명시한 실행 가정
- 검증 필요: 시장 규모, 순위, 판매량, 조회수, 참여율, 규제 사실, 채널 효과 등 제공 자료로 확정할 수 없는 항목
- 추천: 검증 필요 조건을 전제로 한 내부 실행 방향
- 전체 증거 상태: {evidence_status}

### 소스 경고

{warning_lines}

### 사용자 제공 소스 목록

{source_summary_table(sources)}

## 1. Research Brief

| Field | Value | Evidence label | Notes |
|---|---|---|---|
| target_country | {target_country or '검증 필요'} | 확인된 사실 | 입력 CSV 기준 |
| target_channel | {row.get('target_channels') or '검증 필요'} | 확인된 사실 | 입력 CSV 기준 |
| target_brand | {row.get('target_brands') or '검증 필요'} | 확인된 사실 | 입력 CSV 기준 |
| target_product_category | {row.get('target_product_categories') or '검증 필요'} | 확인된 사실 | 입력 CSV 기준 |
| research_objective | {row.get('research_objective') or '검증 필요'} | 확인된 사실 | 입력 CSV 기준 |
| b2b_or_b2c_focus | {row.get('b2b_or_b2c_focus') or '검증 필요'} | 확인된 사실 | B2B 바이어 유입과 B2C 소비자 반응을 분리해야 함 |
| date | {row.get('date') or '검증 필요'} | 확인된 사실 | 입력 CSV 기준 |
| researcher | 로컬 보고서 생성기 | 확인된 사실 | 자동 생성, 외부 조사 없음 |

## 2. Market Overview

| Field | Finding | Evidence label | Notes |
|---|---|---|---|
| market_size_or_signal | 확정 불가 | 검증 필요 | 시장 규모, 매출, 성장률 자료가 제공되지 않음 |
| demand_trend | 확정 불가 | 검증 필요 | 실제 조사 시 소스 자료 필요 |
| consumer_interest | 확정 불가 | 검증 필요 | 플랫폼 반응 자료가 부족함 |
| buyer_interest | 확정 불가 | 검증 필요 | 도매/수입상 문의 데이터 미제공 |
| key_growth_drivers | K-뷰티, 스킨케어, 선케어 관심 가능성은 가정 기반 예시 | 가정 | 실제 시장 자료로 검증 필요 |
| key_barriers | {china_risk_line} | 추천 | 실행 전 검토 필요 |

## 3. Channel Analysis

{build_channel_rows(channels, china_target)}

## 4. Competitor and Content Analysis

| Field | Finding | Evidence label | Notes |
|---|---|---|---|
| competing_brands | {', '.join(brands) if brands else '검증 필요'} | 확인된 사실 | 입력값의 분석 대상 브랜드이며 실제 경쟁 강도는 검증 필요 |
| popular_content_types | 확정 불가 | 검증 필요 | 조회수, 참여율, 랭킹 자료 없음 |
| common_hooks | 제품 효능 단정 표현 대신 사용감/성분/유통 포인트 중심 제안 | 추천 | 화장품 표현 리스크 고려 |
| common_visual_style | 확정 불가 | 검증 필요 | 수동 관찰 자료 추가 필요 |
| common_claims | 의학적/기능성 단정 표현 금지, 검증된 표현만 사용 | 추천 | 국가별 규제 검토 필요 |
| pricing_or_positioning_signal | 확정 불가 | 검증 필요 | 가격/포지셔닝 자료 미제공 |
| engagement_signal | 확정 불가 | 검증 필요 | 조회수, 좋아요, 댓글, 저장 수치 생성 금지 |

## 5. Product/Brand Fit

| Field | Finding | Evidence label | Notes |
|---|---|---|---|
| recommended_brands | {', '.join(recommended_brands) if recommended_brands else '검증 필요'} | 추천 | 승인 필요 브랜드 제외 기준 |
| recommended_product_categories | {', '.join(products) if products else '검증 필요'} | 확인된 사실 | 입력 CSV 기준, 실제 시장 적합성은 검증 필요 |
| reason_for_selection | 입력된 브랜드/제품군을 바탕으로 내부 테스트 후보 구성 | 가정 | 소스 자료 부족으로 확정 추천 아님 |
| target_buyer_type | 100개 이상 주문 가능한 도매상, 수입상, 유통 파트너 | 추천 | AGENTS.md 사업 규칙 기준 |
| differentiation_angle | 제품 사용감, 공급 가능성, MOQ/납기, 바이어 문의 대응력 중심 | 추천 | 외부 제안 전 브랜드 승인 확인 필요 |
| approval_required_check | {', '.join(restricted_brands)}는 승인 필요로 취급하며 외부 포스팅/바이어 제안 추천에서 제외 | 확인된 사실 | 메디큐브는 기본 승인 필요 브랜드 |

## 6. B2B Buyer Acquisition Angle

| Field | Finding | Evidence label | Notes |
|---|---|---|---|
| target_buyer_segments | 도매상, 수입상, 리셀러, 온라인 유통 파트너 | 추천 | 100개 이상 주문 가능성이 기준 |
| buyer_pain_points | 신뢰 가능한 공급처, MOQ, 납기, 브랜드 승인 가능성, 제품 자료 확보 | 가정 | 실제 바이어 인터뷰 필요 |
| value_proposition | K-뷰티 브랜드 소싱, 100개 이상 MOQ 대응, 20-30일 납기 기준 안내 | 추천 | 사업 규칙 기반, 건별 확인 필요 |
| proof_points_needed | 브랜드 승인 여부, 공급 가능 수량, 단가표, 제품 이미지, 성분/표현 검수 자료 | 추천 | 외부 제안 전 준비 필요 |
| message_angle | 소비자 바이럴보다 안정적 소싱과 바이어 문의 전환을 우선 | 추천 | B2B/B2C 분리 |
| lead_capture_method | WeChat/이메일/문의 폼/카탈로그 요청 경로 | 추천 | 중국 계정 운영 리스크 검토 필요 |

## 7. Content Strategy

{build_recommendation_rows(channels, products, row.get('budget_level', ''))}

## 8. Short-form Video Plan

| video_concept | hook | opening_scene | key_scenes | product_shot_direction | caption_direction | CTA | production_difficulty | expected_effect | cost_level | risk_level |
|---|---|---|---|---|---|---|---|---|---|---|
| 제품군 비교형 숏폼 | 중국 바이어가 먼저 확인해야 할 K-뷰티 제품 포인트 | 제품 3종을 한 화면에 배치 | 제품군 소개, 사용 상황, 바이어 체크포인트 | 승인 가능 브랜드만 노출, 메디큐브 제외 | 효능 단정 없이 공급/문의 중심 | 샘플 가능 여부와 MOQ 문의 유도 | 낮음 | 문의 전환 테스트 가능, 확정 효과는 검증 필요 | {recommendation_level_text(row.get('budget_level', ''))} | 중간 |
| 바이어용 체크리스트 숏폼 | 외부 제안 전 확인해야 할 브랜드 승인 포인트 | 체크리스트 화면 | MOQ, 납기, 승인 여부, 자료 요청 절차 | 브랜드 로고 사용 전 승인 확인 | B2B 안내 중심 | WeChat 또는 이메일 문의 | 낮음 | 바이어 신뢰 형성 가능성, 검증 필요 | {recommendation_level_text(row.get('budget_level', ''))} | 낮음-중간 |

## 9. Feed Post Plan

| feed_concept | image_structure | headline | key_copy | product_display_direction | CTA | design_notes | expected_effect | cost_level | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| B2B 제품 제안 카드 | 표지, 제품군, MOQ/납기, 문의 경로 | 중국 바이어용 K-뷰티 제품 검토 자료 | 시장 수치 없이 공급 조건과 검증 필요 항목 중심 | 승인 가능 브랜드만 사용, 메디큐브 제외 | 카탈로그 요청 | 중국어 현지화 검수 필요 | 바이어 문의 유도 가능성, 검증 필요 | {recommendation_level_text(row.get('budget_level', ''))} | 중간 |
| 채널별 콘텐츠 테스트 카드 | 채널별 목적과 리스크 요약 | Xiaohongshu/Douyin/WeChat 테스트 방향 | B2C 반응 관찰과 B2B 문의 전환을 분리 | 제품 이미지는 승인 자료만 사용 | 테스트 운영 문의 | 플랫폼 정책 표현 검수 필요 | 내부 실행 정렬에 도움 | {recommendation_level_text(row.get('budget_level', ''))} | 중간 |

## 10. Execution Plan

| priority | action_item | owner | required_materials | deadline | expected_output | execution_difficulty | expected_effect | cost_level | risk_level |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 실제 소스 자료 보강 | 담당자 | 플랫폼 수동 관찰, 바이어 문의 기록, 승인 가능 브랜드 자료 | {row.get('execution_period') or '검증 필요'} 내 1주차 | 검증 가능한 조사 메모 | 낮음 | 보고서 신뢰도 개선 | 낮음 | 낮음 |
| 2 | 브랜드 승인 여부 확인 | 담당자 | 제한 브랜드 목록, 승인 기록 | 콘텐츠 제작 전 | 외부 사용 가능 브랜드 목록 | 중간 | 승인 리스크 감소 | 낮음 | 중간 |
| 3 | 채널별 파일럿 콘텐츠 제작 | 담당자 | 제품 이미지, 중국어 카피, 문의 경로 | {row.get('execution_period') or '검증 필요'} 내 | 숏폼/피드 초안 | 중간 | 채널 반응 테스트 가능 | 낮음-중간 | 중간 |

## 11. Risks and Compliance

| Risk | Status | Evidence label | Required action |
|---|---|---|---|
| platform_policy_risk | {china_risk_line} | 추천 | 채널별 정책 검토 |
| China_real_name_or_account_risk | {'검증 필요: 계정 실명/운영 권한 확인 필요' if china_target else '해당 시 검증 필요'} | 검증 필요 | 계정 운영 주체와 인증 조건 확인 |
| cosmetics_claim_risk | 효능, 의학적 표현, 기능성 표현은 검증 전 사용 금지 | 추천 | 표현 검수 |
| brand_approval_risk | 메디큐브 및 승인 필요 브랜드는 외부 추천 제외 | 확인된 사실 | 승인 기록 확보 전 노출 금지 |
| translation_localization_risk | 중국어 현지화, 뉘앙스, 플랫폼 표현 방식 검토 필요 | 추천 | 현지화 검수 |
| data_reliability_risk | 소스 자료 부족으로 시장 판단 확정 불가 | 검증 필요 | 추가 자료 수집 필요 |

## 12. Final Recommendation

| Field | Recommendation | Evidence label | Notes |
|---|---|---|---|
| go_or_no_go | {go_or_no_go} | 추천 | 외부 사용 전 추가 검증 필요 |
| recommended_channels | {', '.join(channels) if channels else '검증 필요'} | 추천 | 채널별 역할은 소스 자료 보강 후 확정 |
| recommended_content | B2B 문의 유도형 숏폼/피드와 B2C 반응 관찰 콘텐츠를 분리 운영 | 추천 | 소비자 마케팅과 바이어 전환 목적 혼동 금지 |
| next_actions | 소스 자료 보강, 브랜드 승인 확인, 중국 채널 운영 리스크 검토, 파일럿 콘텐츠 초안 작성 | 추천 | Task 003 Step D 이후 검증 필요 |

## 부록: 사용자 제공 소스 노트 요약

- source_notes.md 존재 여부: {'있음' if str(source_materials['source_notes']).strip() else '없음'}
- 소스 노트 사용 방식: 원문을 시장 사실로 확정하지 않고, 사용자 제공 관찰과 검증 필요 항목으로만 반영
- 검증 상태: {evidence_status}
- 추가 필요 자료: 실제 플랫폼 수동 관찰, 바이어 문의 기록, 승인 가능한 제품 자료, 중국 계정 운영 확인 자료, 화장품 표현 검수 자료
"""


def write_report(output_dir: Path, research_id: str, report: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"market_research_report_{research_id}.md"
    output_path.write_text(report, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local market research report.")
    parser.add_argument("--research-id", required=True, help="Research ID to generate, for example MR-001.")
    parser.add_argument("--input", default="data/research_inputs_sample.csv", help="Input research CSV path.")
    parser.add_argument(
        "--source-root",
        default="data/source_materials/market_research",
        help="Root folder for user-provided source materials.",
    )
    parser.add_argument("--output-dir", default="output", help="Output directory for generated reports.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = resolve_path(args.input)
    source_root = resolve_path(args.source_root)
    output_dir = resolve_path(args.output_dir)

    rows = read_business_csv(input_path)
    validate_input_columns(rows, input_path)
    row = select_research_row(rows, args.research_id)
    source_materials = load_source_materials(source_root, args.research_id)
    report = build_report(row, source_materials)
    output_path = write_report(output_dir, args.research_id, report)

    print("PASS: market research report generated")
    print(f"research_id={args.research_id}")
    print(f"output_path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
