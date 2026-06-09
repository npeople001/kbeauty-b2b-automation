"""Generate a local channel content strategy report from existing research.

This script reads only local CSV and Markdown files. It does not perform
scraping, live web research, automatic web search, browser automation, API
calls, crawlers, requests to external services, or external data collection.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

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

REQUIRED_SECTIONS = [
    "Strategy Summary",
    "Channel Strategy",
    "Short-form Video Strategy",
    "Feed Post Strategy",
    "B2B Buyer Acquisition Content",
    "Weekly Upload Plan",
    "Execution Priority",
    "Risks and Compliance",
    "Final Recommendation",
]

INSUFFICIENT_EVIDENCE_MARKERS = [
    "검증 필요",
    "소스 자료 부족",
    "확정 불가",
    "寃利??꾩슂",
    "?뚯뒪 ?먮즺 遺議",
    "?뺤젙 遺덇",
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


def read_text_file(path: Path, required: bool, label: str, warnings: list[str]) -> str:
    if not path.exists():
        if required:
            fail(f"{label} not found: {path}")
        warnings.append(f"{label} 없음: 소스 자료 부족")
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        if required:
            fail(f"{label} is empty: {path}")
        warnings.append(f"{label} 비어 있음: 소스 자료 부족")
    return text


def read_sources_csv(path: Path, research_id: str, warnings: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        warnings.append("sources.csv 없음: 소스 자료 부족")
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            warnings.append("sources.csv header 없음: 소스 자료 부족")
            return []
        missing = [column for column in SOURCE_COLUMNS if column not in reader.fieldnames]
        if missing:
            warnings.append(f"sources.csv 필수 컬럼 누락: {', '.join(missing)}")
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]

    filtered = [row for row in rows if row.get("research_id") == research_id]
    if not filtered:
        warnings.append("sources.csv에 해당 research_id 자료 없음: 소스 자료 부족")
    return filtered


def load_optional_sources(source_root: Path, research_id: str) -> dict[str, object]:
    warnings: list[str] = []
    source_dir = source_root / research_id
    if not source_dir.exists():
        warnings.append(f"source folder 없음: {source_dir}")
        return {"source_notes": "", "sources": [], "warnings": warnings}

    source_notes = read_text_file(source_dir / "source_notes.md", False, "source_notes.md", warnings)
    sources = read_sources_csv(source_dir / "sources.csv", research_id, warnings)
    return {"source_notes": source_notes, "sources": sources, "warnings": warnings}


def normalize_restricted_brands(value: str) -> list[str]:
    restricted = split_values(value)
    if "메디큐브" not in restricted:
        restricted.append("메디큐브")
    return restricted


def is_china_target(target_country: str) -> bool:
    normalized = target_country.lower()
    return "china" in normalized or "중국" in normalized


def detect_insufficient_evidence(market_report: str, source_data: dict[str, object]) -> bool:
    if any(marker in market_report for marker in INSUFFICIENT_EVIDENCE_MARKERS):
        return True
    if source_data["warnings"]:
        return True
    sources = source_data["sources"]
    if not sources:
        return True
    return not any(source.get("verification_status") == "verified" for source in sources)


def value_or_needed(value: str) -> str:
    return value if value else "검증 필요"


def allowed_brands(row: dict[str, str]) -> tuple[list[str], list[str]]:
    brands = split_values(row.get("target_brands", ""))
    restricted = normalize_restricted_brands(row.get("restricted_or_approval_required_brands", ""))
    allowed = [brand for brand in brands if brand not in restricted]
    return allowed, restricted


def channel_role(channel: str) -> str:
    lower = channel.lower()
    if "wechat" in lower:
        return "B2B 문의 접수, 후속 커뮤니케이션, 자료 전달 경로"
    if "douyin" in lower:
        return "짧은 영상 테스트와 소비자 반응 관찰 보조 채널"
    if "xiaohongshu" in lower:
        return "제품군 이해 콘텐츠와 소비자 반응 관찰 보조 채널"
    return "채널 적합성 검증 및 저비용 콘텐츠 테스트"


def b2c_use_case(channel: str) -> str:
    if "WeChat".lower() in channel.lower():
        return "소비자 마케팅보다는 기존 접점 관리와 문의 응대에 제한적으로 활용"
    return "제품군별 반응을 관찰하되 조회수나 참여율을 수요로 단정하지 않음"


def lead_capture_method(channel: str, china_target: bool) -> str:
    if china_target:
        if "wechat" in channel.lower():
            return "WeChat 문의 후 MOQ, 국가, 브랜드 승인 가능 여부를 확인"
        return "프로필/캡션에서 WeChat 또는 이메일 문의로 연결"
    return "프로필, 이메일, 메신저 문의로 연결 후 MOQ와 수입 가능성을 확인"


def build_channel_strategy(channels: list[str], china_target: bool, evidence_note: str) -> str:
    lines = [
        "| channel_name | channel_role | target_audience | b2b_use_case | b2c_use_case | recommended_content_type | posting_frequency | lead_capture_method | execution_difficulty | expected_effect | cost_level | risk_level |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for channel in channels:
        audience = "중국 소비자 반응 관찰 대상과 K-뷰티 소싱 관심 바이어" if china_target else "소비자 반응 관찰 대상과 B2B 소싱 관심 바이어"
        content_type = "짧은 영상, 제품군 피드, B2B 문의 유도 카드"
        if "wechat" in channel.lower():
            content_type = "B2B 문의 응대 메시지, 제품군 요약, 카탈로그 요청 안내"
        lines.append(
            f"| {channel} | {channel_role(channel)} | {audience} | B2B 바이어 문의 가능성을 확인하고 상담 경로로 전환 | {b2c_use_case(channel)} | {content_type} | 주 1-2회 테스트 또는 문의 응대 기준 운영 | {lead_capture_method(channel, china_target)} | medium | medium: {evidence_note} | low | medium |"
        )
    return "\n".join(lines)


def build_video_strategy(allowed_brand_text: str, product_text: str, evidence_note: str) -> str:
    return f"""| video_title | objective | target_viewer | hook | opening_scene | key_scenes | product_display_direction | script_direction | caption_direction | CTA | required_assets | production_difficulty | expected_effect | risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B2B 바이어용 제품군 체크 영상 | B2B 문의 전환 경로를 테스트 | 도매상, 수입상, 소싱 담당자 | 중국 바이어가 K-뷰티 제품을 볼 때 먼저 확인할 조건 | {product_text} 제품군을 한 화면에 정리 | 제품군 소개; MOQ/납기 확인 항목; 승인 가능 브랜드 안내; 문의 CTA | 승인 가능한 브랜드만 노출: {allowed_brand_text}. 메디큐브는 승인 전 제외 | 효능 단정보다 공급 조건, 문의 절차, 검증 필요 항목 중심 | 중국어 표현은 현지화 검수 전 단정 금지 | MOQ와 공급 가능 브랜드 문의 | 제품 이미지, 승인 가능 브랜드 리스트, 제품 정보, 중국어 검수 카피 | low | medium: {evidence_note} | 화장품 표현, 브랜드 승인, 중국 플랫폼 정책 검토 필요 |
