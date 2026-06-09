"""Validate the controlled integrated runner before full workflow execution."""

from __future__ import annotations

import argparse
import ast
import py_compile
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNNER = ROOT / "automations" / "run_internal_workflow.py"
DEFAULT_SUMMARY = ROOT / "output" / "internal_workflow_summary.md"

REQUIRED_STAGES = [
    "privacy_guard_validation",
    "buyer_lead_validation",
    "buyer_scoring_generation",
    "buyer_score_validation",
    "proposal_message_generation",
    "proposal_message_validation",
    "quotation_generation",
    "quotation_validation",
]

FORBIDDEN_IMPORTS = {
    "requests",
    "urllib.request",
    "httpx",
    "selenium",
    "playwright",
    "smtplib",
}

FORBIDDEN_CALL_PATTERNS = [
    r"\brequests\.",
    r"\burllib\.request\b",
    r"\bhttpx\.",
    r"\bselenium\b",
    r"\bplaywright\b",
    r"\bSMTP\s*\(",
    r"\bsendmail\s*\(",
    r"\bcrawl(?:er|ing)?\s*\(",
    r"\bscrap(?:e|ing)?\s*\(",
    r"\bapi_call\s*\(",
    r"\bbuyer_enrichment\s*\(",
    r"\bcredit_check\s*\(",
]

FORBIDDEN_PATHS = [
    "data/private/",
    "data\\private\\",
    "output/private/",
    "output\\private\\",
    "output/final/",
    "output\\final\\",
]

SUMMARY_REQUIRED_TERMS = [
    "workflow",
    "result",
    "started_at",
    "finished_at",
    "internal review only",
    "external_sending: not included",
    "Stage Results",
    "Stage Details",
    "command",
    "Output Paths",
    "Next Action",
]


@dataclass
class ValidationResult:
    checks: int = 0
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        return False, str(exc)
    return True, ""


def import_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names.add(module)
    return names


def string_values(tree: ast.AST) -> list[str]:
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)
    return values


def function_source_has(text: str, function_name: str, required_terms: list[str]) -> bool:
    pattern = re.compile(rf"def {re.escape(function_name)}\(.*?(?=\ndef |\nclass |\Z)", re.S)
    match = pattern.search(text)
    if not match:
        return False
    source = match.group(0)
    return all(term in source for term in required_terms)


def stage_positions(values: list[str]) -> list[int]:
    positions: list[int] = []
    for stage in REQUIRED_STAGES:
        try:
            positions.append(values.index(stage))
        except ValueError:
            positions.append(-1)
    return positions


def validate_source_structure(runner: Path, result: ValidationResult) -> str:
    result.check(runner.exists(), f"Runner file is missing: {runner}")
    if not runner.exists():
        return ""

    ok, error = compile_file(runner)
    result.check(ok, f"Runner does not compile: {error}")

    text = read_text(runner)
    tree = ast.parse(text)
    imports = import_names(tree)
    strings = string_values(tree)

    result.check("argparse" in imports, "Runner must use argparse.")
    result.check("subprocess" in imports, "Runner must import subprocess.")
    result.check("sys" in imports, "Runner must import sys.")
    result.check("pathlib" in imports or "Path" in text, "Runner must use pathlib/Path.")
    result.check("datetime" in imports or "datetime" in text, "Runner must use timestamp handling.")
    result.check("subprocess.run" in text, "Runner must use subprocess.run.")
    result.check("sys.executable" in text, "Runner must use sys.executable.")
    result.check("shell=True" not in text, "Runner must not use shell=True.")
    result.check("capture_output=True" in text, "Runner must capture subprocess output.")
    result.check("text=True" in text, "Runner must run subprocess in text mode.")
    result.check("buyer_sales_sample" in text, "Runner must support buyer_sales_sample.")

    positions = stage_positions(strings)
    result.check(all(position >= 0 for position in positions), "Runner is missing one or more required stages.")
    result.check(positions == sorted(positions), "Runner stages are not in the required logical order.")
    result.check(strings.index(REQUIRED_STAGES[0]) == min(position for position in positions if position >= 0), "Privacy Guard must be the first required stage.")
    result.check("final_run_summary" in text and "write_summary" in text, "Runner must include final summary behavior.")
    result.check(
        function_source_has(text, "run_workflow", ["privacy_guard_validation", "should_skip"]),
        "Runner must treat Privacy Guard failure as blocking.",
    )
    result.check(
        "--dry-run" in text and "print_dry_run" in text,
        "Runner must support dry-run behavior.",
    )
    result.check(
        "--workflow" in text and "choices=[WORKFLOW_NAME]" in text,
        "Runner must not allow arbitrary workflows by default.",
    )

    forbidden_imports = sorted(FORBIDDEN_IMPORTS.intersection(imports))
    result.check(not forbidden_imports, f"Runner has forbidden imports: {', '.join(forbidden_imports)}")
    for pattern in FORBIDDEN_CALL_PATTERNS:
        result.check(
            not re.search(pattern, text),
            f"Runner appears to contain forbidden implementation pattern: {pattern}",
        )
    for path_text in FORBIDDEN_PATHS:
        result.check(path_text not in text, f"Runner references forbidden private/final path: {path_text}")

    sample_only_terms = [
        "data/buyers_raw_sample.csv",
        "data/buyers_master_sample.csv",
        "data/buyers_scored_sample.csv",
        "data/proposal_messages_sample.csv",
        "data/quotation_inputs_sample.csv",
        "data/quotation_sample.csv",
    ]
    for term in sample_only_terms:
        result.check(term in text, f"Runner should use sample workflow file: {term}")

    return text


