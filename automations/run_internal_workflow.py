"""Controlled local runner for the internal buyer sales sample workflow."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = Path("output/internal_workflow_summary.md")
WORKFLOW_NAME = "buyer_sales_sample"


@dataclass(frozen=True)
class Stage:
    name: str
    command: list[str]
    outputs: tuple[str, ...] = ()


@dataclass
class StageResult:
    name: str
    command: list[str]
    status: str
    return_code: int | None = None
    started_at: str = ""
    finished_at: str = ""
    stdout_summary: str = ""
    stderr_summary: str = ""
    warnings: list[str] = field(default_factory=list)


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def py(*args: str) -> list[str]:
    return [sys.executable, *args]


def build_stages() -> list[Stage]:
    return [
        Stage(
            "privacy_guard_validation",
            py("tests/validate_privacy_guard.py"),
        ),
        Stage(
            "buyer_lead_validation",
            py(
                "tests/validate_buyer_leads.py",
                "--raw",
                "data/buyers_raw_sample.csv",
                "--master",
                "data/buyers_master_sample.csv",
            ),
        ),
        Stage(
            "buyer_scoring_generation",
            py(
                "automations/buyer_scoring/generate_buyer_scores.py",
                "--input",
                "data/buyers_master_sample.csv",
                "--output",
                "data/buyers_scored_sample.csv",
                "--brands",
                "data/brands_master.csv",
            ),
            ("data/buyers_scored_sample.csv",),
        ),
        Stage(
            "buyer_score_validation",
            py(
                "tests/validate_buyer_scores.py",
                "--input",
                "data/buyers_master_sample.csv",
                "--scored",
                "data/buyers_scored_sample.csv",
            ),
        ),
        Stage(
            "proposal_message_generation",
            py(
                "automations/proposal_messages/generate_proposal_messages.py",
                "--buyers",
                "data/buyers_master_sample.csv",
                "--scores",
                "data/buyers_scored_sample.csv",
                "--brands",
                "data/brands_master.csv",
                "--csv-output",
                "data/proposal_messages_sample.csv",
                "--md-output",
                "output/proposal_messages_sample.md",
            ),
            ("data/proposal_messages_sample.csv", "output/proposal_messages_sample.md"),
        ),
        Stage(
            "proposal_message_validation",
            py(
                "tests/validate_proposal_messages.py",
                "--buyers",
                "data/buyers_master_sample.csv",
                "--scores",
                "data/buyers_scored_sample.csv",
                "--messages",
                "data/proposal_messages_sample.csv",
                "--markdown",
                "output/proposal_messages_sample.md",
                "--brands",
                "data/brands_master.csv",
            ),
        ),
        Stage(
            "quotation_generation",
            py(
                "automations/quotation_maker/generate_quotations.py",
                "--buyers",
                "data/buyers_master_sample.csv",
                "--scores",
                "data/buyers_scored_sample.csv",
                "--proposals",
                "data/proposal_messages_sample.csv",
                "--brands",
                "data/brands_master.csv",
                "--quote-inputs",
                "data/quotation_inputs_sample.csv",
                "--csv-output",
                "data/quotation_sample.csv",
                "--xlsx-output",
                "output/quotation_sample.xlsx",
                "--md-output",
                "output/quotation_sample.md",
            ),
            (
                "data/quotation_sample.csv",
                "output/quotation_sample.xlsx",
                "output/quotation_sample.md",
            ),
        ),
        Stage(
            "quotation_validation",
            py(
                "tests/validate_quotations.py",
                "--quote-inputs",
                "data/quotation_inputs_sample.csv",
                "--quotations",
                "data/quotation_sample.csv",
                "--markdown",
                "output/quotation_sample.md",
                "--xlsx",
                "output/quotation_sample.xlsx",
                "--buyers",
                "data/buyers_master_sample.csv",
                "--scores",
                "data/buyers_scored_sample.csv",
                "--proposals",
                "data/proposal_messages_sample.csv",
                "--brands",
                "data/brands_master.csv",
            ),
        ),
    ]


def format_command(command: list[str]) -> str:
    return " ".join(f'"{part}"' if " " in part else part for part in command)


def safe_print(text: str) -> None:
    encoding = sys.stdout.encoding or "utf-8"
    print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def summarize_output(text: str, limit: int = 700) -> str:
    compact = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def warning_lines(*texts: str) -> list[str]:
    warnings: list[str] = []
    for text in texts:
        for line in text.splitlines():
            lowered = line.lower()
            if "warning" in lowered and "warnings=0" not in lowered:
                warnings.append(line.strip())
    return warnings


def run_stage(stage: Stage, continue_on_warning: bool) -> StageResult:
    started_at = timestamp()
    completed = subprocess.run(
        stage.command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    finished_at = timestamp()
    warnings = warning_lines(completed.stdout, completed.stderr)
    status = "PASS" if completed.returncode == 0 else "FAIL"
    if status == "PASS" and warnings and not continue_on_warning:
        status = "FAIL"
    return StageResult(
        name=stage.name,
        command=stage.command,
        status=status,
        return_code=completed.returncode,
        started_at=started_at,
        finished_at=finished_at,
        stdout_summary=summarize_output(completed.stdout),
        stderr_summary=summarize_output(completed.stderr),
        warnings=warnings,
    )


def skipped_result(stage: Stage) -> StageResult:
    return StageResult(
        name=stage.name,
        command=stage.command,
        status="SKIPPED",
        started_at=timestamp(),
        finished_at=timestamp(),
        stderr_summary="Previous stage failed and stop-on-fail is active.",
    )


def print_dry_run(stages: list[Stage], skip_xlsx: bool) -> None:
    safe_print(f"Workflow: {WORKFLOW_NAME}")
    safe_print("Mode: dry-run")
    if skip_xlsx:
        safe_print(
            "Note: --skip-xlsx is not active yet because quotation generation "
            "and validation currently require XLSX output."
        )
    for index, stage in enumerate(stages, start=1):
        safe_print(f"{index}. PLANNED {stage.name}")
        safe_print(f"   {format_command(stage.command)}")
    safe_print(f"{len(stages) + 1}. PLANNED final_run_summary")
    safe_print(f"   internal write_summary {DEFAULT_SUMMARY}")


def write_summary(
    path: Path,
    workflow: str,
    started_at: str,
    finished_at: str,
    results: list[StageResult],
    skip_xlsx: bool,
) -> None:
    overall = "PASS" if all(result.status == "PASS" for result in results) else "FAIL"
    output_paths = [
        "data/buyers_scored_sample.csv",
        "data/proposal_messages_sample.csv",
        "data/quotation_sample.csv",
        "output/proposal_messages_sample.md",
        "output/quotation_sample.md",
        "output/quotation_sample.xlsx",
        str(path).replace("\\", "/"),
    ]
    lines = [
        "# Internal Workflow Summary",
        "",
        f"- workflow: {workflow}",
        f"- result: {overall}",
        f"- started_at: {started_at}",
        f"- finished_at: {finished_at}",
        "- scope: internal review only",
        "- external_sending: not included",
        "- external_collection: not included",
    ]
    if skip_xlsx:
        lines.append(
            "- skip_xlsx_note: requested but not active because existing quotation "
            "steps require XLSX output"
        )
    lines.extend(
        [
            "",
            "## Stage Results",
            "",
            "| order | stage | status | return_code |",
            "| --- | --- | --- | --- |",
        ]
    )
    for index, result in enumerate(results, start=1):
        return_code = "" if result.return_code is None else str(result.return_code)
        lines.append(f"| {index} | {result.name} | {result.status} | {return_code} |")
    lines.extend(["", "## Stage Details", ""])
    for result in results:
        lines.extend(
            [
                f"### {result.name}",
                "",
                f"- status: {result.status}",
                f"- command: `{format_command(result.command)}`",
                f"- started_at: {result.started_at}",
                f"- finished_at: {result.finished_at}",
            ]
        )
        if result.stdout_summary:
            lines.append(f"- stdout_summary: {result.stdout_summary}")
        if result.stderr_summary:
            lines.append(f"- stderr_summary: {result.stderr_summary}")
        if result.warnings:
            lines.append(f"- warnings: {'; '.join(result.warnings)}")
        lines.append("")
    lines.extend(["## Output Paths", ""])
    lines.extend(f"- {output_path}" for output_path in output_paths)
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            "Review this summary and the validation outputs before using any draft internally.",
            "External communication, quotation sending, and external data collection remain out of scope.",
            "",
        ]
    )
    output_path = ROOT / path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_workflow(args: argparse.Namespace) -> int:
    stages = build_stages()
    if args.dry_run:
        print_dry_run(stages, args.skip_xlsx)
        return 0

    started_at = timestamp()
    results: list[StageResult] = []
    should_skip = False

    for stage in stages:
        if should_skip:
            results.append(skipped_result(stage))
            continue
        result = run_stage(stage, args.continue_on_warning)
        results.append(result)
        safe_print(f"{result.status}: {stage.name}")
        if result.stdout_summary:
            safe_print(f"  stdout: {result.stdout_summary}")
        if result.stderr_summary:
            safe_print(f"  stderr: {result.stderr_summary}")
        if stage.name == "privacy_guard_validation" and result.status != "PASS":
            should_skip = True
        elif args.stop_on_fail and result.status != "PASS":
            should_skip = True

    finished_at = timestamp()
    results.append(
        StageResult(
            name="final_run_summary",
            command=["internal", "write_summary", str(args.output_summary)],
            status="PASS",
            started_at=finished_at,
            finished_at=timestamp(),
        )
    )
    write_summary(
        args.output_summary,
        args.workflow,
        started_at,
        finished_at,
        results,
        args.skip_xlsx,
    )
    safe_print(f"Summary written: {(ROOT / args.output_summary).resolve()}")
    return 0 if all(result.status == "PASS" for result in results) else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the controlled internal buyer sales sample workflow."
    )
    parser.add_argument(
        "--workflow",
        default=WORKFLOW_NAME,
        choices=[WORKFLOW_NAME],
        help="Workflow to run. Currently only buyer_sales_sample is supported.",
    )
    parser.add_argument(
        "--stop-on-fail",
        action="store_true",
        default=True,
        help="Stop after the first failed stage. Enabled by default.",
    )
    parser.add_argument(
        "--continue-on-warning",
        action="store_true",
        help="Keep running if a stage prints warning text but exits successfully.",
    )
    parser.add_argument(
        "--skip-xlsx",
        action="store_true",
        help="Reserved for future use; current quotation workflow still requires XLSX.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned stages without executing commands or writing a summary.",
    )
    parser.add_argument(
        "--output-summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help="Markdown summary path for non-dry-run execution.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_workflow(args)


if __name__ == "__main__":
    raise SystemExit(main())
