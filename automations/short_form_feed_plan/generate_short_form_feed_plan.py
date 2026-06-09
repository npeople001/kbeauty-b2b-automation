"""Generate a local short-form video and feed post production plan.

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

INSUFFICIENT_EVIDENCE_MARKERS = [
    "검증 필요",
    "소스 자료 부족",
    "확정 불가",
    "寃利",
    "遺議",
    "遺덇",
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


def read_required_text(path: Path, label: str) -> str:
    if not path.exists():
        fail(f"{label} not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        fail(f"{label} is empty: {path}")
    return text


def read_optional_text(path: Path, label: str, warnings: list[str]) -> str:
    if not path.exists():
        warnings.append(f"{label} 없음: 소스 자료 부족")
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        warnings.append(f"{label} 비어 있음: 소스 자료 부족")
    return text


def read_optional_sources(path: Path, research_id: str, warnings: list[str]) -> list[dict[str, str]]:
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


def load_source_materials(source_root: Path, research_id: str) -> dict[str, object]:
    warnings: list[str] = []
    source_dir = source_root / research_id
    if not source_dir.exists():
        warnings.append(f"source folder 없음: {source_dir}")
        return {"source_notes": "", "sources": [], "warnings": warnings}

    source_notes = read_optional_text(source_dir / "source_notes.md", "source_notes.md", warnings)
    sources = read_optional_sources(source_dir / "sources.csv", research_id, warnings)
    if not source_notes and not sources:
        warnings.append("사용 가능한 소스 자료 없음: 소스 자료 부족")
    return {"source_notes": source_notes, "sources": sources, "warnings": warnings}


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def is_china_target(target_country: str) -> bool:
    normalized = target_country.lower()
    return "china" in normalized or "중국" in normalized


def normalize_restricted_brands(value: str) -> list[str]:
    restricted = split_values(value)
    if "메디큐브" not in restricted:
        restricted.append("메디큐브")
    return restricted


def allowed_brands(row: dict[str, str]) -> tuple[list[str], list[str]]:
    brands = split_values(row.get("target_brands", ""))
    restricted = normalize_restricted_brands(row.get("restricted_or_approval_required_brands", ""))
    allowed = [brand for brand in brands if brand not in restricted]
    return allowed, restricted


def detect_insufficient_evidence(
    market_report: str,
    channel_strategy: str,
    source_data: dict[str, object],
) -> bool:
    combined = f"{market_report}\n{channel_strategy}"
    if any(marker in combined for marker in INSUFFICIENT_EVIDENCE_MARKERS):
        return True
    if source_data["warnings"]:
        return True
    sources = source_data["sources"]
    if not sources:
        return True
    return not any(source.get("verification_status") == "verified" for source in sources)


def safe_join(items: list[str], fallback: str = "검증 필요") -> str:
    return ", ".join(items) if items else fallback


def contains_channel(channels: list[str], name: str) -> bool:
    return any(name.lower() in channel.lower() for channel in channels)


def first_or_default(channels: list[str], default: str) -> str:
    return channels[0] if channels else default


def source_warning_text(source_data: dict[str, object]) -> str:
    warnings = source_data["warnings"]
    if not warnings:
        return "- 추가 소스 경고 없음"
    return "\n".join(f"- {warning}" for warning in warnings)


def build_video_rows(allowed_brand_text: str, product_text: str, evidence_note: str) -> str:
    rows = [
        "| video_id | video_title | target_channel | objective | target_viewer | b2b_or_b2c_focus | hook | opening_scene | scene_by_scene_plan | product_shot_direction | script_direction | caption_direction | subtitle_direction | CTA | required_assets | production_difficulty | expected_effect | cost_level | risk_level | compliance_notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        f"| V-001 | B2B 제품군 체크 영상 | Douyin | B2B 바이어가 문의 전 확인할 제품군과 공급 조건을 정리 | 중국 수입상, 도매상, 소싱 담당자 | b2b | K-뷰티 공급 문의 전 먼저 확인할 3가지 | {product_text} 제품군을 정면 배치하고 제품군명을 표시 | 1. 제품군 소개; 2. MOQ/납기 확인 항목; 3. 승인 가능 브랜드 안내; 4. 문의 CTA | 승인 가능한 브랜드만 노출: {allowed_brand_text}. 메디큐브는 승인 전 제외 | 효능 단정보다 공급 조건, 문의 절차, 검증 필요 항목 중심 | 검증 필요 항목은 확정 표현을 피하고 문의 유도 문구로 정리 | 중국어 자막은 현지 표현 검토 후 사용 | MOQ와 공급 가능 브랜드 문의 | 제품 이미지, 승인 가능 브랜드 목록, 제품 정보, 중국어 검수 카피 | low | medium: {evidence_note} | low | medium | 화장품 효능 표현과 메디큐브 노출은 외부 사용 전 검토 필요 |",
        f"| V-002 | 소비자 반응 관찰용 제품 이해 영상 | Xiaohongshu | 소비자-facing 반응 관찰과 B2B 문의 유도 목적을 분리 | 소비자 반응 관찰 대상과 잠재 바이어 | both | 제품 효능보다 어떤 제품군인지 먼저 확인하세요 | 패키지와 제형 이미지를 짧게 보여주고 제품군명 표시 | 1. 제품군 설명; 2. 사용 상황 예시; 3. 검증 필요 표시; 4. B2B 문의 CTA | 승인 가능한 브랜드 자료만 사용하고 제한 브랜드는 노출하지 않음 | 소비자 구매 유도보다 제품군 이해와 문의 경로 안내 중심 | 조회수, 인기, 판매 성과 표현 금지 | 중국어 표현은 현지화 검토 후 사용 | 카탈로그와 공급 가능 여부 문의 | 제품 사진/짧은 클립, 카테고리 설명, 문의 링크 | medium | medium: 콘텐츠 반응은 참고용이며 실제 효과는 검증 필요 | low | medium | 효과 과장, 번역 오류, 표현 수위 리스크 |",
        f"| V-003 | 바이어 문의 체크리스트 영상 | WeChat | 문의 후 상담에 필요한 확인 항목을 정리 | 100개 이상 주문 가능한 바이어 | b2b | 문의 전에 수량, 국가, 브랜드 승인 여부를 확인해 주세요 | 체크리스트 화면과 승인 가능 브랜드 목록을 표시 | 1. 예상 수량; 2. 국가/채널; 3. 관심 브랜드; 4. 승인/공급 가능 여부; 5. 후속 자료 안내 | 제품 샷보다 체크리스트와 승인 가능 브랜드 자료 중심. 메디큐브는 승인 전 제외 | 바이어 상담 흐름, MOQ, 납기, 필요 자료 중심 | 공용 게시보다 문의 응대용 문구로 작성 | 중국어/한국어 병기 시 현지 표현 검토 | WeChat 또는 이메일로 제품군과 수량 문의 | 문의 응대 템플릿, 브랜드 승인 자료, 카탈로그, MOQ/납기 안내 | low | medium: 문의 응대 기준 정리에 도움, 실제 전환은 검증 필요 | low | medium | 바이어-facing 자료는 승인 가능 브랜드와 검증된 공급 조건만 사용 |",
    ]
    return "\n".join(rows)


def build_feed_rows(allowed_brand_text: str, product_text: str, evidence_note: str) -> str:
    rows = [
        "| feed_id | feed_title | target_channel | objective | image_structure | slide_by_slide_plan | headline | key_copy | product_display_direction | proof_points | CTA | design_notes | required_assets | production_difficulty | expected_effect | cost_level | risk_level | compliance_notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        f"| F-001 | B2B 공급 조건 안내 카드 | Xiaohongshu | 바이어가 제품군, MOQ, 문의 경로를 빠르게 확인 | 표지 1장, 제품군 1장, MOQ/납기 1장, 문의 CTA 1장 | 1. 표지; 2. {product_text}; 3. MOQ/납기; 4. 문의 경로 | K-뷰티 B2B 공급 문의 전 확인할 항목 | 시장 수치 대신 공급 가능성, 승인 여부, 문의 절차 중심 | 승인 가능한 브랜드만 표시: {allowed_brand_text}. 메디큐브는 승인 전 제외 | 브랜드 승인 자료, 제품 이미지, MOQ/납기 확인 자료, 표현 검토 자료 | 카탈로그와 공급 가능 여부 문의 | 중국어 문구는 현지화 검토 후 사용하고 과장 효능 표현 금지 | 제품 이미지, 로고 사용 승인, 제품 정보, 중국어 검수 카피 | low | medium: {evidence_note} | low | medium | 효능 표현, 전후 이미지, 승인 필요 브랜드 노출은 금지 또는 검토 필요 |",
        f"| F-002 | 채널별 콘텐츠 역할 카드 | WeChat | Xiaohongshu, Douyin, WeChat 역할을 분리해 내부 실행 기준 마련 | 채널 역할 1장, B2C 관찰 1장, B2B 문의 경로 1장, 리스크 1장 | 1. 채널 역할; 2. 소비자 반응 관찰; 3. B2B 문의 전환; 4. 리스크 체크 | 채널별 콘텐츠 운영 방향 | B2C 반응 관찰과 B2B 문의 전환을 혼동하지 않도록 작성 | 제품 이미지는 승인 자료만 사용 | 채널 운영 가능 여부, 문의 경로, 승인 가능 브랜드 목록 | 테스트 운영 문의 및 내부 검토 | 플랫폼 정책과 계정 운영 조건은 검증 필요로 표시 | 채널별 설명 문구, 문의 경로, 검수 카피 | low | medium: 실행 우선순위 정리에 유용, 성과는 검증 필요 | low | medium | 중국 계정/실명/플랫폼 리스크와 현지화 리스크 포함 |",
        f"| F-003 | 제품 자료 준비 체크리스트 | WeChat | 바이어 문의 대응 전에 필요한 자료를 정리 | 필요 자료 1장, 승인 자료 1장, 제품 이미지 1장, 후속 액션 1장 | 1. 제품 이미지; 2. 브랜드 승인; 3. MOQ/납기; 4. 후속 문의 | 바이어 응대 전 준비할 자료 | 승인되지 않은 브랜드와 검증되지 않은 표현은 외부 자료에서 제외 | 메디큐브는 명시 승인 전 제외하고 승인 가능한 브랜드 자료만 사용 | 제품 이미지, 브랜드 승인 기록, 공급 가능 수량, MOQ/납기 자료 | 자료 준비 후 공급 가능 브랜드 문의 | 내부 체크리스트 톤으로 구성하고 외부 확정 표현은 피함 | 제품 이미지, 카탈로그, 승인 가능 브랜드 목록, 문의 응대 템플릿 | medium | medium: 문의 대응 자료 준비에 도움, 실제 바이어 수요는 검증 필요 | low | low | 판매 가능성, 인기, 성과 수치 표현 금지 |",
    ]
    return "\n".join(rows)


def build_channel_adaptation(channels: list[str], china_target: bool) -> str:
    tiktok_note = "MR-001은 중국 중심이므로 TikTok/Instagram은 해당 없음."
    if contains_channel(channels, "TikTok") or contains_channel(channels, "Instagram"):
        tiktok_note = "TikTok/Instagram은 짧은 제품군 설명과 B2B 문의 CTA를 현지 채널 상황에 맞춰 조정하되 성과 주장은 금지."

    return f"""| Field | Recommendation |
