"""Generate internal-review quotation draft outputs from local files only.

This script does not send quotations, scrape websites, call APIs, run browser
automation, enrich buyer data, check credit, or collect external data.
"""

from __future__ import annotations

import argparse
import csv
import html
import sys
import zipfile
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

QUOTE_INPUT_COLUMNS = [
    "quote_input_id",
    "buyer_id",
    "brand_name",
    "product_name",
    "product_category",
    "sku_or_option",
    "requested_qty",
    "unit_price",
    "currency",
    "stock_status",
    "available_qty",
    "expiry_date",
    "moq",
    "delivery_lead_time",
    "price_valid_until",
    "supply_status",
    "approval_status",
    "notes",
    "provided_by",
    "provided_at",
]

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

BUYER_REQUIRED_COLUMNS = ["buyer_id", "company_name", "country"]
SCORE_REQUIRED_COLUMNS = ["buyer_id", "approval_block", "priority_tier"]
PROPOSAL_REQUIRED_COLUMNS = ["buyer_id", "message_status"]
BRAND_MIN_COLUMNS = ["brand_ko", "approval_required", "proposal_allowed"]

INSPECTION_COLUMNS = {
    "quotation_status",
    "approval_block",
    "moq_check",
    "unit_price",
    "total_amount",
    "stock_status",
    "expiry_date",
    "supply_status",
    "compliance_notes",
    "required_internal_review",
    "next_action",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = ROOT / path
    return path


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_csv(path: Path, required_columns: list[str], label: str) -> list[dict[str, str]]:
    if not path.exists():
        fail(f"{label} file is missing: {rel(path)}")

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            missing = [column for column in required_columns if column not in fieldnames]
            if missing:
                fail(f"{label} file is missing required columns: {', '.join(missing)}")
            return [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    except UnicodeDecodeError as exc:
        fail(f"{label} file is not readable as utf-8-sig: {exc}")


def read_brands(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        print(f"WARNING: brands master missing; approval-sensitive brand names will still be blocked where possible: {rel(path)}")
        return {}

    rows = read_csv(path, BRAND_MIN_COLUMNS, "brands master")
    return index_by(rows, "brand_ko", "brands master")


def index_by(rows: list[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "").strip()
        if not value:
            fail(f"{label} contains a blank {key}")
        if value in indexed:
            fail(f"{label} contains duplicate {key}: {value}")
        indexed[value] = row
    return indexed


def lower(value: str) -> str:
    return (value or "").strip().lower()


def is_unknown(value: str) -> bool:
    return lower(value) in {"", "unknown", "n/a", "na", "none", "미확인", "확인필요", "검증 필요"}


def is_true(value: str) -> bool:
    return lower(value) in {"true", "yes", "y", "1"}


def parse_decimal(value: str) -> Decimal | None:
    if is_unknown(value):
        return None
    try:
        number = Decimal(value.replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return None
    if number <= 0:
        return None
    return number


def format_decimal(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))}"


def determine_moq_check(requested_qty: str, moq: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    qty = parse_decimal(requested_qty)
    moq_value = parse_decimal(moq)

    if qty is None or moq_value is None:
        notes.append("MOQ 또는 요청 수량 확인 필요")
        return "unknown", notes
    if qty >= moq_value:
        return "pass", notes
    notes.append("요청 수량이 MOQ 미만")
    return "fail", notes


def explicit_approval(row: dict[str, str]) -> bool:
    return lower(row.get("approval_status", "")) == "approved"


def brand_requires_approval(brand_name: str, brand_row: dict[str, str] | None) -> bool:
    if brand_name == "메디큐브":
        return True
    if not brand_row:
        return False
    return is_true(brand_row.get("approval_required", "")) or not is_true(brand_row.get("proposal_allowed", ""))


def build_compliance_notes(
    quote: dict[str, str],
    approval_block: bool,
    moq_check: str,
    price_valid: bool,
    stock_needs_review: bool,
    expiry_needs_review: bool,
    supply_needs_review: bool,
    currency_needs_review: bool,
) -> str:
    notes = [
        "내부 검토용 견적 초안",
        "외부 발송 전 검토 필요",
        "화장품 표현/클레임 포함 금지",
        "세금/운임/관세/인코텀즈 미포함",
        "개인정보 비노출",
    ]
    if approval_block:
        notes.append("브랜드 승인 확인 필요")
    if not price_valid:
        notes.append("가격 확인 필요")
    if stock_needs_review:
        notes.append("재고 확인 필요")
    if expiry_needs_review:
        notes.append("유통기한 확인 필요")
    if supply_needs_review:
        notes.append("공급 가능 여부 확인 필요")
    if moq_check != "pass":
        notes.append("MOQ 확인 필요")
    if currency_needs_review:
        notes.append("통화 및 가격 유효기간 확인 필요")
    if quote.get("notes"):
        notes.append(f"입력 메모: {quote['notes']}")
    return " | ".join(notes)


def determine_status(
    approval_block: bool,
    price_valid: bool,
    stock_needs_review: bool,
    expiry_needs_review: bool,
    moq_check: str,
    quote: dict[str, str],
) -> str:
    if approval_block:
        return "blocked_approval_required"
    if lower(quote.get("stock_status", "")) == "out_of_stock" or lower(quote.get("supply_status", "")) == "unavailable":
        return "not_quotable"
    if not price_valid:
        return "needs_price_confirmation"
    if stock_needs_review:
        return "needs_stock_confirmation"
    if expiry_needs_review:
        return "needs_expiry_confirmation"
    if moq_check != "pass":
        return "needs_moq_confirmation"
    return "draft_ready_for_internal_review"


def determine_next_action(status: str, currency_needs_review: bool) -> str:
    if status == "blocked_approval_required":
        return "내부 브랜드 승인 여부 확인"
    if status == "needs_price_confirmation":
        return "가격 확인 후 견적 재생성"
    if status == "needs_stock_confirmation":
        return "재고 및 공급 가능 수량 확인"
    if status == "needs_expiry_confirmation":
        return "유통기한 확인"
    if status == "needs_moq_confirmation":
        return "MOQ 충족 가능 여부 확인"
    if status == "not_quotable":
        return "공급 불가 사유 확인 후 대체 제품 검토"
    if currency_needs_review:
        return "통화 및 가격 유효기간 확인"
    if status == "needs_buyer_review":
        return "바이어 정보와 내부 검토 상태 확인"
    return "외부 발송 전 대표/담당자 검토"


def build_quotation_rows(
    quote_inputs: list[dict[str, str]],
    buyers_by_id: dict[str, dict[str, str]],
    scores_by_id: dict[str, dict[str, str]],
    proposals_by_id: dict[str, dict[str, str]],
    brands_by_name: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    generated_at = datetime.now().strftime("%Y-%m-%d")
    rows: list[dict[str, str]] = []

    for idx, quote in enumerate(quote_inputs, start=1):
        buyer_id = quote.get("buyer_id", "")
        buyer = buyers_by_id.get(buyer_id)
        score = scores_by_id.get(buyer_id)
        proposal = proposals_by_id.get(buyer_id)

        if buyer is None:
            fail(f"quote input references missing buyer_id in buyer master: {buyer_id}")
        if score is None:
            fail(f"quote input references missing buyer_id in scored buyers: {buyer_id}")
        if proposal is None:
            fail(f"quote input references missing buyer_id in proposal messages: {buyer_id}")

        brand_name = quote.get("brand_name", "")
        brand = brands_by_name.get(brand_name)
        approval_sensitive = brand_requires_approval(brand_name, brand)
        approval_block = (
            is_true(score.get("approval_block", ""))
            or proposal.get("message_status", "") == "blocked_approval_required"
            or (approval_sensitive and not explicit_approval(quote))
        )

        requested_qty = parse_decimal(quote.get("requested_qty", ""))
        unit_price = parse_decimal(quote.get("unit_price", ""))
        price_valid = unit_price is not None
        total_amount = ""
        if requested_qty is not None and unit_price is not None:
            total_amount = format_decimal(requested_qty * unit_price)

        moq_check, moq_notes = determine_moq_check(quote.get("requested_qty", ""), quote.get("moq", ""))
        stock_status = lower(quote.get("stock_status", ""))
        supply_status = lower(quote.get("supply_status", ""))
        available_qty_valid = parse_decimal(quote.get("available_qty", "")) is not None
        stock_needs_review = stock_status in {"", "unknown"} or not available_qty_valid
        expiry_needs_review = is_unknown(quote.get("expiry_date", ""))
        supply_needs_review = supply_status in {"", "unknown", "limited", "unavailable"}
        currency_needs_review = is_unknown(quote.get("currency", "")) or is_unknown(quote.get("price_valid_until", ""))

        status = determine_status(
            approval_block=approval_block,
            price_valid=price_valid,
            stock_needs_review=stock_needs_review,
            expiry_needs_review=expiry_needs_review,
            moq_check=moq_check,
            quote=quote,
        )
        compliance_notes = build_compliance_notes(
            quote=quote,
            approval_block=approval_block,
            moq_check=moq_check,
            price_valid=price_valid,
            stock_needs_review=stock_needs_review,
            expiry_needs_review=expiry_needs_review,
            supply_needs_review=supply_needs_review,
            currency_needs_review=currency_needs_review,
        )
        if moq_notes:
            compliance_notes = f"{compliance_notes} | {' | '.join(moq_notes)}"

        rows.append(
            {
                "quotation_id": f"QUOTE-{idx:04d}",
                "buyer_id": buyer_id,
                "company_name": buyer.get("company_name", ""),
                "country": buyer.get("country", ""),
                "quotation_status": status,
                "approval_block": "true" if approval_block else "false",
                "brand_name": brand_name,
                "product_name": quote.get("product_name", ""),
                "product_category": quote.get("product_category", ""),
                "sku_or_option": quote.get("sku_or_option", ""),
                "requested_qty": quote.get("requested_qty", ""),
                "moq": quote.get("moq", ""),
                "moq_check": moq_check,
                "unit_price": quote.get("unit_price", ""),
                "currency": quote.get("currency", ""),
                "total_amount": total_amount,
                "stock_status": quote.get("stock_status", ""),
                "available_qty": quote.get("available_qty", ""),
                "expiry_date": quote.get("expiry_date", ""),
                "delivery_lead_time": quote.get("delivery_lead_time", ""),
                "price_valid_until": quote.get("price_valid_until", ""),
                "supply_status": quote.get("supply_status", ""),
                "compliance_notes": compliance_notes,
                "required_internal_review": "true",
                "next_action": determine_next_action(status, currency_needs_review),
                "generated_at": generated_at,
            }
        )

    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def col_letter(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def xml_escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def sheet_xml(headers: list[str], rows: list[list[str]], freeze_header: bool = True) -> str:
    all_rows = [headers] + rows
    row_xml: list[str] = []
    for row_index, row in enumerate(all_rows, start=1):
        cells: list[str] = []
        for col_index, value in enumerate(row, start=1):
            cell_ref = f"{col_letter(col_index)}{row_index}"
            style = " s=\"1\"" if row_index == 1 else ""
            cells.append(f'<c r="{cell_ref}" t="inlineStr"{style}><is><t>{xml_escape(value)}</t></is></c>')
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    last_col = col_letter(len(headers))
    last_row = max(1, len(all_rows))
    sheet_views = ""
    if freeze_header:
        sheet_views = (
            '<sheetViews><sheetView workbookViewId="0">'
            '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
            "</sheetView></sheetViews>"
        )
    auto_filter = f'<autoFilter ref="A1:{last_col}{last_row}"/>'
    widths = []
    for col_index, header in enumerate(headers, start=1):
        max_len = max([len(str(header))] + [len(str(row[col_index - 1])) for row in rows]) if rows else len(str(header))
        width = min(max(max_len + 2, 12), 60)
        if header in INSPECTION_COLUMNS:
            width = min(max(width, 22), 70)
        widths.append(f'<col min="{col_index}" max="{col_index}" width="{width}" customWidth="1"/>')
    cols_xml = f"<cols>{''.join(widths)}</cols>"

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"{sheet_views}{cols_xml}<sheetData>{''.join(row_xml)}</sheetData>{auto_filter}</worksheet>"
    )


def workbook_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets>"
        '<sheet name="Quotations" sheetId="1" r:id="rId1"/>'
        '<sheet name="Review Guide" sheetId="2" r:id="rId2"/>'
        "</sheets></workbook>"
    )


def workbook_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        "</Relationships>"
    )


def package_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def content_types_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        "</Types>"
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>'
        "</styleSheet>"
    )


def review_guide_rows() -> list[list[str]]:
    return [
        ["항목", "설명"],
        ["사용 범위", "내부 검토용 견적 초안이며 외부 발송 금지"],
        ["approval_block=true", "승인 필요 브랜드는 외부 제안/견적/피치/광고 문구 진행 금지"],
        ["메디큐브", "명시 승인 전 approval-required로 처리"],
        ["가격/재고/유통기한", "수동 입력값만 사용하며 누락 시 확인 필요로 표시"],
        ["MOQ", "요청 수량이 MOQ 미만이면 needs_moq_confirmation"],
        ["total_amount", "유효한 요청 수량과 단가가 있을 때만 계산"],
        ["미포함 항목", "세금, 운임, 관세, 보험, 인코텀즈, 할인, 최종 계약 조건"],
        ["개인정보", "견적 출력에는 이메일, 전화번호, WeChat, WhatsApp 기본 비노출"],
        ["검증 제한", "바이어 실제성, 결제 능력, 구매 확정, 공급 가능성은 자동 검증하지 않음"],
    ]


def write_xlsx(path: Path, rows: list[dict[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    target = path
    table_rows = [[row.get(column, "") for column in OUTPUT_COLUMNS] for row in rows]

    def write_zip(out_path: Path) -> None:
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types_xml())
            zf.writestr("_rels/.rels", package_rels_xml())
            zf.writestr("xl/workbook.xml", workbook_xml())
            zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml())
            zf.writestr("xl/styles.xml", styles_xml())
            zf.writestr("xl/worksheets/sheet1.xml", sheet_xml(OUTPUT_COLUMNS, table_rows))
            zf.writestr("xl/worksheets/sheet2.xml", sheet_xml(["항목", "설명"], review_guide_rows()[1:]))

    try:
        write_zip(target)
    except PermissionError:
        fallback = target.with_name(f"{target.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{target.suffix}")
        write_zip(fallback)
        return fallback
    return target


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(row["quotation_status"] for row in rows)
    blocked_rows = [row for row in rows if row["approval_block"] == "true"]
    review_rows = [row for row in rows if row["quotation_status"] != "draft_ready_for_internal_review"]

    lines = [
        "# Quotation Sample",
        "",
        "**내부 검토용 견적 초안**",
        "",
        "**외부 발송 금지**",
        "",
        "가격/재고/유통기한/승인 확인 필요",
        "",
        "이 문서는 로컬 수동 입력 자료로 생성된 내부 검토용 초안입니다. 세금, 운임, 관세, 보험, 인코텀즈, 할인, 최종 계약 조건은 포함하지 않습니다.",
        "",
        "## Status Summary",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Approval Block Rows"])
    if blocked_rows:
        for row in blocked_rows:
            lines.append(f"- {row['quotation_id']} / {row['buyer_id']} / {row['brand_name']}: {row['next_action']}")
    else:
        lines.append("- 없음")

    lines.extend(["", "## Rows Requiring Review"])
    if review_rows:
        for row in review_rows:
            lines.append(
                f"- {row['quotation_id']} / {row['buyer_id']} / {row['brand_name']} / "
                f"{row['quotation_status']}: {row['next_action']}"
            )
    else:
        lines.append("- 없음")

    lines.extend(
        [
            "",
            "## Quotation Draft Table",
            "",
            "| quotation_id | buyer_id | company_name | country | quotation_status | approval_block | brand_name | requested_qty | moq | moq_check | unit_price | currency | total_amount | stock_status | expiry_date | next_action |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | --- | ---: | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["quotation_id"],
                    row["buyer_id"],
                    row["company_name"],
                    row["country"],
                    row["quotation_status"],
                    row["approval_block"],
                    row["brand_name"],
                    row["requested_qty"],
                    row["moq"],
                    row["moq_check"],
                    row["unit_price"],
                    row["currency"],
                    row["total_amount"],
                    row["stock_status"],
                    row["expiry_date"],
                    row["next_action"],
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Required Review Notes",
            "",
            "- 외부 발송 전 가격, 재고, 유통기한, 공급 가능 여부, 브랜드 승인, 화장품 표현, 현지 규제, 최종 거래 조건을 확인해야 합니다.",
            "- 메디큐브 및 approval-required 브랜드는 명시 승인 전 외부 제안 또는 견적 발송 대상이 아닙니다.",
            "- 바이어 점수나 우선순위는 내부 영업 우선순위 신호이며 실제성, 신용도, 구매 확정성을 의미하지 않습니다.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate internal-review quotation draft outputs.")
    parser.add_argument("--buyers", default="data/buyers_master_sample.csv")
    parser.add_argument("--scores", default="data/buyers_scored_sample.csv")
    parser.add_argument("--proposals", default="data/proposal_messages_sample.csv")
    parser.add_argument("--brands", default="data/brands_master.csv")
    parser.add_argument("--quote-inputs", default="data/quotation_inputs_sample.csv")
    parser.add_argument("--csv-output", default="data/quotation_sample.csv")
    parser.add_argument("--xlsx-output", default="output/quotation_sample.xlsx")
    parser.add_argument("--md-output", default="output/quotation_sample.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    buyers = read_csv(resolve_path(args.buyers), BUYER_REQUIRED_COLUMNS, "buyer master")
    scores = read_csv(resolve_path(args.scores), SCORE_REQUIRED_COLUMNS, "buyer scores")
    proposals = read_csv(resolve_path(args.proposals), PROPOSAL_REQUIRED_COLUMNS, "proposal messages")
    quote_inputs = read_csv(resolve_path(args.quote_inputs), QUOTE_INPUT_COLUMNS, "quotation inputs")
    brands = read_brands(resolve_path(args.brands))

    buyers_by_id = index_by(buyers, "buyer_id", "buyer master")
    scores_by_id = index_by(scores, "buyer_id", "buyer scores")
    proposals_by_id = index_by(proposals, "buyer_id", "proposal messages")

    rows = build_quotation_rows(quote_inputs, buyers_by_id, scores_by_id, proposals_by_id, brands)

    csv_output = resolve_path(args.csv_output)
    xlsx_output = resolve_path(args.xlsx_output)
    md_output = resolve_path(args.md_output)
    write_csv(csv_output, rows)
    actual_xlsx = write_xlsx(xlsx_output, rows)
    write_markdown(md_output, rows)

    print("Generated quotation outputs")
    print(f"CSV: {rel(csv_output)}")
    print(f"XLSX: {rel(actual_xlsx)}")
    print(f"Markdown: {rel(md_output)}")
    print(f"Rows: {len(rows)}")


if __name__ == "__main__":
    main()