def run_dry_run(runner: Path, summary: Path, result: ValidationResult) -> None:
    before_exists = summary.exists()
    before_mtime = summary.stat().st_mtime_ns if before_exists else None
    completed = subprocess.run(
        [sys.executable, str(runner), "--workflow", "buyer_sales_sample", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    after_exists = summary.exists()
    after_mtime = summary.stat().st_mtime_ns if after_exists else None
    output = f"{completed.stdout}\n{completed.stderr}"

    result.check(completed.returncode == 0, "Runner dry-run must exit successfully.")
    result.check("dry-run" in output.lower(), "Dry-run output must identify simulation mode.")
    result.check("PLANNED" in output, "Dry-run output must include planned stages.")
    result.check("python" in output.lower() or ".py" in output, "Dry-run output must include planned commands.")
    for stage in REQUIRED_STAGES:
        result.check(stage in output, f"Dry-run output missing stage: {stage}")
    result.check("final_run_summary" in output, "Dry-run output missing final summary stage.")
    result.check(before_exists == after_exists, "Dry-run must not create or delete the summary file.")
    if before_exists and after_exists:
        result.check(before_mtime == after_mtime, "Dry-run must not modify the existing summary file.")


def validate_summary(summary: Path, result: ValidationResult) -> None:
    if not summary.exists():
        result.failures.append(f"Summary check requested but summary does not exist: {summary}")
        return
    text = read_text(summary)
    for term in SUMMARY_REQUIRED_TERMS:
        result.check(term in text, f"Summary missing required term: {term}")
    for stage in REQUIRED_STAGES + ["final_run_summary"]:
        result.check(stage in text, f"Summary missing stage: {stage}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the Integrated Runner.")
    parser.add_argument("--runner", default=str(DEFAULT_RUNNER), help="Path to runner script.")
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY), help="Path to workflow summary.")
    parser.add_argument(
        "--check-summary",
        action="store_true",
        help="Validate an existing full-run summary file.",
    )
    parser.add_argument(
        "--dry-run-output",
        default="",
        help="Reserved path for future dry-run output capture validation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = ValidationResult()
    runner = resolve_path(args.runner)
    summary = resolve_path(args.summary)

    validate_source_structure(runner, result)
    if runner.exists():
        run_dry_run(runner, summary, result)

    if args.dry_run_output:
        result.warn(False, "--dry-run-output is reserved for future file-based dry-run validation.")

    if args.check_summary:
        validate_summary(summary, result)

    if result.failures:
        print("FAIL: integrated runner validation failed")
    else:
        print("PASS: integrated runner validation passed")
    print(f"checks={result.checks}")
    print(f"warnings={len(result.warnings)}")
    print(f"failures={len(result.failures)}")

    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for failure in result.failures:
        print(f"FAILURE: {failure}")

    return 1 if result.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
