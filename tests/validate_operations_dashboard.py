from __future__ import annotations

import argparse
import ast
import csv
import py_compile
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DASHBOARD = ROOT / "output" / "operations_dashboard.md"
DEFAULT_GENERATOR = ROOT / "automations" / "operations_dashboard" / "generate_operations_dashboard.py"
DEFAULT_BUYERS = ROOT / "data" / "buyers_master_sample.csv"
DEFAULT_SCORES = ROOT / "data" / "buyers_scored_sample.csv"
DEFAULT_PROPOSALS = ROOT / "data" / "proposal_messages_sample.csv"
DEFAULT_QUOTATIONS = ROOT / "data" / "quotation_sample.csv"
DEFAULT_BRANDS = ROOT / "data" / "brands_master.csv"

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "argparse",
    "collections",
    "csv",
    "datetime",
    "pathlib",
    "sys",
}

FORBIDDEN_IMPORTS = {
    "requests",
    "urllib.request",
    "httpx",
    "selenium",
    "playwright",
    "smtplib",
}

FORBIDDEN_SOURCE_PATTERNS = [
    re.compile(r"\bshell\s*=\s*True\b"),
    re.compile(r"\brequests\."),
    re.compile(r"\burllib\.request\b"),
    re.compile(r"\bhttpx\."),
    re.compile(r"\bselenium\b"),
    re.compile(r"\bplaywright\b"),
    re.compile(r"\bSMTP\s*\("),
    re.compile(r"\bsendmail\s*\("),
    re.compile(r"\bapi_call\s*\("),
    re.compile(r"\bbuyer_enrichment\s*\("),
    re.compile(r"\bcredit_check\s*\("),
    re.compile(r"\bcrawl(?:er|ing)?\s*\("),
    re.compile(r"\bscrap(?:e|ing)?\s*\("),
]

PRIVATE_PATHS = [
    "data/private",
    "output/private",
    "output/final",
]

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Integrated Runner Status",
    "Buyer Pipeline Summary",
    "Buyer Priority Summary",
    "Approval & Brand Risk Summary",
    "Proposal Message Summary",
    "Quotation Summary",
    "MOQ / Price / Stock / Expiry Issues",
    "Next Action Summary",
    "Internal Review Required Items",
    "Key Risks and Warnings",
    "Final Operational Recommendation",
]

REQUIRED_METRICS = [
    "integrated_runner_result",
    "integrated_runner_stage_count",
    "total_buyers",
    "buyer_count_by_priority_tier",
    "buyer_count_by_approval_block",
    "buyer_count_by_lead_status",
    "proposal_count_by_message_status",
    "quotation_count_by_quotation_status",
    "moq_issue_count",
    "price_confirmation_needed_count",
    "stock_confirmation_needed_count",
    "expiry_confirmation_needed_count",
    "approval_required_brand_issue_count",
    "medicube_blocked_or_review_needed_count",
    "required_internal_review_count",
    "next_action_summary",
    "key_risk_count",
]

PRIVACY_FORBIDDEN_TERMS = [
    "contact_email",
    "contact_phone",
    "wechat_id",
    "whatsapp",
    "phone",
    "email",
    "private_note",
    "real_contact",
    "real_price",
    "real_stock",
    "real_expiry",
]

FORBIDDEN_DASHBOARD_WORDING = [
    "external-ready",
    "send-ready",
    "final quotation",
    "approved quotation",
    "verified buyer",
    "credit-approved buyer",
    "purchase probability",
    "automatic sending",
    "buyer authenticity verification",
    "commercially approved price",
    "live market verified",
]

