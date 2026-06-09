"""Validate generated channel content strategy Markdown reports.

This script reads only a local Markdown file. It does not perform scraping,
live web research, automatic web search, browser automation, API calls,
crawling, requests to external services, or external data collection.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SECTIONS = [
    "Strategy Summary",
    "Channel Strategy",
    "Short-form Video Strategy",
    "Feed Post Strategy",
    "B2B Buyer Acquisition Content",
    "Weekly Upload Plan",
    "Execution Priority",
    "Risks and Compliance",
    "Final Recommendation",
]

KOREAN_MARKERS = [
    "전략",
    "보고서",
    "검증 필요",
    "메디큐브",
    "중국",
    "화장품",
    "寃利",
    "硫붾뵒",
    "以묎뎅",
]

INSUFFICIENT_EVIDENCE_MARKERS = [
    "검증 필요",
    "소스 자료 부족",
    "확정 불가",
    "가정",
    "寃利",
    "뚯뒪",
    "뺤젙",
    "媛",
]

CHINA_MARKERS = ["China", "중국", "以묎뎅"]
CHINA_CHANNEL_GROUPS = [
    ["Xiaohongshu", "샤오홍슈", "?ㅼ삤?띿뒋"],
    ["Douyin", "더우인", "?꾩슦"],
    ["WeChat", "위챗", "?꾩콟"],
]
CHINA_RISK_GROUPS = [
    ["계정", "怨꾩젙"],
    ["실명", "?ㅻ챸"],
    ["플랫폼 정책", "?뚮옯???뺤콉"],
    ["현지화", "?꾩???"],
    ["화장품 표현", "?붿옣???쒗쁽"],
]

RECOMMENDATION_TERM_GROUPS = [
    ["execution_difficulty", "difficulty", "실행 난이도", "?ㅽ뻾 ?쒖씠"],
    ["expected_effect", "기대 효과", "湲곕? ?④낵"],
    ["cost_level", "비용 수준", "鍮꾩슜 ?섏?"],
    ["risk_level", "리스크 수준", "由ъ뒪???섏?"],
]

VIDEO_TERM_GROUPS = [
    ["hook", "후크", "?꾪궧"],
    ["opening_scene", "opening scene", "오프닝", "?ㅽ봽"],
    ["key_scenes", "key scenes", "핵심 장면", "?듭떖 ?λ㈃"],
    ["product_display_direction", "product display", "제품 노출", "?쒗뭹 ?몄텧"],
    ["CTA"],
    ["required_assets", "required assets", "필요 소재", "?꾩슂 ?뚯옱"],
    ["production_difficulty", "production difficulty", "제작 난이도", "?쒖옉 ?쒖씠"],
    ["expected_effect", "expected effect", "기대 효과", "湲곕? ?④낵"],
    ["risk", "리스크", "由ъ뒪"],
]

FEED_TERM_GROUPS = [
    ["image_structure", "image structure", "이미지 구조", "?대?吏 援ъ“"],
    ["headline", "헤드라인", "?ㅻ뱶?쇱씤"],
    ["key_copy", "key copy", "핵심 카피", "?듭떖 移댄뵾"],
    ["proof_points", "proof points", "증빙 포인트", "利앸튃 ?ъ씤"],
    ["CTA"],
    ["design_notes", "design notes", "디자인 참고", "?붿옄??李멸퀬"],
    ["expected_effect", "expected effect", "기대 효과", "湲곕? ?④낵"],
    ["risk", "리스크", "由ъ뒪"],
]

WEEKLY_TERM_GROUPS = [
    ["week", "주차", "二쇱감"],
    ["channel", "채널", "梨꾨꼸"],
    ["content_type", "content type", "콘텐츠 유형", "肄섑뀗痢??좏삎"],
    ["topic", "주제", "二쇱젣"],
    ["required_materials", "required materials", "필요 소재", "?꾩슂 ?뚯옱"],
]

PRIORITY_TERM_GROUPS = [
    ["priority", "우선순위", "?곗꽑?쒖쐞"],
    ["action_item", "action item", "실행 항목", "?ㅽ뻾 ??ぉ"],
    ["reason", "이유", "?댁쑀"],
    ["difficulty", "난이도", "?쒖씠"],
    ["expected_effect", "expected effect", "기대 효과", "湲곕? ?④낵"],
    ["cost_level", "cost level", "비용 수준", "鍮꾩슜 ?섏?"],
    ["risk_level", "risk level", "리스크 수준", "由ъ뒪???섏?"],
]

SAFE_MEDICUBE_CONTEXT = [
    "승인",
    "승인 전",
    "제외",
    "제한",
    "금지",
    "추천 금지",
    "외부 추천에서 제외",
    "approval",
    "restricted",
    "excluded",
    "not externally recommended",
    "뱀씤",
    "쒖쇅",
    "湲덉",
]

BAD_MEDICUBE_RECOMMENDATION_PATTERNS = [
    r"(메디큐브|硫붾뵒\?먮툕).{0,30}(추천|게시 추천|광고|제안 추천)",
    r"(recommend|recommended).{0,30}(메디큐브|硫붾뵒\?먮툕)",
]

FAKE_SOURCE_PATTERNS = [
    r"example\.com(?![^\\n]*(placeholder|예시|sample))",
    r"\bSource:\s*(?!user-provided|provided|source_notes|sources\.csv)",
]

SUSPICIOUS_PERFORMANCE_PATTERNS = [
    r"(시장\s*점유율|랭킹|순위|판매량|매출|조회수|참여율|전환율|engagement rate|conversion rate|views|ranking|sales volume|platform performance)[^.\n|]*(\d[\d,]*(?:\.\d+)?%?)",
    r"(\d[\d,]*(?:\.\d+)?%)",
]


def resolve_path(path_value: str | Path) -> Path:
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
        return ""


def contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def check_term_group(text: str, group: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in group)


def section_text(text: str, section: str) -> str:
    pattern = re.compile(rf"^##\s+\d+\.\s+{re.escape(section)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    next_match = re.search(r"^##\s+\d+\.\s+", text[match.end() :], re.MULTILINE)
    if not next_match:
        return text[match.end() :]
    return text[match.end() : match.end() + next_match.start()]


def has_uncertainty_near(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 120) : min(len(text), end + 160)]
    return contains_any(window, INSUFFICIENT_EVIDENCE_MARKERS)


def validate_required_sections(text: str, failures: list[str]) -> None:
    for section in REQUIRED_SECTIONS:
        if f"## " not in text or section not in text:
            failures.append(f"missing required section: {section}")


def validate_china_checks(text: str, failures: list[str]) -> None:
    if not contains_any(text, CHINA_MARKERS):
        return
    for group in CHINA_CHANNEL_GROUPS:
        if not check_term_group(text, group):
            failures.append(f"China channel term missing: one of {group}")
    for group in CHINA_RISK_GROUPS:
        if not check_term_group(text, group):
            failures.append(f"China risk term missing: one of {group}")


def validate_brand_approval(text: str, failures: list[str]) -> None:
    medicube_names = ["메디큐브", "硫붾뵒?먮툕"]
    for name in medicube_names:
        start = 0
        while True:
            index = text.find(name, start)
            if index == -1:
                break
            context = text[max(0, index - 80) : index + 120]
            if not contains_any(context, SAFE_MEDICUBE_CONTEXT):
                failures.append(f"메디큐브 context is not clearly restricted/excluded near: {context[:120]}")
            start = index + len(name)

    for pattern in BAD_MEDICUBE_RECOMMENDATION_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            context = text[max(0, match.start() - 80) : min(len(text), match.end() + 120)]
            if not contains_any(context, SAFE_MEDICUBE_CONTEXT):
                failures.append(f"메디큐브 appears externally recommended: {match.group(0)}")


def validate_fake_sources(text: str, failures: list[str]) -> None:
    for pattern in FAKE_SOURCE_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            failures.append(f"fake or unsupported source pattern found: {match.group(0)}")


def validate_fake_performance_claims(text: str, failures: list[str]) -> None:
    for pattern in SUSPICIOUS_PERFORMANCE_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            if not has_uncertainty_near(text, match.start(), match.end()):
                failures.append(f"unsupported performance/statistical claim found: {match.group(0)}")


def validate_section_terms(text: str, section: str, term_groups: list[list[str]], failures: list[str]) -> None:
    content = section_text(text, section)
    if not content:
        failures.append(f"cannot inspect missing section content: {section}")
        return
    for group in term_groups:
        if not check_term_group(content, group):
            failures.append(f"{section} missing required term: one of {group}")


def validate_report(text: str) -> list[str]:
    failures: list[str] = []

    if not text.strip():
        failures.append("report is empty")
        return failures

    if not contains_any(text, KOREAN_MARKERS):
        failures.append("Korean text does not appear to be preserved")

    validate_required_sections(text, failures)

    if "B2B" not in text or "B2C" not in text:
        failures.append("B2B and B2C are not clearly separated")

    validate_china_checks(text, failures)
    validate_brand_approval(text, failures)
    validate_fake_sources(text, failures)
    validate_fake_performance_claims(text, failures)

    for group in RECOMMENDATION_TERM_GROUPS:
        if not check_term_group(text, group):
            failures.append(f"required recommendation evaluation term missing: one of {group}")

    validate_section_terms(text, "Short-form Video Strategy", VIDEO_TERM_GROUPS, failures)
    validate_section_terms(text, "Feed Post Strategy", FEED_TERM_GROUPS, failures)
    validate_section_terms(text, "Weekly Upload Plan", WEEKLY_TERM_GROUPS, failures)
    validate_section_terms(text, "Execution Priority", PRIORITY_TERM_GROUPS, failures)

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a generated channel content strategy report.")
    parser.add_argument("--report", required=True, help="Path to generated Markdown strategy report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_path = resolve_path(args.report)
    failures: list[str] = []
    text = read_report(report_path, failures)

    if text:
        failures.extend(validate_report(text))

    if failures:
        print("FAIL: channel content strategy validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: channel content strategy validation passed")
    print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
