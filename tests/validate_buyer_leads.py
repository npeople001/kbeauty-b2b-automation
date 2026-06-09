import argparse
import csv
import sys
from pathlib import Path


RAW_COLUMNS = [
    "buyer_id",
    "company_name",
    "country",
    "city",
    "buyer_type",
    "sales_channel",
    "platform",
    "website",
    "sns_url",
    "contact_name",
    "contact_email",
    "contact_phone",
    "wechat_id",
    "whatsapp",
    "language",
    "interested_brands",
    "interested_categories",
    "estimated_order_qty",
    "moq_fit",
    "china_relevance",
    "payment_risk",
    "repeat_purchase_potential",
    "lead_source",
    "lead_status",
    "priority",
    "next_action",
    "notes",
    "created_at",
    "updated_at",
]

MASTER_EXTRA_COLUMNS = [
    "validation_status",
    "approval_warning",
    "contact_privacy_level",
    "recommended_follow_up",
    "proposal_brand_check",
]

MASTER_COLUMNS = RAW_COLUMNS + MASTER_EXTRA_COLUMNS

REQUIRED_FIELDS = ["buyer_id", "company_name", "country", "lead_status", "created_at"]

ALLOWED_VALUES = {
    "buyer_type": {
        "importer",
        "distributor",
        "wholesaler",
        "retailer",
        "online_seller",
        "live_commerce",
        "influencer_commerce",
        "beauty_chain",
        "trading_company",
        "unknown",
        "other",
    },
    "sales_channel": {
        "offline",
        "online",
        "marketplace",
        "social_commerce",
        "live_commerce",
        "b2b_platform",
        "distributor_network",
        "mixed",
        "unknown",
        "other",
    },
    "platform": {
        "Xiaohongshu",
        "Douyin",
        "WeChat",
        "Taobao",
        "1688",
        "TikTok",
        "Instagram",
        "Shopee",
        "Lazada",
        "Amazon",
        "Telegram",
        "VK",
        "website",
        "offline",
        "unknown",
        "other",
    },
    "language": {
        "Korean",
        "English",
        "Chinese",
        "Russian",
        "Vietnamese",
        "Thai",
        "Indonesian",
        "Malay",
        "Arabic",
        "Spanish",
        "unknown",
        "other",
    },
    "moq_fit": {"yes", "no", "unknown"},
    "china_relevance": {"high", "medium", "low", "unknown"},
    "payment_risk": {"high", "medium", "low", "unknown"},
    "repeat_purchase_potential": {"high", "medium", "low", "unknown"},
    "lead_status": {
        "new",
        "researching",
        "contacted",
        "replied",
        "qualified",
        "sample_requested",
        "quotation_sent",
        "negotiating",
        "won",
        "lost",
        "on_hold",
        "disqualified",
    },
    "priority": {"high", "medium", "low", "unknown"},
}

VALIDATION_STATUS_VALUES = {"valid", "review_needed", "invalid"}
CONTACT_PRIVACY_VALUES = {"sample_placeholder", "internal_use", "masked", "unknown"}
PROPOSAL_BRAND_CHECK_VALUES = {"clear", "approval_required_review", "unknown"}
MEDICUBE = "\uba54\ub514\ud050\ube0c"


def has_utf8_bom(path):
    return path.read_bytes().startswith(b"\xef\xbb\xbf")


def read_csv(path, label, expected_columns, errors):
    if not path.exists():
        errors.append(f"{label}: file does not exist: {path}")
        return [], ""

    if not has_utf8_bom(path):
        errors.append(f"{label}: UTF-8 BOM is missing")

    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        errors.append(f"{label}: cannot read with utf-8-sig: {exc}")
        return [], ""

    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames != expected_columns:
        errors.append(
            f"{label}: column order mismatch. expected={expected_columns}, actual={reader.fieldnames}"
        )
        return [], text

    rows = list(reader)
    return rows, text


def has_hangul(text):
    return any("\uac00" <= char <= "\ud7a3" for char in text)


def has_cjk(text):
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def split_brands(value):
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def expected_moq_fit(value):
    value = (value or "").strip()
    try:
        qty = int(value)
    except ValueError:
        return "unknown"
    if qty >= 100:
        return "yes"
    if 1 <= qty <= 99:
        return "no"
    return "unknown"