|---|---|
| xiaohongshu_adaptation | 정보형 카드와 짧은 제품군 설명 중심. 소비자 반응은 관찰용이며 바이어 수요로 단정하지 않음. |
| douyin_adaptation | 15-30초 숏폼으로 제품군, 문의 CTA, 승인 가능 브랜드만 간결하게 구성. 조회수나 성과 예측은 하지 않음. |
| wechat_adaptation | B2B 문의 접수, 후속 자료 전달, MOQ/납기 확인 경로로 사용. 계정 운영과 실명/권한은 검증 필요. |
| tiktok_instagram_adaptation | {tiktok_note} |
| b2b_buyer_facing_adaptation | 공급 가능성, 승인 가능 브랜드, MOQ, 납기, 문의 경로 중심으로 조정. 바이어-facing 자료는 검증된 표현만 사용. |
| consumer_facing_adaptation | 소비자 반응 관찰용으로 활용하되 도매 수요로 단정하지 않음. B2B CTA와 소비자-facing 문구를 분리. |"""


def build_weekly_schedule(channels: list[str]) -> str:
    first_channel = first_or_default(channels, "Xiaohongshu")
    inquiry_channel = "WeChat" if contains_channel(channels, "WeChat") else first_channel
    return f"""| week | content_id | channel | content_type | topic | production_task | required_materials | owner | expected_output |