| 소비자 반응 관찰용 제품 이해 영상 | B2C 반응 관찰과 B2B 문의 유도를 분리 | 소비자 반응 관찰 대상과 잠재 바이어 | 제품 효능보다 어떤 제품군인지 먼저 확인하세요 | 제품 텍스처나 패키지 이미지를 짧게 노출 | 제품군 설명; 사용 상황 예시; 검증 필요 표시; B2B 문의 CTA | 승인 가능 자료만 사용하고 제한 브랜드는 노출하지 않음 | 소비자 구매 유도보다 제품군 이해와 문의 경로 안내 중심 | 조회수, 인기, 판매 성과 표현 금지 | 카탈로그와 공급 가능 여부 문의 | 제품 사진/짧은 클립, 카테고리 설명, 문의 링크 | medium | medium: 콘텐츠 반응을 내부 참고용으로 확인 가능, 성과는 검증 필요 | 성과 과장, 현지화 오류, 표현 심의 리스크 |"""


def build_feed_strategy(allowed_brand_text: str, product_text: str, evidence_note: str) -> str:
    return f"""| feed_title | objective | image_structure | headline | key_copy | product_display_direction | proof_points | CTA | design_notes | expected_effect | risk |
|---|---|---|---|---|---|---|---|---|---|---|
| B2B 제품 제안 카드 | 바이어가 문의 전 제품군과 공급 조건을 이해하도록 지원 | 1장 표지; 2장 제품군; 3장 MOQ/납기; 4장 문의 경로 | K-뷰티 {product_text} 공급 검토 자료 | 시장 수치나 인기 표현 없이 공급 가능 조건과 검증 필요 항목 중심 | 승인 가능한 브랜드만 표시: {allowed_brand_text}. 메디큐브는 승인 전 제외 | 브랜드 승인 여부, 공급 가능 수량, 제품 이미지, 표현 검수 자료 | 카탈로그 및 공급 가능 여부 문의 | 중국어/현지 표현은 게시 전 검수 필요 | medium: {evidence_note} | 화장품 표현, 브랜드 승인, 현지화 리스크 |
| 채널별 콘텐츠 테스트 카드 | Xiaohongshu, Douyin, WeChat 역할을 분리해 내부 실행 기준 마련 | 채널 역할; B2C 관찰; B2B 문의 경로; 리스크 체크 | 채널별 콘텐츠 운영 방향 | B2C 반응 관찰과 B2B 문의 전환을 혼동하지 않도록 작성 | 제품 이미지는 승인 자료만 사용 | 채널 운영 가능 여부, 문의 경로, 승인 가능 브랜드 리스트 | 테스트 운영 문의 및 내부 검토 | 플랫폼 정책과 계정 운영 조건은 검증 필요로 표시 | medium: 실행 우선순위 정리에 도움, 성과는 검증 필요 | 플랫폼 정책, 계정 운영, 리소스 부족 리스크 |"""


def build_weekly_plan(channels: list[str], execution_period: str) -> str:
    main_channel = channels[0] if channels else "검증 필요"
    inquiry_channel = next((channel for channel in channels if "wechat" in channel.lower()), "WeChat")
    return f"""| week | channel | content_type | topic | format | purpose | required_materials | expected_output |
