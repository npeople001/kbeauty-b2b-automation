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

RESTRICTED_PATH_PREFIXES = [
    "data/private/",
    "data/private/templates/",
    "output/private/",
    "output/final/",
    "local_config/",
]

RESTRICTED_LOCAL_FOLDERS = [
    "data/private",
    "data/private/templates",
    "output/private",
    "output/final",
]

SENSITIVE_PATH_PATTERNS = [
    "data/private/**",
    "output/private/**",
    "output/final/**",
    "local_config/**",
    "*_real.csv",
    "*_real.xlsx",
    "*_private.csv",
    "*_private.xlsx",
    "*_production.csv",
    "*_contacts.csv",
    "*_contacts.xlsx",
    "*_contact*.csv",
    "*_contact*.xlsx",
    "*_buyers_real.csv",
    "*_prices.csv",
    "*_prices.xlsx",
    "*_price*.csv",
    "*_price*.xlsx",
    "*_price_list.csv",
    "*_stock.csv",
    "*_stock.xlsx",
    "*_stock*.csv",
    "*_stock*.xlsx",
    "*_inventory.csv",
    "*_expiry.csv",
    "*_expiry.xlsx",
    "*_expiry*.csv",
    "*_expiry*.xlsx",
    "*_quotation_final.*",
    "*_approved_quotation.*",
    "*_commercially_approved.*",
    "*_supplier_terms.*",
    "*_contract_terms.*",
    "*_payment_terms.*",
    "*_incoterms.*",
    "*_final_quotation.*",
    "*_external_ready.*",
    "*_send_ready.*",
    "*real_data*",
    "*private_data*",
    "*buyer_contacts*",
    "*wechat*",
    "*whatsapp*",
    "*supplier_terms*",
    "*distributor_terms*",
    "*internal_margin*",
    "*final_quote*",
    "*final_quotation*",
    "*external_ready*",
    "*send_ready*",
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

KNOWN_IGNORED_GENERATED_OUTPUTS = [
    "output/operations_dashboard.md",
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
    "not external-ready",
    "not final quotation",
    "not in",
    "not appear",
    "must not",
    "do not",
    "prohibited",
    "no automatic sending",
    "no external sending",
    "planning only",
    "documentation only",
    "future candidate",
    "future validator",
    "out of scope",
    "never commit",
    "sample-to-real mapping",
    "approval gate",
    "privacy guard",
    "manual review",
    "restricted path",
    "future real/private",
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
SAFE_PLACEHOLDER_TERMS = {
    "example.invalid",
    "+00-0000-0000",
    "buyer_example_001",
    "contact_name_example",
    "wechat_example",
    "whatsapp_example",
    "line_example",
    "kakao_example",
    "price_placeholder",
    "stock_placeholder",
    "expiry_yyyy_mm_dd",
    "approval_required_placeholder",
    "sample_only",
    "internal_review_only",
    "not_external_ready",
    "not_final_quotation",
    "sample_contact",
    "sample_buyer",
    "sample_price",
    "sample_stock",
    "sample_expiry",
}

SAFE_INTERNAL_REVIEW_TERMS = {
    "internal-review",
    "internal review",
    "internal_review",
    "internal_review_only",
    "draft",
    "sample",
    "sample-only",
    "sample_only",
    "placeholder",
    "not external-ready",
    "not_external_ready",
    "not final quotation",
    "not_final_quotation",
    "blocked",
    "excluded",
    "approval_block",
}

SENSITIVE_CONTENT_MARKERS = {
    "contact": [
        "contact_email",
        "contact_phone",
        "wechat_id",
        "whatsapp",
        "kakao_id",
        "line_id",
        "real_contact",
        "private_contact",
        "buyer_contact",
        "buyer_legal_name",
        "legal_name",
    ],
    "commercial_terms": [
        "real_price",
        "private_price",
        "negotiated_price",
        "confirmed_price",
        "supplier_price",
        "distributor_price",
        "supplier_private_terms",
        "distributor_private_terms",
        "payment_terms_real",
        "incoterms_real",
    ],
    "stock_expiry": [
        "real_stock",
        "private_stock",
        "confirmed_stock",
        "stock_quantity",
        "real_expiry",
        "private_expiry",
        "confirmed_expiry",
        "expiry_date",
    ],
    "internal_margin": [
        "internal_margin",
    ],
    "final_quotation": [
        "final_quotation",
        "final_quote",
        "approved_quotation",
        "commercially_approved",
    ],
    "external_ready": [
        "external_ready",
        "send_ready",
        "ready_to_send",
        "approved_to_send",
    ],
}

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


def format_issue(
    severity: str,
    source: str,
    path: str,
    reason: str,
    fix: str,
    detail: str = "",
) -> str:
    message = f"{severity} [{source}] {path}: {reason}"
    if detail:
        message = f"{message} ({detail})"
    return f"{message}. Suggested fix: {fix}"


def add_warning(result: Result, source: str, path: str, reason: str, fix: str, detail: str = "") -> None:
    result.warn(format_issue("WARNING", source, path, reason, fix, detail))


def add_failure(result: Result, source: str, path: str, reason: str, fix: str, detail: str = "") -> None:
    result.fail(format_issue("FAIL", source, path, reason, fix, detail))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repository privacy guardrails.")
    parser.add_argument("--root", default=".", help="Repository root path")
    parser.add_argument(
        "--mode",
        default="all",
        choices=["all", "working-tree", "staged-only"],
        help="Validation mode",
    )
    parser.add_argument(
        "--staged-only",
        action="store_true",
        help="Shortcut for --mode staged-only",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run safe in-memory synthetic Privacy Guard checks without touching repository data",
    )
    return parser.parse_args()


def normalize_rel(path: Path, root: Path) -> str:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        rel = path
    return normalize_git_path(str(rel))


def normalize_git_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


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
    return [normalize_git_path(line) for line in stdout.splitlines() if line.strip()]


def tracked_files(root: Path, result: Result) -> list[str]:
    code, stdout, stderr = run_git(root, ["ls-files"])
    if code != 0:
        result.fail(f"git tracked file inspection failed: {stderr.strip() or stdout.strip()}")
        return []
    return [normalize_git_path(line) for line in stdout.splitlines() if line.strip()]


def working_tree_files(root: Path, result: Result) -> list[str]:
    if git_available(root):
        code1, tracked, err1 = run_git(root, ["ls-files"])
        code2, untracked, err2 = run_git(root, ["ls-files", "--others", "--exclude-standard"])
        if code1 == 0 and code2 == 0:
            files = set()
            files.update(normalize_git_path(line) for line in tracked.splitlines() if line.strip())
            files.update(normalize_git_path(line) for line in untracked.splitlines() if line.strip())
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


def docs_path(rel_path: str) -> bool:
    normalized = normalize_git_path(rel_path).lower()
    return normalized in {"readme.md", "agents.md"} or (normalized.startswith("docs/") and normalized.endswith(".md"))


def code_path(rel_path: str) -> bool:
    normalized = normalize_git_path(rel_path).lower()
    return normalized.startswith("tests/") or normalized.startswith("automations/")


def strict_content_path(rel_path: str) -> bool:
    normalized = normalize_git_path(rel_path).lower()
    name = Path(normalized).name
    suffix = Path(normalized).suffix
    if normalized.startswith("data/") and suffix in {".csv", ".xlsx"}:
        return True
    if normalized.startswith("output/") and suffix in {".csv", ".xlsx", ".md"}:
        return True
    return False


def sample_safe_strict_path(rel_path: str) -> bool:
    normalized = normalize_git_path(rel_path).lower()
    name = Path(normalized).name
    if normalized.startswith("data/") and ("_sample" in name or name.startswith("sample_")):
        return True
    return normalized in {
        "data/brands_master.csv",
        "data/brands_raw.csv",
        "data/buyers_raw.csv",
        "data/research_inputs_sample.csv",
    }


def safe_lower(value: str) -> str:
    return (value or "").strip().lower()


def line_contains_safe_context(line: str) -> bool:
    lowered = safe_lower(line)
    return any(term in lowered for term in SAFE_CONTEXT_TERMS)


def value_contains_safe_placeholder(value: str) -> bool:
    lowered = safe_lower(value)
    return any(term in lowered for term in SAFE_PLACEHOLDER_TERMS)


def line_contains_sample_or_internal_review_context(line: str) -> bool:
    lowered = safe_lower(line)
    return any(term in lowered for term in SAFE_PLACEHOLDER_TERMS | SAFE_INTERNAL_REVIEW_TERMS)


def docs_or_code_context_is_safe(rel_path: str, line: str) -> bool:
    if not (docs_path(rel_path) or code_path(rel_path)):
        return False
    return line_contains_safe_context(line) or line_contains_sample_or_internal_review_context(line)


def is_sensitive_path(rel_path: str) -> bool:
    return matching_sensitive_path_pattern(rel_path) is not None


def matching_sensitive_path_pattern(rel_path: str) -> str | None:
    normalized = normalize_git_path(rel_path).lower()
    name = Path(normalized).name
    for pattern in SENSITIVE_PATH_PATTERNS:
        lowered_pattern = pattern.lower()
        if fnmatch.fnmatch(normalized, lowered_pattern) or fnmatch.fnmatch(name, lowered_pattern):
            return pattern
    return None


def exempt_from_sensitive_filename_check(rel_path: str) -> bool:
    normalized = normalize_git_path(rel_path).lower()
    if normalized in {"readme.md", "agents.md", "tests/validate_privacy_guard.py"}:
        return True
    return normalized.startswith("docs/") and normalized.endswith(".md")


def is_restricted_path(rel_path: str) -> bool:
    normalized = normalize_git_path(rel_path)
    return any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in RESTRICTED_PATH_PREFIXES)


def check_restricted_paths(root: Path, result: Result, mode: str, staged_set: set[str]) -> None:
    for rel_path in sorted(staged_set):
        if is_restricted_path(rel_path):
            add_failure(
                result,
                "path",
                rel_path,
                "restricted private/final path is staged",
                "Unstage the file and keep real/private/final data outside Git.",
            )

    if mode != "staged-only":
        for rel_path in tracked_files(root, result):
            if is_restricted_path(rel_path):
                add_failure(
                    result,
                    "path",
                    rel_path,
                    "restricted private/final path is tracked",
                    "Remove the private/final path from Git tracking after manual review.",
                )

        for folder in RESTRICTED_LOCAL_FOLDERS:
            folder_path = root / folder
            if not folder_path.exists():
                continue
            normalized = normalize_git_path(folder)
            tracked_under_folder = any(path == normalized or path.startswith(f"{normalized}/") for path in tracked_files(root, result))
            staged_under_folder = any(path == normalized or path.startswith(f"{normalized}/") for path in staged_set)
            ignored = git_check_ignore(root, f"{normalized}/example.placeholder") if git_available(root) else False
            if not tracked_under_folder and not staged_under_folder and ignored:
                add_warning(
                    result,
                    "path",
                    normalized,
                    "restricted folder exists locally but is ignored and untracked",
                    "Review local-only files and do not commit private/final data.",
                )
            elif not tracked_under_folder and not staged_under_folder:
                add_failure(
                    result,
                    "path",
                    normalized,
                    "restricted folder exists locally but is not confirmed ignored",
                    "Confirm .gitignore protection or remove the folder before proceeding.",
                )


def read_text(path: Path, result: Result, rel_path: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        result.warn(f"{rel_path}: skipped non-UTF-8 or binary-like text file")
        return None
    except OSError as exc:
        result.fail(f"{rel_path}: cannot read file: {exc}")
        return None


def check_sensitive_filenames(root: Path, result: Result, mode: str, staged_set: set[str]) -> None:
    paths_to_check = set(staged_set)
    if mode != "staged-only":
        paths_to_check.update(tracked_files(root, result))

    for rel_path in sorted(paths_to_check):
        if exempt_from_sensitive_filename_check(rel_path):
            continue
        pattern = matching_sensitive_path_pattern(rel_path)
        if not pattern:
            continue
        tracked = git_tracked(root, rel_path) if git_available(root) else False
        staged = rel_path in staged_set
        if staged:
            add_failure(
                result,
                "filename",
                rel_path,
                "sensitive real/private/commercial filename is staged",
                "Unstage the file and keep real/private/commercial files ignored or outside the repository.",
                f"pattern={pattern}",
            )
        elif tracked:
            add_failure(
                result,
                "filename",
                rel_path,
                "sensitive real/private/commercial filename is tracked",
                "Remove the sensitive file from Git tracking after confirming it is not needed in the repository.",
                f"pattern={pattern}",
            )


def check_gitignore(root: Path, result: Result) -> None:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        result.fail(".gitignore is missing")
        return
    text = gitignore.read_text(encoding="utf-8")
    lines = {line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")}
    for pattern in REQUIRED_GITIGNORE_PATTERNS:
        if pattern not in lines:
            add_failure(
                result,
                "policy",
                ".gitignore",
                "required privacy ignore pattern is missing",
                "Add the missing ignore rule in an approved .gitignore update step.",
                f"pattern={pattern}",
            )

    for rel_path in PROTECTED_EXAMPLE_PATHS:
        if not git_check_ignore(root, rel_path):
            add_failure(
                result,
                "policy",
                rel_path,
                "example private path is not protected by .gitignore",
                "Review .gitignore in an approved step before creating any private files.",
            )

    for rel_path in SAMPLE_NOT_IGNORED:
        if git_check_ignore(root, rel_path):
            add_failure(
                result,
                "policy",
                rel_path,
                "sample/source file is accidentally ignored",
                "Adjust .gitignore in an approved step so committed sample/source files remain trackable.",
            )


def check_known_ignored_generated_outputs(root: Path, result: Result) -> None:
    for rel_path in KNOWN_IGNORED_GENERATED_OUTPUTS:
        path = root / rel_path
        if path.exists() and git_check_ignore(root, rel_path):
            add_warning(
                result,
                "ignored-output",
                rel_path,
                "generated output exists locally and is ignored",
                "This is allowed for internal generated output, but do not force-add or commit it.",
            )


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
                        if domain != PLACEHOLDER_EMAIL_DOMAIN and not value_contains_safe_placeholder(value):
                            add_failure(
                                result,
                                "content",
                                f"{rel_path}:{row_number}",
                                "sample contact_email is not example.invalid or an approved placeholder",
                                "Replace sample contact emails with example.invalid or an approved placeholder value.",
                            )
                    elif column in {"contact_phone", "whatsapp"}:
                        if value != PLACEHOLDER_PHONE and not value_contains_safe_placeholder(value):
                            add_failure(
                                result,
                                "content",
                                f"{rel_path}:{row_number}",
                                f"sample {column} is not placeholder phone",
                                "Replace sample phone values with +00-0000-0000 or an approved placeholder value.",
                            )
                    elif column == "wechat_id":
                        if PLACEHOLDER_WECHAT_PREFIX not in value.lower() and not value_contains_safe_placeholder(value):
                            add_failure(
                                result,
                                "content",
                                f"{rel_path}:{row_number}",
                                "sample wechat_id is not placeholder-style",
                                "Use a placeholder-style WeChat value such as placeholder_* or WECHAT_EXAMPLE.",
                            )
                    elif column == "contact_name":
                        if not value.startswith(PLACEHOLDER_CONTACT_PREFIX) and not value_contains_safe_placeholder(value):
                            add_failure(
                                result,
                                "content",
                                f"{rel_path}:{row_number}",
                                "sample contact_name is not placeholder-style",
                                "Use a sample contact name or CONTACT_NAME_EXAMPLE placeholder.",
                            )
    except csv.Error as exc:
        result.warn(f"{rel_path}: CSV parse warning during contact check: {exc}")


def check_emails_in_text(text: str, rel_path: str, result: Result) -> None:
    for match in EMAIL_RE.finditer(text):
        domain = match.group(1).lower()
        if domain != PLACEHOLDER_EMAIL_DOMAIN:
            add_failure(
                result,
                "content",
                rel_path,
                "non-placeholder email detected",
                "Remove real email addresses or replace sample values with example.invalid.",
                f"value={match.group(0)}",
            )


def check_phone_like_in_text(text: str, rel_path: str, result: Result) -> None:
    if "contact_phone" not in text and "whatsapp" not in text:
        return
    for match in PHONE_RE.finditer(text):
        value = match.group(0)
        placeholder_international = re.fullmatch(r"\+\d{1,3}(?:-0+)+", value) is not None
        if value != PLACEHOLDER_PHONE and not placeholder_international and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            add_warning(
                result,
                "content",
                rel_path,
                "phone-like value needs review",
                "Confirm this is a placeholder or remove private contact data before commit.",
                f"value={value}",
            )


def marker_context_is_sample_safe(line: str) -> bool:
    return line_contains_sample_or_internal_review_context(line)


def check_sensitive_content_markers(text: str, rel_path: str, result: Result) -> None:
    if docs_path(rel_path) or code_path(rel_path):
        return
    if not strict_content_path(rel_path):
        return
    if sample_safe_strict_path(rel_path):
        return

    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if marker_context_is_sample_safe(lowered):
            continue
        for category, markers in SENSITIVE_CONTENT_MARKERS.items():
            for marker in markers:
                if marker in lowered:
                    result.fail(
                        format_issue(
                            "FAIL",
                            "content",
                            f"{rel_path}:{line_number}",
                            "sensitive marker detected in strict data/output file",
                            "Move real/private content outside tracked files or mark sample/internal-review placeholders clearly.",
                            f"category={category}, marker={marker}",
                        )
                    )


def check_disclaimer(text: str, rel_path: str, result: Result) -> None:
    relevant = rel_path in DISCLAIMER_FILES or any(keyword in rel_path for keyword in DISCLAIMER_FILE_KEYWORDS)
    if not relevant:
        return
    lowered = text.lower()
    if not any(term.lower() in lowered for term in DISCLAIMER_TERMS):
        add_failure(
            result,
            "content",
            rel_path,
            "internal-review disclaimer is missing",
            "Add an internal-review-only disclaimer before using proposal or quotation sample outputs.",
        )


def line_has_safe_medicube_context(line: str) -> bool:
    return line_contains_safe_context(line)


def check_medicube_context(text: str, rel_path: str, result: Result) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not any(term in line for term in MEDICUBE_TERMS):
            continue
        lowered = line.lower()
        risky = any(term.lower() in lowered for term in RISKY_MEDICUBE_TERMS)
        recommended_value = "recommended_brands" in lowered and not any(term in lowered for term in ["excluded", "blank", "must not", "not in"])
        if (risky or recommended_value) and not line_has_safe_medicube_context(line):
            add_failure(
                result,
                "content",
                f"{rel_path}:{line_number}",
                "approval-required brand appears in risky external-ready context",
                "Keep approval-required brands blocked/excluded unless explicit approval is recorded.",
            )


def check_python_forbidden_code(path: Path, rel_path: str, text: str, result: Result) -> None:
    if not rel_path.endswith(".py"):
        return
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        add_warning(
            result,
            "external-automation",
            rel_path,
            "Python parse warning",
            "Review the file manually; Privacy Guard could not complete AST checks.",
            str(exc),
        )
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name in FORBIDDEN_IMPORT_MODULES or name in FORBIDDEN_IMPORT_PREFIXES:
                    add_failure(
                        result,
                        "external-automation",
                        rel_path,
                        "forbidden import detected",
                        "Remove external collection/sending implementation from this repository scope.",
                        f"import={name}",
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in FORBIDDEN_IMPORT_MODULES or module in FORBIDDEN_IMPORT_PREFIXES:
                add_failure(
                    result,
                    "external-automation",
                    rel_path,
                    "forbidden import detected",
                    "Remove external collection/sending implementation from this repository scope.",
                    f"import={module}",
                )

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#") or "does not" in stripped.lower() or "do not" in stripped.lower():
            continue
        for pattern in FORBIDDEN_CODE_PATTERNS:
            if pattern.search(line):
                add_failure(
                    result,
                    "external-automation",
                    f"{rel_path}:{line_number}",
                    "forbidden operational code pattern detected",
                    "Remove scraping/API/browser/email/messaging/sending implementation from this task scope.",
                )


def synthetic_content_fails(rel_path: str, text: str) -> bool:
    result = Result()
    check_sensitive_content_markers(text, rel_path, result)
    return bool(result.failures)


def run_self_test() -> int:
    checks = 0
    failures: list[str] = []

    def expect(name: str, condition: bool) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    restricted_paths = [
        "data/private/buyer_contacts_real.csv",
        "data/private/templates/price_real_template.csv",
        "output/private/operations_dashboard_real.md",
        "output/final/final_quotation.pdf",
        "local_config/private_settings.json",
    ]
    for rel_path in restricted_paths:
        expect(f"restricted path blocked: {rel_path}", is_restricted_path(rel_path))

    expect(
        "documentation mention is not path-blocked",
        not is_restricted_path("docs/privacy_guard_enhancement_spec.md"),
    )

    sensitive_filename_paths = [
        "data/buyer_contacts_real.csv",
        "data/buyer_prices_private.csv",
        "data/stock_real.csv",
        "data/expiry_real.xlsx",
        "output/final_quotation.md",
        "output/external_ready_proposal.md",
        "output/send_ready_quote.md",
    ]
    for rel_path in sensitive_filename_paths:
        expect(f"sensitive filename classified: {rel_path}", is_sensitive_path(rel_path))

    safe_filename_paths = [
        "docs/real_data_migration_privacy_guard_spec.md",
        "docs/sample_to_real_mapping.md",
        "README.md",
        "AGENTS.md",
        "tests/validate_privacy_guard.py",
        "data/buyers_master_sample.csv",
        "data/buyers_scored_sample.csv",
        "data/proposal_messages_sample.csv",
        "data/quotation_sample.csv",
        "data/brands_master.csv",
        "data/buyers_raw.csv",
    ]
    for rel_path in safe_filename_paths:
        allowed = exempt_from_sensitive_filename_check(rel_path) or not is_sensitive_path(rel_path)
        expect(f"safe filename allowed: {rel_path}", allowed)

    strict_content_fail_cases = [
        ("data/buyers_live.csv", "buyer_id,contact_email\nB001,buyer@example.invalid"),
        ("data/pricing_live.csv", "sku,negotiated_price\nSKU001,1000"),
        ("output/proposal.md", "status: external_ready"),
        ("output/quotation.md", "status: final_quotation"),
        ("output/stock_report.md", "status: confirmed_stock"),
        ("output/margin_report.csv", "brand,internal_margin\nA,10"),
    ]
    for rel_path, text in strict_content_fail_cases:
        expect(f"strict content marker fails: {rel_path}", synthetic_content_fails(rel_path, text))

    safe_content_pass_cases = [
        ("data/buyers_master_sample.csv", "buyer_id,contact_name\nBUYER_EXAMPLE_001,SAMPLE_CONTACT"),
        ("data/buyers_raw.csv", "buyer_id,wechat_id\nBUYER_EXAMPLE_001,WECHAT_EXAMPLE"),
        ("docs/manual_approval_gate.md", "Final quotation must not be automatically sent."),
        ("tests/validate_privacy_guard.py", '"requests", "httpx", "external_ready"'),
    ]
    for rel_path, text in safe_content_pass_cases:
        expect(f"safe content passes: {rel_path}", not synthetic_content_fails(rel_path, text))

    status = "SELF-TEST PASS" if not failures else "SELF-TEST FAIL"
    print(status)
    print(f"synthetic_checks={checks}")
    print(f"failures={len(failures)}")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


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
    check_sensitive_content_markers(text, rel_path, result)
    check_emails_in_text(text, rel_path, result)
    check_phone_like_in_text(text, rel_path, result)
    check_disclaimer(text, rel_path, result)
    check_medicube_context(text, rel_path, result)
    check_python_forbidden_code(path, rel_path, text, result)


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    mode = "staged-only" if args.staged_only else args.mode
    if mode == "working-tree":
        mode = "all"
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
    if has_git:
        check_restricted_paths(root, result, mode, staged)
        check_sensitive_filenames(root, result, mode, staged)
        if mode != "staged-only":
            check_known_ignored_generated_outputs(root, result)

    for rel_path in rel_paths:
        scan_file(root, rel_path, result)

    status = "PASS" if not result.failures else "FAIL"
    print(f"{status}: privacy guard validation {'passed' if status == 'PASS' else 'failed'}")
    print(f"mode={mode}")
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
