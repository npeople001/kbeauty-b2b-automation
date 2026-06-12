"""Synthetic approval gate validator skeleton.

Task 015 Step C creates only a self-test capable skeleton. It does not read
real/private files, create folders, approve external use, create final
quotations, send messages, scrape, call APIs, enrich buyers, or check credit.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ALLOWED_APPROVAL_STATUSES = {
    "not_required",
    "required",
    "pending",
    "approved",
    "rejected",
    "expired",
    "exception_approved",
    "review_needed",
}

APPROVED_STATUSES = {"approved", "exception_approved"}

MEDICUBE_TERMS = {"medicube", "메디큐브", "硫붾뵒?먮툕"}

MEDICUBE_TERMS.add("메디큐브")

FINAL_MARKERS = {
    "final_quotation",
    "final quote",
    "final_quote",
    "approved_quotation",
    "commercially_approved",
}

EXTERNAL_READY_MARKERS = {
    "external_ready",
    "send_ready",
    "ready_to_send",
    "approved_to_send",
}

DOC_CONTEXTS = {"docs", "policy", "documentation"}
PROPOSAL_CONTEXTS = {"proposal"}
QUOTATION_CONTEXTS = {"quotation"}
DASHBOARD_CONTEXTS = {"dashboard", "report"}

ALLOWED_SAMPLE_FILES = {
    "data/brands_master.csv": "brand",
    "data/buyers_master_sample.csv": "buyer",
    "data/buyers_scored_sample.csv": "score",
    "data/proposal_messages_sample.csv": "proposal",
    "data/quotation_sample.csv": "quotation",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    source: str
    message: str
    suggested_fix: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate synthetic approval gate rules."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run synthetic approval gate self-tests only.",
    )
    return parser.parse_args()


def normalized(value: Any) -> str:
    return str(value or "").strip()


def normalized_lower(value: Any) -> str:
    return normalized(value).lower()


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return normalized_lower(value) == "true"


def is_medicube_brand(value: str) -> bool:
    text = normalized_lower(value)
    return any(term.lower() in text for term in MEDICUBE_TERMS)


def is_blocked_or_excluded_context(record: dict[str, Any]) -> bool:
    text = normalized_lower(record.get("output_text"))
    return any(
        term in text
        for term in [
            "blocked",
            "excluded",
            "approval_review_required",
            "blocked_approval_required",
            "approval-required",
            "approval required",
            "not external",
            "not buyer-facing",
            "internal approval",
            "internal review",
            "internal-review",
            "내부",
            "승인",
            "제외",
            "차단",
        ]
    )


def medicube_context(record: dict[str, Any]) -> str:
    context = normalized_lower(record.get("context"))
    if is_doc_context(context):
        return "policy"
    if context == "brand":
        return "brand_reference"
    if context == "buyer":
        return "buyer_interest"
    if context == "score":
        return "scoring"
    if is_proposal_context(context):
        return "proposal"
    if is_quotation_context(context):
        return "quotation"
    if is_dashboard_context(context):
        return "dashboard"
    if as_bool(record.get("internal_review_only")):
        return "internal_review"
    return context or "unknown"


def evaluate_medicube_record(record: dict[str, Any]) -> list[Finding]:
    brand_text = " ".join(
        [
            normalized(record.get("brand_name")),
            normalized(record.get("output_text")),
        ]
    )
    if not is_medicube_brand(brand_text):
        return []

    context = normalized_lower(record.get("context"))
    med_context = medicube_context(record)
    proposal_allowed = normalized_lower(record.get("proposal_allowed")) == "true"
    proposal_disallowed = normalized_lower(record.get("proposal_allowed")) == "false"
    approval_block = as_bool(record.get("approval_block"))
    approved = is_approved(record)
    blocked_or_excluded = is_blocked_or_excluded_context(record) or proposal_disallowed

    if is_doc_context(context) or med_context in {"brand_reference", "buyer_interest", "scoring", "dashboard"}:
        return [
            finding(
                "INFO",
                "medicube",
                f"Medicube appears in {med_context} context",
                "Allow policy/reference/internal-review mention; do not use externally without approval.",
            )
        ]

    if is_proposal_context(context) or is_quotation_context(context):
        if approval_block and proposal_allowed:
            return [
                finding(
                    "FAIL",
                    f"medicube/{context}",
                    "Medicube approval_block=true with proposal_allowed=true",
                    "approval_block overrides score_total, priority_tier, buyer interest, and proposal_allowed unless explicit approved exception exists.",
                )
            ]

        if approval_block and blocked_or_excluded:
            return [
                finding(
                    "WARNING",
                    f"medicube/{context}",
                    "Medicube appears in blocked/excluded/internal-review context",
                    "Keep blocked internally. approval_block overrides score_total, priority_tier, buyer interest, and proposal_allowed unless explicit approved exception exists.",
                )
            ]

        if approved and not approval_block:
            return [
                finding(
                    "INFO",
                    f"medicube/{context}",
                    "Medicube has approved or exception_approved status in synthetic context",
                    "Continue internal review; INFO is not external sending approval.",
                )
            ]

        if not approved:
            if blocked_or_excluded:
                return [
                    finding(
                        "WARNING",
                        f"medicube/{context}",
                        "Medicube appears without approval but is clearly blocked/excluded/internal-review only",
                        "Keep blocked internally until approval_status=approved or exception_approved.",
                    )
                ]
            return [
                finding(
                    "FAIL",
                    f"medicube/{context}",
                    "Medicube proposal/quotation context requires approval_status=approved or exception_approved",
                    "Keep blocked internally or add a valid private approval record in a future approved workflow. approval_block overrides score_total and priority_tier.",
                )
            ]

    return [
        finding(
            "WARNING",
            "medicube",
            f"Medicube appears in {med_context} context",
            "Review manually before any external use.",
        )
    ]


def is_doc_context(context: str) -> bool:
    return normalized_lower(context) in DOC_CONTEXTS


def is_proposal_context(context: str) -> bool:
    return normalized_lower(context) in PROPOSAL_CONTEXTS


def is_quotation_context(context: str) -> bool:
    return normalized_lower(context) in QUOTATION_CONTEXTS


def is_dashboard_context(context: str) -> bool:
    return normalized_lower(context) in DASHBOARD_CONTEXTS


def is_ready_context(record: dict[str, Any]) -> bool:
    text = normalized_lower(record.get("output_text"))
    return (
        as_bool(record.get("proposal_ready"))
        or as_bool(record.get("quotation_ready"))
        or any(
            term in text
            for term in [
                "proposal_ready",
                "quotation_ready",
                "ready for proposal",
                "ready for quotation",
                "ready_to_propose",
                "ready_to_quote",
                "commercially_approved",
            ]
        )
    )


def has_marker(text: str, markers: set[str]) -> bool:
    lowered = normalized_lower(text)
    return any(marker in lowered for marker in markers)


def finding(severity: str, source: str, message: str, suggested_fix: str) -> Finding:
    return Finding(
        severity=severity,
        source=source,
        message=message,
        suggested_fix=suggested_fix,
    )


def approval_status(record: dict[str, Any]) -> str:
    return normalized_lower(record.get("approval_status"))


def is_approved(record: dict[str, Any]) -> bool:
    return approval_status(record) in APPROVED_STATUSES


def approval_expired(record: dict[str, Any]) -> bool:
    expiry = normalized(record.get("approval_expiry"))
    if not expiry:
        return False
    try:
        return date.fromisoformat(expiry) < date.today()
    except ValueError:
        return False


def evaluate_approval_record(record: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    context = normalized_lower(record.get("context"))
    status = approval_status(record)
    output_text = normalized(record.get("output_text"))
    brand_name = normalized(record.get("brand_name"))
    related_output_file = normalized_lower(record.get("related_output_file"))
    ready_context = is_ready_context(record)
    internal_review_only = as_bool(record.get("internal_review_only"))

    if status and status not in ALLOWED_APPROVAL_STATUSES:
        findings.append(
            finding(
                "WARNING",
                "approval",
                f"unknown approval_status: {status}",
                "Use an allowed approval_status value.",
            )
        )

    if as_bool(record.get("approval_block")) and not is_approved(record):
        if as_bool(record.get("internal_review_only")) and normalized_lower(record.get("proposal_allowed")) == "false":
            findings.append(
                finding(
                    "WARNING",
                    "approval",
                    "approval_block=true in internal-review proposal-disallowed context",
                    "Keep visible as a blocker and do not use externally.",
                )
            )
        else:
            findings.append(
                finding(
                    "FAIL",
                    "approval",
                    "approval_block=true without approved or exception_approved status",
                    "Keep blocked until explicit approval or exception approval is recorded.",
                )
            )

    if as_bool(record.get("approval_required")) and not status:
        if ready_context:
            findings.append(
                finding(
                    "FAIL",
                    "approval",
                    "approval_required=true but approval_status is missing in ready proposal/quotation context",
                    "Keep as internal-review only until approval_status is approved or exception_approved.",
                )
            )
        elif internal_review_only:
            findings.append(
                finding(
                    "WARNING",
                    "approval",
                    "approval_required=true without approval_status in internal-review context",
                    "Keep internal only until explicit approval status exists.",
                )
            )
        else:
            findings.append(
                finding(
                    "FAIL",
                    "approval",
                    "approval_required=true but approval_status is missing",
                    "Add explicit approval_status before continuing.",
                )
            )

    if as_bool(record.get("approval_required")) and status in {
        "pending",
        "rejected",
        "expired",
        "review_needed",
        "required",
    }:
        if ready_context:
            findings.append(
                finding(
                    "FAIL",
                    "approval",
                    f"approval_required=true with blocking status in ready context: {status}",
                    "Do not continue proposal/quotation use until approval is approved or exception_approved.",
                )
            )
        elif not internal_review_only:
            findings.append(
                finding(
                    "FAIL",
                    "approval",
                    f"approval_required=true with blocking status: {status}",
                    "Resolve approval before external-use workflow.",
                )
            )
        else:
            findings.append(
                finding(
                    "WARNING",
                    "approval",
                    "approval_required=true in internal-review context",
                    "Keep internal only until explicit approval is recorded.",
                )
            )

    if is_proposal_context(context) and normalized_lower(record.get("proposal_allowed")) == "false":
        if ready_context and not internal_review_only:
            findings.append(
                finding(
                    "FAIL",
                    "proposal",
                    "proposal_allowed=false but proposal context is marked ready/allowed",
                    "Keep proposal blocked until proposal_allowed is true with valid approval.",
                )
            )
        else:
            findings.append(
                finding(
                    "WARNING",
                    "proposal",
                    "proposal_allowed=false appears as intended proposal blocker",
                    "Keep as internal-review blocker unless explicit approval changes it.",
                )
            )

    if is_quotation_context(context) and normalized_lower(record.get("proposal_allowed")) == "false":
        findings.append(
            finding(
                "WARNING",
                "quotation",
                "proposal_allowed=false appears as intended quotation blocker",
                "Keep quotation blocked unless explicit approval changes it.",
            )
        )

    findings.extend(evaluate_medicube_record(record))

    if not is_doc_context(context):
        if has_marker(output_text, FINAL_MARKERS) and not (
            as_bool(record.get("final_process_enabled"))
            and as_bool(record.get("final_approval"))
        ):
            source = "quotation/final-quotation" if is_quotation_context(context) else "final-quotation"
            findings.append(
                finding(
                    "FAIL",
                    source,
                    "final quotation marker appears before final process approval",
                    "Remove final quotation wording or complete a future approved final process.",
                )
            )

        if has_marker(output_text, EXTERNAL_READY_MARKERS) and not as_bool(
            record.get("external_approval")
        ):
            findings.append(
                finding(
                    "FAIL",
                    "external-use",
                    "external-ready/send-ready marker appears before approval",
                    "Keep output internal-review only until external approval exists.",
                )
            )

    if is_approved(record):
        if not normalized(record.get("approval_owner")):
            findings.append(
                finding(
                    "FAIL",
                    "approval",
                    "approved record missing approval_owner",
                    "Record approval owner for approved or exception-approved decisions.",
                )
            )
        if not normalized(record.get("approval_date")):
            findings.append(
                finding(
                    "FAIL",
                    "approval",
                    "approved record missing approval_date",
                    "Record approval date for approved or exception-approved decisions.",
                )
            )

    if approval_expired(record):
        findings.append(
            finding(
                "FAIL",
                "approval",
                "approval_expiry is in the past",
                "Reconfirm approval before continuing.",
            )
        )

    if related_output_file.startswith("output/final/"):
        findings.append(
            finding(
                "FAIL",
                "quotation",
                "related_output_file references output/final before final process exists",
                "Keep final outputs out of current workflow scope.",
            )
        )

    if status == "not_required" and normalized_lower(record.get("brand_category")) in {
        "sensitive",
        "high-risk",
        "high_risk",
    }:
        findings.append(
            finding(
                "WARNING",
                "brand",
                "not_required approval status on sensitive/high-risk brand category",
                "Review whether manual approval is still needed.",
            )
        )

    if normalized(record.get("approval_notes")) and not normalized(
        record.get("approval_expiry")
    ):
        findings.append(
            finding(
                "WARNING",
                "approval",
                "approval notes present without approval_expiry",
                "Consider adding approval expiry or review schedule.",
            )
        )

    if is_dashboard_context(context) and as_bool(record.get("mentions_approval_blockers")):
        findings.append(
            finding(
                "WARNING",
                "dashboard",
                "dashboard/report mentions approval blockers",
                "Keep warning visible and do not treat dashboard PASS as approval.",
            )
        )

    if is_quotation_context(context) and as_bool(record.get("commercial_terms_placeholder")):
        findings.append(
            finding(
                "WARNING",
                "quotation",
                "quotation uses placeholder or sample-safe commercial terms",
                "Verify price, stock, expiry, MOQ, payment, shipping, tax, duties, and incoterms before external use.",
            )
        )

    if normalized_lower(record.get("approval_owner")).startswith("approver_example"):
        findings.append(
            finding(
                "WARNING",
                "approval",
                "approval_owner uses placeholder value",
                "Replace placeholder before real approval use.",
            )
        )

    if as_bool(record.get("manual_review_recommended")):
        findings.append(
            finding(
                "WARNING",
                "approval",
                "manual review is recommended",
                "Complete human approval review before external use.",
            )
        )

    if not findings:
        findings.append(
            finding(
                "INFO",
                "approval",
                "no approval gate blockers detected in synthetic record",
                "Continue internal review only; INFO is not external approval.",
            )
        )

    return findings


def has_severity(findings: list[Finding], severity: str) -> bool:
    return any(item.severity == severity for item in findings)


def csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [
            {normalized_lower(key): normalized(value) for key, value in row.items()}
            for row in reader
        ]
        columns = [normalized_lower(column) for column in (reader.fieldnames or [])]
    return rows, columns


def first_value(row: dict[str, str], names: list[str]) -> str:
    for name in names:
        value = normalized(row.get(name))
        if value:
            return value
    return ""


def row_text(row: dict[str, str]) -> str:
    return " ".join(normalized(value) for value in row.values())


def row_has_approval_placeholder(row: dict[str, str]) -> bool:
    text = row_text(row).lower()
    return any(
        term in text
        for term in [
            "approval_required",
            "approval_required_review",
            "approval_required_brand",
            "approval_warning",
            "approval_required_brand_detected",
        ]
    )


def sample_safe_blocking_context(row: dict[str, str]) -> bool:
    text = row_text(row).lower()
    return any(
        term in text
        for term in [
            "blocked",
            "excluded",
            "approval_required_review",
            "approval_required_brand",
            "not external",
            "not external quotation-ready",
            "internal review",
            "internal-review",
            "내부",
            "외부 발송 전",
            "승인",
        ]
    )


def evaluate_sample_row(path: str, context: str, row: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    brand_name = first_value(row, ["brand_name", "brand_ko", "brand_en"])
    approval_required = as_bool(first_value(row, ["approval_required"]))
    approval_block = as_bool(first_value(row, ["approval_block"]))
    proposal_allowed_text = normalized_lower(first_value(row, ["proposal_allowed"]))
    proposal_allowed = proposal_allowed_text == "true"
    proposal_disallowed = proposal_allowed_text == "false"
    status = normalized_lower(first_value(row, ["approval_status"]))
    record = {
        "context": context,
        "brand_name": brand_name,
        "approval_block": first_value(row, ["approval_block"]),
        "approval_required": first_value(row, ["approval_required"]),
        "proposal_allowed": first_value(row, ["proposal_allowed"]),
        "approval_status": status,
        "output_text": row_text(row),
        "internal_review_only": sample_safe_blocking_context(row),
    }

    if approval_block and proposal_allowed:
        findings.append(
            finding(
                "FAIL",
                context,
                f"{path}: approval_block=true with proposal_allowed=true",
                "Keep blocked brands proposal-disallowed until approval is explicit.",
            )
        )

    if approval_required and proposal_allowed and not approval_block and not status:
        findings.append(
            finding(
                "WARNING",
                context,
                f"{path}: approval_required=true with proposal_allowed=true but no approval_status",
                "Future private approval records are required before external use.",
            )
        )

    if approval_required and not status:
        findings.append(
            finding(
                "WARNING",
                context,
                f"{path}: approval_required=true without approval_status in sample/reference row",
                "Keep as internal/reference only until approval status exists.",
            )
        )

    if approval_required and proposal_disallowed:
        findings.append(
            finding(
                "WARNING",
                context,
                f"{path}: approval_required=true with proposal_allowed=false",
                "Expected blocker; keep external proposal disabled until approved.",
            )
        )

    if approval_block and proposal_disallowed:
        findings.append(
            finding(
                "WARNING",
                context,
                f"{path}: approval_block=true with proposal_allowed=false",
                "Expected blocker; keep visible for internal review.",
            )
        )

    if row_has_approval_placeholder(row):
        findings.append(
            finding(
                "WARNING",
                context,
                f"{path}: approval placeholder or approval-review marker found",
                "Confirm this remains sample/internal-review only.",
            )
        )

    if context in {"proposal", "quotation"}:
        if approval_block and proposal_allowed:
            findings.append(
                finding(
                    "FAIL",
                    context,
                    f"{path}: {context} row is blocked but proposal_allowed=true",
                    "Do not continue proposal/quotation use until approval data is corrected.",
                )
            )
        elif approval_block and sample_safe_blocking_context(row):
            findings.append(
                finding(
                    "WARNING",
                    context,
                    f"{path}: approval_block=true appears in blocking/internal-review context",
                    "Allowed for current sample, but external use remains blocked.",
                )
            )

        for med_finding in evaluate_medicube_record(record):
            if med_finding.severity == "INFO":
                continue
            findings.append(
                finding(
                    med_finding.severity,
                    med_finding.source,
                    f"{path}: {med_finding.message}",
                    med_finding.suggested_fix,
                )
            )

    if not findings:
        findings.append(
            finding(
                "INFO",
                context,
                f"{path}: sample-safe approval row has no Step D blockers",
                "Continue internal review only; INFO is not external approval.",
            )
        )

    return findings


def validate_sample_files(root: Path) -> tuple[int, list[Finding]]:
    files_scanned = 0
    findings: list[Finding] = []

    for rel_path, context in ALLOWED_SAMPLE_FILES.items():
        path = root / rel_path
        if not path.exists():
            findings.append(
                finding(
                    "WARNING",
                    "file",
                    f"{rel_path}: optional sample/internal-review file missing",
                    "Create or regenerate sample file only in an approved task if needed.",
                )
            )
            continue

        try:
            rows, columns = csv_rows(path)
        except csv.Error as exc:
            findings.append(
                finding(
                    "FAIL",
                    "file",
                    f"{rel_path}: malformed CSV prevents approval validation: {exc}",
                    "Fix CSV structure before approval validation.",
                )
            )
            continue
        except OSError as exc:
            findings.append(
                finding(
                    "FAIL",
                    "file",
                    f"{rel_path}: cannot read file: {exc}",
                    "Confirm file exists and is readable.",
                )
            )
            continue

        files_scanned += 1
        if not columns:
            findings.append(
                finding(
                    "FAIL",
                    "file",
                    f"{rel_path}: CSV has no header columns",
                    "Add expected sample/internal-review columns.",
                )
            )
            continue

        for row in rows:
            findings.extend(evaluate_sample_row(rel_path, context, row))

    return files_scanned, findings


def run_self_test() -> int:
    checks: list[tuple[str, dict[str, Any], str]] = [
        (
            "approval_block without approval fails",
            {"approval_block": True, "approval_status": "pending"},
            "FAIL",
        ),
        (
            "approval required missing status fails",
            {"approval_required": True},
            "FAIL",
        ),
        (
            "proposal_allowed false in proposal fails",
            {"context": "proposal", "proposal_allowed": "false", "proposal_ready": True},
            "FAIL",
        ),
        (
            "Medicube proposal without approval fails",
            {"brand_name": "Medicube", "context": "proposal", "approval_status": "pending"},
            "FAIL",
        ),
        (
            "Korean Medicube quotation without approval fails",
            {"brand_name": "硫붾뵒?먮툕", "context": "quotation", "approval_status": "rejected"},
            "FAIL",
        ),
        (
            "final quotation marker fails",
            {"context": "quotation", "output_text": "final_quotation draft"},
            "FAIL",
        ),
        (
            "external-ready marker fails",
            {
                "context": "proposal",
                "output_text": "external_ready proposal",
                "external_approval": False,
            },
            "FAIL",
        ),
        (
            "approved missing owner/date fails",
            {"approval_status": "approved"},
            "FAIL",
        ),
        (
            "expired approval fails",
            {
                "approval_status": "approved",
                "approval_owner": "APPROVER_EXAMPLE",
                "approval_date": "2026-01-01",
                "approval_expiry": "2000-01-01",
            },
            "FAIL",
        ),
        (
            "output final reference fails",
            {"related_output_file": "output/final/final_quotation.pdf"},
            "FAIL",
        ),
        (
            "approval required internal review warns",
            {
                "approval_required": True,
                "approval_status": "pending",
                "internal_review_only": True,
            },
            "WARNING",
        ),
        (
            "not required sensitive category warns",
            {"approval_status": "not_required", "brand_category": "sensitive"},
            "WARNING",
        ),
        (
            "notes without expiry warns",
            {"approval_notes": "SAMPLE_APPROVAL_NOTE"},
            "WARNING",
        ),
        (
            "dashboard blockers warn",
            {"context": "dashboard", "mentions_approval_blockers": True},
            "WARNING",
        ),
        (
            "placeholder owner warns",
            {"approval_owner": "APPROVER_EXAMPLE"},
            "WARNING",
        ),
        (
            "manual review recommended warns",
            {"manual_review_recommended": True},
            "WARNING",
        ),
        (
            "docs policy approval gate passes",
            {
                "context": "docs",
                "output_text": "approval gate policy mentions final_quotation and external_ready",
            },
            "INFO",
        ),
        (
            "sample placeholder approval fields pass",
            {
                "context": "sample",
                "brand_name": "BRAND_EXAMPLE",
                "buyer_id": "BUYER_EXAMPLE_001",
                "related_output_file": "output/example_internal_review.md",
            },
            "INFO",
        ),
        (
            "not required sample-safe passes",
            {
                "context": "sample",
                "approval_required": False,
                "proposal_allowed": True,
                "approval_status": "not_required",
            },
            "INFO",
        ),
        (
            "approval block false internal review passes",
            {"context": "internal_review", "approval_block": False},
            "INFO",
        ),
        (
            "Medicube docs policy passes",
            {
                "context": "docs",
                "brand_name": "Medicube",
                "output_text": "Medicube policy: approval-required and blocked unless approved",
            },
            "INFO",
        ),
        (
            "score and tier internal review pass",
            {
                "context": "internal_review",
                "score_total": 100,
                "priority_tier": "A",
                "approval_block": False,
            },
            "INFO",
        ),
        (
            "approval block with proposal allowed fails",
            {"approval_block": True, "proposal_allowed": True},
            "FAIL",
        ),
        (
            "approval required missing status reference warns",
            {
                "context": "brand",
                "approval_required": True,
                "internal_review_only": True,
            },
            "WARNING",
        ),
        (
            "approval block and proposal disallowed warns",
            {
                "context": "brand",
                "approval_block": True,
                "proposal_allowed": "false",
                "internal_review_only": True,
            },
            "WARNING",
        ),
        (
            "approval not required and proposal allowed passes",
            {"approval_required": False, "proposal_allowed": True},
            "INFO",
        ),
        (
            "Medicube proposal missing approval with proposal allowed fails",
            {
                "context": "proposal",
                "brand_name": "Medicube",
                "proposal_allowed": True,
            },
            "FAIL",
        ),
        (
            "Medicube quotation pending approval with proposal allowed fails",
            {
                "context": "quotation",
                "brand_name": "Medicube",
                "approval_status": "pending",
                "proposal_allowed": True,
            },
            "FAIL",
        ),
        (
            "Korean Medicube proposal rejected approval with proposal allowed fails",
            {
                "context": "proposal",
                "brand_name": "메디큐브",
                "approval_status": "rejected",
                "proposal_allowed": True,
            },
            "FAIL",
        ),
        (
            "Medicube proposal approval block with proposal allowed fails",
            {
                "context": "proposal",
                "brand_name": "Medicube",
                "approval_block": True,
                "proposal_allowed": True,
                "score_total": 100,
                "priority_tier": "A",
            },
            "FAIL",
        ),
        (
            "Medicube quotation approval block with proposal allowed fails",
            {
                "context": "quotation",
                "brand_name": "Medicube",
                "approval_block": True,
                "proposal_allowed": True,
            },
            "FAIL",
        ),
        (
            "Medicube proposal blocked and proposal disallowed warns",
            {
                "context": "proposal",
                "brand_name": "Medicube",
                "approval_block": True,
                "proposal_allowed": "false",
                "output_text": "internal review blocked approval-required",
            },
            "WARNING",
        ),
        (
            "Medicube quotation internal review blocked warns",
            {
                "context": "quotation",
                "brand_name": "Medicube",
                "approval_block": True,
                "output_text": "internal review blocked not external quotation-ready",
            },
            "WARNING",
        ),
        (
            "Medicube brand reference approval required warns",
            {
                "context": "brand",
                "brand_name": "Medicube",
                "approval_required": True,
                "internal_review_only": True,
            },
            "WARNING",
        ),
        (
            "Medicube approved proposal passes",
            {
                "context": "proposal",
                "brand_name": "Medicube",
                "approval_status": "approved",
                "approval_owner": "APPROVER_EXAMPLE",
                "approval_date": "2026-06-12",
                "approval_block": False,
            },
            "INFO",
        ),
        (
            "Medicube exception approved quotation passes",
            {
                "context": "quotation",
                "brand_name": "Medicube",
                "approval_status": "exception_approved",
                "approval_owner": "APPROVER_EXAMPLE",
                "approval_date": "2026-06-12",
                "approval_block": False,
            },
            "INFO",
        ),
        (
            "proposal required pending and ready fails",
            {
                "context": "proposal",
                "approval_required": True,
                "approval_status": "pending",
                "proposal_ready": True,
            },
            "FAIL",
        ),
        (
            "proposal send ready without external approval fails",
            {"context": "proposal", "output_text": "send_ready draft"},
            "FAIL",
        ),
        (
            "proposal external ready without external approval fails",
            {"context": "proposal", "output_text": "external_ready draft"},
            "FAIL",
        ),
        (
            "proposal final quotation marker fails",
            {"context": "proposal", "output_text": "final_quotation marker"},
            "FAIL",
        ),
        (
            "quotation required missing status and ready fails",
            {
                "context": "quotation",
                "approval_required": True,
                "quotation_ready": True,
            },
            "FAIL",
        ),
        (
            "quotation final quotation without final process fails",
            {"context": "quotation", "output_text": "final_quotation marker"},
            "FAIL",
        ),
        (
            "quotation approved quotation without final approval fails",
            {"context": "quotation", "output_text": "approved_quotation marker"},
            "FAIL",
        ),
        (
            "quotation commercially approved internal review fails",
            {"context": "quotation", "output_text": "commercially_approved internal review"},
            "FAIL",
        ),
        (
            "proposal required internal review warns",
            {
                "context": "proposal",
                "approval_required": True,
                "approval_status": "pending",
                "internal_review_only": True,
            },
            "WARNING",
        ),
        (
            "proposal allowed false intended blocker warns",
            {
                "context": "proposal",
                "proposal_allowed": "false",
                "internal_review_only": True,
            },
            "WARNING",
        ),
        (
            "quotation required internal review warns",
            {
                "context": "quotation",
                "approval_required": True,
                "approval_status": "pending",
                "internal_review_only": True,
            },
            "WARNING",
        ),
        (
            "quotation approval block and proposal disallowed warns",
            {
                "context": "quotation",
                "approval_block": True,
                "proposal_allowed": "false",
                "internal_review_only": True,
            },
            "WARNING",
        ),
        (
            "quotation placeholder commercial terms warn",
            {"context": "quotation", "commercial_terms_placeholder": True},
            "WARNING",
        ),
        (
            "proposal sample safe internal review passes",
            {
                "context": "proposal",
                "approval_required": False,
                "proposal_allowed": True,
                "approval_status": "not_required",
                "internal_review_only": True,
            },
            "INFO",
        ),
        (
            "quotation sample safe internal review passes",
            {
                "context": "quotation",
                "approval_required": False,
                "proposal_allowed": True,
                "approval_status": "not_required",
                "internal_review_only": True,
            },
            "INFO",
        ),
    ]

    failures: list[str] = []
    warning_count = 0

    for name, record, expected_severity in checks:
        findings = evaluate_approval_record(record)
        if not has_severity(findings, expected_severity):
            failures.append(
                f"{name}: expected {expected_severity}, got "
                f"{','.join(item.severity for item in findings)}"
            )
        if has_severity(findings, "WARNING"):
            warning_count += 1

    status = "PASS" if not failures else "FAIL"
    print(f"{status}: approval gate self-test {'passed' if status == 'PASS' else 'failed'}")
    print("mode=self-test")
    print(f"synthetic_checks={len(checks)}")
    print(f"warnings={0 if not failures else warning_count}")
    print(f"failures={len(failures)}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")

    return 0 if not failures else 1


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    root = Path(__file__).resolve().parents[1]
    files_scanned, findings = validate_sample_files(root)
    warnings = [item for item in findings if item.severity == "WARNING"]
    failures = [item for item in findings if item.severity == "FAIL"]
    status = "PASS" if not failures else "FAIL"

    print(f"{status}: approval gate validation {'passed' if status == 'PASS' else 'failed'}")
    print("mode=all")
    print(f"files_scanned={files_scanned}")
    print(f"warnings={len(warnings)}")
    print(f"failures={len(failures)}")

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(
                f"- WARNING [{warning.source}] {warning.message} "
                f"Suggested fix: {warning.suggested_fix}"
            )

    if failures:
        print("Failures:")
        for failure in failures:
            print(
                f"- FAIL [{failure.source}] {failure.message} "
                f"Suggested fix: {failure.suggested_fix}"
            )

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
