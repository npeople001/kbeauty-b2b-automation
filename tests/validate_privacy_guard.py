"""Validate privacy and real-data guardrails before commit or operation.

This validator uses only local repository files and the Python standard
library. It does not scrape, search, call APIs, automate browsers, enrich buyer
data, check credit, send email/messages/quotations, or collect external data.
"""

from __future__ import annotations

import argparse
import ast
import csv
import fnmatch
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


TEXT_SUFFIXES = {".md", ".csv", ".txt", ".py", ".json", ".yaml", ".yml", ".gitignore"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__"}
SKIP_SUFFIXES = {".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".html"}

SENSITIVE_PATH_PATTERNS = [
    "data/private/**",
    "output/private/**",
    "output/final/**",
    "local_config/**",
    "*_real.csv",
    "*_private.csv",
    "*_production.csv",
    "*_contacts.csv",
    "*_buyers_real.csv",
    "*_prices.csv",
    "*_price_list.csv",
    "*_stock.csv",
    "*_inventory.csv",
    "*_expiry.csv",
    "*_quotation_final.*",
    "*_supplier_terms.*",
    "*_contract_terms.*",
    "*_payment_terms.*",
    "*_incoterms.*",
    "*_final_quotation.*",
    "*_external_ready.*",
    "*_send_ready.*",
    ".env",
    "*.key",
    "*_token*",
    "*_credentials*",
    "credentials.*",
    "secrets.*",
    "local_settings.*",
    "local_config.*",
]

REQUIRED_GITIGNORE_PATTERNS = [
    "data/private/**",
    "output/private/**",
    "output/final/**",
    "local_config/**",
    "*_real.csv",
    "*_private.csv",
    "*_contacts.csv",
    "*_prices.csv",
    "*_stock.csv",
    "*_expiry.csv",
    "*_quotation_final.*",
    "*_credentials*",
    ".env",
]

SAMPLE_NOT_IGNORED = [
    "data/buyers_master_sample.csv",
    "data/quotation_inputs_sample.csv",
    "docs/real_sample_data_policy.md",
    "tests/validate_quotations.py",
]

PROTECTED_EXAMPLE_PATHS = [
    "data/private/buyers/buyers_real.csv",
    "data/private/pricing/price_list_real.csv",
    "data/private/stock/stock_private.csv",
    "data/private/expiry/expiry_private.csv",
    "output/private/quotation_final.xlsx",
    "output/final/buyer_external_ready.pdf",
    "local_config/settings.local",
    "supplier_terms_private.csv",
]

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
PHONE_RE = re.compile(r"(?:\+\d{1,3}[- ]?)?(?:\d[- ]?){7,}\d")
MEDICUBE_TERMS = {"메디큐브", "硫붾뵒?먮툕"}
SAFE_CONTEXT_TERMS = [
    "approval-required",
    "approval required",
    "approval_required",
    "proposal_allowed=false",
    "blocked",
    "excluded",
    "excluded_brands",
    "approval_block",
    "internal-review",
    "internal review",
    "not external",
    "not in",
    "not appear",
    "must not",
    "must be excluded",
    "should be blank",
    "remove",
    "exclusion",
    "validation",
    "requires director approval",
    "승인",
    "차단",
    "제외",
    "내부 검토",
]
RISKY_MEDICUBE_TERMS = [
    "recommended_brands",
    "external-ready",
    "proposal-ready",
    "quotation-ready",
    "send_ready",
    "external_ready",
    "final quotation",
    "buyer-facing proposal",
]

CONTACT_FIELDS = {"contact_email", "contact_phone", "wechat_id", "whatsapp", "contact_name"}
PLACEHOLDER_EMAIL_DOMAIN = "example.invalid"
PLACEHOLDER_PHONE = "+00-0000-0000"
PLACEHOLDER_WECHAT_PREFIX = "placeholder"
PLACEHOLDER_CONTACT_PREFIX = "Sample Contact"

DISCLAIMER_FILES = {
    "data/proposal_messages_sample.csv",
    "data/quotation_sample.csv",
}
DISCLAIMER_FILE_KEYWORDS = ["proposal_messages", "quotation_sample"]
DISCLAIMER_TERMS = [
    "내부 검토용",
    "internal review",
    "외부 발송 전 검토 필요",
    "외부 발송 금지",
    "외부로 발송되지",
    "?대? 寃?좎슜",
    "?몃? 諛쒖넚 湲덉?",
]

FORBIDDEN_IMPORT_MODULES = {
    "requests",
    "httpx",
    "selenium",
    "playwright",
    "smtplib",
}
FORBIDDEN_IMPORT_PREFIXES = {
    "urllib.request",
}
FORBIDDEN_CODE_PATTERNS = [
    re.compile(r"\bSMTP\s*\(", re.IGNORECASE),
    re.compile(r"\.sendmail\s*\(", re.IGNORECASE),
    re.compile(r"\brequests\.(get|post|put|delete|request)\s*\(", re.IGNORECASE),
    re.compile(r"\bhttpx\.(get|post|put|delete|request)\s*\(", re.IGNORECASE),
    re.compile(r"\bwebdriver\.", re.IGNORECASE),
]


@dataclass
class Result:
    scanned: int = 0
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repository privacy guardrails.")
    parser.add_argument("--root", default=".", help="Repository root path")
    parser.add_argument(
        "--mode",
        default="working-tree",
        choices=["working-tree", "staged-only"],
        help="Validation mode",
    )
    parser.add_argument(
        "--staged-only",
        action="store_true",
        help="Shortcut for --mode staged-only",
    )
    return parser.parse_args()


def normalize_rel(path: Path, root: Path) -> str:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        rel = path
    return str(rel).replace("\\", "/")


def run_git(root: Path, args: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", "git is unavailable"
    return proc.returncode, proc.stdout, proc.stderr


def git_available(root: Path) -> bool:
    code, _, _ = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    return code == 0


def git_check_ignore(root: Path, rel_path: str) -> bool:
    code, _, _ = run_git(root, ["check-ignore", "-q", "--", rel_path])
    return code == 0


def git_tracked(root: Path, rel_path: str) -> bool:
    code, _, _ = run_git(root, ["ls-files", "--error-unmatch", "--", rel_path])
    return code == 0


def staged_files(root: Path, result: Result) -> list[str]:
    code, stdout, stderr = run_git(root, ["diff", "--cached", "--name-only"])
    if code != 0:
        result.fail(f"git staged file inspection failed: {stderr.strip() or stdout.strip()}")
        return []
    return [line.strip().replace("\\", "/") for line in stdout.splitlines() if line.strip()]


def working_tree_files(root: Path, result: Result) -> list[str]:
    if git_available(root):
        code1, tracked, err1 = run_git(root, ["ls-files"])
        code2, untracked, err2 = run_git(root, ["ls-files", "--others", "--exclude-standard"])
        if code1 == 0 and code2 == 0:
            files = set()
            files.update(line.strip().replace("\\", "/") for line in tracked.splitlines() if line.strip())
            files.update(line.strip().replace("\\", "/") for line in untracked.splitlines() if line.strip())
            return sorted(files)
        result.warn(f"git file listing failed; falling back to directory walk: {err1.strip()} {err2.strip()}".strip())

    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            files.append(normalize_rel(path, root))
    return sorted(files)


def text_like(rel_path: str) -> bool:
    name = Path(rel_path).name
    suffix = Path(rel_path).suffix.lower()
    if name == ".gitignore":
        return True
    return suffix in TEXT_SUFFIXES


def should_skip(rel_path: str) -> bool:
    path = Path(rel_path)
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    suffix = path.suffix.lower()
    if suffix in SKIP_SUFFIXES:
        return True
    if rel_path.startswith("output/") and rel_path != "output/.gitkeep":
        return True
    return False


def is_sensitive_path(rel_path: str) -> bool:
    name = Path(rel_path).name
    return any(fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern) for pattern in SENSITIVE_PATH_PATTERNS)


def read_text(path: Path, result: Result, rel_path: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        result.warn(f"{rel_path}: skipped non-UTF-8 or binary-like text file")
        return None
    except OSError as exc:
        result.fail(f"{rel_path}: cannot read file: {exc}")
        return None


def check_sensitive_filenames(root: Path, rel_paths: list[str], result: Result, staged_set: set[str]) -> None:
    for rel_path in rel_paths:
        if not is_sensitive_path(rel_path):
            continue
        ignored = git_check_ignore(root, rel_path) if git_available(root) else False
        tracked = git_tracked(root, rel_path) if git_available(root) else False
        staged = rel_path in staged_set
        if staged or (not ignored and not tracked):
            result.fail(f"{rel_path}: high-risk filename/path is not safely ignored")
        elif ignored:
            result.warn(f"{rel_path}: high-risk filename/path is protected by .gitignore")


def check_gitignore(root: Path, result: Result) -> None:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        result.fail(".gitignore is missing")
        return
    text = gitignore.read_text(encoding="utf-8")
    lines = {line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")}
    for pattern in REQUIRED_GITIGNORE_PATTERNS:
        if pattern not in lines:
            result.fail(f".gitignore missing required privacy pattern: {pattern}")

    for rel_path in PROTECTED_EXAMPLE_PATHS:
        if not git_check_ignore(root, rel_path):
            result.fail(f".gitignore does not protect example private path: {rel_path}")

    for rel_path in SAMPLE_NOT_IGNORED:
        if git_check_ignore(root, rel_path):
            result.fail(f"sample/source file is accidentally ignored: {rel_path}")


def check_contact_csv(path: Path, rel_path: str, result: Result) -> None:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if not reader.fieldnames:
                return
            contact_columns = [column for column in reader.fieldnames if column in CONTACT_FIELDS]
            if not contact_columns:
                return
            for row_number, row in enumerate(reader, start=2):
                for column in contact_columns:
                    value = (row.get(column) or "").strip()
                    if not value:
                        continue
                    if column == "contact_email":
                        domain = value.split("@")[-1].lower() if "@" in value else ""
                        if domain != PLACEHOLDER_EMAIL_DOMAIN:
                            result.fail(f"{rel_path}:{row_number}: sample contact_email is not example.invalid")
                    elif column in {"contact_phone", "whatsapp"}:
                        if value != PLACEHOLDER_PHONE:
                            result.fail(f"{rel_path}:{row_number}: sample {column} is not placeholder phone")
                    elif column == "wechat_id":
                        if PLACEHOLDER_WECHAT_PREFIX not in value.lower():
                            result.fail(f"{rel_path}:{row_number}: sample wechat_id is not placeholder-style")
                    elif column == "contact_name":
                        if not value.startswith(PLACEHOLDER_CONTACT_PREFIX):
                            result.fail(f"{rel_path}:{row_number}: sample contact_name is not placeholder-style")
    except csv.Error as exc:
        result.warn(f"{rel_path}: CSV parse warning during contact check: {exc}")


def check_emails_in_text(text: str, rel_path: str, result: Result) -> None:
    for match in EMAIL_RE.finditer(text):
        domain = match.group(1).lower()
        if domain != PLACEHOLDER_EMAIL_DOMAIN:
            result.fail(f"{rel_path}: non-placeholder email detected: {match.group(0)}")


def check_phone_like_in_text(text: str, rel_path: str, result: Result) -> None:
    if "contact_phone" not in text and "whatsapp" not in text:
        return
    for match in PHONE_RE.finditer(text):
        value = match.group(0)
        placeholder_international = re.fullmatch(r"\+\d{1,3}(?:-0+)+", value) is not None
        if value != PLACEHOLDER_PHONE and not placeholder_international and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            result.warn(f"{rel_path}: phone-like value needs review: {value}")


def check_disclaimer(text: str, rel_path: str, result: Result) -> None:
    relevant = rel_path in DISCLAIMER_FILES or any(keyword in rel_path for keyword in DISCLAIMER_FILE_KEYWORDS)
    if not relevant:
        return
    lowered = text.lower()
    if not any(term.lower() in lowered for term in DISCLAIMER_TERMS):
        result.fail(f"{rel_path}: internal-review disclaimer is missing")


def line_has_safe_medicube_context(line: str) -> bool:
    lowered = line.lower()
    return any(term.lower() in lowered for term in SAFE_CONTEXT_TERMS)


def check_medicube_context(text: str, rel_path: str, result: Result) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not any(term in line for term in MEDICUBE_TERMS):
            continue
        lowered = line.lower()
        risky = any(term.lower() in lowered for term in RISKY_MEDICUBE_TERMS)
        recommended_value = "recommended_brands" in lowered and not any(term in lowered for term in ["excluded", "blank", "must not", "not in"])
        if (risky or recommended_value) and not line_has_safe_medicube_context(line):
            result.fail(f"{rel_path}:{line_number}: approval-required brand appears in risky external-ready context")


def check_python_forbidden_code(path: Path, rel_path: str, text: str, result: Result) -> None:
    if not rel_path.endswith(".py"):
        return
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        result.warn(f"{rel_path}: Python parse warning: {exc}")
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name in FORBIDDEN_IMPORT_MODULES or name in FORBIDDEN_IMPORT_PREFIXES:
                    result.fail(f"{rel_path}: forbidden import detected: {name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in FORBIDDEN_IMPORT_MODULES or module in FORBIDDEN_IMPORT_PREFIXES:
                result.fail(f"{rel_path}: forbidden import detected: {module}")

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#") or "does not" in stripped.lower() or "do not" in stripped.lower():
            continue
        for pattern in FORBIDDEN_CODE_PATTERNS:
            if pattern.search(line):
                result.fail(f"{rel_path}:{line_number}: forbidden operational code pattern detected")


def scan_file(root: Path, rel_path: str, result: Result) -> None:
    if should_skip(rel_path) or not text_like(rel_path):
        return
    path = root / rel_path
    if not path.exists() or not path.is_file():
        return
    text = read_text(path, result, rel_path)
    if text is None:
        return
    result.scanned += 1

    if rel_path.endswith(".csv"):
        check_contact_csv(path, rel_path, result)
    check_emails_in_text(text, rel_path, result)
    check_phone_like_in_text(text, rel_path, result)
    check_disclaimer(text, rel_path, result)
    check_medicube_context(text, rel_path, result)
    check_python_forbidden_code(path, rel_path, text, result)


def main() -> int:
    args = parse_args()
    mode = "staged-only" if args.staged_only else args.mode
    root = Path(args.root).resolve()
    result = Result()

    if not root.exists():
        print("FAIL: privacy guard validation failed")
        print(f"- root does not exist: {root}")
        return 1

    has_git = git_available(root)
    if not has_git:
        if mode == "staged-only":
            print("FAIL: privacy guard validation failed")
            print("- git is unavailable; staged-only mode cannot inspect staged files")
            return 1
        result.warn("git is unavailable; falling back to working-tree directory scan")

    staged = set(staged_files(root, result)) if has_git else set()
    rel_paths = staged_files(root, result) if mode == "staged-only" and has_git else working_tree_files(root, result)

    check_gitignore(root, result)
    check_sensitive_filenames(root, rel_paths, result, staged)

    for rel_path in rel_paths:
        scan_file(root, rel_path, result)

    status = "PASS" if not result.failures else "FAIL"
    print(f"{status}: privacy guard validation {'passed' if status == 'PASS' else 'failed'}")
    print(f"files_scanned={result.scanned}")
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