|---|---|---|---|---|---|---|---|
| 1주차 | 내부 준비 | 자산 준비 | 승인 가능 브랜드와 제품 자료 정리 | 체크리스트 | 외부 노출 전 승인/표현 리스크 감소 | 브랜드 승인 기록, 제품 이미지, 제품 정보 | 게시 가능 브랜드/자료 목록 |
| 2주차 | {main_channel} | 피드 포스트 | B2B 공급 조건 안내 | 4장 카드뉴스 | B2B 문의 유도와 B2C 관찰 분리 | 제품 이미지, MOQ/납기 안내, 문의 CTA | 피드 초안 1건 |
| 3주차 | Douyin | 짧은 영상 | 제품군 체크 영상 | 15-30초 영상 | 짧은 영상 반응 관찰과 문의 경로 테스트 | 제품 클립, 승인 브랜드 리스트, 중국어 검수 카피 | 영상 초안 1건 |
| 4주차 | {inquiry_channel} | 문의 응대 자료 | 바이어 문의 후속 안내 | 메시지 템플릿/요약 자료 | 문의 후 MOQ, 국가, 브랜드 승인 가능 여부 확인 | 카탈로그, 승인 가능 브랜드 리스트, 응대 문구 | B2B 문의 응대 템플릿 |"""


def build_report(row: dict[str, str], market_report: str, source_data: dict[str, object]) -> str:
    research_id = row["research_id"]
    target_country = value_or_needed(row.get("target_country", ""))
    channels = split_values(row.get("target_channels", ""))
    brands, restricted = allowed_brands(row)
    products = split_values(row.get("target_product_categories", ""))
    china_target = is_china_target(target_country)
    insufficient = detect_insufficient_evidence(market_report, source_data)
    evidence_note = "시장조사 보고서의 소스 자료가 제한되어 검증 필요" if insufficient else "제공 자료 기반으로 내부 검토 가능"
    evidence_status = "검증 필요 / 소스 자료 부족 / 확정 불가" if insufficient else "제공 자료 기반 내부 검토"
    go_or_no_go = "go_with_caution" if insufficient else "go"
    first_channel = "WeChat" if china_target and "WeChat" in channels else (channels[0] if channels else "검증 필요")
    product_text = ", ".join(products) if products else "제품군 검증 필요"
    allowed_brand_text = ", ".join(brands) if brands else "승인 가능 브랜드 검증 필요"
    restricted_text = ", ".join(restricted)
    source_warnings = source_data["warnings"]
    source_warning_text = "\n".join(f"- {warning}" for warning in source_warnings) if source_warnings else "- 추가 소스 경고 없음"

    if china_target:
        china_risks = "중국 계정 운영, 실명/계정 인증, 플랫폼 정책, 현지화, 화장품 표현 리스크는 모두 검증 필요"
    else:
        china_risks = "중국 대상이 아닐 경우에도 현지 플랫폼 정책, 현지화, 화장품 표현 리스크 검토 필요"

    return f"""# 채널 콘텐츠 전략 보고서 - {research_id}

