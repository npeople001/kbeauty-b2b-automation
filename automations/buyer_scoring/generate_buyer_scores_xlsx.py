from __future__ import annotations

import argparse
import csv
import html
import sys
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "buyers_scored_sample.csv"
DEFAULT_OUTPUT = ROOT / "output" / "buyers_scored_sample.xlsx"

REQUIRED_COLUMNS = [
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

INSPECTION_COLUMNS = {
    "score_total",
    "priority_tier",
    "risk_flags",
    "approval_block",
    "recommended_next_action",
    "scoring_summary",
}

SCORING_GUIDE_ROWS = [
    ["Field", "Meaning", "Review note"],
    ["score_total", "Internal sales priority score", "0-100 internal prioritization score only; it does not prove buyer quality or purchase certainty."],
    ["priority_tier", "A/B/C/Hold", "A=high priority, B=medium priority, C=low priority, Hold=do not prioritize until review issue is resolved."],
    ["approval_block", "Approval restriction status", "true means external proposal, buyer-facing pitch, quotation, public content, or ad copy must not proceed for the approval-required brand."],
    ["risk_flags", "Risk and limitation flags", "source_manual_only and buyer_unverified are expected flags because this workflow uses manually provided local data only."],
    ["recommended_next_action", "Internal next action", "Use this as a sales follow-up guide, not as verified buyer intent or payment ability."],
    ["Scoring scope", "Internal sales prioritization only", "The score does not verify buyer authenticity, creditworthiness, payment ability, or purchase certainty."],
    ["메디큐브", "Approval-required brand", "메디큐브 requires explicit approval before external proposal, buyer-facing pitch, quotation, public content, or advertising copy."],
    ["Encoding", "Korean/English/中文 preservation", "XLSX output preserves Korean, English, and Chinese text when those values are present in the source CSV."],
    ["External collection", "Not performed", "No scraping, live web research, automatic web search, APIs, browser automation, crawlers, buyer enrichment, or credit checks are performed."],
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


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
                fail(f"input CSV columns do not match required scoring columns: {columns}")
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
        width = min(max(max_length + 2, 12), 90)
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
    <sheet name="Buyer Scores" sheetId="1" r:id="rId1"/>
    <sheet name="Scoring Guide" sheetId="2" r:id="rId2"/>
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
    score_rows = [[row.get(column, "") for column in REQUIRED_COLUMNS] for row in rows]
    guide_headers = SCORING_GUIDE_ROWS[0]
    guide_rows = SCORING_GUIDE_ROWS[1:]

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr("[Content_Types].xml", content_types_xml())
        xlsx.writestr("_rels/.rels", root_relationships_xml())
        xlsx.writestr("xl/workbook.xml", workbook_xml())
        xlsx.writestr("xl/_rels/workbook.xml.rels", workbook_relationships_xml())
        xlsx.writestr("xl/styles.xml", styles_xml())
        xlsx.writestr(
            "xl/worksheets/sheet1.xml",
            worksheet_xml(REQUIRED_COLUMNS, score_rows, INSPECTION_COLUMNS),
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
    parser = argparse.ArgumentParser(description="Generate buyer scores XLSX from scored buyer CSV.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input scored buyer CSV path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output XLSX path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)

    rows = read_rows(input_path)
    actual_output = write_xlsx(rows, output_path)
    print(f"PASS: generated {rel(actual_output)}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
