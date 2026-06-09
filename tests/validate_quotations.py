"""Validate internal-review quotation draft outputs.

This validator uses only local files and Python standard library modules.
It does not send quotations, scrape websites, call APIs, run browser
automation, enrich buyer data, check credit, or collect external data.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET


OUTPUT_COLUMNS = [
    "quotation_id",
    "buyer_id",
    "company_name",
    "country",
    "quotation_status",
    "approval_block",
    "brand_name",
    "product_name",
    "product_category",
    "sku_or_option",
    "requested_qty",
    "moq",
    "moq_check",
    "unit_price",
    "currency",
    "total_amount",
    "stock_status",
    "available_qty",
    "expiry_date",
    "delivery_lead_time",
    "price_valid_until",
    "supply_status",
    "compliance_notes",
    "required_internal_review",
    "next_action",
    "generated_at",
]

ALLOWED_STATUS = {
    "draft_ready_for_internal_review",
    "blocked_approval_required",
    "needs_price_confirmation",
    "needs_stock_confirmation",
    "needs_expiry_confirmation",
    "needs_moq_confirmation",
    "needs_buyer_review",
    "not_quotable",
}
ALLOWED_BOOL = {"true", "false"}
ALLOWED_MOQ_CHECK = {"pass", "fail", "unknown"}
ALLOWED_STOCK_STATUS = {"in_stock", "limited", "out_of_stock", "unknown"}
ALLOWED_SUPPLY_STATUS = {"available", "limited", "unavailable", "unknown"}
ALLOWED_CURRENCY = {"KRW", "USD", "CNY", "EUR", "RUB", "THB", "VND", "IDR", "MYR", "SGD", "unknown", "other"}

CONTACT_FIELDS = {"contact_email", "contact_phone", "wechat_id", "whatsapp"}
INTERNAL_CAUTIONS = ["내부 검토용 견적 초안", "내부 검토용"]
EXTERNAL_CAUTIONS = ["외부 발송 금지", "외부 발송 전 검토 필요"]
MEDICUBE = "메디큐브"

FORBIDDEN_COMMERCIAL_TERMS = [
    "guaranteed result",
    "clinically proven",
    "dermatologist approved",
    "before/after",
    "exclusive rights",
    "exclusive distribution",
    "official certification",
    "final contract",
    "final payment terms",
    "final incoterms",
    "final shipping terms",
    "의학적 효능",
    "임상 입증",
    "피부과 인증",
    "비포애프터",
    "독점권",
    "공식 인증",
    "최종 계약",
    "최종 결제 조건",
    "최종 인코텀즈",
    "최종 배송 조건",
]

DANGEROUS_CODE_PATTERNS = [
    r"^\s*import\s+smtplib\b",
    r"^\s*from\s+smtplib\s+import\b",
    r"^\s*import\s+requests\b",
    r"^\s*from\s+requests\s+import\b",
    r"^\s*import\s+httpx\b",
    r"^\s*from\s+httpx\s+import\b",
    r"^\s*import\s+selenium\b",
    r"^\s*from\s+selenium\s+import\b",
    r"^\s*import\s+playwright\b",
    r"^\s*from\s+playwright\s+import\b",
    r"urllib\.request",
    r"\.sendmail\s*\(",
    r"SMTP\s*\(",
    r"requests\.",
    r"httpx\.",
    r"webdriver\.",
    r"playwright\.",
]


class Validator:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated quotation draft outputs.")
    parser.add_argument("--quote-inputs", required=True)
    parser.add_argument("--quotations", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--xlsx", required=True)
    parser.add_argument("--buyers", required=True)
    parser.add_argument("--scores", required=True)
    parser.add_argument("--proposals", required=True)
    parser.add_argument("--brands", required=True)
    parser.add_argument("--generator", default="automations/quotation_maker/generate_quotations.py")
    return parser.parse_args()


def has_bom(path: Path) -> bool:
    data = path.read_bytes()
    return len(data) >= 3 and data[:3] == b"\xef\xbb\xbf"


def read_csv_file(path: Path, validator: Validator, label: str) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        validator.fail(f"{label}: file does not exist: {path}")
        return [], []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
            return reader.fieldnames or [], rows
    except UnicodeDecodeError as exc:
        validator.fail(f"{label}: CSV is not readable with utf-8-sig: {exc}")
    except csv.Error as exc:
        validator.fail(f"{label}: CSV parse error: {exc}")
    return [], []


def read_text(path: Path, validator: Validator, label: str) -> str:
    if not path.exists():
        validator.fail(f"{label}: file does not exist: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        validator.fail(f"{label}: file is not readable as UTF-8: {exc}")
    return ""


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key, "")}


def truthy(value: str) -> bool:
    return value.strip().lower() in {"true", "yes", "y", "1"}


def unknown(value: str) -> bool:
    return value.strip().lower() in {"", "unknown", "n/a", "na", "none", "미확인", "확인필요", "검증 필요"}


def positive_decimal(value: str) -> Decimal | None:
    if unknown(value):
        return None
    try:
        number = Decimal(value.replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return None
    if number <= 0:
        return None
    return number


def expected_moq_check(quote_input: dict[str, str]) -> str:
    qty = positive_decimal(quote_input.get("requested_qty", ""))
    moq = positive_decimal(quote_input.get("moq", ""))
    if qty is None or moq is None:
        return "unknown"
    return "pass" if qty >= moq else "fail"


def expected_total(quote_input: dict[str, str]) -> str:
    qty = positive_decimal(quote_input.get("requested_qty", ""))
    unit_price = positive_decimal(quote_input.get("unit_price", ""))
    if qty is None or unit_price is None:
        return ""
    return f"{(qty * unit_price).quantize(Decimal('0.01'))}"


def brand_requires_approval(brand_name: str, brand_row: dict[str, str] | None) -> bool:
    if brand_name == MEDICUBE:
        return True
    if not brand_row:
        return False
    return truthy(brand_row.get("approval_required", "")) or not truthy(brand_row.get("proposal_allowed", ""))


def explicit_approval(quote_input: dict[str, str]) -> bool:
    return quote_input.get("approval_status", "").strip().lower() == "approved"


def validate_files(args: argparse.Namespace, validator: Validator) -> dict[str, Path]:
    paths = {
        "quote_inputs": Path(args.quote_inputs),
        "quotations": Path(args.quotations),
        "markdown": Path(args.markdown),
        "xlsx": Path(args.xlsx),
        "buyers": Path(args.buyers),
        "scores": Path(args.scores),
        "proposals": Path(args.proposals),
        "brands": Path(args.brands),
        "generator": Path(args.generator),
    }
    for label, path in paths.items():
        validator.check(path.exists(), f"{label}: required file is missing: {path}")
    if paths["quotations"].exists():
        validator.check(has_bom(paths["quotations"]), "quotations: output CSV must use UTF-8 BOM")
    return paths


def validate_required_columns(headers: list[str], validator: Validator) -> None:
    validator.check(headers == OUTPUT_COLUMNS, "quotations: output columns must match required order exactly")


def validate_row_consistency(
    quote_inputs: list[dict[str, str]],
    quotations: list[dict[str, str]],
    buyers: list[dict[str, str]],
    scores: list[dict[str, str]],
    proposals: list[dict[str, str]],
    validator: Validator,
) -> None:
    validator.check(len(quote_inputs) == len(quotations), "quotations: row count must match quotation input row count")
    buyer_ids = {row.get("buyer_id", "") for row in buyers}
    score_ids = {row.get("buyer_id", "") for row in scores}
    proposal_ids = {row.get("buyer_id", "") for row in proposals}
    seen_quote_ids: set[str] = set()

    for row in quotations:
        quote_id = row.get("quotation_id", "")
        validator.check(bool(quote_id), "quotations: quotation_id must not be blank")
        validator.check(quote_id not in seen_quote_ids, f"quotations: duplicate quotation_id: {quote_id}")
        seen_quote_ids.add(quote_id)
        buyer_id = row.get("buyer_id", "")
        validator.check(buyer_id in buyer_ids, f"quotations: buyer_id not found in buyer master: {buyer_id}")
        validator.check(buyer_id in score_ids, f"quotations: buyer_id not found in scored buyers: {buyer_id}")
        validator.check(buyer_id in proposal_ids, f"quotations: buyer_id not found in proposal messages: {buyer_id}")


def validate_allowed_values(quotations: list[dict[str, str]], validator: Validator) -> None:
    for row in quotations:
        quote_id = row.get("quotation_id", "")
        validator.check(row.get("quotation_status", "") in ALLOWED_STATUS, f"{quote_id}: invalid quotation_status")
        validator.check(row.get("approval_block", "") in ALLOWED_BOOL, f"{quote_id}: approval_block must be true or false")
        validator.check(row.get("moq_check", "") in ALLOWED_MOQ_CHECK, f"{quote_id}: moq_check must be pass, fail, or unknown")
        validator.check(row.get("required_internal_review", "") in ALLOWED_BOOL, f"{quote_id}: required_internal_review must be true or false")
        validator.check(row.get("stock_status", "") in ALLOWED_STOCK_STATUS, f"{quote_id}: invalid stock_status")
        validator.check(row.get("supply_status", "") in ALLOWED_SUPPLY_STATUS, f"{quote_id}: invalid supply_status")
        validator.check(row.get("currency", "") in ALLOWED_CURRENCY, f"{quote_id}: invalid currency")


def validate_sample_scenarios(
    quote_inputs: list[dict[str, str]],
    quotations: list[dict[str, str]],
    validator: Validator,
) -> None:
    by_input_id = dict(zip([row.get("quote_input_id", "") for row in quote_inputs], quotations))
    expected = {
        "QI-0001": ("draft_ready_for_internal_review", "false", None),
        "QI-0002": ("blocked_approval_required", "true", None),
        "QI-0003": ("needs_price_confirmation", "false", None),
        "QI-0004": ("needs_stock_confirmation", "false", None),
        "QI-0005": ("needs_expiry_confirmation", "false", None),
        "QI-0006": ("needs_moq_confirmation", "false", "fail"),
    }
    for quote_input_id, (status, approval_block, moq_check) in expected.items():
        row = by_input_id.get(quote_input_id)
        validator.check(row is not None, f"{quote_input_id}: expected sample scenario row missing")
        if not row:
            continue
        validator.check(row.get("quotation_status") == status, f"{quote_input_id}: expected status {status}")
        validator.check(row.get("approval_block") == approval_block, f"{quote_input_id}: expected approval_block={approval_block}")
        if moq_check:
            validator.check(row.get("moq_check") == moq_check, f"{quote_input_id}: expected moq_check={moq_check}")


def validate_approval_blocks(
    quote_inputs: list[dict[str, str]],
    quotations: list[dict[str, str]],
    scores: list[dict[str, str]],
    proposals: list[dict[str, str]],
    brands: list[dict[str, str]],
    validator: Validator,
) -> None:
    scores_by_id = index_by(scores, "buyer_id")
    proposals_by_id = index_by(proposals, "buyer_id")
    brands_by_name = index_by(brands, "brand_ko")

    for quote_input, row in zip(quote_inputs, quotations):
        buyer_id = row.get("buyer_id", "")
        brand_name = row.get("brand_name", "")
        score = scores_by_id.get(buyer_id, {})
        proposal = proposals_by_id.get(buyer_id, {})
        brand = brands_by_name.get(brand_name)
        should_block = (
            truthy(score.get("approval_block", ""))
            or proposal.get("message_status", "") == "blocked_approval_required"
            or (brand_requires_approval(brand_name, brand) and not explicit_approval(quote_input))
        )
        if should_block:
            validator.check(row.get("approval_block") == "true", f"{row.get('quotation_id')}: approval_block should be true")
            validator.check(
                row.get("quotation_status") == "blocked_approval_required",
                f"{row.get('quotation_id')}: approval-blocked row should use blocked_approval_required",
            )
        if brand_name == MEDICUBE and not explicit_approval(quote_input):
            validator.check(row.get("approval_block") == "true", "메디큐브: must be blocked unless explicit approval exists")
        if score.get("priority_tier") == "A" and should_block:
            validator.check(row.get("approval_block") == "true", f"{row.get('quotation_id')}: A tier must not override approval block")


def validate_commercial_values(
    quote_inputs: list[dict[str, str]],
    quotations: list[dict[str, str]],
    validator: Validator,
) -> None:
    for quote_input, row in zip(quote_inputs, quotations):
        quote_id = row.get("quotation_id", "")
        stronger = row.get("quotation_status") == "blocked_approval_required"
        unit_price = positive_decimal(quote_input.get("unit_price", ""))
        stock_invalid = unknown(quote_input.get("stock_status", "")) or positive_decimal(quote_input.get("available_qty", "")) is None
        expiry_invalid = unknown(quote_input.get("expiry_date", ""))
        supply_invalid = unknown(quote_input.get("supply_status", ""))
        stock_unavailable = quote_input.get("stock_status", "").lower() == "out_of_stock" or quote_input.get("supply_status", "").lower() == "unavailable"

        validator.check(row.get("unit_price", "") == quote_input.get("unit_price", ""), f"{quote_id}: unit_price must come from quote input")
        validator.check(row.get("stock_status", "") == quote_input.get("stock_status", ""), f"{quote_id}: stock_status must come from quote input")
        validator.check(row.get("available_qty", "") == quote_input.get("available_qty", ""), f"{quote_id}: available_qty must come from quote input")
        validator.check(row.get("expiry_date", "") == quote_input.get("expiry_date", ""), f"{quote_id}: expiry_date must come from quote input")
        validator.check(row.get("supply_status", "") == quote_input.get("supply_status", ""), f"{quote_id}: supply_status must come from quote input")

        if unit_price is None and not stronger:
            validator.check(row.get("quotation_status") == "needs_price_confirmation", f"{quote_id}: missing price should require price confirmation")
        if stock_invalid and not stronger and unit_price is not None:
            validator.check(row.get("quotation_status") == "needs_stock_confirmation", f"{quote_id}: missing stock should require stock confirmation")
        if expiry_invalid and not stronger and unit_price is not None and not stock_invalid:
            validator.check(row.get("quotation_status") == "needs_expiry_confirmation", f"{quote_id}: missing expiry should require expiry confirmation")
        if supply_invalid:
            validator.check("공급" in row.get("compliance_notes", ""), f"{quote_id}: missing supply should add supply confirmation caution")
        if stock_unavailable and not stronger:
            validator.check(row.get("quotation_status") == "not_quotable", f"{quote_id}: unavailable stock/supply should be not_quotable")


def validate_moq_and_totals(
    quote_inputs: list[dict[str, str]],
    quotations: list[dict[str, str]],
    validator: Validator,
) -> None:
    for quote_input, row in zip(quote_inputs, quotations):
        quote_id = row.get("quotation_id", "")
        expected_check = expected_moq_check(quote_input)
        expected_line_total = expected_total(quote_input)
        validator.check(row.get("moq_check") == expected_check, f"{quote_id}: incorrect moq_check")
        if expected_check == "fail":
            validator.check(row.get("quotation_status") != "draft_ready_for_internal_review", f"{quote_id}: MOQ fail must not be draft-ready")
        validator.check(row.get("total_amount", "") == expected_line_total, f"{quote_id}: incorrect total_amount")
        if unknown(row.get("currency", "")):
            validator.check("통화" in row.get("compliance_notes", ""), f"{quote_id}: missing currency should add currency caution")
        for forbidden in ["tax", "shipping", "duties", "discount", "insurance", "customs", "incoterms"]:
            validator.check(forbidden not in row.get("total_amount", "").lower(), f"{quote_id}: total_amount must not include {forbidden}")


def validate_compliance_and_privacy(
    quotations: list[dict[str, str]],
    markdown_text: str,
    validator: Validator,
) -> None:
    output_header_terms = set(OUTPUT_COLUMNS)
    exposed_fields = sorted(output_header_terms & CONTACT_FIELDS)
    validator.check(not exposed_fields, f"quotations: contact fields must not be output columns: {', '.join(exposed_fields)}")

    combined_output = markdown_text + "\n" + "\n".join(
        " ".join(row.get(column, "") for column in OUTPUT_COLUMNS) for row in quotations
    )
    for field in CONTACT_FIELDS:
        validator.check(field not in combined_output, f"outputs: contact field name exposed: {field}")

    for row in quotations:
        quote_id = row.get("quotation_id", "")
        notes = row.get("compliance_notes", "")
        next_action = row.get("next_action", "")
        status = row.get("quotation_status", "")
        validator.check(bool(notes), f"{quote_id}: compliance_notes must not be blank")
        validator.check(bool(next_action), f"{quote_id}: next_action must not be blank")
        validator.check(any(term in notes for term in INTERNAL_CAUTIONS), f"{quote_id}: internal-review caution missing")
        validator.check(any(term in notes for term in EXTERNAL_CAUTIONS), f"{quote_id}: external sending caution missing")
        if status == "needs_price_confirmation":
            validator.check("가격" in notes, f"{quote_id}: price confirmation caution missing")
        if status == "needs_stock_confirmation":
            validator.check("재고" in notes, f"{quote_id}: stock confirmation caution missing")
        if status == "needs_expiry_confirmation":
            validator.check("유통기한" in notes, f"{quote_id}: expiry confirmation caution missing")
        if status == "needs_moq_confirmation":
            validator.check("MOQ" in notes, f"{quote_id}: MOQ confirmation caution missing")
        if status == "blocked_approval_required":
            validator.check("승인" in notes, f"{quote_id}: brand approval caution missing")

    validator.check(any(term in markdown_text for term in INTERNAL_CAUTIONS), "markdown: internal-review disclaimer missing")
    validator.check(any(term in markdown_text for term in ["외부 발송 금지", "외부 발송"]), "markdown: external sending prohibition missing")


def validate_forbidden_claims_and_scope(
    quotations: list[dict[str, str]],
    markdown_text: str,
    generator_text: str,
    validator: Validator,
) -> None:
    combined_output = markdown_text + "\n" + "\n".join(
        " ".join(row.get(column, "") for column in OUTPUT_COLUMNS) for row in quotations
    )
    negation_markers = ["not include", "not included", "not final", "must not", "do not", "미포함", "포함하지", "금지"]
    for line in combined_output.splitlines():
        lowered_line = line.lower()
        if any(marker in lowered_line for marker in negation_markers):
            continue
        for term in FORBIDDEN_COMMERCIAL_TERMS:
            validator.check(term.lower() not in lowered_line, f"outputs: unsupported claim/commercial term found: {term}")
    validator.check("sent externally" not in combined_output.lower(), "markdown/output must not imply quotations were sent externally")

    for line_number, line in enumerate(generator_text.splitlines(), start=1):
        lowered = line.lower()
        if "does not" in lowered or "do not" in lowered:
            continue
        for pattern in DANGEROUS_CODE_PATTERNS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                validator.fail(f"generator scope: forbidden implementation indicator on line {line_number}: {line.strip()}")


def xlsx_sheet_names(path: Path, validator: Validator) -> tuple[set[str], str]:
    if not path.exists():
        return set(), ""
    try:
        with zipfile.ZipFile(path) as zf:
            workbook_xml = zf.read("xl/workbook.xml").decode("utf-8")
            sheet_text = ""
            for name in zf.namelist():
                if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                    sheet_text += zf.read(name).decode("utf-8", errors="replace")
            root = ET.fromstring(workbook_xml)
            namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            names = {sheet.attrib.get("name", "") for sheet in root.findall(".//main:sheet", namespace)}
            return names, sheet_text
    except (KeyError, zipfile.BadZipFile, ET.ParseError, UnicodeDecodeError) as exc:
        validator.fail(f"xlsx: cannot inspect workbook: {exc}")
        return set(), ""


def validate_xlsx(path: Path, validator: Validator) -> None:
    validator.check(path.exists(), f"xlsx: file does not exist: {path}")
    names, sheet_text = xlsx_sheet_names(path, validator)
    validator.check("Quotations" in names, "xlsx: missing Quotations sheet")
    validator.check("Review Guide" in names, "xlsx: missing Review Guide sheet")
    validator.check("내부" in sheet_text, "xlsx: Korean internal-review text should be preserved")
    validator.check("需要内部批准" in sheet_text, "xlsx: Chinese sample text should be preserved where practical")
    validator.check("final" not in sheet_text.lower() or "not final" in sheet_text.lower(), "xlsx: must not imply final external quotation")


def validate_encoding(quotations_text: str, markdown_text: str, validator: Validator) -> None:
    combined = quotations_text + "\n" + markdown_text
    validator.check("내부 검토용 견적 초안" in combined, "encoding: Korean text must be preserved")
    validator.check("需要内部批准" in combined, "encoding: Chinese text must be preserved")
    validator.check(MEDICUBE in combined, "encoding: 메디큐브 must be preserved correctly")


def main() -> None:
    args = parse_args()
    validator = Validator()
    paths = validate_files(args, validator)

    quote_input_headers, quote_inputs = read_csv_file(paths["quote_inputs"], validator, "quote_inputs")
    quotation_headers, quotations = read_csv_file(paths["quotations"], validator, "quotations")
    _, buyers = read_csv_file(paths["buyers"], validator, "buyers")
    _, scores = read_csv_file(paths["scores"], validator, "scores")
    _, proposals = read_csv_file(paths["proposals"], validator, "proposals")
    _, brands = read_csv_file(paths["brands"], validator, "brands")
    markdown_text = read_text(paths["markdown"], validator, "markdown")
    generator_text = read_text(paths["generator"], validator, "generator")
    quotations_text = read_text(paths["quotations"], validator, "quotations text")

    validate_required_columns(quotation_headers, validator)
    validate_row_consistency(quote_inputs, quotations, buyers, scores, proposals, validator)
    validate_allowed_values(quotations, validator)
    validate_sample_scenarios(quote_inputs, quotations, validator)
    validate_approval_blocks(quote_inputs, quotations, scores, proposals, brands, validator)
    validate_commercial_values(quote_inputs, quotations, validator)
    validate_moq_and_totals(quote_inputs, quotations, validator)
    validate_compliance_and_privacy(quotations, markdown_text, validator)
    validate_forbidden_claims_and_scope(quotations, markdown_text, generator_text, validator)
    validate_xlsx(paths["xlsx"], validator)
    validate_encoding(quotations_text, markdown_text, validator)

    if validator.failures:
        print("FAIL: quotation validation failed")
        for failure in validator.failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("PASS: quotation validation passed")
    print(f"quote_input_rows={len(quote_inputs)}")
    print(f"quotation_rows={len(quotations)}")


if __name__ == "__main__":
    main()