> 이 보고서는 로컬 CSV 입력, 기존 시장조사 보고서, 사용자 제공 소스 자료만 사용해 생성되었습니다. 스크래핑, 라이브 웹리서치, 자동 웹검색, API 호출, 브라우저 자동화, 크롤링, 외부 데이터 수집은 수행하지 않았습니다.

## 증거 및 사용 제한 요약

- 증거 상태: {evidence_status}
- 확인된 사실: research_id, target_country, target_channels, target_brands, product categories 등 입력 CSV 값
- 관찰: 사용자 제공 source_notes.md 및 sources.csv에 포함된 수동 관찰이 있을 때만 사용
- 가정: 제한된 자료를 바탕으로 내부 실행 검토를 위해 작성한 전략 가정
- 검증 필요: 시장 규모, 순위, 판매량, 조회수, 참여율, 플랫폼 성과, 규제 사실, 바이어 수요
- 추천: 외부 사용 전 검증과 브랜드 승인 확인이 필요한 내부 실행 제안

### 소스 제한

{source_warning_text}

## 1. Strategy Summary

| Field | Value |
|---|---|
| summary_conclusion | {target_country} 대상 전략은 B2B 바이어 문의 경로와 B2C 소비자 반응 관찰을 분리한 조건부 진행이 적절합니다. {evidence_note}. |
| recommended_channels | {', '.join(channels) if channels else '검증 필요'} |
| recommended_brands_or_categories | {allowed_brand_text} / {product_text} |
| first_content_direction | 효능 단정이나 시장 성과 주장보다 승인 가능 브랜드, 제품군, MOQ, 납기, 문의 경로를 정리하는 콘텐츠 |
| expected_effect | medium: 내부 실행 기준과 초기 문의 경로를 정리할 수 있으나 실제 성과는 검증 필요 |
| key_risks | {china_risks}; 브랜드 승인 리스크; 소스 자료 부족; 실행 리소스 부족 |

## 2. Channel Strategy

{build_channel_strategy(channels, china_target, evidence_note)}

## 3. Short-form Video Strategy

{build_video_strategy(allowed_brand_text, product_text, evidence_note)}

## 4. Feed Post Strategy

{build_feed_strategy(allowed_brand_text, product_text, evidence_note)}

## 5. B2B Buyer Acquisition Content

| target_buyer_segment | buyer_pain_point | message_angle | proof_needed | recommended_post_type | inquiry_conversion_path | follow_up_action |
|---|---|---|---|---|---|---|
| 100개 이상 주문 가능한 도매상, 수입상, 유통사, 온라인 셀러, 소싱 담당자 | 승인 가능 브랜드, MOQ, 납기, 공급 가능 수량, 제품 자료 확인 필요 | 소비자 인기 주장보다 공급 조건과 문의 절차를 명확히 제시 | 브랜드 승인 기록, 공급 가능 수량, 제품 이미지, 제품 정보, 화장품 표현 검수 자료 | B2B 문의 유도 피드, 제품군 체크 영상, 문의 응대 메시지 | 콘텐츠 노출 -> 프로필/캡션 확인 -> WeChat 또는 이메일 문의 -> MOQ/국가/브랜드 승인 가능 여부 확인 -> 승인 가능 자료 발송 | 제한 브랜드({restricted_text})는 승인 전 제외하고, 구매 수량/국가/희망 브랜드/납기 기준 확인 후 후속 자료 발송 |

## 6. Weekly Upload Plan

{build_weekly_plan(channels, row.get('execution_period', '4 weeks'))}

## 7. Execution Priority