BUYER_COLUMNS = ["buyer_id", "lead_status", "moq_fit", "approval_warning", "proposal_brand_check", "next_action"]
SCORE_COLUMNS = ["buyer_id", "score_total", "priority_tier", "approval_block", "recommended_next_action"]
PROPOSAL_COLUMNS = ["buyer_id", "message_status", "approval_block", "required_internal_review", "next_action"]
QUOTATION_COLUMNS = [
    "buyer_id",
    "quotation_status",
    "approval_block",
    "brand_name",
    "moq_check",
    "unit_price",
    "stock_status",
    "expiry_date",
    "required_internal_review",
    "next_action",
]
BRAND_COLUMNS = ["brand_ko", "approval_required", "proposal_allowed"]


@dataclass
class Result:
    checks: int = 0
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(message)

    def warn(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.warnings.append(message)


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def normalize_path(path: Path) -> str:
    return str(path).replace("\\", "/").lower()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Operations Dashboard output and generator safety.")
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD))
    parser.add_argument("--generator", default=str(DEFAULT_GENERATOR))
    parser.add_argument("--buyers", default=str(DEFAULT_BUYERS))
    parser.add_argument("--scores", default=str(DEFAULT_SCORES))
    parser.add_argument("--proposals", default=str(DEFAULT_PROPOSALS))
    parser.add_argument("--quotations", default=str(DEFAULT_QUOTATIONS))
    parser.add_argument("--brands", default=str(DEFAULT_BRANDS))
    parser.add_argument("--skip-dashboard", action="store_true")
    return parser.parse_args()


def read_text(path: Path, result: Result, label: str) -> str:
    result.check(path.exists(), f"{label}: file does not exist: {path}")
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        result.check(False, f"{label}: not readable as UTF-8: {exc}")
        return ""


def read_csv_rows(path: Path, required_columns: list[str], result: Result, label: str) -> tuple[list[str], list[dict[str, str]]]:
    result.check(path.exists(), f"{label}: file does not exist: {path}")
    if not path.exists():
        return [], []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            columns = reader.fieldnames or []
            result.check(bool(columns), f"{label}: header row is missing")
            missing = [column for column in required_columns if column not in columns]
            result.check(not missing, f"{label}: missing required columns: {', '.join(missing)}")
            rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
            return columns, rows
    except UnicodeDecodeError as exc:
        result.check(False, f"{label}: not readable as utf-8-sig: {exc}")
    except csv.Error as exc:
        result.check(False, f"{label}: CSV parse error: {exc}")
    return [], []


def validate_private_path_arguments(paths: list[Path], result: Result) -> None:
    for path in paths:
        normalized = normalize_path(path)
        for private_path in PRIVATE_PATHS:
            result.check(private_path not in normalized, f"path must not use protected private/final location: {path}")


def import_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
    return names


def validate_generator(generator: Path, result: Result) -> None:
    result.check(generator.exists(), f"generator: file does not exist: {generator}")
    if not generator.exists():
        return

    try:
        py_compile.compile(str(generator), doraise=True)
    except py_compile.PyCompileError as exc:
        result.check(False, f"generator: compile failed: {exc}")
        return

    text = read_text(generator, result, "generator")
    if not text:
        return
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        result.check(False, f"generator: AST parse failed: {exc}")
        return

    imports = import_names(tree)
    result.check("argparse" in imports, "generator: argparse import is expected")
    result.check("csv" in imports, "generator: csv import is expected")
    result.check("pathlib" in imports, "generator: pathlib import is expected")
    result.check("collections" in imports, "generator: collections import is expected")
    result.check("datetime" in imports, "generator: datetime import is expected")

    forbidden_imports = sorted(FORBIDDEN_IMPORTS.intersection(imports))
    result.check(not forbidden_imports, f"generator: forbidden imports found: {', '.join(forbidden_imports)}")

    unexpected_imports = sorted(
        name for name in imports if name.split(".", 1)[0] not in ALLOWED_IMPORT_ROOTS and name not in ALLOWED_IMPORT_ROOTS
    )
    result.check(not unexpected_imports, f"generator: unexpected non-standard imports found: {', '.join(unexpected_imports)}")

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        result.check(not pattern.search(text), f"generator: forbidden source pattern found: {pattern.pattern}")

    result.check("shell=True" not in text, "generator: must not use shell=True")
    default_assignments = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("DEFAULT_") or line.strip().startswith("parser.add_argument")
    ]
    default_text = "\n".join(default_assignments).lower()
    result.check("data/private" not in default_text, "generator: must not default to data/private")
    result.check("output/private" not in default_text, "generator: must not default to output/private")
    result.check("output/final" not in default_text, "generator: must not default to output/final")
    result.check("operations_dashboard.xlsx" not in text, "generator: must not create XLSX dashboard in v1")
    result.check(
        "operations_dashboard_summary.csv" not in text,
        "generator: must not create data/operations_dashboard_summary.csv in v1",
    )
    result.check("DEFAULT_OUTPUT" in text and "operations_dashboard.md" in text, "generator: expected Markdown output default missing")
    result.check("--dry-run" in text, "generator: --dry-run support is required")


def contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def validate_required_sections(text: str, result: Result) -> None:
    for section in REQUIRED_SECTIONS:
        result.check(f"## {section}" in text, f"dashboard: required section missing: {section}")


def validate_required_metrics(text: str, result: Result) -> None:
    for metric in REQUIRED_METRICS:
        result.check(metric in text, f"dashboard: required metric label missing: {metric}")


def validate_dashboard_wording(text: str, result: Result) -> None:
    disclaimer_groups = [
        ["내부검토용", "internal review", "internal-review", "?대?寃?좎슜"],
        ["외부 발송 금지", "no external", "not externally", "?몃? 諛쒖넚 湲덉?"],
        ["최종 상업 승인 아님", "not final commercial", "not a final commercial", "理쒖쥌 ?곸뾽 ?뱀씤 ?꾨떂"],
        ["draft", "internal-review output"],
        ["score_total"],
        ["approval_block=true", "approval_block"],
        ["priority_tier", "score_total"],
        ["메디큐브", "Medicube", "硫붾뵒?먮툕"],
    ]
    for terms in disclaimer_groups:
        result.check(contains_any(text, terms), f"dashboard: required disclaimer/wording missing: {' / '.join(terms)}")

    lowered = text.lower()
    for term in PRIVACY_FORBIDDEN_TERMS:
        result.check(term not in lowered, f"dashboard: privacy-sensitive field name must not appear: {term}")
    for term in FORBIDDEN_DASHBOARD_WORDING:
        result.check(term not in lowered, f"dashboard: forbidden wording appears: {term}")
    for private_path in PRIVATE_PATHS:
        result.check(private_path not in lowered, f"dashboard: private/final path appears: {private_path}")


def validate_approval_safety(text: str, result: Result) -> None:
    result.check("approval_block" in text, "dashboard: approval_block summary is missing")
    result.check(contains_any(text, ["메디큐브", "Medicube", "硫붾뵒?먮툕"]), "dashboard: Medicube warning is missing")
    result.check(
        contains_any(text, ["approval-required", "approval required", "승인 필요", "?뱀씤 ?꾩슂", "review-required"]),
        "dashboard: approval-required/review-required wording is missing",
    )
    result.check(
        contains_any(text, ["proposal_allowed=false", "blocked", "not allowed", "차단"]),
        "dashboard: proposal_allowed=false or blocked/not allowed wording is missing",
    )
    result.check(
        contains_any(text, ["priority_tier", "score_total"]) and contains_any(text, ["approval_block=true", "approval_block"]),
        "dashboard: priority/score override caution is missing",
    )


