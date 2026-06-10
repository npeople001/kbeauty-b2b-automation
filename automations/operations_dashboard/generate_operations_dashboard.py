from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DEFAULT_RUNNER_SUMMARY = ROOT / "output" / "internal_workflow_summary.md"
DEFAULT_BUYERS = ROOT / "data" / "buyers_master_sample.csv"
DEFAULT_SCORES = ROOT / "data" / "buyers_scored_sample.csv"
DEFAULT_PROPOSALS = ROOT / "data" / "proposal_messages_sample.csv"
DEFAULT_QUOTATIONS = ROOT / "data" / "quotation_sample.csv"
DEFAULT_BRANDS = ROOT / "data" / "brands_master.csv"
DEFAULT_OUTPUT = ROOT / "output" / "operations_dashboard.md"

PRIVATE_PATH_MARKERS = (
    "data/private",
    "output/private",
    "output/final",
)

DASHBOARD_SECTIONS = [
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

REQUIRED_COLUMNS = {
    "buyers": ["buyer_id", "lead_status", "moq_fit", "approval_warning", "proposal_brand_check", "next_action"],
    "scores": ["buyer_id", "score_total", "priority_tier", "risk_flags", "approval_block", "recommended_next_action"],
    "proposals": ["buyer_id", "approval_block", "message_status", "excluded_brands", "required_internal_review", "next_action"],
    "quotations": [
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
    ],
    "brands": ["brand_ko", "approval_required", "proposal_allowed"],
}

CONTACT_OR_PRIVATE_FIELDS = {
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
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def clean(value: str | None) -> str:
    return (value or "").strip()


def lower(value: str | None) -> str:
    return clean(value).lower()


def normalized_path(path: Path) -> str:
    return str(path).replace("\\", "/").lower()


def reject_private_path(path: Path, label: str) -> None:
    normalized = normalized_path(path)
    for marker in PRIVATE_PATH_MARKERS:
        if marker in normalized:
            fail(f"{label} uses a protected path: {rel(path)}")


def is_true(value: str | None) -> bool:
    return lower(value) in {"true", "yes", "y", "1"}


def is_unknown(value: str | None) -> bool:
    return lower(value) in {"", "unknown", "n/a", "na", "none", "tbd", "pending"}


def contains_medicube(value: str | None) -> bool:
    text = clean(value).lower()
    return "메디큐브" in text or "medicube" in text or "硫붾뵒" in text


def read_csv_rows(path: Path, label: str, required_columns: list[str]) -> tuple[list[str], list[dict[str, str]]]:
    reject_private_path(path, label)
    if not path.exists():
        fail(f"{label} file is missing: {rel(path)}")

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            fieldnames = reader.fieldnames or []
            if not fieldnames:
                fail(f"{label} file has no header row: {rel(path)}")
            missing = [column for column in required_columns if column not in fieldnames]
            if missing:
                fail(f"{label} file is missing required columns: {', '.join(missing)}")
            rows = [{key: clean(value) for key, value in row.items()} for row in reader]
            return fieldnames, rows
    except UnicodeDecodeError as exc:
        fail(f"{label} file is not readable as utf-8-sig: {exc}")


def read_optional_text(path: Path, label: str, warnings: list[str]) -> str:
    reject_private_path(path, label)
    if not path.exists():
        warnings.append(f"{label} missing: {rel(path)}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        warnings.append(f"{label} is not readable as UTF-8: {exc}")
        return ""


def count_by(rows: list[dict[str, str]], column: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        value = clean(row.get(column)) or "UNKNOWN"
        counter[value] += 1
    return counter


def bool_counter(rows: list[dict[str, str]], column: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter["true" if is_true(row.get(column)) else "false"] += 1
    return counter


def any_row_text(row: dict[str, str]) -> str:
    safe_values = []
    for key, value in row.items():
        if key in CONTACT_OR_PRIVATE_FIELDS:
            continue
        safe_values.append(clean(value))
    return " | ".join(safe_values)


def parse_runner_summary(text: str) -> dict[str, str | int]:
    if not text:
        return {"result": "UNKNOWN", "stage_count": 0, "pass_count": 0, "warning_count": 0, "fail_count": 0}

    result = "UNKNOWN"
    pass_count = 0
    warning_count = 0
    fail_count = 0
    stage_count = 0

    for raw_line in text.splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if lowered.startswith("- result:"):
            result = clean(line.split(":", 1)[1]) or "UNKNOWN"
        if "|" in line:
            cells = [clean(cell) for cell in line.strip("|").split("|")]
            if cells and cells[0].isdigit():
                stage_count += 1
                joined = " ".join(cells).upper()
                if "PASS" in joined:
                    pass_count += 1
                if "WARNING" in joined:
                    warning_count += 1
                if "FAIL" in joined:
                    fail_count += 1

    return {
        "result": result,
        "stage_count": stage_count,
        "pass_count": pass_count,
        "warning_count": warning_count,
        "fail_count": fail_count,
    }


def text_contains_issue(text: str, *keywords: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def make_top_summary(counter: Counter[str], limit: int = 8) -> list[str]:
    if not counter:
        return ["- N/A"]
    return [f"- {value}: {count}" for value, count in counter.most_common(limit)]


def build_metrics(
    runner_text: str,
    buyers: list[dict[str, str]],
    scores: list[dict[str, str]],
    proposals: list[dict[str, str]],
    quotations: list[dict[str, str]],
    brands: list[dict[str, str]],
    warnings: list[str],
) -> dict[str, object]:
    runner = parse_runner_summary(runner_text)

    moq_issue_count = 0
    for row in buyers:
        if lower(row.get("moq_fit")) in {"no", "unknown", ""}:
            moq_issue_count += 1
    for row in quotations:
        if lower(row.get("moq_check")) not in {"pass", "ok", "yes"}:
            moq_issue_count += 1

    price_confirmation_needed_count = 0
    stock_confirmation_needed_count = 0
    expiry_confirmation_needed_count = 0
    for row in quotations:
        text = any_row_text(row)
        if is_unknown(row.get("unit_price")) or text_contains_issue(text, "price", "가격", "confirmation"):
            price_confirmation_needed_count += 1
        if is_unknown(row.get("stock_status")) or text_contains_issue(text, "stock", "inventory", "재고"):
            stock_confirmation_needed_count += 1
        if is_unknown(row.get("expiry_date")) or text_contains_issue(text, "expiry", "유통기한"):
            expiry_confirmation_needed_count += 1

    approval_issue_count = 0
    for row in buyers:
        if clean(row.get("approval_warning")) or lower(row.get("proposal_brand_check")) == "approval_required_review":
            approval_issue_count += 1
    approval_issue_count += sum(1 for row in scores if is_true(row.get("approval_block")))
    approval_issue_count += sum(1 for row in proposals if is_true(row.get("approval_block")))
    approval_issue_count += sum(1 for row in quotations if is_true(row.get("approval_block")))
    approval_issue_count += sum(
        1
        for row in brands
        if is_true(row.get("approval_required")) or lower(row.get("proposal_allowed")) == "false"
    )

    medicube_issue_count = 0
    for source_rows in (buyers, scores, proposals, quotations, brands):
        for row in source_rows:
            text = any_row_text(row)
            if contains_medicube(text):
                if (
                    "approval" in text.lower()
                    or "block" in text.lower()
                    or "review" in text.lower()
                    or "승인" in text
                    or "검토" in text
                ):
                    medicube_issue_count += 1

    internal_review_count = sum(1 for row in proposals if is_true(row.get("required_internal_review")))
    internal_review_count += sum(1 for row in quotations if is_true(row.get("required_internal_review")))
    internal_review_count += sum(1 for row in scores if is_true(row.get("approval_block")))
    internal_review_count += sum(1 for row in buyers if clean(row.get("approval_warning")))

    next_actions: Counter[str] = Counter()
    for row in buyers:
        if clean(row.get("next_action")):
            next_actions[clean(row.get("next_action"))] += 1
    for row in scores:
        if clean(row.get("recommended_next_action")):
            next_actions[clean(row.get("recommended_next_action"))] += 1
    for row in proposals:
        if clean(row.get("next_action")):
            next_actions[clean(row.get("next_action"))] += 1
    for row in quotations:
        if clean(row.get("next_action")):
            next_actions[clean(row.get("next_action"))] += 1

    key_risks: list[str] = []
    if warnings:
        key_risks.append("입력 또는 실행 요약 확인 필요")
    if str(runner.get("result", "UNKNOWN")).upper() not in {"PASS", "SUCCESS"}:
        key_risks.append("Integrated Runner 결과 재확인 필요")
    if approval_issue_count:
        key_risks.append("승인 필요 브랜드 이슈")
    if medicube_issue_count:
        key_risks.append("메디큐브 승인 검토 필요")
    if moq_issue_count:
        key_risks.append("MOQ 확인 필요")
    if price_confirmation_needed_count:
        key_risks.append("가격 확인 필요")
    if stock_confirmation_needed_count:
        key_risks.append("재고 확인 필요")
    if expiry_confirmation_needed_count:
        key_risks.append("유통기한 확인 필요")
    if internal_review_count:
        key_risks.append("내부 검토 필요 항목 존재")

    return {
        "runner": runner,
        "total_buyers": len(buyers),
        "buyer_count_by_priority_tier": count_by(scores, "priority_tier"),
        "buyer_count_by_approval_block": bool_counter(scores, "approval_block"),
        "buyer_count_by_lead_status": count_by(buyers, "lead_status"),
        "proposal_count_by_message_status": count_by(proposals, "message_status"),
        "quotation_count_by_quotation_status": count_by(quotations, "quotation_status"),
        "moq_issue_count": moq_issue_count,
        "price_confirmation_needed_count": price_confirmation_needed_count,
        "stock_confirmation_needed_count": stock_confirmation_needed_count,
        "expiry_confirmation_needed_count": expiry_confirmation_needed_count,
        "approval_required_brand_issue_count": approval_issue_count,
        "medicube_blocked_or_review_needed_count": medicube_issue_count,
        "required_internal_review_count": internal_review_count,
        "next_action_summary": next_actions,
        "key_risks": key_risks,
        "key_risk_count": len(key_risks),
    }


def render_dashboard(metrics: dict[str, object], warnings: list[str]) -> str:
    runner = metrics["runner"]
    assert isinstance(runner, dict)

    lines = [
        "# Operations Dashboard",
        "",
        f"- generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- status: 내부검토용",
        "- external_use: 외부 발송 금지",
        "- commercial_approval: 최종 상업 승인 아님",
        "",
        "## Executive Summary",
        "",
        "- 이 대시보드는 로컬 샘플/내부검토용 출력만 요약합니다.",
        "- 제안 메시지와 견적 결과는 draft 또는 internal-review output입니다.",
        "- score_total은 바이어 실제성, 신용도, 구매 가능성을 증명하지 않습니다.",
        "- approval_block=true는 priority_tier 또는 score_total보다 우선합니다.",
        "- 메디큐브/Medicube는 승인 필요 브랜드이며 명시 승인 전 외부 제안 대상이 아닙니다.",
        f"- total_buyers: {metrics['total_buyers']}",
        f"- key_risk_count: {metrics['key_risk_count']}",
        "",
        "## Integrated Runner Status",
        "",
        f"- integrated_runner_result: {runner.get('result')}",
        f"- integrated_runner_stage_count: {runner.get('stage_count')}",
        f"- pass_count: {runner.get('pass_count')}",
        f"- warning_count: {runner.get('warning_count')}",
        f"- fail_count: {runner.get('fail_count')}",
        "",
        "## Buyer Pipeline Summary",
        "",
        "- buyer_count_by_lead_status:",
        *make_top_summary(metrics["buyer_count_by_lead_status"]),  # type: ignore[arg-type]
        "",
        "## Buyer Priority Summary",
        "",
        "- buyer_count_by_priority_tier:",
        *make_top_summary(metrics["buyer_count_by_priority_tier"]),  # type: ignore[arg-type]
        "- buyer_count_by_approval_block:",
        *make_top_summary(metrics["buyer_count_by_approval_block"]),  # type: ignore[arg-type]
        "",
        "## Approval & Brand Risk Summary",
        "",
        f"- approval_required_brand_issue_count: {metrics['approval_required_brand_issue_count']}",
        f"- medicube_blocked_or_review_needed_count: {metrics['medicube_blocked_or_review_needed_count']}",
        "- 승인 필요 브랜드는 내부 승인 전 buyer-facing pitch, public content, quotation 대상으로 사용할 수 없습니다.",
        "",
        "## Proposal Message Summary",
        "",
        "- proposal_count_by_message_status:",
        *make_top_summary(metrics["proposal_count_by_message_status"]),  # type: ignore[arg-type]
        "- 제안 메시지는 내부 검토 초안이며 실제 발송 지시가 아닙니다.",
        "",
        "## Quotation Summary",
        "",
        "- quotation_count_by_quotation_status:",
        *make_top_summary(metrics["quotation_count_by_quotation_status"]),  # type: ignore[arg-type]
        "- 견적 결과 PASS는 최종 상업 승인을 의미하지 않습니다.",
        "",
        "## MOQ / Price / Stock / Expiry Issues",
        "",
        f"- moq_issue_count: {metrics['moq_issue_count']}",
        f"- price_confirmation_needed_count: {metrics['price_confirmation_needed_count']}",
        f"- stock_confirmation_needed_count: {metrics['stock_confirmation_needed_count']}",
        f"- expiry_confirmation_needed_count: {metrics['expiry_confirmation_needed_count']}",
        "",
        "## Next Action Summary",
        "",
        "- next_action_summary:",
        *make_top_summary(metrics["next_action_summary"]),  # type: ignore[arg-type]
        "",
        "## Internal Review Required Items",
        "",
        f"- required_internal_review_count: {metrics['required_internal_review_count']}",
        "- 내부 검토 필요 항목은 외부 커뮤니케이션 전에 담당자 확인이 필요합니다.",
        "",
        "## Key Risks and Warnings",
        "",
    ]

    key_risks = metrics["key_risks"]
    if isinstance(key_risks, list) and key_risks:
        lines.extend(f"- {risk}" for risk in key_risks)
    else:
        lines.append("- 현재 샘플 기준 핵심 경고 없음")

    if warnings:
        lines.append("- 입력 경고:")
        lines.extend(f"- {warning}" for warning in warnings)

    lines.extend(
        [
            "",
            "## Final Operational Recommendation",
            "",
            "- 운영 판단은 PASS/WARNING/FAIL 요약과 내부 검토 항목을 함께 확인한 뒤 진행합니다.",
            "- approval_block=true 또는 승인 필요 브랜드 이슈가 있으면 외부 제안/견적 단계로 넘기지 않습니다.",
            "- 가격, 재고, 유통기한, MOQ, 납기 조건은 실제 사용 전 수동 검증이 필요합니다.",
            "- 이 대시보드는 내부 운영 점검용이며 외부 발송 또는 최종 상업 문서가 아닙니다.",
            "",
        ]
    )
    return "\n".join(lines)


def load_inputs(args: argparse.Namespace) -> tuple[dict[str, list[dict[str, str]]], str, list[str]]:
    warnings: list[str] = []
    paths = {
        "runner_summary": resolve_path(args.runner_summary),
        "buyers": resolve_path(args.buyers),
        "scores": resolve_path(args.scores),
        "proposals": resolve_path(args.proposals),
        "quotations": resolve_path(args.quotations),
        "brands": resolve_path(args.brands),
    }
    for label, path in paths.items():
        reject_private_path(path, label)

    runner_text = read_optional_text(paths["runner_summary"], "runner summary", warnings)
    data: dict[str, list[dict[str, str]]] = {}
    for label in ("buyers", "scores", "proposals", "quotations", "brands"):
        _, rows = read_csv_rows(paths[label], label, REQUIRED_COLUMNS[label])
        data[label] = rows
    return data, runner_text, warnings


def print_dry_run(args: argparse.Namespace, data: dict[str, list[dict[str, str]]], warnings: list[str]) -> None:
    print("DRY RUN: no dashboard file written")
    print("planned_inputs:")
    print(f"- runner_summary: {rel(resolve_path(args.runner_summary))}")
    print(f"- buyers: {rel(resolve_path(args.buyers))}")
    print(f"- scores: {rel(resolve_path(args.scores))}")
    print(f"- proposals: {rel(resolve_path(args.proposals))}")
    print(f"- quotations: {rel(resolve_path(args.quotations))}")
    print(f"- brands: {rel(resolve_path(args.brands))}")
    print(f"planned_output: {rel(resolve_path(args.output))}")
    print("planned_sections:")
    for section in DASHBOARD_SECTIONS:
        print(f"- {section}")
    print("row_counts:")
    for label in ("buyers", "scores", "proposals", "quotations", "brands"):
        print(f"- {label}: {len(data[label])}")
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local internal operations dashboard.")
    parser.add_argument("--runner-summary", default=str(DEFAULT_RUNNER_SUMMARY))
    parser.add_argument("--buyers", default=str(DEFAULT_BUYERS))
    parser.add_argument("--scores", default=str(DEFAULT_SCORES))
    parser.add_argument("--proposals", default=str(DEFAULT_PROPOSALS))
    parser.add_argument("--quotations", default=str(DEFAULT_QUOTATIONS))
    parser.add_argument("--brands", default=str(DEFAULT_BRANDS))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = resolve_path(args.output)
    reject_private_path(output_path, "output")

    data, runner_text, warnings = load_inputs(args)

    if args.dry_run:
        print_dry_run(args, data, warnings)
        return

    metrics = build_metrics(
        runner_text,
        data["buyers"],
        data["scores"],
        data["proposals"],
        data["quotations"],
        data["brands"],
        warnings,
    )
    dashboard = render_dashboard(metrics, warnings)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dashboard, encoding="utf-8")
    print(f"PASS: operations dashboard generated: {rel(output_path)}")


if __name__ == "__main__":
    main()
