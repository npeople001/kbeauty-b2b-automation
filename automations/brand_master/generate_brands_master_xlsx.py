from __future__ import annotations

import csv
import html
import sys
import zipfile
from datetime import datetime
from pathlib import Path


# Uses only the Python standard library because this repository does not yet
# have dependency management. If richer XLSX editing is needed later, consider
# documenting and adding openpyxl.
ROOT = Path(__file__).resolve().parents[2]
SOURCE_CSV = ROOT / "data" / "brands_master.csv"
OUTPUT_XLSX = ROOT / "output" / "brands_master.xlsx"

REQUIRED_COLUMNS = [
    "brand_ko",
    "brand_en",
    "category",
    "sub_category",
    "approval_required",
    "approval_note",
    "china_priority",
    "global_priority",
    "proposal_allowed",
    "notes",
]

INSPECTION_COLUMNS = {"approval_required", "proposal_allowed"}

HEADER_DISPLAY_MAP = {
    "brand_ko": "브랜드명",
    "brand_en": "영문명",
    "category": "카테고리",
    "sub_category": "세부카테고리",
    "approval_required": "승인필요여부",
    "approval_note": "승인메모",
    "china_priority": "중국우선순위",
    "global_priority": "글로벌우선순위",
    "proposal_allowed": "제안가능여부",
    "notes": "비고",
}

DISPLAY_VALUE_MAP = {
    "category": {
        "cosmetics": "화장품",
        "health": "건강기능/이너뷰티",
    },
    "sub_category": {
        "unknown": "미분류",
    },
    "approval_required": {
        "true": "승인필요",
        "false": "승인불필요",
    },
    "proposal_allowed": {
        "true": "제안가능",
        "false": "제안불가",
    },
    "china_priority": {
        "high": "높음",
        "medium": "보통",
        "low": "낮음",
        "unknown": "미정",
    },
    "global_priority": {
        "high": "높음",
        "medium": "보통",
        "low": "낮음",
        "unknown": "미정",
    },
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def read_rows() -> list[dict[str, str]]:
    if not SOURCE_CSV.exists():
        fail(f"required source CSV does not exist: {SOURCE_CSV.relative_to(ROOT)}")

    try:
        with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            columns = reader.fieldnames or []
            missing = [column for column in REQUIRED_COLUMNS if column not in columns]
            if missing:
                fail(f"source CSV is missing required columns: {missing}")
            return list(reader)
    except UnicodeDecodeError as exc:
        fail(f"source CSV is not valid UTF-8: {exc}")


def cell_xml(row_index: int, column_index: int, value: str, style: int = 0) -> str:
    coordinate = f"{column_name(column_index)}{row_index}"
    escaped_value = html.escape(value or "")
    style_attr = f' s="{style}"' if style else ""
    return (
        f'<c r="{coordinate}" t="inlineStr"{style_attr}>'
        f"<is><t>{escaped_value}</t></is></c>"
    )


def display_value(column: str, value: str) -> str:
    return DISPLAY_VALUE_MAP.get(column, {}).get(value, value)


def display_header(column: str) -> str:
    return HEADER_DISPLAY_MAP.get(column, column)


def worksheet_xml(rows: list[dict[str, str]]) -> str:
    header_cells = [
        cell_xml(1, index, display_header(column), 1 if column in INSPECTION_COLUMNS else 2)
        for index, column in enumerate(REQUIRED_COLUMNS, start=1)
    ]
    row_xml = [f'<row r="1">{"".join(header_cells)}</row>']

    for row_index, row in enumerate(rows, start=2):
        cells = []
        for column_index, column in enumerate(REQUIRED_COLUMNS, start=1):
            style = 3 if column in INSPECTION_COLUMNS else 0
            cells.append(cell_xml(row_index, column_index, display_value(column, row.get(column, "")), style))
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    widths = []
    for index, column in enumerate(REQUIRED_COLUMNS, start=1):
        max_length = len(display_header(column))
        for row in rows:
            max_length = max(max_length, len(display_value(column, row.get(column, ""))))
        width = min(max(max_length + 2, 12), 60)
        widths.append(f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>')

    sheet_dimension = f"A1:{column_name(len(REQUIRED_COLUMNS))}{len(rows) + 1}"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <dimension ref="{sheet_dimension}"/>
  <sheetViews>
    <sheetView workbookViewId="0">
      <pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>
      <selection pane="bottomLeft" activeCell="A2" sqref="A2"/>
    </sheetView>
  </sheetViews>
  <cols>{"".join(widths)}</cols>
  <sheetData>{"".join(row_xml)}</sheetData>
  <autoFilter ref="{sheet_dimension}"/>
</worksheet>
"""


def workbook_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="brands_master" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
"""


def workbook_relationships_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
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


def fallback_output_path() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return OUTPUT_XLSX.with_name(f"{OUTPUT_XLSX.stem}_{timestamp}{OUTPUT_XLSX.suffix}")


def write_xlsx_to_path(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr("[Content_Types].xml", content_types_xml())
        xlsx.writestr("_rels/.rels", root_relationships_xml())
        xlsx.writestr("xl/workbook.xml", workbook_xml())
        xlsx.writestr("xl/_rels/workbook.xml.rels", workbook_relationships_xml())
        xlsx.writestr("xl/styles.xml", styles_xml())
        xlsx.writestr("xl/worksheets/sheet1.xml", worksheet_xml(rows))


def write_xlsx(rows: list[dict[str, str]]) -> Path:
    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    try:
        write_xlsx_to_path(rows, OUTPUT_XLSX)
        return OUTPUT_XLSX
    except PermissionError:
        fallback_path = fallback_output_path()
        write_xlsx_to_path(rows, fallback_path)
        print(
            "WARN: output/brands_master.xlsx could not be overwritten. "
            f"Generated fallback file: {fallback_path.relative_to(ROOT)}"
        )
        return fallback_path


def main() -> None:
    rows = read_rows()
    output_path = write_xlsx(rows)
    print(f"PASS: generated {output_path.relative_to(ROOT)}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
