"""Generate internal-review proposal message drafts from local CSV files.

This script reads only local files. It does not send emails, DMs, WeChat
messages, WhatsApp messages, platform messages, or any external communication.
It does not perform scraping, live web research, automatic web search, APIs,
browser automation, crawlers, buyer enrichment, credit checks, requests,
messaging automation, or external data collection.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUYERS = ROOT / "data" / "buyers_master_sample.csv"
DEFAULT_SCORES = ROOT / "data" / "buyers_scored_sample.csv"
DEFAULT_BRANDS = ROOT / "data" / "brands_master.csv"
DEFAULT_CSV_OUTPUT = ROOT / "data" / "proposal_messages_sample.csv"
DEFAULT_MD_OUTPUT = ROOT / "output" / "proposal_messages_sample.md"

OUTPUT_COLUMNS = [
    "message_id",
    "buyer_id",
    "company_name",
    "country",
    "language",
    "priority_tier",
    "approval_block",
    "message_status",
    "message_type",
    "subject_or_opening",
    "message_body",
    "recommended_brands",
    "excluded_brands",
    "compliance_notes",
    "required_internal_review",
    "next_action",
    "generated_at",
]

BUYER_COLUMNS = [
    "buyer_id",
    "company_name",
    "country",
    "language",
    "interested_brands",
    "interested_categories",
    "estimated_order_qty",
    "moq_fit",
    "payment_risk",
    "lead_status",
    "approval_warning",
    "proposal_brand_check",
]

SCORE_COLUMNS = [
    "buyer_id",
    "priority_tier",
    "risk_flags",
    "approval_block",
    "recommended_next_action",
]

BRAND_COLUMNS = [
    "brand_ko",
    "approval_required",
    "proposal_allowed",
]

CONTACT_FIELD_NAMES = {
    "contact_email",
    "contact_phone",
    "wechat_id",
    "whatsapp",
}


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


def read_csv_rows(path: Path, label: str) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        fail(f"{label} not found: {rel(path)}")

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                fail(f"{label} has no header row: {rel(path)}")
            rows = [{key: clean(value) for key, value in row.items()} for row in reader]
            return reader.fieldnames, rows
    except UnicodeDecodeError as exc:
        fail(f"{label} is not readable with utf-8-sig: {exc}")


def validate_columns(columns: list[str], required: list[str], label: str) -> None:
    missing = [column for column in required if column not in columns]
    if missing:
        fail(f"{label} missing required columns: {', '.join(missing)}")


def index_by_buyer_id(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row_index, row in enumerate(rows, start=2):
        buyer_id = clean(row.get("buyer_id"))
        if not buyer_id:
            fail(f"{label} has blank buyer_id at row {row_index}")
        if buyer_id in indexed:
            fail(f"{label} has duplicate buyer_id: {buyer_id}")
        indexed[buyer_id] = row
    return indexed


def split_values(value: str) -> list[str]:
    normalized = value.replace(",", ";")
    return [item.strip() for item in normalized.split(";") if item.strip()]


def bool_text(value: str | None) -> bool:
    return lower(value) == "true"


def load_brand_rules(path: Path) -> dict[str, dict[str, bool]]:
    rules = {"메디큐브": {"approval_required": True, "proposal_allowed": False}}
    if not path.exists():
        print(f"WARN: brands master not found: {rel(path)}; using cautious default rules")
        return rules

    columns, rows = read_csv_rows(path, "brands master")
    validate_columns(columns, BRAND_COLUMNS, "brands master")
    for row in rows:
        brand = clean(row.get("brand_ko"))
        if not brand:
            continue
        rules[brand] = {
            "approval_required": bool_text(row.get("approval_required")),
            "proposal_allowed": bool_text(row.get("proposal_allowed")),
        }
    return rules


def is_safe_brand(brand: str, brand_rules: dict[str, dict[str, bool]]) -> bool:
    if brand == "메디큐브":
        return False
    rule = brand_rules.get(brand)
    if rule is None:
        return False
    return not rule["approval_required"] and rule["proposal_allowed"]


def select_brands(
    buyer: dict[str, str],
    brand_rules: dict[str, dict[str, bool]],
    approval_blocked: bool,
) -> tuple[list[str], list[str]]:
    safe: list[str] = []
    excluded: list[str] = []
    for brand in split_values(buyer.get("interested_brands", "")):
        if is_safe_brand(brand, brand_rules) and not approval_blocked:
            safe.append(brand)
        else:
            excluded.append(brand)
    return safe, excluded


def output_language(raw_language: str) -> str:
    language = clean(raw_language)
    if language in {"Chinese", "Korean", "English"}:
        return language
    return "English"


def has_missing_key_info(buyer: dict[str, str]) -> bool:
    return not clean(buyer.get("buyer_id")) or not clean(buyer.get("company_name")) or not clean(buyer.get("country"))


def approval_is_blocked(buyer: dict[str, str], score: dict[str, str]) -> bool:
    if bool_text(score.get("approval_block")):
        return True
    if lower(buyer.get("proposal_brand_check")) == "approval_required_review":
        return True
    if clean(buyer.get("approval_warning")):
        return True
    if "메디큐브" in split_values(buyer.get("interested_brands", "")):
        return True
    return False


def determine_status(buyer: dict[str, str], score: dict[str, str], approval_blocked: bool) -> str:
    if approval_blocked:
        return "blocked_approval_required"
    if has_missing_key_info(buyer):
        return "needs_more_buyer_info"
    if lower(buyer.get("payment_risk")) == "high":
        return "needs_payment_risk_review"
    if lower(buyer.get("moq_fit")) in {"no", "unknown"}:
        return "needs_moq_confirmation"
    return "draft_ready_for_internal_review"


def determine_type(buyer: dict[str, str], score: dict[str, str], status: str, approval_blocked: bool) -> str:
    if approval_blocked:
        return "approval_review_required"
    lead_status = lower(buyer.get("lead_status"))
    if lead_status in {"contacted", "replied", "qualified"}:
        return "follow_up"
    if status == "needs_moq_confirmation" or clean(score.get("priority_tier")) in {"C", "Hold"}:
        return "low_priority_nurture"
    if lower(buyer.get("moq_fit")) == "yes" and clean(score.get("priority_tier")) == "A":
        return "quotation_intro"
    if clean(buyer.get("interested_categories")):
        return "product_category_intro"
    return "first_contact"


def build_required_review(
    buyer: dict[str, str],
    status: str,
    language: str,
    approval_blocked: bool,
    recommended_brands: list[str],
) -> str:
    if approval_blocked:
        return "true"
    if status != "draft_ready_for_internal_review":
        return "true"
    if language != "Korean":
        return "true"
    if lower(buyer.get("payment_risk")) in {"high", "unknown", ""}:
        return "true"
    if lower(buyer.get("moq_fit")) in {"no", "unknown", ""}:
        return "true"
    if not recommended_brands:
        return "true"
    return "false"


def build_subject(language: str, message_type: str) -> str:
    if message_type == "approval_review_required":
        return "Internal approval review required before proposal"
    if message_type == "quotation_intro":
        if language == "Chinese":
            return "内部审核草稿：K-beauty供货报价准备"
        if language == "Korean":
            return "내부 검토용 초안: K-뷰티 견적 준비"
        return "Internal review draft: K-beauty quotation preparation"
    if message_type == "follow_up":
        if language == "Chinese":
            return "内部审核草稿：K-beauty产品类别跟进"
        if language == "Korean":
            return "내부 검토용 초안: K-뷰티 제품군 후속 확인"
        return "Internal review draft: K-beauty category follow-up"
    if message_type == "low_priority_nurture":
        return "Internal review draft: cautious K-beauty follow-up"
    if message_type == "product_category_intro":
        return "Internal review draft: K-beauty category discussion"
    return "Internal review draft: K-beauty supply introduction"


def brand_text(brands: list[str], categories: str, language: str) -> str:
    if brands:
        joined = "; ".join(brands)
        if language == "Chinese":
            return f"可内部审核的品牌候选：{joined}"
        if language == "Korean":
            return f"내부 검토 가능한 브랜드 후보: {joined}"
        return f"Brand candidates for internal review: {joined}"
    if categories:
        if language == "Chinese":
            return f"先以产品类别讨论为主：{categories}"
        if language == "Korean":
            return f"우선 제품군 중심으로 논의: {categories}"
        return f"Start with category-level discussion: {categories}"
    if language == "Chinese":
        return "先确认目标产品类别后再准备品牌建议。"
    if language == "Korean":
        return "목표 제품군을 먼저 확인한 뒤 브랜드 제안을 검토합니다."
    return "Confirm target product categories before reviewing brand suggestions."


def build_message_body(
    buyer: dict[str, str],
    score: dict[str, str],
    language: str,
    message_type: str,
    recommended_brands: list[str],
    excluded_brands: list[str],
) -> str:
    company = clean(buyer.get("company_name"))
    categories = clean(buyer.get("interested_categories"))
    brands_or_categories = brand_text(recommended_brands, categories, language)
    disclaimer_ko = "내부 검토용 초안입니다. 외부로 발송되지 않았으며, 발송 전 내부 검토가 필요합니다."

    if message_type == "approval_review_required":
        excluded = "; ".join(excluded_brands) if excluded_brands else "승인 필요 브랜드"
        localized_note = ""
        if language == "Chinese":
            localized_note = "内部审核提示：该品牌需先完成内部批准，批准前不得对外提案或报价。\n"
        return (
            f"{disclaimer_ko}\n"
            f"{localized_note}"
            f"내부 승인 검토 필요: {company}의 관심 브랜드 중 {excluded}가 승인 필요 또는 제안 제한 대상으로 확인되었습니다.\n"
            "승인 전에는 해당 브랜드의 외부 제안, buyer-facing pitch, 견적, 공개 콘텐츠, 광고 문구를 진행하지 마십시오.\n"
            "다음 단계는 승인 가능 여부를 내부에서 확인하고, 필요 시 승인 가능한 브랜드 또는 제품군 중심의 대안을 별도로 검토하는 것입니다.\n"
            "이 문구는 내부 지침이며 구매자에게 보낼 제안문이 아닙니다."
        )

    if language == "Chinese":
        return (
            f"{disclaimer_ko}\n"
            "以下内容为内部审核草稿，不是已发送的信息。\n"
            f"您好，{company}。我们可在内部确认后，就K-beauty批发/出口合作进行谨慎沟通。\n"
            f"{brands_or_categories}\n"
            "一般业务条件可按MOQ 100+件、交期约20-30天作为初步讨论基础，但最终条件需确认产品、数量、库存和供应情况后再定。\n"
            "如需下一步沟通，请先内部确认品牌权限、数量、付款风险、翻译和合规表达。"
        )

    if language == "Korean":
        return (
            f"{disclaimer_ko}\n"
            f"{company} 대상 K-뷰티 B2B 공급 논의를 위한 보수적인 초안입니다.\n"
            f"{brands_or_categories}\n"
            "MOQ 100개 이상 및 배송 리드타임 20-30일은 일반적인 논의 기준이며, 최종 조건은 제품, 수량, 재고, 공급 가능 여부 확인 후 정해야 합니다.\n"
            "외부 발송 전 브랜드 승인, 가격/재고, 화장품 표현, 결제 리스크, 현지화 검토가 필요합니다."
        )

    return (
        f"{disclaimer_ko}\n"
        "This is an internal-review draft only and has not been sent externally.\n"
        f"Hello {company}, this draft may be used internally to review a cautious K-beauty wholesale/export discussion.\n"
        f"{brands_or_categories}\n"
        "General business discussion may start from MOQ 100+ units and an estimated 20-30 day delivery lead time, but final terms require confirmation of product, quantity, availability, and supply conditions.\n"
        "Before any external use, review brand approval, quantity fit, payment risk, cosmetics wording, and localization."
    )


def build_compliance_notes(
    buyer: dict[str, str],
    score: dict[str, str],
    language: str,
    approval_blocked: bool,
    excluded_brands: list[str],
    recommended_brands: list[str],
) -> str:
    notes = [
        "내부 검토용 초안",
        "외부 발송 전 검토 필요",
        "가격/재고/유통기한 확인 필요",
        "화장품 표현 검토 필요",
        "자동 발송 없음",
    ]
    if approval_blocked or excluded_brands:
        notes.append("브랜드 승인 확인 필요")
    if language != "Korean":
        notes.append("현지화/번역 검토 필요")
    if lower(buyer.get("moq_fit")) in {"no", "unknown", ""}:
        notes.append("MOQ 확인 필요")
    if lower(buyer.get("payment_risk")) in {"high", "unknown", ""}:
        notes.append("결제 리스크 검토 필요")
    if "buyer_unverified" in lower(score.get("risk_flags")):
        notes.append("바이어 실제성은 이 자동화에서 검증하지 않음")
    if "source_manual_only" in lower(score.get("risk_flags")):
        notes.append("수동 제공 데이터 기반")
    if not recommended_brands:
        notes.append("안전한 추천 브랜드 없음 또는 제품군 중심 논의 필요")
    return "; ".join(dict.fromkeys(notes))


def build_next_action(
    buyer: dict[str, str],
    score: dict[str, str],
    status: str,
    approval_blocked: bool,
    recommended_brands: list[str],
) -> str:
    if approval_blocked:
        return "내부 승인 검토를 먼저 진행하고, 승인 전에는 외부 제안/피치/견적/공개 콘텐츠/광고 문구를 진행하지 않습니다."
    if status == "needs_moq_confirmation":
        return "외부 제안 전 예상 주문 수량과 MOQ 100+ 충족 가능성을 내부에서 먼저 확인합니다."
    if status == "needs_payment_risk_review":
        return "외부 제안 전 결제 조건과 결제 리스크를 내부 검토합니다."
    if not recommended_brands:
        return "승인 가능한 브랜드가 없으므로 제품군 중심 메시지로 내부 재검토합니다."
    return clean(score.get("recommended_next_action")) or "브랜드 승인과 제품 조건을 확인한 뒤 내부 검토를 진행합니다."


def build_message(
    index: int,
    buyer: dict[str, str],
    score: dict[str, str],
    brand_rules: dict[str, dict[str, bool]],
    generated_at: str,
) -> dict[str, str]:
    approval_blocked = approval_is_blocked(buyer, score)
    recommended_brands, excluded_brands = select_brands(buyer, brand_rules, approval_blocked)
    language = output_language(buyer.get("language", ""))
    status = determine_status(buyer, score, approval_blocked)
    message_type = determine_type(buyer, score, status, approval_blocked)
    subject = build_subject(language, message_type)
    body = build_message_body(buyer, score, language, message_type, recommended_brands, excluded_brands)
    required_review = build_required_review(buyer, status, language, approval_blocked, recommended_brands)
    compliance_notes = build_compliance_notes(
        buyer,
        score,
        language,
        approval_blocked,
        excluded_brands,
        recommended_brands,
    )
    next_action = build_next_action(buyer, score, status, approval_blocked, recommended_brands)

    return {
        "message_id": f"MSG-{index:04d}",
        "buyer_id": clean(buyer.get("buyer_id")),
        "company_name": clean(buyer.get("company_name")),
        "country": clean(buyer.get("country")),
        "language": language,
        "priority_tier": clean(score.get("priority_tier")),
        "approval_block": "true" if approval_blocked else "false",
        "message_status": status,
        "message_type": message_type,
        "subject_or_opening": subject,
        "message_body": body,
        "recommended_brands": "; ".join(recommended_brands),
        "excluded_brands": "; ".join(excluded_brands),
        "compliance_notes": compliance_notes,
        "required_internal_review": required_review,
        "next_action": next_action,
        "generated_at": generated_at,
    }


def validate_join(buyer_index: dict[str, dict[str, str]], score_rows: list[dict[str, str]]) -> None:
    buyer_ids = set(buyer_index)
    score_ids = {clean(row.get("buyer_id")) for row in score_rows}
    missing_buyers = sorted(score_ids - buyer_ids)
    extra_buyers = sorted(buyer_ids - score_ids)
    if missing_buyers:
        fail(f"buyer_id present in scores but missing from buyers: {', '.join(missing_buyers)}")
    if extra_buyers:
        fail(f"buyer_id present in buyers but missing from scores: {', '.join(extra_buyers)}")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Proposal Messages Sample",
        "",
        "내부 검토용 초안입니다. 이 파일의 메시지는 외부로 발송되지 않았으며, 자동 발송 기능도 포함하지 않습니다.",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['message_id']} - {row['buyer_id']}",
                "",
                f"- company_name: {row['company_name']}",
                f"- country: {row['country']}",
                f"- language: {row['language']}",
                f"- priority_tier: {row['priority_tier']}",
                f"- approval_block: {row['approval_block']}",
                f"- message_status: {row['message_status']}",
                f"- message_type: {row['message_type']}",
                f"- recommended_brands: {row['recommended_brands']}",
                f"- excluded_brands: {row['excluded_brands']}",
                f"- required_internal_review: {row['required_internal_review']}",
                "",
                f"### Subject or Opening",
                "",
                row["subject_or_opening"],
                "",
                "### Message Body",
                "",
                row["message_body"],
                "",
                "### Compliance Notes",
                "",
                row["compliance_notes"],
                "",
                "### Next Action",
                "",
                row["next_action"],
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate internal-review proposal message drafts from local CSV files.")
    parser.add_argument("--buyers", default=str(DEFAULT_BUYERS), help="Input buyer master CSV path")
    parser.add_argument("--scores", default=str(DEFAULT_SCORES), help="Input buyer scores CSV path")
    parser.add_argument("--brands", default=str(DEFAULT_BRANDS), help="Input brand approval CSV path")
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT), help="Output proposal messages CSV path")
    parser.add_argument("--md-output", default=str(DEFAULT_MD_OUTPUT), help="Output proposal messages Markdown path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    buyers_path = resolve_path(args.buyers)
    scores_path = resolve_path(args.scores)
    brands_path = resolve_path(args.brands)
    csv_output_path = resolve_path(args.csv_output)
    md_output_path = resolve_path(args.md_output)

    buyer_columns, buyer_rows = read_csv_rows(buyers_path, "buyer master CSV")
    score_columns, score_rows = read_csv_rows(scores_path, "buyer scores CSV")
    validate_columns(buyer_columns, BUYER_COLUMNS, "buyer master CSV")
    validate_columns(score_columns, SCORE_COLUMNS, "buyer scores CSV")

    buyer_index = index_by_buyer_id(buyer_rows, "buyer master CSV")
    score_index = index_by_buyer_id(score_rows, "buyer scores CSV")
    validate_join(buyer_index, score_rows)

    brand_rules = load_brand_rules(brands_path)
    generated_at = date.today().isoformat()
    output_rows = [
        build_message(index, buyer_index[score_row["buyer_id"]], score_row, brand_rules, generated_at)
        for index, score_row in enumerate(score_rows, start=1)
    ]

    write_csv(csv_output_path, output_rows)
    write_markdown(md_output_path, output_rows)

    print("PASS: proposal messages generated")
    print(f"buyers={rel(buyers_path)}")
    print(f"scores={rel(scores_path)}")
    print(f"csv_output={rel(csv_output_path)}")
    print(f"md_output={rel(md_output_path)}")
    print(f"rows={len(output_rows)}")
    for row in output_rows:
        print(
            "buyer_id={buyer_id} message_status={message_status} message_type={message_type} approval_block={approval_block}".format(
                **row
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
