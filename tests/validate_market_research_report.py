"""Validate generated market research Markdown reports.

This script reads only a local Markdown report. It does not perform scraping,
live web research, automatic web search, browser automation, API calls,
crawling, or external data collection.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SECTIONS = [
    "Research Brief",
    "Market Overview",
    "Channel Analysis",
    "Competitor and Content Analysis",
    "Product/Brand Fit",
    "B2B Buyer Acquisition Angle",
    "Content Strategy",
    "Short-form Video Plan",
    "Feed Post Plan",
    "Execution Plan",
    "Risks and Compliance",
    "Final Recommendation",
]

EVIDENCE_LABELS = [
    "확인된 사실",
    "관찰",
    "가정",
    "검증 필요",
    "추천",
]

INSUFFICIENT_EVIDENCE_WORDING = [
    "소스 자료 부족",
    "확정 불가",
    "검증 필요",
]

CHINA_RISK_TERMS = [
    "계정",
    "실명",
    "플랫폼 정책",
    "현지화",
    "화장품 표현",
]

RECOMMENDATION_FIELD_GROUPS = [
    ("실행 난이도", "execution_difficulty", "production_difficulty"),
    ("기대 효과", "expected_effect"),
    ("비용 수준", "cost_level"),
    ("리스크 수준", "risk_level"),
]

SAFE_UNVERIFIED_MARKERS = [
    "검증 필요",
    "소스 자료 부족",
    "확정 불가",
    "자료 없음",
    "미제공",
    "생성 금지",
    "확정할 수 없는",
    "제공되지 않음",
    "provided source",
    "needs_review",
]

SUSPICIOUS_STAT_PATTERNS = [
    re.compile(r"\d+(?:\.\d+)?\s*%"),
    re.compile(r"(시장\s*규모|market\s*size|CAGR|GMV)", re.IGNORECASE),
    re.compile(r"(랭킹|순위|ranking)", re.IGNORECASE),
    re.compile(r"(판매량|sales\s*volume)", re.IGNORECASE),
    re.compile(r"(조회수|\bviews?\b)", re.IGNORECASE),
    re.compile(r"(참여율|engagement\s*rate)", re.IGNORECASE),
]

FAKE_SOURCE_PATTERNS = [
    re.compile(r"\bSource:\s*", re.IGNORECASE),
    re.compile(r"\bCitation:\s*", re.IGNORECASE),
    re.compile(r"https?://(?:www\.)?example\.com", re.IGNORECASE),
]

PROHIBITED_EXTERNAL_COLLECTION_TERMS = [
    "requests",
    "selenium",
    "playwright",
    "browser automation",
    "automatic web search",
    "live web research",
    "crawling",
]


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def read_report(path: Path, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"report file does not exist: {path}")
        return ""

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        failures.append(f"report is not readable as UTF-8: {exc}")
    except OSError as exc:
        failures.append(f"report cannot be read: {exc}")
    return ""


def has_korean_text(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))


def line_is_safely_marked(line: str) -> bool:
    return any(marker in line for marker in SAFE_UNVERIFIED_MARKERS)


def validate_required_sections(text: str, failures: list[str]) -> None:
    for index, section in enumerate(REQUIRED_SECTIONS, start=1):
        pattern = rf"^##\s+{index}\.\s+{re.escape(section)}\s*$"
        if not re.search(pattern, text, re.MULTILINE):
            failures.append(f"missing required section: {index}. {section}")


def validate_required_terms(text: str, terms: list[str], check_name: str, failures: list[str]) -> None:
    for term in terms:
        if term not in text:
            failures.append(f"{check_name} missing required term: {term}")


def validate_b2b_b2c_separation(text: str, failures: list[str]) -> None:
    has_b2b = "B2B" in text and ("바이어" in text or "buyer" in text.lower())
    has_b2c = "B2C" in text and ("소비자" in text or "consumer" in text.lower())
    has_separation_word = "분리" in text or "separate" in text.lower()

    if not has_b2b:
        failures.append("B2B buyer acquisition context is missing")
    if not has_b2c:
        failures.append("B2C consumer marketing context is missing")
    if not has_separation_word:
        failures.append("B2B and B2C separation is not clearly stated")


def report_targets_china(text: str) -> bool:
    return "target_country | China" in text or "target_country | 중국" in text or "중국" in text


def validate_china_risks(text: str, failures: list[str]) -> None:
    if not report_targets_china(text):
        return
    validate_required_terms(text, CHINA_RISK_TERMS, "China risk check", failures)


def validate_brand_approval(text: str, failures: list[str]) -> None:
    if "메디큐브" not in text:
        failures.append("brand approval check missing 메디큐브")
        return

    explicit_approval = "메디큐브 승인 완료" in text or "메디큐브 외부 사용 승인" in text
    allowed_context_terms = [
        "승인 필요",
        "제외",
        "외부 추천 제외",
        "노출 금지",
        "추천에서 제외",
        "restricted",
        "approval-required",
        "not externally recommended",
    ]
    dangerous_context_terms = [
        "메디큐브 추천",
        "메디큐브를 추천",
        "메디큐브 외부 포스팅",
        "메디큐브 바이어 제안",
        "메디큐브 public content",
    ]

    for line_number, line in enumerate(text.splitlines(), start=1):
        if "메디큐브" not in line:
            continue

        if any(term in line for term in dangerous_context_terms) and not explicit_approval:
            if "제외" not in line and "금지" not in line:
                failures.append(f"메디큐브 may be externally recommended without approval at line {line_number}: {line.strip()}")

        if not any(term in line for term in allowed_context_terms):
            failures.append(f"메디큐브 appears without approval/restriction context at line {line_number}: {line.strip()}")


def validate_fake_sources(text: str, failures: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern in FAKE_SOURCE_PATTERNS:
            if not pattern.search(line):
                continue
            if "placeholder" in line.lower() or "사용자 제공" in line or line_is_safely_marked(line):
                continue
            failures.append(f"possible fake source pattern at line {line_number}: {line.strip()}")


def validate_suspicious_statistics(text: str, failures: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern in SUSPICIOUS_STAT_PATTERNS:
            if not pattern.search(line):
                continue
            if line_is_safely_marked(line):
                continue
            failures.append(f"unsupported statistic-like claim at line {line_number}: {line.strip()}")
            break


def validate_recommendation_fields(text: str, failures: list[str]) -> None:
    normalized = text.lower()
    for terms in RECOMMENDATION_FIELD_GROUPS:
        if not any(term.lower() in normalized for term in terms):
            failures.append(f"recommendation field missing: {' or '.join(terms)}")


def validate_no_external_collection_language(text: str, failures: list[str]) -> None:
    for term in PROHIBITED_EXTERNAL_COLLECTION_TERMS:
        if term not in text:
            continue
        if "수행하지 않았" in text or "does not perform" in text or "금지" in text:
            continue
        failures.append(f"report appears to include external collection behavior: {term}")


def validate_report(path: Path) -> list[str]:
    failures: list[str] = []
    text = read_report(path, failures)
    if not text:
        return failures

    if not has_korean_text(text):
        failures.append("Korean text is not preserved")

    validate_required_sections(text, failures)
    validate_required_terms(text, EVIDENCE_LABELS, "evidence label check", failures)
    validate_required_terms(text, INSUFFICIENT_EVIDENCE_WORDING, "insufficient-evidence check", failures)
    validate_b2b_b2c_separation(text, failures)
    validate_china_risks(text, failures)
    validate_brand_approval(text, failures)
    validate_fake_sources(text, failures)
    validate_suspicious_statistics(text, failures)
    validate_recommendation_fields(text, failures)
    validate_no_external_collection_language(text, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a generated market research Markdown report.")
    parser.add_argument("--report", required=True, help="Path to the generated Markdown report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_path = resolve_path(args.report)
    failures = validate_report(report_path)

    if failures:
        print("FAIL: market research report validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: market research report validation passed")
    print(f"report_path={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