|---|---|---|---|---|---|---|---|---|
| 1주차 | PREP-001 | 내부 준비 | other | 승인 가능 브랜드와 제품 자료 정리 | 메디큐브 제외 여부, 제품 이미지, 제품 정보, MOQ/납기 자료 확인 | 승인 가능 브랜드 목록, 제품 이미지, 제품 정보, 문의 응대 자료 | 담당자 | 게시 가능 브랜드/제품 자료 목록 |
| 2주차 | F-001 | {first_channel} | feed_post | B2B 공급 조건 안내 | 4장 카드뉴스 초안 제작 및 중국어 표현 검토 | 제품 이미지, MOQ/납기 안내, 문의 CTA, 현지화 검수 | 담당자 | 피드 초안 1건 |
| 3주차 | V-001 | Douyin | short_form_video | B2B 제품군 체크 영상 | 15-30초 영상 초안 제작, 자막/캡션 검토 | 제품 이미지/클립, 승인 가능 브랜드 목록, 중국어 자막 초안 | 담당자 | 영상 초안 1건 |
| 4주차 | F-003 | {inquiry_channel} | b2b_pitch_post | 바이어 문의 대응 자료 | 문의 응대용 체크리스트와 후속 메시지 방향 정리 | 카탈로그, 승인 자료, MOQ/납기 안내, 문의 템플릿 | 담당자 | 문의 응대 자료 초안 |"""


def build_asset_checklist(allowed_brand_text: str, restricted_text: str) -> str:
    return f"""| Field | Status |
