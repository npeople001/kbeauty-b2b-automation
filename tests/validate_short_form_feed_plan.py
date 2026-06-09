"""Validate generated short-form video and feed plan reports.

This validator checks local Markdown output only. It does not collect external
data, perform web research, call APIs, or verify live market facts.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Executive Summary",
    "Short-form Video Production Plan",
    "Feed Post Production Plan",
    "Channel-Specific Adaptation",
    "Weekly Production Schedule",
    "Asset Checklist",
    "B2B Inquiry Conversion Plan",
    "Risks and Compliance",
    "Final Recommendation",
]

VIDEO_FIELDS = [
    "video_id",
    "video_title",
    "target_channel",
    "objective",
    "target_viewer",
    "b2b_or_b2c_focus",
    "hook",
    "opening_scene",
    "scene_by_scene_plan",
    "product_shot_direction",
    "script_direction",
    "caption_direction",
    "subtitle_direction",
    "CTA",
    "required_assets",
    "production_difficulty",
    "expected_effect",
    "cost_level",
    "risk_level",
    "compliance_notes",
]

FEED_FIELDS = [
    "feed_id",
    "feed_title",
    "target_channel",
    "objective",
    "image_structure",
    "slide_by_slide_plan",
    "headline",
    "key_copy",
    "product_display_direction",
    "proof_points",
    "CTA",
    "design_notes",
    "required_assets",
    "production_difficulty",
    "expected_effect",
    "cost_level",
    "risk_level",
    "compliance_notes",
]

WEEKLY_FIELDS = [
    "week",
    "content_id",
    "channel",
    "content_type",
    "topic",
    "production_task",
    "required_materials",
    "owner",
    "expected_output",
]

ASSET_TERMS = [
    "product_images",
    "product_videos",
    "texture_shots",
    "package_shots",
    "before_after_restrictions",
    "brand_approval_materials",
    "translation",
    "localization",
    "proof_documents_if_needed",
]

B2B_CONVERSION_FIELDS = [
    "content_id",
    "buyer_segment",
    "inquiry_trigger",
    "CTA",
    "landing_or_contact_path",
    "follow_up_message_direction",
    "required_sales_materials",
]

CAUTION_TERMS = [
    "검증 필요",
    "소스 자료 부족",
    "확정 불가",
    "가정",
    "추가 확인",
    "확인 필요",
    "금지",
    "제외",
    "하지 않",
    "않음",
]

INSUFFICIENT_EVIDENCE_TERMS = ["검증 필요", "소스 자료 부족", "확정 불가"]

SUSPICIOUS_CLAIM_PATTERNS = [
    r"\b\d+(?:\.\d+)?\s*%",
    r"\b\d+(?:\.\d+)?\s*(?:만|천|억)?\s*(?:조회|뷰|views)\b",
    r"(?:시장\s*규모|market\s*size)",
    r"(?:랭킹|순위|ranking|ranked)",
    r"(?:판매량|매출|sales\s*volume|revenue)",
    r"(?:조회수|view\s*count|views)",
    r"(?:참여율|engagement\s*rate)",
    r"(?:전환율|conversion\s*rate)",
    r"(?:보장|guarantee|guaranteed)",
]

SAFE_BRAND_CONTEXT_TERMS = [
    "승인",
    "approval",
    "approval-required",
    "restricted",
    "제외",
    "금지",
    "차단",
    "명시 승인",
    "외부 추천에서 제외",
    "not externally recommended",
]

UNSAFE_BRAND_RECOMMENDATION_PATTERNS = [
    r"메디큐브.*(?:외부\s*게시|공개\s*콘텐츠|바이어\s*제안|광고\s*카피).*추천",
    r"메디큐브.*(?:recommend|recommended).*(?:external|public|buyer-facing|advertising)",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a generated short-form video and feed plan report."
    )
    parser.add_argument(
        "--report",
        default="output/short_form_feed_plan_MR-001.md",
        help="Path to the Markdown report to validate.",
    )
    return parser.parse_args()


def read_report(path: Path, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"[report_exists] Report file does not exist: {path}")
        return ""
    if not path.is_file():
        failures.append(f"[report_exists] Report path is not a file: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        failures.append(f"[utf8_readable] Report is not readable as UTF-8: {exc}")
    except OSError as exc:
        failures.append(f"[utf8_readable] Could not read report: {exc}")
    return ""


def normalize(text: str) -> str:
    return text.lower()


def section_body(text: str, section: str) -> str:
    pattern = re.compile(
        rf"^##\s+\d+\.\s+{re.escape(section)}\s*$([\s\S]*?)(?=^##\s+\d+\.|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1) if match else ""


def require_terms(
    text: str,
    terms: list[str],
    failures: list[str],
    check_name: str,
    context: str,
) -> None:
    lowered = normalize(text)
    missing = [term for term in terms if term.lower() not in lowered]
    if missing:
        failures.append(
            f"[{check_name}] Missing required terms in {context}: {', '.join(missing)}"
        )


def require_any(
    text: str,
    terms: list[str],
    failures: list[str],
    check_name: str,
    context: str,
) -> None:
    lowered = normalize(text)
    if not any(term.lower() in lowered for term in terms):
        failures.append(
            f"[{check_name}] None of the required terms were found in {context}: "
            + ", ".join(terms)
        )


def has_caution(line: str) -> bool:
    lowered = normalize(line)
    return any(term.lower() in lowered for term in CAUTION_TERMS)


def validate_required_sections(text: str, failures: list[str]) -> None:
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^##\s+\d+\.\s+{re.escape(section)}\s*$", text, re.MULTILINE):
            failures.append(f"[required_sections] Missing section: {section}")


def validate_korean_text(text: str, failures: list[str]) -> None:
    if not re.search(r"[가-힣]", text):
        failures.append("[korean_text] No Korean Hangul text was found in the report.")


def validate_core_structure(text: str, failures: list[str]) -> None:
    require_terms(text, ["V-001", "V-002", "V-003"], failures, "video_items", "report")
    require_terms(text, ["F-001", "F-002", "F-003"], failures, "feed_items", "report")

    video_section = section_body(text, "Short-form Video Production Plan")
    feed_section = section_body(text, "Feed Post Production Plan")
    weekly_section = section_body(text, "Weekly Production Schedule")
    asset_section = section_body(text, "Asset Checklist")
    conversion_section = section_body(text, "B2B Inquiry Conversion Plan")

    require_terms(video_section, VIDEO_FIELDS, failures, "video_fields", "video plan section")
    require_terms(feed_section, FEED_FIELDS, failures, "feed_fields", "feed plan section")
    require_terms(
        weekly_section,
        WEEKLY_FIELDS,
        failures,
        "weekly_schedule_fields",
        "weekly production schedule section",
    )
    require_terms(asset_section, ASSET_TERMS, failures, "asset_checklist", "asset checklist")
    require_terms(
        conversion_section,
        B2B_CONVERSION_FIELDS,
        failures,
        "b2b_conversion_fields",
        "B2B inquiry conversion section",
    )


def validate_b2b_b2c_separation(text: str, failures: list[str]) -> None:
    require_terms(text, ["B2B", "B2C"], failures, "b2b_b2c_separation", "report")
    require_any(
        text,
        ["b2b_or_b2c_focus", "바이어", "소비자", "buyer", "consumer"],
        failures,
        "b2b_b2c_separation",
        "report",
    )


def validate_china_requirements(text: str, failures: list[str]) -> None:
    target_is_china = any(term in text for term in ["China", "중국"])
    if not target_is_china:
        return

    require_terms(
        text,
        ["Xiaohongshu", "Douyin", "WeChat"],
        failures,
        "china_channels",
        "China-targeted report",
    )

    risk_groups = {
        "account": ["계정", "account"],
        "real_name": ["실명", "real-name", "real name"],
        "platform_policy": ["플랫폼 정책", "platform policy"],
        "localization": ["현지화", "localization"],
        "cosmetics_expression": ["화장품 표현", "cosmetics claim", "cosmetics expression"],
    }
    for check, terms in risk_groups.items():
        require_any(text, terms, failures, f"china_risk_{check}", "China risk content")


def validate_brand_approval(text: str, failures: list[str]) -> None:
    medicube_lines = [line for line in text.splitlines() if "메디큐브" in line]
    if not medicube_lines:
        failures.append("[brand_approval] 메디큐브 approval-required handling is not mentioned.")
        return

    for line in medicube_lines:
        lowered = normalize(line)
        if not any(term.lower() in lowered for term in SAFE_BRAND_CONTEXT_TERMS):
            failures.append(
                "[brand_approval] 메디큐브 appears without approval/restriction context: "
                + line.strip()
            )

    for pattern in UNSAFE_BRAND_RECOMMENDATION_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            line = text[max(0, text.rfind("\n", 0, match.start())) : text.find("\n", match.end())]
            if not has_caution(line):
                failures.append(
                    "[brand_approval] Possible external recommendation of approval-required brand: "
                    + line.strip()
                )


def validate_evidence_and_claims(text: str, failures: list[str]) -> None:
    require_terms(
        text,
        INSUFFICIENT_EVIDENCE_TERMS,
        failures,
        "insufficient_evidence",
        "report",
    )

    for source_pattern in [r"\bSource\s*:", r"\bSources\s*:"]:
        for match in re.finditer(source_pattern, text, flags=re.IGNORECASE):
            line = text[max(0, text.rfind("\n", 0, match.start())) : text.find("\n", match.end())]
            if "user-provided" not in normalize(line) and "사용자 제공" not in line:
                failures.append(
                    "[fake_source_pattern] Source-like citation without user-provided context: "
                    + line.strip()
                )

    for match in re.finditer(r"example\.com", text, flags=re.IGNORECASE):
        window = text[max(0, match.start() - 80) : match.end() + 80]
        if "placeholder" not in normalize(window) and "예시" not in window:
            failures.append("[fake_source_pattern] example.com is not clearly marked as a placeholder.")

    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in SUSPICIOUS_CLAIM_PATTERNS]
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in compiled_patterns) and not has_caution(line):
            failures.append(
                "[unsupported_claim] Suspicious claim is not clearly marked as unverified "
                f"on line {line_number}: {line.strip()}"
            )


def validate_recommendation_fields(text: str, failures: list[str]) -> None:
    require_terms(
        text,
        ["production_difficulty", "expected_effect", "cost_level", "risk_level"],
        failures,
        "recommendation_fields",
        "report",
    )
    require_any(
        text,
        ["실행 난이도", "제작 난이도", "production_difficulty"],
        failures,
        "recommendation_fields",
        "difficulty field",
    )
    require_any(
        text,
        ["기대 효과", "expected_effect"],
        failures,
        "recommendation_fields",
        "expected effect field",
    )
    require_any(
        text,
        ["비용 수준", "cost_level"],
        failures,
        "recommendation_fields",
        "cost level field",
    )
    require_any(
        text,
        ["리스크 수준", "risk_level"],
        failures,
        "recommendation_fields",
        "risk level field",
    )


def run_validation(report_path: Path) -> list[str]:
    failures: list[str] = []
    text = read_report(report_path, failures)
    if not text:
        return failures

    validate_korean_text(text, failures)
    validate_required_sections(text, failures)
    validate_core_structure(text, failures)
    validate_b2b_b2c_separation(text, failures)
    validate_china_requirements(text, failures)
    validate_brand_approval(text, failures)
    validate_evidence_and_claims(text, failures)
    validate_recommendation_fields(text, failures)
    return failures


def main() -> int:
    args = parse_args()
    report_path = Path(args.report)
    failures = run_validation(report_path)

    if failures:
        print("FAIL: short-form/feed plan validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: short-form/feed plan validation passed")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
