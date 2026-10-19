"""Validate selected Open DART reported financial accounts without changing raw data.

This module checks internal API consistency, not independent filing authenticity.
"""

from __future__ import annotations

from typing import Any

ACCOUNT_IDS = {
    "revenue": "ifrs-full_Revenue",
    "operating_income": "dart_OperatingIncomeLoss",
    "net_income": "ifrs-full_ProfitLoss",
}
PERMITTED_STATEMENTS = {"IS", "CIS"}


def _parse_amount(value: Any) -> int | None:
    if value is None or value == "" or value == "-":
        return None
    if isinstance(value, bool):
        raise ValueError("BooleanAmount")
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        raise ValueError("InvalidAmountType")
    cleaned = value.replace(",", "").strip()
    if not cleaned or cleaned in {"-", "+"}:
        return None
    if cleaned.lstrip("+-").isdigit():
        return int(cleaned)
    raise ValueError("InvalidAmount")


def _extract(rows: list[dict], account_id: str, field: str) -> dict:
    matches = [r for r in rows if r.get("account_id") == account_id
               and r.get("sj_div") in PERMITTED_STATEMENTS]
    if not matches:
        return {"status": "missing", "value": None, "statements": []}
    values = set()
    statements = sorted({str(r.get("sj_div")) for r in matches})
    try:
        for row in matches:
            currency = row.get("currency")
            if currency != "KRW":
                return {"status": "invalid_currency", "value": None,
                        "statements": statements}
            value = _parse_amount(row.get(field))
            if value is not None:
                values.add(value)
    except ValueError as exc:
        return {"status": "invalid_amount", "value": None,
                "statements": statements, "error": str(exc)}
    if not values:
        return {"status": "missing", "value": None, "statements": statements}
    if len(values) > 1:
        return {"status": "conflict", "value": None, "statements": statements}
    return {"status": "ok", "value": values.pop(), "statements": statements}


def validate_half_year(q1: dict, half: dict) -> dict:
    """Compare Q1 and half-year CFS raw collections for the same company/year.

    Only confirms arithmetic consistency of DART API values. It does not
    establish that the filing text was independently checked.
    """
    result = {"status": "error", "period_verified": False,
              "source_verified": False, "checks": {}, "errors": [],
              "corp_code": half.get("corp_code") if isinstance(half, dict) else None,
              "year": half.get("year") if isinstance(half, dict) else None}
    if not isinstance(q1, dict) or not isinstance(half, dict):
        result["errors"].append("InvalidPayload")
        return result
    if q1.get("status") != "ok" or half.get("status") != "ok":
        result["errors"].append("CollectorNotOK")
        return result
    if (q1.get("corp_code") != half.get("corp_code") or
        str(q1.get("year")) != str(half.get("year")) or
        q1.get("report_code") != "11013" or half.get("report_code") != "11012" or
        q1.get("fs_div") != "CFS" or half.get("fs_div") != "CFS"):
        result["errors"].append("MetadataMismatch")
        return result
    q1_rows, half_rows = q1.get("accounts"), half.get("accounts")
    if not isinstance(q1_rows, list) or not isinstance(half_rows, list):
        result["errors"].append("InvalidAccounts")
        return result
    for label, account_id in ACCOUNT_IDS.items():
        first = _extract(q1_rows, account_id, "thstrm_amount")
        cumulative = _extract(half_rows, account_id, "thstrm_add_amount")
        quarter = _extract(half_rows, account_id, "thstrm_amount")
        valid = all(item["status"] == "ok" for item in (first, cumulative, quarter))
        calculated = cumulative["value"] - first["value"] if valid else None
        matched = bool(valid and calculated == quarter["value"])
        result["checks"][label] = {
            "account_id": account_id, "q1_krw": first["value"],
            "half_cumulative_krw": cumulative["value"],
            "q2_reported_krw": quarter["value"],
            "q2_calculated_krw": calculated,
            "arithmetic_match": matched,
            "field_statuses": {"q1": first["status"],
                               "half_cumulative": cumulative["status"],
                               "q2_reported": quarter["status"]},
        }
        if not matched:
            result["errors"].append(f"{label}:ValidationFailed")
    result["status"] = "ok" if not result["errors"] else "failed"
    result["period_verified"] = result["status"] == "ok"
    return result
