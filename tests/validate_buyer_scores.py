from __future__ import annotations

import argparse
import ast
import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "buyers_master_sample.csv"
DEFAULT_SCORED = ROOT / "data" / "buyers_scored_sample.csv"
DEFAULT_SCRIPT = ROOT / "automations" / "buyer_scoring" / "generate_buyer_scores.py"

EXPECTED_COLUMNS = [
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

CONTACT_COLUMNS = {
    "contact_email",
    "contact_phone",
    "wechat_id",
    "whatsapp",
}

FORBIDDEN_CLAIMS = [
    "buyer is real",
    "verified buyer",
    "creditworthy",
    "creditworthiness verified",
    "payment ability verified",
    "guaranteed to purchase",
    "purchase certainty",
    "구매 확정입니다",
    "신용 검증 완료",
    "결제 능력 검증",
    "바이어 실제성 검증 완료",
]

FORBIDDEN_IMPORTS = {
    "requests",
    "urllib.request",
    "httpx",
    "selenium",
    "playwright",
}

FORBIDDEN_ACTIVE_CALL_PATTERNS = [
    r"\brequests\.",
    r"\burllib\.request\b",
    r"\bhttpx\.",
    r"\bselenium\b",
    r"\bplaywright\b",
    r"\bcrawl(?:er|ing)?\(",
    r"\bscrap(?:e|ing)?\(",
    r"\bapi_call\(",
    r"\bbuyer_enrichment\(",
    r"\bcredit_check",
]


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def has_bom(path: Path) -> bool:
    with path.open("rb") as file:
        return file.read(3) == b"\xef\xbb\xbf"


def read_csv(path: Path, label: str, failures: list[str]) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        failures.append(f"{label}: file does not exist: {path}")
        return [], []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                failures.append(f"{label}: missing header row")
                return [], []
            return reader.fieldnames, [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    except UnicodeDecodeError as exc:
        failures.append(f"{label}: not readable with utf-8-sig: {exc}")
        return [], []


def by_buyer_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("buyer_id", ""): row for row in rows}


def split_flags(value: str) -> set[str]:
    return {item.strip() for item in value.split(";") if item.strip()}


def is_true(value: str) -> bool:
    return value.strip().lower() == "true"


def contains_korean(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))


def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def check_files(input_path: Path, scored_path: Path, failures: list[str]) -> None:
    if not input_path.exists():
        failures.append(f"input: file does not exist: {input_path}")
    if not scored_path.exists():
        failures.append(f"scored: file does not exist: {scored_path}")
    if scored_path.exists() and not has_bom(scored_path):
        failures.append("scored: UTF-8 BOM is missing")


def check_columns(scored_columns: list[str], failures: list[str]) -> None:
    if scored_columns != EXPECTED_COLUMNS:
        failures.append(f"scored: output columns do not match expected order: {scored_columns}")
    leaked = [column for column in scored_columns if column in CONTACT_COLUMNS]
    if leaked:
        failures.append(f"scored: privacy-sensitive contact columns must not be copied: {', '.join(leaked)}")


def check_row_consistency(input_rows: list[dict[str, str]], scored_rows: list[dict[str, str]], failures: list[str]) -> None:
    input_ids = [row.get("buyer_id", "") for row in input_rows]
    scored_ids = [row.get("buyer_id", "") for row in scored_rows]
    if len(input_rows) != len(scored_rows):
        failures.append(f"row count mismatch: input={len(input_rows)} scored={len(scored_rows)}")
    if input_ids != scored_ids:
        failures.append(f"buyer_id sequence mismatch: input={input_ids} scored={scored_ids}")
    if any(not buyer_id for buyer_id in scored_ids):
        failures.append("scored: buyer_id values must be non-empty")
    duplicates = sorted({buyer_id for buyer_id in scored_ids if scored_ids.count(buyer_id) > 1})
    if duplicates:
        failures.append(f"scored: duplicate buyer_id values found: {', '.join(duplicates)}")


def check_score_fields(scored_rows: list[dict[str, str]], failures: list[str]) -> None:
    allowed_tiers = {"A", "B", "C", "Hold"}
    for row in scored_rows:
        buyer_id = row.get("buyer_id", "UNKNOWN")
        try:
            score = int(row.get("score_total", ""))
        except ValueError:
            failures.append(f"{buyer_id}: score_total is not numeric")
            continue
        if score < 0 or score > 100:
            failures.append(f"{buyer_id}: score_total outside 0-100: {score}")
        if row.get("priority_tier") not in allowed_tiers:
            failures.append(f"{buyer_id}: invalid priority_tier: {row.get('priority_tier')}")
        for field in ["scoring_summary", "recommended_next_action", "scoring_version", "scored_at"]:
            if not row.get(field, "").strip():
                failures.append(f"{buyer_id}: {field} must not be blank")