| priority | action_item | reason | difficulty | expected_effect | cost_level | risk_level |
|---|---|---|---|---|---|---|
| 1 | 승인 가능 브랜드 목록 확인 | 메디큐브 등 승인 필요 브랜드의 외부 노출을 막기 위해 필요 | low | high: 외부 게시와 바이어 제안 리스크 감소 | low | medium |
| 2 | 제품 이미지와 제품 정보 정리 | 영상/피드 제작에 필요한 기본 자료 확보 | medium | medium: 콘텐츠 제작 가능 상태 확보 | low | medium |
| 3 | 중국어 카피 및 화장품 표현 검수 | 효능, 기능성, 의료적 표현 리스크를 낮추기 위해 필요 | medium | high: 외부 표현 리스크 감소 | medium | high |
| 4 | WeChat 또는 이메일 문의 경로 정리 | B2B 문의를 실제 상담으로 전환하기 위한 운영 기준 필요 | low | medium: 문의 응대 흐름 정리 | low | medium |
| 5 | Xiaohongshu/Douyin 테스트 콘텐츠 초안 제작 | 소비자 반응 관찰과 바이어 문의 유도를 분리해 테스트 | medium | medium: 내부 테스트 자산 확보, 성과는 검증 필요 | low | medium |

## 8. Risks and Compliance

| Field | Risk |
|---|---|
| platform_policy_risk | 중국 플랫폼 정책과 게시 가능 표현은 실제 운영 전 확인 필요. 플랫폼별 정책 변화 가능성 때문에 검증 필요. |
| China_account_or_real_name_risk | 중국 대상 전략이므로 계정 운영 주체, 실명/계정 인증, 운영 권한 확인 필요. 현재 자료만으로 확정 불가. |
| cosmetics_claim_risk | 미백, 여드름, 치료, 임상, 기능성 단정 표현은 검증 전 사용 금지. 제품 효능 주장은 소스 자료 부족. |
| brand_approval_risk | {restricted_text}는 승인 전 외부 게시, 공용 콘텐츠, 바이어 제안, 광고 카피에서 제외. 메디큐브는 명시 승인 전 추천 금지. |
| localization_risk | 중국어 번역, 플랫폼 문체, 금지 표현, 소비자/바이어 표현 차이는 현지화 검수 필요. |
| resource_risk | {row.get('budget_level') or 'unknown'} 예산과 {row.get('execution_period') or '검증 필요'} 실행 기간 기준으로 촬영, 디자인, 응대 리소스 부족 가능. |

## 9. Final Recommendation

| Field | Value |
|---|---|
| go_or_no_go | {go_or_no_go} |
| first_channel_to_start | {first_channel} |
| first_content_to_create | B2B 공급 조건 안내 피드 초안과 문의 응대 경로 정리 |
| next_actions | 1. 승인 가능 브랜드 확인 2. 제품 이미지/정보 정리 3. 중국어/화장품 표현 검수 4. WeChat 또는 이메일 문의 경로 정리 5. Xiaohongshu/Douyin 테스트 콘텐츠 초안 작성 |

## 내부 검토 메모

- 이 전략은 대표자급 내부 검토용 초안입니다.
- 실제 게시, 광고, 바이어 제안, 외부 자료에는 추가 검증이 필요합니다.
- 시장 규모, 순위, 판매량, 조회수, 참여율, 플랫폼 성과, 바이어 수요는 생성하지 않았습니다.
- 메디큐브는 승인 전 외부 추천에서 제외했습니다.
"""


def write_report(output_dir: Path, research_id: str, report: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"channel_content_strategy_{research_id}.md"
    output_path.write_text(report, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local channel content strategy report.")
    parser.add_argument("--research-id", required=True, help="Research ID to generate, for example MR-001.")
    parser.add_argument("--input", default="data/research_inputs_sample.csv", help="Input research CSV path.")
    parser.add_argument(
        "--research-report-dir",
        default="output",
        help="Directory containing market_research_report_{research_id}.md.",
    )
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
    research_report_dir = resolve_path(args.research_report_dir)
    source_root = resolve_path(args.source_root)
    output_dir = resolve_path(args.output_dir)

    rows = read_business_csv(input_path)
    validate_input_columns(rows, input_path)
    row = select_research_row(rows, args.research_id)

    market_report_path = research_report_dir / f"market_research_report_{args.research_id}.md"
    warnings: list[str] = []
    market_report = read_text_file(market_report_path, True, "market research report", warnings)
    source_data = load_optional_sources(source_root, args.research_id)

    report = build_report(row, market_report, source_data)
    output_path = write_report(output_dir, args.research_id, report)

    print("PASS: channel content strategy report generated")
    print(f"research_id={args.research_id}")
    print(f"output_path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