|---|---|
| product_images | {allowed_brand_text} 제품 이미지: 확인 필요. 외부 이미지 자동 수집 금지. |
| product_videos | 제품 사용감/패키지 영상: 소스 자료 부족. 직접 촬영 또는 사용자 제공 자료 필요. |
| texture_shots | 제형 컷: 검증 필요. 효능 암시 표현 없이 사용. |
| package_shots | 패키지 정면 컷: 필요. 승인 가능한 브랜드만 사용. |
| before_after_restrictions | 전후 이미지는 승인 및 규제 확인 전 사용 금지. |
| brand_approval_materials | {restricted_text}: 명시 승인 전 외부 노출 금지. 승인 가능 브랜드 자료 확인 필요. |
| translation_localization_materials | 중국어 카피 검수 자료: 확인 필요. 현지화 전 외부 사용 금지. |
| proof_documents_if_needed | MOQ/납기 확인 자료, 브랜드 승인 자료, 표현 검토 자료: 검증 필요. |"""


def build_b2b_conversion() -> str:
    return """| content_id | buyer_segment | inquiry_trigger | CTA | landing_or_contact_path | follow_up_message_direction | required_sales_materials |
|---|---|---|---|---|---|---|
| V-001 | 100개 이상 주문 가능한 중국 수입상, 도매상, 소싱 담당자 | 공급 가능 브랜드와 MOQ를 확인하고 싶을 때 | MOQ와 공급 가능 브랜드 문의 | Douyin/Xiaohongshu 노출 -> WeChat 또는 이메일 문의 -> 담당자 확인 | 국가, 예상 수량, 관심 브랜드, 승인 가능 여부, MOQ/납기 확인 | 승인 가능 브랜드 목록, 제품 이미지, 카탈로그, MOQ/납기 안내 |
| F-001 | 중국 온라인 셀러, 도매상, 유통 파트너 | 제품군과 공급 조건을 빠르게 확인하고 싶을 때 | 카탈로그와 공급 가능 여부 문의 | 피드 CTA -> WeChat 또는 이메일 -> 자료 요청 접수 | 관심 제품군, 수량, 판매 채널, 요청 자료 확인 | 카탈로그, 제품 정보, 승인 가능 브랜드 목록, 표현 검토 자료 |
| F-003 | 문의 후 후속 자료가 필요한 잠재 바이어 | 승인 가능 브랜드와 공급 조건 자료가 필요할 때 | 문의 후 공급 자료 요청 | WeChat/이메일 상담 -> 자료 발송 -> 후속 확인 | 제한 브랜드 제외, 구매 수량, 국가, 납기 요구 확인 | 문의 응대 템플릿, MOQ/납기 자료, 브랜드 승인 자료 |"""


def build_risks(restricted_text: str, budget_level: str, execution_period: str) -> str:
    return f"""| Field | Risk |