def check_unique_buyer_ids(rows, label, errors):
    seen = set()
    for index, row in enumerate(rows, start=2):
        buyer_id = row.get("buyer_id", "").strip()
        if not buyer_id:
            errors.append(f"{label}: row {index} buyer_id is blank")
            continue
        if buyer_id in seen:
            errors.append(f"{label}: duplicate buyer_id: {buyer_id}")
        seen.add(buyer_id)


def check_required_fields(rows, label, errors):
    for index, row in enumerate(rows, start=2):
        for field in REQUIRED_FIELDS:
            if not row.get(field, "").strip():
                errors.append(f"{label}: row {index} required field is blank: {field}")


def check_allowed_values(rows, label, errors):
    for index, row in enumerate(rows, start=2):
        for field, allowed in ALLOWED_VALUES.items():
            value = row.get(field, "").strip()
            if value not in allowed:
                errors.append(
                    f"{label}: row {index} invalid {field}: {value!r}. allowed={sorted(allowed)}"
                )


def check_qty_and_moq(rows, label, errors):
    for index, row in enumerate(rows, start=2):
        qty = row.get("estimated_order_qty", "").strip()
        if qty and not qty.isdigit():
            errors.append(f"{label}: row {index} estimated_order_qty must be numeric or blank: {qty!r}")
        expected = expected_moq_fit(qty)
        actual = row.get("moq_fit", "").strip()
        if actual != expected:
            errors.append(
                f"{label}: row {index} MOQ mismatch. estimated_order_qty={qty!r}, "
                f"expected moq_fit={expected}, actual={actual}"
            )


def check_language_preserved(text, label, errors):
    if not has_hangul(text):
        errors.append(f"{label}: Korean text was not detected")
    if not has_cjk(text):
        errors.append(f"{label}: Chinese/CJK text was not detected")


def check_placeholder_contacts(rows, label, errors):
    for index, row in enumerate(rows, start=2):
        email = row.get("contact_email", "").strip()
        phone = row.get("contact_phone", "").strip()
        wechat_id = row.get("wechat_id", "").strip()
        whatsapp = row.get("whatsapp", "").strip()
        website = row.get("website", "").strip()
        sns_url = row.get("sns_url", "").strip()
        contact_name = row.get("contact_name", "").strip()

        if email and not email.endswith("@example.invalid"):
            errors.append(f"{label}: row {index} sample email must use example.invalid")
        if phone and phone != "+00-0000-0000":
            errors.append(f"{label}: row {index} sample phone must use +00-0000-0000")
        if whatsapp and whatsapp != "+00-0000-0000":
            errors.append(f"{label}: row {index} sample WhatsApp must use +00-0000-0000")
        if wechat_id and "placeholder" not in wechat_id:
            errors.append(f"{label}: row {index} sample WeChat ID must include placeholder")
        if contact_name and not contact_name.startswith("Sample Contact"):
            errors.append(f"{label}: row {index} sample contact_name must be fictional")
        if website and "example.invalid" not in website:
            errors.append(f"{label}: row {index} sample website must use example.invalid")
        if sns_url and "example.invalid" not in sns_url:
            errors.append(f"{label}: row {index} sample sns_url must use example.invalid")


def load_restricted_brands(path):
    restricted = {MEDICUBE}
    if not path.exists():
        return restricted

    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return restricted

    reader = csv.DictReader(text.splitlines())
    for row in reader:
        brand = (row.get("brand_ko") or "").strip()
        approval_required = (row.get("approval_required") or "").strip().lower() == "true"
        proposal_allowed = (row.get("proposal_allowed") or "").strip().lower()
        if brand and (approval_required or proposal_allowed == "false"):
            restricted.add(brand)
    return restricted


def check_raw(rows, text, errors):
    check_unique_buyer_ids(rows, "raw", errors)
    check_required_fields(rows, "raw", errors)
    check_language_preserved(text, "raw", errors)
    check_placeholder_contacts(rows, "raw", errors)
    check_allowed_values(rows, "raw", errors)
    check_qty_and_moq(rows, "raw", errors)