def validate_proposal_quotation_safety(text: str, result: Result) -> None:
    result.check(
        contains_any(text, ["proposal messages are internal drafts", "제안 메시지는 내부", "proposal message", "draft"]),
        "dashboard: proposal draft/internal wording is missing",
    )
    result.check(
        contains_any(text, ["quotations are internal drafts", "견적", "internal drafts", "quotation outputs"]),
        "dashboard: quotation draft/internal wording is missing",
    )
    result.check(
        contains_any(text, ["not final commercial", "최종 상업 승인", "final commercial approval"]),
        "dashboard: quotation PASS final-commercial caution is missing",
    )
    result.check(
        not contains_any(text, ["send now", "send to buyer", "ready to send externally"]),
        "dashboard: external sending instruction appears",
    )


def validate_row_counts(
    text: str,
    buyers: list[dict[str, str]],
    scores: list[dict[str, str]],
    proposals: list[dict[str, str]],
    quotations: list[dict[str, str]],
    brands: list[dict[str, str]],
    result: Result,
) -> None:
    expected = {
        "total_buyers": len(buyers),
        "scores": len(scores),
        "proposals": len(proposals),
        "quotations": len(quotations),
        "brands": len(brands),
    }
    result.check(f"total_buyers: {expected['total_buyers']}" in text, "dashboard: total_buyers count appears wrong or missing")
    for label in ("scores", "proposals", "quotations", "brands"):
        result.warn(str(expected[label]) in text, f"dashboard: {label} row count is not visibly confirmed")


def validate_dashboard(
    dashboard: Path,
    buyers: list[dict[str, str]],
    scores: list[dict[str, str]],
    proposals: list[dict[str, str]],
    quotations: list[dict[str, str]],
    brands: list[dict[str, str]],
    result: Result,
) -> None:
    text = read_text(dashboard, result, "dashboard")
    if not text:
        return
    validate_required_sections(text, result)
    validate_required_metrics(text, result)
    validate_dashboard_wording(text, result)
    validate_approval_safety(text, result)
    validate_proposal_quotation_safety(text, result)
    validate_row_counts(text, buyers, scores, proposals, quotations, brands, result)


def main() -> int:
    args = parse_args()
    result = Result()

    generator = resolve_path(args.generator)
    dashboard = resolve_path(args.dashboard)
    buyers_path = resolve_path(args.buyers)
    scores_path = resolve_path(args.scores)
    proposals_path = resolve_path(args.proposals)
    quotations_path = resolve_path(args.quotations)
    brands_path = resolve_path(args.brands)

    validate_private_path_arguments(
        [generator, dashboard, buyers_path, scores_path, proposals_path, quotations_path, brands_path],
        result,
    )
    validate_generator(generator, result)

    _, buyers = read_csv_rows(buyers_path, BUYER_COLUMNS, result, "buyers")
    _, scores = read_csv_rows(scores_path, SCORE_COLUMNS, result, "scores")
    _, proposals = read_csv_rows(proposals_path, PROPOSAL_COLUMNS, result, "proposals")
    _, quotations = read_csv_rows(quotations_path, QUOTATION_COLUMNS, result, "quotations")
    _, brands = read_csv_rows(brands_path, BRAND_COLUMNS, result, "brands")

    result.check(len(buyers) > 0, "buyers: expected at least one sample row")
    result.check(len(scores) == len(buyers), "scores: row count should match buyers")
    result.check(len(proposals) == len(buyers), "proposals: row count should match buyers")
    result.check(len(quotations) > 0, "quotations: expected at least one sample row")
    result.check(len(brands) > 0, "brands: expected at least one brand row")

    if args.skip_dashboard:
        result.warn(not dashboard.exists(), "dashboard output already exists; Step E expected no generated dashboard")
    else:
        validate_dashboard(dashboard, buyers, scores, proposals, quotations, brands, result)

    status = "PASS" if not result.failures else "FAIL"
    print(f"{status}: operations dashboard validation {'passed' if status == 'PASS' else 'failed'}")
    print(f"checks={result.checks}")
    print(f"warnings={len(result.warnings)}")
    print(f"failures={len(result.failures)}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.failures:
        print("Failures:")
        for failure in result.failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