|---|---|
| cosmetics_claim_risk | 미백, 여드름 치료, 전후 비교, 기능성 단정 표현은 검증 전 사용 금지. 제품 효능 주장은 소스 자료 부족. |
| brand_approval_risk | {restricted_text}은 명시 승인 전 외부 게시, 공용 콘텐츠, 바이어 제안, 광고 카피, 영상 스크립트, 피드 카피에서 제외. |
| China_account_or_platform_risk | 중국 계정 운영 주체, 실명/계정 조건, Xiaohongshu/Douyin/WeChat 플랫폼 정책 확인 필요. 현재 자료만으로 확정 불가. |
| localization_risk | 중국어 번역, 플랫폼 문체, 금지 표현, 소비자/바이어 표현 차이는 현지화 검토 필요. |
| production_resource_risk | {budget_level or 'unknown'} 예산과 {execution_period or '확인 필요'} 실행 기간 기준으로 촬영, 디자인, 검수 리소스 부족 가능. |
| evidence_limitation_risk | 소스 자료 부족으로 시장 반응, 채널 성과, 바이어 수요는 확정 불가. 모든 성과 관련 판단은 검증 필요. |"""


def build_report(
    row: dict[str, str],
    market_report: str,
    channel_strategy: str,
    source_data: dict[str, object],
) -> str:
    research_id = row["research_id"]
    target_country = row.get("target_country", "")
    channels = split_values(row.get("target_channels", ""))
    products = split_values(row.get("target_product_categories", ""))
    allowed, restricted = allowed_brands(row)
    china_target = is_china_target(target_country)
    insufficient = detect_insufficient_evidence(market_report, channel_strategy, source_data)
    evidence_note = "기존 보고서의 소스 자료가 제한되어 검증 필요"
    if not insufficient:
        evidence_note = "제공 자료 기반 내부 검토 가능"

    allowed_brand_text = safe_join(allowed, "승인 가능 브랜드 확인 필요")
    restricted_text = safe_join(restricted, "메디큐브")
    product_text = safe_join(products, "제품군 확인 필요")
    go_or_no_go = "go_with_caution" if insufficient else "go"
    first_channel = "WeChat" if china_target and contains_channel(channels, "WeChat") else first_or_default(channels, "확인 필요")

    return f"""# 숏폼 영상 & 피드 제작 계획 - {research_id}

> 이 보고서는 로컬 CSV 입력, 기존 시장조사 보고서, 기존 채널 콘텐츠 전략 보고서, 사용자 제공 소스 자료만 사용해 생성했습니다. 스크래핑, 라이브 웹리서치, 자동 웹검색, API 호출, 브라우저 자동화, 크롤러, 외부 데이터 수집은 수행하지 않았습니다.

## 증거 및 사용 제한 요약

- 확인된 사실: research_id, target_country, target_channels, target_brands, product categories 등 입력 CSV 값
- 관찰: 사용자 제공 source_notes.md 및 sources.csv에 포함된 수동 관찰이 있을 때만 사용
- 가정: 제한된 자료를 바탕으로 제작 가능성을 정리한 내부 계획 가정
- 검증 필요: 시장 규모, 순위, 판매량, 조회수, 참여율, 플랫폼 성과, 바이어 수요, 규제 사실
- 추천: 외부 사용 전 검증과 브랜드 승인 확인이 필요한 제작 제안
- 전체 증거 상태: {"검증 필요 / 소스 자료 부족 / 확정 불가" if insufficient else "제공 자료 기반 내부 검토 가능"}

### 소스 제한

{source_warning_text(source_data)}

## 1. Executive Summary