def check_master(raw_rows, master_rows, text, restricted_brands, errors):
    if len(master_rows) != len(raw_rows):
        errors.append(f"master: row count mismatch. raw={len(raw_rows)}, master={len(master_rows)}")

    raw_ids = [row.get("buyer_id", "") for row in raw_rows]
    master_ids = [row.get("buyer_id", "") for row in master_rows]
    if master_ids != raw_ids:
        errors.append(f"master: buyer_id order mismatch. raw={raw_ids}, master={master_ids}")

    check_unique_buyer_ids(master_rows, "master", errors)
    check_required_fields(master_rows, "master", errors)
    check_language_preserved(text, "master", errors)
    check_placeholder_contacts(master_rows, "master", errors)
    check_allowed_values(master_rows, "master", errors)
    check_qty_and_moq(master_rows, "master", errors)

    for index, row in enumerate(master_rows, start=2):
        validation_status = row.get("validation_status", "").strip()
        contact_privacy_level = row.get("contact_privacy_level", "").strip()
        proposal_brand_check = row.get("proposal_brand_check", "").strip()
        approval_warning = row.get("approval_warning", "").strip()
        recommended_follow_up = row.get("recommended_follow_up", "").strip()
        interested_brands = split_brands(row.get("interested_brands", ""))
        matched_restricted = [brand for brand in interested_brands if brand in restricted_brands]

        if validation_status not in VALIDATION_STATUS_VALUES:
            errors.append(f"master: row {index} invalid validation_status: {validation_status!r}")
        if contact_privacy_level not in CONTACT_PRIVACY_VALUES:
            errors.append(
                f"master: row {index} invalid contact_privacy_level: {contact_privacy_level!r}"
            )
        if proposal_brand_check not in PROPOSAL_BRAND_CHECK_VALUES:
            errors.append(
                f"master: row {index} invalid proposal_brand_check: {proposal_brand_check!r}"
            )
        if not recommended_follow_up:
            errors.append(f"master: row {index} recommended_follow_up is blank")

        if MEDICUBE in interested_brands:
            if not approval_warning:
                errors.append(f"master: row {index} Medicube approval_warning is blank")
            if proposal_brand_check != "approval_required_review":
                errors.append(
                    f"master: row {index} Medicube row must have proposal_brand_check=approval_required_review"
                )
            if validation_status != "review_needed":
                errors.append(
                    f"master: row {index} Medicube row must have validation_status=review_needed"
                )

        if matched_restricted:
            if not approval_warning:
                errors.append(
                    f"master: row {index} restricted brand warning missing: {matched_restricted}"
                )
            if proposal_brand_check != "approval_required_review":
                errors.append(
                    f"master: row {index} restricted brand must have approval_required_review: "
                    f"{matched_restricted}"
                )
        else:
            if proposal_brand_check != "clear":
                errors.append(
                    f"master: row {index} unrestricted brands should have proposal_brand_check=clear"
                )


def parse_args():
    parser = argparse.ArgumentParser(description="Validate buyer lead raw and master CSV files.")
    parser.add_argument("--raw", required=True, help="Path to raw buyer lead CSV")
    parser.add_argument("--master", required=True, help="Path to master buyer lead CSV")
    parser.add_argument(
        "--brands",
        default="data/brands_master.csv",
        help="Path to brand master CSV for approval-required brand checks",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    errors = []

    raw_path = Path(args.raw)
    master_path = Path(args.master)
    brands_path = Path(args.brands)

    raw_rows, raw_text = read_csv(raw_path, "raw", RAW_COLUMNS, errors)
    master_rows, master_text = read_csv(master_path, "master", MASTER_COLUMNS, errors)
    restricted_brands = load_restricted_brands(brands_path)

    if raw_rows:
        check_raw(raw_rows, raw_text, errors)
    if raw_rows and master_rows:
        check_master(raw_rows, master_rows, master_text, restricted_brands, errors)

    if errors:
        print("FAIL: buyer lead validation failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS: buyer lead validation passed")
    print(f"- raw: {raw_path}")
    print(f"- master: {master_path}")
    print(f"- rows: {len(raw_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