def check_approval(input_rows: list[dict[str, str]], scored_rows: list[dict[str, str]], failures: list[str]) -> None:
    scored_map = by_buyer_id(scored_rows)
    for input_row in input_rows:
        buyer_id = input_row.get("buyer_id", "")
        scored = scored_map.get(buyer_id, {})
        interested_brands = input_row.get("interested_brands", "")
        proposal_check = input_row.get("proposal_brand_check", "")
        should_block = proposal_check == "approval_required_review" or "메디큐브" in interested_brands
        if should_block and not is_true(scored.get("approval_block", "")):
            failures.append(f"{buyer_id}: approval_block must be true for approval-required brand/check")
        if is_true(scored.get("approval_block", "")):
            action = scored.get("recommended_next_action", "")
            has_internal_review = "internal approval review" in action.lower() or "내부 승인 검토" in action
            if scored.get("priority_tier") != "Hold" and not has_internal_review:
                failures.append(f"{buyer_id}: approval_block=true must be Hold unless action is internal approval review only")

    buyer_0004 = scored_map.get("BUYER-0004")
    if not buyer_0004:
        failures.append("BUYER-0004: required sample row missing from scored output")
        return
    flags = split_flags(buyer_0004.get("risk_flags", ""))
    action = buyer_0004.get("recommended_next_action", "")
    if not is_true(buyer_0004.get("approval_block", "")):
        failures.append("BUYER-0004: approval_block must be true")
    if buyer_0004.get("priority_tier") != "Hold":
        failures.append("BUYER-0004: priority_tier must be Hold")
    if "approval_required_brand" not in flags:
        failures.append("BUYER-0004: risk_flags must include approval_required_brand")
    if "internal approval review" not in action.lower() and "내부 승인 검토" not in action:
        failures.append("BUYER-0004: recommended_next_action must include internal approval review or 내부 승인 검토")


def check_moq(input_rows: list[dict[str, str]], scored_rows: list[dict[str, str]], failures: list[str]) -> None:
    scored_map = by_buyer_id(scored_rows)
    for input_row in input_rows:
        buyer_id = input_row.get("buyer_id", "")
        scored = scored_map.get(buyer_id, {})
        flags = split_flags(scored.get("risk_flags", ""))
        moq_fit = input_row.get("moq_fit", "")
        if moq_fit == "no":
            if scored.get("priority_tier") == "A":
                failures.append(f"{buyer_id}: moq_fit=no row must not be A")
            if "moq_not_met" not in flags:
                failures.append(f"{buyer_id}: moq_fit=no row must include moq_not_met")
        if moq_fit == "unknown" and not ({"moq_unknown", "quantity_unconfirmed"} & flags):
            failures.append(f"{buyer_id}: moq_fit=unknown row must include moq_unknown or quantity_unconfirmed")

    buyer_0002 = scored_map.get("BUYER-0002", {})
    if buyer_0002.get("priority_tier") == "A":
        failures.append("BUYER-0002: must not be A")
    buyer_0003_flags = split_flags(scored_map.get("BUYER-0003", {}).get("risk_flags", ""))
    if not ({"moq_unknown", "quantity_unconfirmed"} & buyer_0003_flags):
        failures.append("BUYER-0003: must include moq_unknown or quantity_unconfirmed")


def check_manual_flags(scored_rows: list[dict[str, str]], failures: list[str]) -> None:
    for row in scored_rows:
        buyer_id = row.get("buyer_id", "UNKNOWN")
        flags = split_flags(row.get("risk_flags", ""))
        if "source_manual_only" not in flags:
            failures.append(f"{buyer_id}: risk_flags must include source_manual_only")
        if "buyer_unverified" not in flags:
            failures.append(f"{buyer_id}: risk_flags must include buyer_unverified")

    combined_text = "\n".join(
        " ".join(row.get(field, "") for field in EXPECTED_COLUMNS)
        for row in scored_rows
    ).lower()
    for claim in FORBIDDEN_CLAIMS:
        if claim.lower() in combined_text:
            failures.append(f"scored: output contains unsupported claim: {claim}")


