"""Generate scored buyer leads from local buyer master CSV data.

This script uses only local CSV files. It does not perform scraping, live web
research, automatic web search, browser automation, API calls, requests,
crawling, buyer enrichment, credit checks, or external data collection.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "buyers_master_sample.csv"
DEFAULT_OUTPUT = ROOT / "data" / "buyers_scored_sample.csv"
DEFAULT_BRANDS = ROOT / "data" / "brands_master.csv"

SCORING_VERSION = "buyer_scoring_v1.0"

OUTPUT_COLUMNS = [
    "buyer_id",
    "score_total",
    "priority_tier",
    "scoring_summary",
    "positive_factors",
    "negative_factors",
    "risk_flags",
    "approval_block",
    "recommended_next_action",
    "scoring_version",
    "scored_at",
]

REQUIRED_INPUT_COLUMNS = [
    "buyer_id",
    "company_name",
    "country",
    "buyer_type",
    "sales_channel",
    "platform",
    "contact_email",
    "wechat_id",
    "whatsapp",
    "interested_brands",
    "estimated_order_qty",
    "moq_fit",
    "china_relevance",
    "payment_risk",
    "repeat_purchase_potential",
    "lead_status",
    "next_action",
    "approval_warning",
    "proposal_brand_check",
]

BRAND_COLUMNS = [
    "brand_ko",
    "approval_required",
    "proposal_allowed",
]

SEA_COUNTRIES = {
    "vietnam",
    "thailand",
    "indonesia",
    "malaysia",
    "philippines",
    "singapore",
}

BUYER_TYPE_POINTS = {
    "importer": 12,
    "distributor": 12,
    "wholesaler": 10,
    "beauty_chain": 10,
    "trading_company": 6,
    "online_seller": 5,
    "live_commerce": 5,
    "influencer_commerce": 3,
    "retailer": 4,
    "unknown": -5,
    "other": 0,
}

SALES_CHANNEL_POINTS = {
    "distributor_network": 10,
    "b2b_platform": 8,
    "mixed": 6,
    "marketplace": 5,
    "offline": 5,
    "online": 4,
    "social_commerce": 4,
    "live_commerce": 4,
    "unknown": -3,
    "other": 0,
}

PLATFORM_POINTS = {
    "wechat": 8,
    "douyin": 6,
    "xiaohongshu": 6,
    "1688": 6,
    "taobao": 5,
    "tiktok": 4,
    "instagram": 3,
    "shopee": 5,
    "lazada": 5,
    "amazon": 4,
    "telegram": 3,
    "vk": 3,
    "offline": 2,
    "website": 2,
    "unknown": -2,
    "other": 0,
}

LEAD_STATUS_POINTS = {
    "new": 0,
    "researching": 2,
    "contacted": 5,
    "replied": 10,
    "qualified": 15,
    "sample_requested": 15,
    "quotation_sent": 12,
    "negotiating": 15,
    "won": 5,
    "lost": -30,
    "on_hold": -15,
    "disqualified": -40,
}

CONTACT_FIELDS = [
    "contact_email",
    "wechat_id",
    "whatsapp",
    "contact_name",
    "contact_phone",
    "website",
    "sns_url",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def clean(value: str | None) -> str:
    return (value or "").strip()


def lower(value: str | None) -> str:
    return clean(value).lower()


def split_brands(value: str) -> list[str]:
    normalized = value.replace(",", ";")
    return [item.strip() for item in normalized.split(";") if item.strip()]


def read_csv_rows(path: Path, label: str) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        fail(f"{label} CSV not found: {rel(path)}")

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                fail(f"{label} CSV has no header row: {rel(path)}")
            rows = [{key: clean(value) for key, value in row.items()} for row in reader]
            return reader.fieldnames, rows
    except UnicodeDecodeError as exc:
        fail(f"{label} CSV is not readable with utf-8-sig: {exc}")


def validate_input(columns: list[str], rows: list[dict[str, str]]) -> None:
    missing = [column for column in REQUIRED_INPUT_COLUMNS if column not in columns]
    if missing:
        fail(f"input CSV missing required columns: {', '.join(missing)}")

    seen: set[str] = set()
    for row_index, row in enumerate(rows, start=2):
        buyer_id = clean(row.get("buyer_id"))
        if not buyer_id:
            fail(f"buyer_id is missing at input row {row_index}; file was not scored")
        if buyer_id in seen:
            fail(f"duplicate buyer_id found: {buyer_id}; file was not scored")
        seen.add(buyer_id)


def load_restricted_brands(path: Path) -> set[str]:
    restricted = {"메디큐브"}
    if not path.exists():
        return restricted

    columns, rows = read_csv_rows(path, "brands master")
    missing = [column for column in BRAND_COLUMNS if column not in columns]
    if missing:
        fail(f"brands master missing required columns: {', '.join(missing)}")

    for row in rows:
        brand = clean(row.get("brand_ko"))
        if not brand:
            continue
        approval_required = lower(row.get("approval_required")) == "true"
        proposal_allowed = lower(row.get("proposal_allowed")) != "true"
        if approval_required or proposal_allowed:
            restricted.add(brand)
    return restricted


def parse_quantity(value: str) -> int | None:
    text = clean(value).replace(",", "")
    if not text:
        return None
    try:
        quantity = int(text)
    except ValueError:
        return None
    if quantity <= 0:
        return None
    return quantity


def add_factor(factors: list[str], text: str) -> None:
    if text and text not in factors:
        factors.append(text)


def add_flag(flags: set[str], flag: str) -> None:
    if flag:
        flags.add(flag)


def clamp(score: int) -> int:
    return max(0, min(100, score))


def is_china_row(row: dict[str, str]) -> bool:
    country = lower(row.get("country"))
    china_relevance = lower(row.get("china_relevance"))
    platform = lower(row.get("platform"))
    return (
        "china" in country
        or "중국" in country
        or china_relevance in {"high", "medium"}
        or platform in {"wechat", "douyin", "xiaohongshu", "taobao", "1688"}
    )


def has_contact(row: dict[str, str]) -> bool:
    return any(clean(row.get(field)) for field in CONTACT_FIELDS)


def has_explicit_approval(row: dict[str, str]) -> bool:
    approval_text = " ".join(
        [
            lower(row.get("approval_warning")),
            lower(row.get("proposal_brand_check")),
            lower(row.get("notes")),
        ]
    )
    return "explicit_approval" in approval_text or "approved" in approval_text


def approval_blocked(row: dict[str, str], restricted_brands: set[str]) -> bool:
    if clean(row.get("approval_warning")):
        return True
    if lower(row.get("proposal_brand_check")) == "approval_required_review":
        return True

    brands = split_brands(row.get("interested_brands", ""))
    if any(brand in restricted_brands for brand in brands):
        return not has_explicit_approval(row)
    return False


def default_tier(score: int) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    return "Hold"


def cap_tier(tier: str, cap: str) -> str:
    order = {"A": 3, "B": 2, "C": 1, "Hold": 0}
    return tier if order[tier] <= order[cap] else cap


def score_moq(row: dict[str, str], flags: set[str], positive: list[str], negative: list[str]) -> int:
    moq_fit = lower(row.get("moq_fit"))
    if moq_fit == "yes":
        add_factor(positive, "MOQ 충족")
        return 20
    if moq_fit == "no":
        add_flag(flags, "moq_not_met")
        add_factor(negative, "MOQ 미달")
        return -30
    add_flag(flags, "moq_unknown")
    add_factor(negative, "MOQ 확인 필요")
    return -10


def score_quantity(row: dict[str, str], flags: set[str], positive: list[str], negative: list[str]) -> int:
    quantity = parse_quantity(row.get("estimated_order_qty", ""))
    if quantity is None:
        add_flag(flags, "quantity_unconfirmed")
        add_factor(negative, "예상 주문 수량 미확인")
        return 0
    if quantity >= 500:
        add_factor(positive, "예상 주문 수량 500개 이상")
        return 10
    if quantity >= 100:
        add_factor(positive, "예상 주문 수량 100개 이상")
        return 5
    add_factor(negative, "예상 주문 수량 100개 미만")
    return -10


def score_country(row: dict[str, str], flags: set[str], positive: list[str], negative: list[str]) -> int:
    country = lower(row.get("country"))
    if not country or country == "unknown":
        add_flag(flags, "country_unknown")
        add_factor(negative, "국가 미확인")
        return -5
    if "china" in country or "중국" in country:
        add_factor(positive, "중국 우선 시장")
        return 15
    if country in SEA_COUNTRIES:
        add_factor(positive, "동남아 활성 시장")
        return 8
    if country == "russia":
        add_factor(positive, "러시아 활성 시장")
        return 8
    add_factor(positive, "해외 바이어 후보")
    return 3


def score_china_relevance(row: dict[str, str], positive: list[str], negative: list[str]) -> int:
    relevance = lower(row.get("china_relevance"))
    if relevance == "high":
        add_factor(positive, "중국 관련성 높음")
        return 10
    if relevance == "medium":
        add_factor(positive, "중국 관련성 보통")
        return 5
    if relevance == "unknown":
        add_factor(negative, "중국 관련성 미확인")
        return -2
    return 0


def score_lookup(
    row: dict[str, str],
    field: str,
    points: dict[str, int],
    unknown_flag: str | None,
    positive_label: str,
    negative_label: str,
    flags: set[str],
    positive: list[str],
    negative: list[str],
) -> int:
    value = lower(row.get(field))
    score = points.get(value, 0)
    if value == "unknown" and unknown_flag:
        add_flag(flags, unknown_flag)
    if score > 0:
        add_factor(positive, f"{positive_label}: {clean(row.get(field))}")
    elif score < 0:
        add_factor(negative, f"{negative_label}: {clean(row.get(field)) or 'unknown'}")
    return score


def score_payment(row: dict[str, str], flags: set[str], positive: list[str], negative: list[str]) -> int:
    risk = lower(row.get("payment_risk"))
    if risk == "low":
        add_factor(positive, "결제 리스크 낮음")
        return 8
    if risk == "medium":
        add_flag(flags, "payment_risk_medium")
        add_factor(negative, "결제 리스크 보통")
        return -5
    if risk == "high":
        add_flag(flags, "payment_risk_high")
        add_factor(negative, "결제 리스크 높음")
        return -20
    add_flag(flags, "payment_risk_unknown")
    add_factor(negative, "결제 리스크 미확인")
    return -3


def score_repeat(row: dict[str, str], positive: list[str], negative: list[str]) -> int:
    value = lower(row.get("repeat_purchase_potential"))
    if value == "high":
        add_factor(positive, "반복구매 가능성 높음")
        return 10
    if value == "medium":
        add_factor(positive, "반복구매 가능성 보통")
        return 5
    if value == "low":
        add_factor(negative, "반복구매 가능성 낮음")
        return -5
    return 0


def score_lead_status(row: dict[str, str], flags: set[str], positive: list[str], negative: list[str]) -> int:
    status = lower(row.get("lead_status"))
    score = LEAD_STATUS_POINTS.get(status, 0)
    if status in {"qualified", "sample_requested", "negotiating", "quotation_sent", "replied", "contacted"}:
        add_factor(positive, f"리드 상태 진행 중: {clean(row.get('lead_status'))}")
    if status in {"lost", "on_hold", "disqualified"}:
        add_factor(negative, f"리드 상태 주의: {clean(row.get('lead_status'))}")
    if status == "on_hold":
        add_flag(flags, "on_hold")
    return score


def score_contact(row: dict[str, str], flags: set[str], positive: list[str], negative: list[str]) -> int:
    score = 0
    if clean(row.get("contact_email")):
        score += 2
        add_factor(positive, "이메일 연락처 있음")
    if is_china_row(row) and clean(row.get("wechat_id")):
        score += 5
        add_factor(positive, "중국 바이어용 WeChat 연락처 있음")
    if clean(row.get("whatsapp")):
        score += 2
        add_factor(positive, "WhatsApp 연락처 있음")
    if has_contact(row):
        add_flag(flags, "privacy_sensitive_contact")
    else:
        score -= 10
        add_flag(flags, "contact_incomplete")
        add_factor(negative, "연락처 미확인")
    return score


def score_next_action(row: dict[str, str], flags: set[str], positive: list[str], negative: list[str]) -> int:
    if clean(row.get("next_action")):
        add_factor(positive, "다음 액션 있음")
        return 5
    add_flag(flags, "next_action_missing")
    add_factor(negative, "다음 액션 없음")
    return -5


def build_next_action(row: dict[str, str], tier: str, approval_block: bool) -> str:
    moq_fit = lower(row.get("moq_fit"))
    payment_risk = lower(row.get("payment_risk"))
    existing_action = clean(row.get("next_action"))

    if approval_block:
        return "내부 승인 검토를 먼저 진행하고, 승인 전에는 해당 브랜드의 외부 제안/피치/견적/공개 콘텐츠/광고 문구를 진행하지 않습니다."
    if moq_fit == "no":
        return "바이어가 MOQ 100개 이상을 맞출 수 있는지 확인하고, 수량 확대 또는 카테고리 묶음 가능성을 문의합니다."
    if moq_fit == "unknown":
        return "제안 전 예상 주문 수량과 MOQ 충족 가능성을 먼저 확인합니다."
    if payment_risk == "high":
        return "관리자 검토와 안전한 결제 조건 확인 후 후속 제안 여부를 판단합니다."
    if tier == "A":
        return "승인 가능 브랜드 기준으로 제안서 또는 견적 검토를 준비합니다."
    if tier == "B":
        return "부족한 정보를 확인하고 후속 상담 자료를 준비합니다."
    if tier == "C":
        return "낮은 우선순위로 관리하며 추가 관심 브랜드와 주문 가능 수량을 확인합니다."
    return existing_action or "핵심 정보 확인 후 내부 검토를 진행합니다."


def build_summary(row: dict[str, str], tier: str, score: int, approval_block: bool) -> str:
    buyer_id = row["buyer_id"]
    if approval_block:
        return f"{buyer_id}는 상업적 관심 요소가 있어도 승인 필요 브랜드가 포함되어 priority_tier가 Hold로 지정되었습니다. 이 점수는 내부 우선순위 참고용이며 바이어 실제성, 신용도, 구매 가능성을 검증하지 않습니다."
    if tier == "A":
        return f"{buyer_id}는 MOQ, 시장 우선순위, 연락 가능성 기준에서 내부 후속 우선순위가 높습니다. 점수 {score}점은 내부 참고용이며 구매 확정이나 신용 검증이 아닙니다."
    if tier == "B":
        return f"{buyer_id}는 일부 긍정 요소가 있으나 결제 리스크, 정보 부족, 후속 확인이 필요합니다. 점수 {score}점은 내부 참고용입니다."
    if tier == "C":
        return f"{buyer_id}는 MOQ 또는 정보 완성도 측면에서 낮은 우선순위로 분류되었습니다. 추가 확인 전 외부 제안은 신중해야 합니다."
    return f"{buyer_id}는 핵심 이슈가 있어 우선 진행을 보류해야 합니다. 점수 {score}점은 내부 참고용이며 바이어 검증 결과가 아닙니다."


def score_row(row: dict[str, str], restricted_brands: set[str], scored_at: str) -> dict[str, str]:
    flags: set[str] = {"source_manual_only", "buyer_unverified"}
    positive: list[str] = []
    negative: list[str] = []

    if is_china_row(row):
        add_flag(flags, "china_platform_operation_unverified")

    score = 50
    score += score_moq(row, flags, positive, negative)
    score += score_quantity(row, flags, positive, negative)
    score += score_country(row, flags, positive, negative)
    score += score_china_relevance(row, positive, negative)
    score += score_lookup(row, "buyer_type", BUYER_TYPE_POINTS, "buyer_type_unknown", "buyer type 적합", "buyer type 확인 필요", flags, positive, negative)
    score += score_lookup(row, "sales_channel", SALES_CHANNEL_POINTS, None, "판매 채널 적합", "판매 채널 확인 필요", flags, positive, negative)
    score += score_lookup(row, "platform", PLATFORM_POINTS, None, "플랫폼 적합", "플랫폼 확인 필요", flags, positive, negative)
    score += score_payment(row, flags, positive, negative)
    score += score_repeat(row, positive, negative)
    score += score_lead_status(row, flags, positive, negative)

    approval_block = approval_blocked(row, restricted_brands)
    if approval_block:
        add_flag(flags, "approval_required_brand")
        add_factor(negative, "승인 필요 브랜드 포함")

    score += score_contact(row, flags, positive, negative)
    score += score_next_action(row, flags, positive, negative)

    score = clamp(score)
    tier = default_tier(score)

    if approval_block:
        tier = "Hold"
    if lower(row.get("lead_status")) == "disqualified":
        tier = "Hold"
    if lower(row.get("lead_status")) == "lost":
        tier = cap_tier(tier, "C")
    if lower(row.get("payment_risk")) == "high":
        tier = cap_tier(tier, "B")
    if lower(row.get("moq_fit")) == "no":
        tier = cap_tier(tier, "B")
    if not clean(row.get("company_name")) or not clean(row.get("country")):
        tier = "Hold"

    next_action = build_next_action(row, tier, approval_block)
    summary = build_summary(row, tier, score, approval_block)

    return {
        "buyer_id": row["buyer_id"],
        "score_total": str(score),
        "priority_tier": tier,
        "scoring_summary": summary,
        "positive_factors": "; ".join(positive) if positive else "해당 없음",
        "negative_factors": "; ".join(negative) if negative else "해당 없음",
        "risk_flags": "; ".join(sorted(flags)),
        "approval_block": "true" if approval_block else "false",
        "recommended_next_action": next_action,
        "scoring_version": SCORING_VERSION,
        "scored_at": scored_at,
    }


def write_scored_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate scored buyer lead CSV from local buyer master CSV.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input buyer master CSV path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output scored buyer CSV path")
    parser.add_argument("--brands", default=str(DEFAULT_BRANDS), help="Optional local brands master CSV path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)
    brands_path = resolve_path(args.brands)

    columns, rows = read_csv_rows(input_path, "input buyer master")
    validate_input(columns, rows)
    restricted_brands = load_restricted_brands(brands_path)
    scored_at = date.today().isoformat()
    scored_rows = [score_row(row, restricted_brands, scored_at) for row in rows]
    write_scored_rows(output_path, scored_rows)

    print("PASS: buyer scores generated")
    print(f"input={rel(input_path)}")
    print(f"output={rel(output_path)}")
    print(f"rows={len(scored_rows)}")
    for row in scored_rows:
        print(
            "buyer_id={buyer_id} score_total={score_total} priority_tier={priority_tier} approval_block={approval_block}".format(
                **row
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

