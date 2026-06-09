"""Validate Task 008 proposal message outputs.

This validator uses only local files and the Python standard library. It does
not send messages, perform scraping, call APIs, use browser automation, enrich
buyer data, run credit checks, or collect external data.
"""

from __future__ import annotations

import argparse
import ast
import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BUYERS = ROOT / "data" / "buyers_master_sample.csv"
DEFAULT_SCORES = ROOT / "data" / "buyers_scored_sample.csv"
DEFAULT_MESSAGES = ROOT / "data" / "proposal_messages_sample.csv"
DEFAULT_MARKDOWN = ROOT / "output" / "proposal_messages_sample.md"
DEFAULT_BRANDS = ROOT / "data" / "brands_master.csv"
DEFAULT_GENERATOR = ROOT / "automations" / "proposal_messages" / "generate_proposal_messages.py"

EXPECTED_COLUMNS = [
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

BUYER_REQUIRED_COLUMNS = [
    "buyer_id",
    "company_name",
    "country",
    "language",
    "interested_brands",
    "moq_fit",
    "payment_risk",
    "proposal_brand_check",
]

SCORE_REQUIRED_COLUMNS = [
    "buyer_id",
    "priority_tier",
    "approval_block",
]

BRAND_REQUIRED_COLUMNS = [
    "brand_ko",
    "approval_required",
    "proposal_allowed",
]

ALLOWED_LANGUAGES = {"Korean", "English", "Chinese"}
ALLOWED_TIERS = {"A", "B", "C", "Hold"}
ALLOWED_BOOLEANS = {"true", "false"}
ALLOWED_STATUSES = {
    "draft_ready_for_internal_review",
    "blocked_approval_required",
    "needs_more_buyer_info",
    "needs_moq_confirmation",
    "needs_payment_risk_review",
}
ALLOWED_TYPES = {
    "first_contact",
    "follow_up",
    "quotation_intro",
    "product_category_intro",
    "approval_review_required",
    "low_priority_nurture",
}

CONTACT_COLUMNS = {"contact_email", "contact_phone", "wechat_id", "whatsapp"}
CONTACT_PATTERNS = [
    re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    re.compile(r"placeholder_wechat_\d+", re.IGNORECASE),
    re.compile(r"\+00-\d{4}-\d{4}"),
]

DISALLOWED_IMPORTS = {
    "smtplib",
    "imaplib",
    "poplib",
    "requests",
    "urllib.request",
    "httpx",
    "selenium",
    "playwright",
    "socket",
    "http.client",
}

SCOPE_PATTERNS = [
    "smtplib",
    "email sending",
    "SMTP",
    "requests",
    "urllib.request",
    "httpx",
    "selenium",
    "playwright",
    "browser automation",
    "API calls",
    "crawling",
    "scraping",
    "DM sending",
    "WeChat sending",
    "WhatsApp sending",
    "messaging automation",
]

NEGATION_MARKERS = [
    "does not",
    "do not",
    "no ",
    "not ",
    "without",
    "금지",
    "없음",
    "않",
]

UNSUPPORTED_CLAIM_PATTERNS = [
    (re.compile(r"\bprice\s*[:=]\s*\$?\d", re.IGNORECASE), "price amount"),
    (re.compile(r"\b(stock|inventory)\s*[:=]\s*\d", re.IGNORECASE), "stock or inventory amount"),
    (re.compile(r"\bexpiry\s*date\s*[:=]", re.IGNORECASE), "expiry date"),
    (re.compile(r"official certification\s*(confirmed|approved|complete|completed|verified)", re.IGNORECASE), "official certification"),
    (re.compile(r"exclusive distribution rights\s*(granted|confirmed|available)", re.IGNORECASE), "exclusive distribution rights"),
    (re.compile(r"contract terms\s*(confirmed|final|approved)", re.IGNORECASE), "contract terms"),
    (re.compile(r"clinical(ly)?\s+(proven|verified|tested|certified)", re.IGNORECASE), "clinical claim"),
    (re.compile(r"dermatolog(ical|ically)\s+(proven|verified|tested|certified)", re.IGNORECASE), "dermatological claim"),
    (re.compile(r"\b(cures?|treats?|heals?)\b", re.IGNORECASE), "medical claim"),
    (re.compile(r"before\s*/\s*after", re.IGNORECASE), "before/after claim"),
    (re.compile(r"guaranteed\s+(results?|sales|performance|purchase)", re.IGNORECASE), "guaranteed result"),
    (re.compile(r"\b(no\.?\s*1|top\s*\d+|rank(ed)?\s*#?\d+)\b", re.IGNORECASE), "ranking claim"),
    (re.compile(r"\b(views?|engagement rate|conversion rate|platform performance)\s*[:=]?\s*\d+%?", re.IGNORECASE), "platform performance metric"),
    (re.compile(r"buyer\s+(is\s+)?(creditworthy|verified|authentic|guaranteed|likely to purchase)", re.IGNORECASE), "buyer verification claim"),
    (re.compile(r"구매\s*확정"), "purchase certainty"),
    (re.compile(r"신용\s*검증\s*완료"), "credit verification"),
    (re.compile(r"바이어\s*검증\s*완료"), "buyer authenticity verification"),
    (re.compile(r"재고\s*(있음|보유|확정)"), "stock claim"),
    (re.compile(r"가격\s*(확정|제공|보장)"), "price claim"),
    (re.compile(r"인증\s*(완료|확정)"), "certification claim"),
    (re.compile(r"독점권\s*(확정|제공)"), "exclusive rights claim"),
    (re.compile(r"임상\s*(입증|검증|완료)"), "clinical claim"),
    (re.compile(r"의학적\s*(효과|치료)"), "medical claim"),
    (re.compile(r"전후\s*사진"), "before/after claim"),
    (re.compile(r"효과\s*보장"), "guaranteed result"),
]


def clean(value: str | None) -> str:
    return (value or "").strip()


def lower(value: str | None) -> str:
    return clean(value).lower()


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def has_utf8_bom(path: Path) -> bool:
    with path.open("rb") as file:
        return file.read(3) == b"\xef\xbb\xbf"


def read_csv_rows(path: Path, label: str, failures: list[str]) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        failures.append(f"{label} does not exist: {rel(path)}")
        return [], []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                failures.append(f"{label} has no header row: {rel(path)}")
                return [], []
            rows = [{key: clean(value) for key, value in row.items()} for row in reader]
            return reader.fieldnames, rows
    except UnicodeDecodeError as exc:
        failures.append(f"{label} is not readable with utf-8-sig: {exc}")
        return [], []


def read_markdown(path: Path, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"proposal messages Markdown does not exist: {rel(path)}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        failures.append(f"proposal messages Markdown is not readable with UTF-8: {exc}")
        return ""


def require_columns(actual: list[str], expected: list[str], label: str, failures: list[str], exact: bool = False) -> None:
    if exact:
        if actual != expected:
            failures.append(f"{label} columns are not in exact required order: {actual}")
        return
    missing = [column for column in expected if column not in actual]
    if missing:
        failures.append(f"{label} missing required columns: {', '.join(missing)}")


def index_by_buyer_id(rows: list[dict[str, str]], label: str, failures: list[str]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for index, row in enumerate(rows, start=2):
        buyer_id = clean(row.get("buyer_id"))
        if not buyer_id:
            failures.append(f"{label} has blank buyer_id at row {index}")
            continue
        if buyer_id in indexed:
            failures.append(f"{label} has duplicate buyer_id: {buyer_id}")
        indexed[buyer_id] = row
    return indexed


def split_values(value: str) -> list[str]:
    normalized = value.replace(",", ";")
    return [item.strip() for item in normalized.split(";") if item.strip()]


def load_restricted_brands(path: Path, failures: list[str]) -> set[str]:
    restricted = {"메디큐브"}
    if not path.exists():
        return restricted
    columns, rows = read_csv_rows(path, "brands master CSV", failures)
    require_columns(columns, BRAND_REQUIRED_COLUMNS, "brands master CSV", failures)
    for row in rows:
        brand = clean(row.get("brand_ko"))
        if not brand:
            continue
        if lower(row.get("approval_required")) == "true" or lower(row.get("proposal_allowed")) != "true":
            restricted.add(brand)
    return restricted


def validate_files(paths: dict[str, Path], failures: list[str]) -> None:
    for label, path in paths.items():
        if not path.exists():
            failures.append(f"{label} file does not exist: {rel(path)}")
    if paths["messages"].exists() and not has_utf8_bom(paths["messages"]):
        failures.append("proposal messages CSV does not have UTF-8 BOM")


def validate_row_consistency(
    buyer_rows: list[dict[str, str]],
    score_rows: list[dict[str, str]],
    message_rows: list[dict[str, str]],
    failures: list[str],
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    buyer_index = index_by_buyer_id(buyer_rows, "buyer master CSV", failures)
    score_index = index_by_buyer_id(score_rows, "scored buyer CSV", failures)
    message_index = index_by_buyer_id(message_rows, "proposal messages CSV", failures)

    if len(message_rows) != len(score_rows):
        failures.append(f"proposal message row count {len(message_rows)} does not match scored buyer row count {len(score_rows)}")
    if set(message_index) != set(score_index):
        failures.append("proposal message buyer_id values do not match scored buyer CSV")
    if set(score_index) - set(buyer_index):
        failures.append(f"scored buyer_id values missing from buyer master: {', '.join(sorted(set(score_index) - set(buyer_index)))}")

    message_ids: set[str] = set()
    for row_number, row in enumerate(message_rows, start=2):
        message_id = clean(row.get("message_id"))
        if not message_id:
            failures.append(f"message_id is blank at proposal message row {row_number}")
        elif message_id in message_ids:
            failures.append(f"duplicate message_id found: {message_id}")
        message_ids.add(message_id)

    return buyer_index, score_index, message_index


def validate_allowed_values(message_rows: list[dict[str, str]], failures: list[str]) -> None:
    for row in message_rows:
        buyer_id = clean(row.get("buyer_id"))
        if clean(row.get("language")) not in ALLOWED_LANGUAGES:
            failures.append(f"{buyer_id}: language is not allowed: {row.get('language')}")
        if clean(row.get("priority_tier")) not in ALLOWED_TIERS:
            failures.append(f"{buyer_id}: priority_tier is not allowed: {row.get('priority_tier')}")
        if lower(row.get("approval_block")) not in ALLOWED_BOOLEANS:
            failures.append(f"{buyer_id}: approval_block must be true or false")
        if lower(row.get("required_internal_review")) not in ALLOWED_BOOLEANS:
            failures.append(f"{buyer_id}: required_internal_review must be true or false")
        if clean(row.get("message_status")) not in ALLOWED_STATUSES:
            failures.append(f"{buyer_id}: message_status is not allowed: {row.get('message_status')}")
        if clean(row.get("message_type")) not in ALLOWED_TYPES:
            failures.append(f"{buyer_id}: message_type is not allowed: {row.get('message_type')}")


def has_internal_review_disclaimer(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            clean(row.get("subject_or_opening")),
            clean(row.get("message_body")),
            clean(row.get("compliance_notes")),
        ]
    )
    return (
        "내부 검토용 초안" in text
        or "internal-review draft" in text.lower()
        or "内部审核草稿" in text
    )


def validate_required_text(message_rows: list[dict[str, str]], failures: list[str]) -> None:
    required_text_fields = ["subject_or_opening", "message_body", "compliance_notes", "next_action", "generated_at"]
    for row in message_rows:
        buyer_id = clean(row.get("buyer_id"))
        for field in required_text_fields:
            if not clean(row.get(field)):
                failures.append(f"{buyer_id}: {field} must not be blank")
        if not has_internal_review_disclaimer(row):
            failures.append(f"{buyer_id}: internal-review disclaimer is missing")


def is_approval_blocked(row: dict[str, str]) -> bool:
    return lower(row.get("approval_block")) == "true"


def contains_buyer_facing_proposal_copy(row: dict[str, str]) -> bool:
    body = clean(row.get("message_body"))
    if "구매자에게 보낼 제안문이 아닙니다" in body:
        return False
    if "internal guidance" in body.lower() or "내부 승인 검토" in body:
        return False
    buyer_facing_markers = ["Hello ", "您好", "we can offer", "we propose", "견적을 드립니다", "제안드립니다"]
    return any(marker in body for marker in buyer_facing_markers)


def validate_approval_blocks(
    buyer_index: dict[str, dict[str, str]],
    score_index: dict[str, dict[str, str]],
    message_index: dict[str, dict[str, str]],
    failures: list[str],
) -> None:
    for buyer_id, score in score_index.items():
        row = message_index.get(buyer_id)
        buyer = buyer_index.get(buyer_id, {})
        if not row:
            continue
        if lower(score.get("approval_block")) == "true" and lower(row.get("approval_block")) != "true":
            failures.append(f"{buyer_id}: scored approval_block=true but proposal approval_block is not true")
        if is_approval_blocked(row):
            if clean(row.get("message_status")) != "blocked_approval_required":
                failures.append(f"{buyer_id}: approval-blocked row must use blocked_approval_required")
            if clean(row.get("message_type")) != "approval_review_required":
                failures.append(f"{buyer_id}: approval-blocked row must use approval_review_required")
            if lower(row.get("required_internal_review")) != "true":
                failures.append(f"{buyer_id}: approval-blocked row must require internal review")
            if clean(row.get("recommended_brands")):
                failures.append(f"{buyer_id}: approval-blocked row must have blank recommended_brands")
            if contains_buyer_facing_proposal_copy(row):
                failures.append(f"{buyer_id}: approval-blocked message_body appears to contain buyer-facing proposal copy")
            if "승인" not in clean(row.get("next_action")) and "approval" not in lower(row.get("next_action")):
                failures.append(f"{buyer_id}: approval-blocked next_action must require internal approval review")
        interested = split_values(buyer.get("interested_brands", ""))
        if any(brand == "메디큐브" for brand in interested) and "메디큐브" not in clean(row.get("excluded_brands")):
            failures.append(f"{buyer_id}: 메디큐브 interested brand must appear in excluded_brands")

    buyer_0004 = message_index.get("BUYER-0004")
    if not buyer_0004:
        failures.append("BUYER-0004 message row is missing")
        return
    expected = {
        "approval_block": "true",
        "message_status": "blocked_approval_required",
        "message_type": "approval_review_required",
        "required_internal_review": "true",
    }
    for field, value in expected.items():
        if lower(buyer_0004.get(field)) != value:
            failures.append(f"BUYER-0004: {field} must be {value}")
    if clean(buyer_0004.get("recommended_brands")):
        failures.append("BUYER-0004: recommended_brands must be blank")
    if "메디큐브" not in clean(buyer_0004.get("excluded_brands")):
        failures.append("BUYER-0004: excluded_brands must include 메디큐브")


def validate_brands(
    buyer_index: dict[str, dict[str, str]],
    message_rows: list[dict[str, str]],
    restricted_brands: set[str],
    failures: list[str],
) -> None:
    for row in message_rows:
        buyer_id = clean(row.get("buyer_id"))
        recommended = split_values(row.get("recommended_brands", ""))
        excluded = split_values(row.get("excluded_brands", ""))
        for brand in recommended:
            if brand in restricted_brands:
                failures.append(f"{buyer_id}: restricted brand appears in recommended_brands: {brand}")
        buyer = buyer_index.get(buyer_id, {})
        interested = split_values(buyer.get("interested_brands", ""))
        for brand in interested:
            if brand in restricted_brands and brand not in excluded:
                failures.append(f"{buyer_id}: approval-required interested brand is not in excluded_brands: {brand}")
        if lower(row.get("approval_block")) == "true" and clean(row.get("priority_tier")) == "A":
            failures.append(f"{buyer_id}: high priority tier must not override approval_block")


def validate_moq_and_payment(
    buyer_index: dict[str, dict[str, str]],
    message_index: dict[str, dict[str, str]],
    failures: list[str],
) -> None:
    for buyer_id, buyer in buyer_index.items():
        row = message_index.get(buyer_id)
        if not row:
            continue
        status = clean(row.get("message_status"))
        approval_blocked = lower(row.get("approval_block")) == "true"
        if lower(buyer.get("moq_fit")) in {"no", "unknown"} and not approval_blocked:
            if status != "needs_moq_confirmation":
                failures.append(f"{buyer_id}: moq_fit={buyer.get('moq_fit')} should use needs_moq_confirmation")
            body = lower(row.get("message_body"))
            if "final proposal" in body or "견적을 드립니다" in body or "제안드립니다" in body:
                failures.append(f"{buyer_id}: message_body pushes final proposal when MOQ is not confirmed")
        if lower(buyer.get("payment_risk")) == "high" and not approval_blocked:
            if status != "needs_payment_risk_review":
                failures.append(f"{buyer_id}: payment_risk=high should use needs_payment_risk_review")


def text_has_unsupported_claim(text: str) -> str | None:
    for pattern, label in UNSUPPORTED_CLAIM_PATTERNS:
        if pattern.search(text):
            return label
    return None


def validate_forbidden_content(message_rows: list[dict[str, str]], failures: list[str]) -> None:
    fields = ["message_body", "subject_or_opening", "recommended_brands", "compliance_notes"]
    for row in message_rows:
        buyer_id = clean(row.get("buyer_id"))
        for field in fields:
            text = clean(row.get(field))
            label = text_has_unsupported_claim(text)
            if label:
                failures.append(f"{buyer_id}: unsupported {label} found in {field}")


def validate_privacy(message_columns: list[str], message_rows: list[dict[str, str]], markdown_text: str, failures: list[str]) -> None:
    exposed_columns = CONTACT_COLUMNS.intersection(message_columns)
    if exposed_columns:
        failures.append(f"proposal output includes contact/privacy columns: {', '.join(sorted(exposed_columns))}")

    output_text = markdown_text + "\n" + "\n".join(
        row.get("message_body", "") for row in message_rows
    )
    for pattern in CONTACT_PATTERNS:
        if pattern.search(output_text):
            failures.append(f"proposal output exposes contact-like data matching pattern: {pattern.pattern}")


def line_is_negated(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in NEGATION_MARKERS)


def validate_generator_scope(generator_path: Path, failures: list[str]) -> None:
    if not generator_path.exists():
        failures.append(f"proposal message generator is missing: {rel(generator_path)}")
        return
    source = generator_path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        failures.append(f"generator cannot be parsed: {exc}")
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name in DISALLOWED_IMPORTS:
                    failures.append(f"generator imports disallowed module: {name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in DISALLOWED_IMPORTS:
                failures.append(f"generator imports from disallowed module: {module}")

    lines = source.splitlines()
    for line_number, line in enumerate(lines, start=1):
        for pattern in SCOPE_PATTERNS:
            previous = lines[line_number - 2] if line_number >= 2 else ""
            previous_two = lines[line_number - 3] if line_number >= 3 else ""
            context = f"{previous_two} {previous} {line}"
            if pattern.lower() in line.lower() and not line_is_negated(context):
                failures.append(f"generator line {line_number} may imply disallowed scope: {pattern}")


def validate_language_and_markdown(message_rows: list[dict[str, str]], markdown_text: str, failures: list[str]) -> None:
    combined = markdown_text + "\n" + "\n".join(
        " ".join(row.get(field, "") for field in EXPECTED_COLUMNS) for row in message_rows
    )
    if "내부 검토용 초안" not in combined:
        failures.append("Korean internal review note is missing")
    if "메디큐브" not in combined:
        failures.append("메디큐브 text is not preserved")
    if not any("아누아" in row.get("recommended_brands", "") for row in message_rows):
        failures.append("Korean brand text is not preserved in recommended_brands")
    chinese_rows = [row for row in message_rows if row.get("language") == "Chinese"]
    for row in chinese_rows:
        text = row.get("subject_or_opening", "") + row.get("message_body", "")
        if not re.search(r"[\u4e00-\u9fff]", text):
            failures.append(f"{row.get('buyer_id')}: Chinese-language row does not contain Chinese text")
    english_rows = [row for row in message_rows if row.get("language") == "English"]
    for row in english_rows:
        text = row.get("subject_or_opening", "") + row.get("message_body", "")
        if "Internal review draft" not in text and "internal-review draft" not in text:
            failures.append(f"{row.get('buyer_id')}: English/default row does not contain English draft text")
    if "has been sent externally" in markdown_text and "has not been sent externally" not in markdown_text:
        failures.append("Markdown may imply messages were sent externally")
    if "외부로 발송되었습니다" in markdown_text:
        failures.append("Markdown implies messages were sent externally")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated proposal message drafts.")
    parser.add_argument("--buyers", default=str(DEFAULT_BUYERS), help="Buyer master CSV path")
    parser.add_argument("--scores", default=str(DEFAULT_SCORES), help="Scored buyer CSV path")
    parser.add_argument("--messages", default=str(DEFAULT_MESSAGES), help="Proposal messages CSV path")
    parser.add_argument("--markdown", default=str(DEFAULT_MARKDOWN), help="Proposal messages Markdown path")
    parser.add_argument("--brands", default=str(DEFAULT_BRANDS), help="Brand master CSV path")
    parser.add_argument("--generator", default=str(DEFAULT_GENERATOR), help="Proposal message generator script path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = {
        "buyers": resolve_path(args.buyers),
        "scores": resolve_path(args.scores),
        "messages": resolve_path(args.messages),
        "markdown": resolve_path(args.markdown),
        "brands": resolve_path(args.brands),
        "generator": resolve_path(args.generator),
    }

    failures: list[str] = []
    validate_files(paths, failures)

    buyer_columns, buyer_rows = read_csv_rows(paths["buyers"], "buyer master CSV", failures)
    score_columns, score_rows = read_csv_rows(paths["scores"], "scored buyer CSV", failures)
    message_columns, message_rows = read_csv_rows(paths["messages"], "proposal messages CSV", failures)
    markdown_text = read_markdown(paths["markdown"], failures)

    require_columns(buyer_columns, BUYER_REQUIRED_COLUMNS, "buyer master CSV", failures)
    require_columns(score_columns, SCORE_REQUIRED_COLUMNS, "scored buyer CSV", failures)
    require_columns(message_columns, EXPECTED_COLUMNS, "proposal messages CSV", failures, exact=True)

    buyer_index, score_index, message_index = validate_row_consistency(buyer_rows, score_rows, message_rows, failures)
    restricted_brands = load_restricted_brands(paths["brands"], failures)

    validate_allowed_values(message_rows, failures)
    validate_required_text(message_rows, failures)
    validate_approval_blocks(buyer_index, score_index, message_index, failures)
    validate_brands(buyer_index, message_rows, restricted_brands, failures)
    validate_moq_and_payment(buyer_index, message_index, failures)
    validate_forbidden_content(message_rows, failures)
    validate_privacy(message_columns, message_rows, markdown_text, failures)
    validate_generator_scope(paths["generator"], failures)
    validate_language_and_markdown(message_rows, markdown_text, failures)

    if failures:
        print("FAIL: proposal message validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: proposal message validation passed")
    print(f"buyers={rel(paths['buyers'])}")
    print(f"scores={rel(paths['scores'])}")
    print(f"messages={rel(paths['messages'])}")
    print(f"markdown={rel(paths['markdown'])}")
    print(f"rows={len(message_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