def check_payment_risk(input_rows: list[dict[str, str]], scored_rows: list[dict[str, str]], failures: list[str]) -> None:
    scored_map = by_buyer_id(scored_rows)
    for input_row in input_rows:
        buyer_id = input_row.get("buyer_id", "")
        scored = scored_map.get(buyer_id, {})
        flags = split_flags(scored.get("risk_flags", ""))
        payment_risk = input_row.get("payment_risk", "")
        if payment_risk == "high":
            if scored.get("priority_tier") == "A":
                failures.append(f"{buyer_id}: payment_risk=high row must not be A")
            if "payment_risk_high" not in flags:
                failures.append(f"{buyer_id}: payment_risk=high row must include payment_risk_high")
        if payment_risk == "unknown" and "payment_risk_unknown" not in flags:
            failures.append(f"{buyer_id}: payment_risk=unknown row should include payment_risk_unknown")


def check_privacy(scored_columns: list[str], scored_rows: list[dict[str, str]], failures: list[str]) -> None:
    leaked = CONTACT_COLUMNS & set(scored_columns)
    if leaked:
        failures.append(f"scored: contact columns leaked: {', '.join(sorted(leaked))}")
    combined = "\n".join(" ".join(row.values()) for row in scored_rows)
    suspicious_patterns = [
        r"buyer\d+@example\.invalid",
        r"\+00-0000-0000",
        r"placeholder_wechat_\d+",
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, combined):
            failures.append(f"scored: personal/contact placeholder data should not be copied: {pattern}")
    if "연락처 있음" in combined and "buyer quality" in combined.lower():
        failures.append("scored: contact readiness must not be treated as buyer quality")


def check_text_preservation(input_rows: list[dict[str, str]], scored_rows: list[dict[str, str]], failures: list[str]) -> None:
    input_text = "\n".join(" ".join(row.values()) for row in input_rows)
    scored_text = "\n".join(" ".join(row.values()) for row in scored_rows)
    if not contains_korean(scored_text):
        failures.append("scored: Korean text is not readable")
    if "메디큐브" not in input_text:
        failures.append("input: 메디큐브 sample text is missing or corrupted")
    if "메디큐브" in scored_text and "메디큐브" not in scored_text:
        failures.append("scored: 메디큐브 text is corrupted")
    if contains_chinese(scored_text) and not re.search(r"[\u4e00-\u9fff]", scored_text):
        failures.append("scored: Chinese text appears corrupted")


def check_scoring_script(script_path: Path, failures: list[str]) -> None:
    if not script_path.exists():
        failures.append(f"script: scoring script not found: {script_path}")
        return
    text = script_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        failures.append(f"script: syntax error while checking imports: {exc}")
        return

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    forbidden_imports = sorted(module for module in imported_modules if module in FORBIDDEN_IMPORTS)
    if forbidden_imports:
        failures.append(f"script: forbidden external collection imports found: {', '.join(forbidden_imports)}")

    code_without_docstrings = ast.get_source_segment(text, tree) or text
    for pattern in FORBIDDEN_ACTIVE_CALL_PATTERNS:
        if re.search(pattern, code_without_docstrings):
            failures.append(f"script: forbidden external collection indicator found: {pattern}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate scored buyer lead CSV output.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input buyer master CSV path")
    parser.add_argument("--scored", default=str(DEFAULT_SCORED), help="Scored buyer CSV path")
    parser.add_argument("--script", default=str(DEFAULT_SCRIPT), help="Buyer scoring script path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = resolve_path(args.input)
    scored_path = resolve_path(args.scored)
    script_path = resolve_path(args.script)
    failures: list[str] = []

    check_files(input_path, scored_path, failures)
    input_columns, input_rows = read_csv(input_path, "input", failures)
    scored_columns, scored_rows = read_csv(scored_path, "scored", failures)

    if scored_columns:
        check_columns(scored_columns, failures)
    if input_rows and scored_rows:
        check_row_consistency(input_rows, scored_rows, failures)
        check_score_fields(scored_rows, failures)
        check_approval(input_rows, scored_rows, failures)
        check_moq(input_rows, scored_rows, failures)
        check_manual_flags(scored_rows, failures)
        check_payment_risk(input_rows, scored_rows, failures)
        check_privacy(scored_columns, scored_rows, failures)
        check_text_preservation(input_rows, scored_rows, failures)
    check_scoring_script(script_path, failures)

    if failures:
        print("FAIL: buyer score validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: buyer score validation passed")
    print(f"input_rows={len(input_rows)}")
    print(f"scored_rows={len(scored_rows)}")
    print(f"scored_file={scored_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