| Field | Value |
|---|---|
| summary_conclusion | {target_country} 대상 숏폼/피드 제작은 B2B 바이어 문의 유도와 B2C 소비자 반응 관찰을 분리해 조건부 진행하는 것이 적절합니다. 기존 보고서의 근거가 제한되어 외부 사용 전 검증 필요입니다. |
| priority_content | V-001 B2B 제품군 체크 영상, F-001 B2B 공급 조건 안내 카드, F-003 제품 자료 준비 체크리스트 |
| recommended_channels | {safe_join(channels)} |
| expected_effect | medium: 문의 경로와 제작 우선순위를 정리할 수 있으나 실제 성과는 검증 필요 |
| key_risks | 중국 계정/플랫폼 운영, 현지화, 화장품 표현, 브랜드 승인, 제품 이미지/영상 부족, 소스 자료 부족 |

## 2. Short-form Video Production Plan

{build_video_rows(allowed_brand_text, product_text, evidence_note)}

## 3. Feed Post Production Plan

{build_feed_rows(allowed_brand_text, product_text, evidence_note)}

## 4. Channel-Specific Adaptation

{build_channel_adaptation(channels, china_target)}

## 5. Weekly Production Schedule

{build_weekly_schedule(channels)}

## 6. Asset Checklist

{build_asset_checklist(allowed_brand_text, restricted_text)}

## 7. B2B Inquiry Conversion Plan

{build_b2b_conversion()}

## 8. Risks and Compliance

{build_risks(restricted_text, row.get("budget_level", ""), row.get("execution_period", ""))}

## 9. Final Recommendation

| Field | Value |
|---|---|
| go_or_no_go | {go_or_no_go} |
| first_video_to_make | V-001: B2B 제품군 체크 영상 |
| first_feed_to_make | F-001: B2B 공급 조건 안내 카드 |
| next_actions | 1. 승인 가능 브랜드 확인 2. 제품 이미지/영상 자료 정리 3. 중국어 카피와 화장품 표현 검토 4. {first_channel} 또는 이메일 문의 경로 정리 5. 외부 게시 전 검증 및 승인 |

## 내부 검토 메모

- 이 계획은 내부 제작 준비용 초안입니다.
- 실제 게시, 광고, 바이어 제안, 외부 영상 스크립트, 피드 카피에는 추가 검증이 필요합니다.
- 시장 규모, 순위, 판매량, 조회수, 참여율, 플랫폼 성과, 바이어 수요는 생성하지 않았습니다.
- 메디큐브는 명시 승인 전 외부 추천에서 제외했습니다.
"""


def write_report(output_dir: Path, research_id: str, report: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"short_form_feed_plan_{research_id}.md"
    output_path.write_text(report, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local short-form video and feed production plan.")
    parser.add_argument("--research-id", required=True, help="Research ID to generate, for example MR-001.")
    parser.add_argument("--input", default="data/research_inputs_sample.csv", help="Input research CSV path.")
    parser.add_argument(
        "--market-report-dir",
        default="output",
        help="Directory containing market_research_report_{research_id}.md.",
    )
    parser.add_argument(
        "--channel-strategy-dir",
        default="output",
        help="Directory containing channel_content_strategy_{research_id}.md.",
    )
    parser.add_argument(
        "--source-root",
        default="data/source_materials/market_research",
        help="Root folder for user-provided market research source materials.",
    )
    parser.add_argument("--output-dir", default="output", help="Output directory for generated plans.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = resolve_path(args.input)
    market_report_dir = resolve_path(args.market_report_dir)
    channel_strategy_dir = resolve_path(args.channel_strategy_dir)
    source_root = resolve_path(args.source_root)
    output_dir = resolve_path(args.output_dir)

    rows = read_business_csv(input_path)
    validate_input_columns(rows, input_path)
    row = select_research_row(rows, args.research_id)

    market_report_path = market_report_dir / f"market_research_report_{args.research_id}.md"
    channel_strategy_path = channel_strategy_dir / f"channel_content_strategy_{args.research_id}.md"
    market_report = read_required_text(market_report_path, "market research report")
    channel_strategy = read_required_text(channel_strategy_path, "channel content strategy report")
    source_data = load_source_materials(source_root, args.research_id)

    report = build_report(row, market_report, channel_strategy, source_data)
    output_path = write_report(output_dir, args.research_id, report)

    print("PASS: short-form/feed production plan generated")
    print(f"research_id={args.research_id}")
    print(f"output_path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
