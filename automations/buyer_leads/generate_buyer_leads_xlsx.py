from __future__ import annotations

import argparse
import csv
import html
import sys
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "buyers_master_sample.csv"
DEFAULT_OUTPUT = ROOT / "output" / "buyers_master_sample.xlsx"

REQUIRED_COLUMNS = [
    "buyer_id",
    "company_name",
    "country",
    "city",
    "buyer_type",
    "sales_channel",
    "platform",
    "website",
    "sns_url",
    "contact_name",
    "contact_email",
    "contact_phone",
    "wechat_id",
    "whatsapp",
    "language",
    "interested_brands",
    "interested_categories",
    "estimated_order_qty",
    "moq_fit",
    "china_relevance",
    "payment_risk",
    "repeat_purchase_potential",
    "lead_source",
    "lead_status",
    "priority",
    "next_action",
    "notes",
    "created_at",
    "updated_at",
    "validation_status",
    "approval_warning",
    "contact_privacy_level",
    "recommended_follow_up",
    "proposal_brand_check",
]

INSPECTION_COLUMNS = {
    "moq_fit",
    "validation_status",
    "approval_warning",
    "contact_privacy_level",
    "proposal_brand_check",
    "priority",
    "next_action",
}

REVIEW_GUIDE_ROWS = [
    ["Field", "Meaning", "Review note"],
    ["moq_fit", "MOQ 100+ fit check", "yes=100+ units, no=1-99 units, unknown=blank/unknown/0/non-numeric quantity."],
    ["validation_status", "Overall sample validation status", "valid=usable sample row, review_needed=manual review required, invalid=severe structural issue."],
    ["approval_warning", "Approval-required brand warning", "If populated, do not use the brand externally before internal approval."],
    ["proposal_brand_check", "External proposal brand check", "clear=no approval-restricted brand detected, approval_required_review=approval needed."],
    ["contact_privacy_level", "Contact privacy level", "sample_placeholder means contact data is fictional and safe for sample testing."],
    ["메디큐브", "Approval-required brand", "Requires approval before external proposal, public content, quotation, or buyer-facing pitch."],
    ["Scope", "Local file workflow only", "No scraping, live research, automated search, browser automation, or external collection is performed."],
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def read_rows(input_path: Path) -> list[dict[str, str]]:
    if not input_path.exists():
        fail(f"input CSV does not exist: {rel(input_path)}")

    try:
        with input_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            columns = reader.fieldnames or []
            if columns != REQUIRED_COLUMNS:
                fail(f"input CSV columns do not match required master columns: {columns}")
            return list(reader)
    except UnicodeDecodeError as exc:
        fail(f"input CSV is not readable with utf-8-sig: {exc}")


def cell_xml(row_index: int, column_index: int, value: str, style: int = 0) -> str:
    coordinate = f"{column_name(column_index)}{row_index}"
    escaped_value = html.escape(value or "")
    style_attr = f' s="{style}"' if style else ""
    return (
        f'<c r="{coordinate}" t="inlineStr"{style_attr}>'
        f"<is><t>{escaped_value}</t></is></c>"
    )


def worksheet_xml(headers: list[str], rows: list[list[str]], highlight_columns: set[str] | None = None) -> str:
    highlight_columns = highlight_columns or set()
    header_cells = []
    for index, header in enumerate(headers, start=1):
        style = 1 if header in highlight_columns else 2
        header_cells.append(cell_xml(1, index, header, style))

    row_xml = [f'<row r="1">{"".join(header_cells)}</row>']
    for row_index, row in enumerate(rows, start=2):
        cells = []
        for column_index, value in enumerate(row, start=1):
            header = headers[column_index - 1]
            style = 3 if header in highlight_columns else 0
            cells.append(cell_xml(row_index, column_index, value, style))
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    widths = []
    for index, header in enumerate(headers, start=1):
        max_length = len(header)
        for row in rows:
            if index - 1 < len(row):
                max_length = max(max_length, len(row[index - 1] or ""))
        width = min(max(max_length + 2, 12), 80)
        widths.append(f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>')

    last_row = max(len(rows) + 1, 1)
    dimension = f"A1:{column_name(len(headers))}{last_row}"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <dimension ref="{dimension}"/>
  <sheetViews>
    <sheetView workbookViewId="0">
      <pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>
      <selection pane="bottomLeft" activeCell="A2" sqref="A2"/>
    </sheetView>
  </sheetViews>
  <cols>{"".join(widths)}</cols>
  <sheetData>{"".join(row_xml)}</sheetData>
  <autoFilter ref="{dimension}"/>
</worksheet>
"""


def workbook_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Buyer Leads" sheetId="1" r:id="rId1"/>
    <sheet name="Review Guide" sheetId="2" r:id="rId2"/>
  </sheets>
</workbook>
"""


def workbook_relationships_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""


def root_relationships_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""


def content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
"""


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><name val="Calibri"/></font>
  </fonts>
  <fills count="4">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFD9EAF7"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFFE0B2"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="4">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="3" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
    <xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0" applyFill="1"/>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>
"""


def fallback_output_path(output_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")


def write_xlsx_to_path(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lead_rows = [[row.get(column, "") for column in REQUIRED_COLUMNS] for row in rows]
    guide_headers = REVIEW_GUIDE_ROWS[0]
    guide_rows = REVIEW_GUIDE_ROWS[1:]

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr("[Content_Types].xml", content_types_xml())
        xlsx.writestr("_rels/.rels", root_relationships_xml())
        xlsx.writestr("xl/workbook.xml", workbook_xml())
        xlsx.writestr("xl/_rels/workbook.xml.rels", workbook_relationships_xml())
        xlsx.writestr("xl/styles.xml", styles_xml())
        xlsx.writestr(
            "xl/worksheets/sheet1.xml",
            worksheet_xml(REQUIRED_COLUMNS, lead_rows, INSPECTION_COLUMNS),
        )
        xlsx.writestr(
            "xl/worksheets/sheet2.xml",
            worksheet_xml(guide_headers, guide_rows, set(guide_headers)),
        )


def write_xlsx(rows: list[dict[str, str]], output_path: Path) -> Path:
    try:
        write_xlsx_to_path(rows, output_path)
        return output_path
    except PermissionError:
        fallback_path = fallback_output_path(output_path)
        write_xlsx_to_path(rows, fallback_path)
        print(
            f"WARN: {rel(output_path)} could not be overwritten. "
            f"Generated fallback file: {rel(fallback_path)}"
        )
        return fallback_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate buyer leads XLSX from master CSV.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input buyer master CSV path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output XLSX path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    rows = read_rows(input_path)
    actual_output = write_xlsx(rows, output_path)
    print(f"PASS: generated {rel(actual_output)}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
