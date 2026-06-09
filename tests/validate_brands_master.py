from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "brands_raw.csv"
MASTER_PATH = ROOT / "data" / "brands_master.csv"

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

PRIORITY_VALUES = {"high", "medium", "low", "unknown"}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            return list(csv.DictReader(csv_file))
    except UnicodeDecodeError as exc:
        fail(f"{path} is not valid UTF-8: {exc}")


def main() -> None:
    if not RAW_PATH.exists():
        fail("data/brands_raw.csv does not exist")

    if not MASTER_PATH.exists():
        fail("data/brands_master.csv does not exist")

    raw_rows = read_csv(RAW_PATH)
    master_rows = read_csv(MASTER_PATH)

    with MASTER_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = reader.fieldnames or []

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing_columns:
        fail(f"brands_master.csv is missing required columns: {missing_columns}")

    if len(master_rows) != len(raw_rows):
        fail(
            "brands_master.csv row count does not match brands_raw.csv: "
            f"{len(master_rows)} != {len(raw_rows)}"
        )

    blank_brand_rows = [
        index for index, row in enumerate(master_rows, start=2) if not row["brand_ko"].strip()
    ]
    if blank_brand_rows:
        fail(f"blank brand_ko values found on CSV rows: {blank_brand_rows}")

    medicube_rows = [row for row in master_rows if row["brand_ko"] == "메디큐브"]
    if len(medicube_rows) != 1:
        fail(f"expected exactly one 메디큐브 row, found {len(medicube_rows)}")

    medicube = medicube_rows[0]
    if medicube["approval_required"] != "true":
        fail("메디큐브 must have approval_required=true")

    if medicube["proposal_allowed"] != "false":
        fail("메디큐브 must have proposal_allowed=false")

    invalid_approval_rows = [
        row["brand_ko"]
        for row in master_rows
        if row["approval_required"] == "true" and row["proposal_allowed"] != "false"
    ]
    if invalid_approval_rows:
        fail(
            "approval_required=true rows must have proposal_allowed=false unless explicitly "
            f"approved: {invalid_approval_rows}"
        )

    required_korean_values = {"라곰", "메디큐브", "조선미녀", "네추럴라이즈"}
    found_brands = {row["brand_ko"] for row in master_rows}
    missing_korean_values = sorted(required_korean_values - found_brands)
    if missing_korean_values:
        fail(f"Korean text was not preserved for: {missing_korean_values}")

    invalid_priority_rows = []
    for index, row in enumerate(master_rows, start=2):
        for column in ("china_priority", "global_priority"):
            if row[column] not in PRIORITY_VALUES:
                invalid_priority_rows.append((index, row["brand_ko"], column, row[column]))

    if invalid_priority_rows:
        fail(f"invalid priority values found: {invalid_priority_rows}")

    print("PASS: brands master validation passed")
    print(f"raw_rows={len(raw_rows)} master_rows={len(master_rows)}")


if __name__ == "__main__":
    main()
