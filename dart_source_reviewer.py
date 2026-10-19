"""Review manually documented DART filing comparisons; no network access.

A positive result attests only to the supplied evidence record, not independent
verification of a DART filing by this module.
"""
from __future__ import annotations

from typing import Any

METRICS = ("revenue", "operating_income", "net_income")
PERIODS = ("q2", "half")


def _integer(value: Any) -> bool:
    return type(value) is int


def compare_filing_values(api_result: dict, evidence: dict) -> dict:
    """Compare six KRW values against a manually documented filing record.

    api_result is the output of validate_half_year(). evidence requires:
    corp_code, year, report_code='11012', fs_div='CFS', unit='KRW',
    filing_receipt_no, verification_method='manual_filing_comparison',
    verified_by, checked_at, and source_values[metric][period].
    """
    result = {
        "status": "unverified", "source_verified": False,
        "verification_method": None, "filing_receipt_no": None,
        "matched_count": 0, "expected_count": 6, "mismatches": [],
        "errors": [],
    }
    if not isinstance(api_result, dict) or not isinstance(evidence, dict):
        result["status"] = "invalid_metadata"
        result["errors"].append("InvalidPayload")
        return result
    if api_result.get("status") != "ok" or not api_result.get("period_verified"):
        result["errors"].append("APIValidationNotOK")
        return result

    expected = {
        "corp_code": api_result.get("corp_code"),
        "year": api_result.get("year"),
        "report_code": "11012", "fs_div": "CFS", "unit": "KRW",
    }
    for key, value in expected.items():
        actual = evidence.get(key)
        if (str(actual) != str(value) if key == "year" else actual != value):
            result["errors"].append(f"MetadataMismatch:{key}")
    if result["errors"]:
        result["status"] = "invalid_metadata"
        return result

    receipt = evidence.get("filing_receipt_no")
    if not isinstance(receipt, str) or len(receipt) != 14 or not receipt.isascii() or not receipt.isdigit():
        result["status"] = "invalid_metadata"
        result["errors"].append("InvalidReceiptNo")
        return result
    result["filing_receipt_no"] = receipt

    if (evidence.get("verification_method") != "manual_filing_comparison"
            or not isinstance(evidence.get("verified_by"), str)
            or not evidence["verified_by"].strip()
            or not isinstance(evidence.get("checked_at"), str)
            or not evidence["checked_at"].strip()):
        result["errors"].append("MissingVerificationEvidence")
        return result
    result["verification_method"] = "manual_filing_comparison"

    values = evidence.get("source_values")
    checks = api_result.get("checks")
    if not isinstance(values, dict) or not isinstance(checks, dict):
        result["status"] = "incomplete"
        result["errors"].append("MissingValuesOrChecks")
        return result

    missing = []
    for metric in METRICS:
        source_metric = values.get(metric)
        api_metric = checks.get(metric)
        if not isinstance(source_metric, dict) or not isinstance(api_metric, dict):
            missing.append(metric)
            continue
        for period, api_field in (("q2", "q2_reported_krw"),
                                  ("half", "half_cumulative_krw")):
            actual = source_metric.get(period)
            reference = api_metric.get(api_field)
            if not _integer(actual) or not _integer(reference):
                missing.append(f"{metric}.{period}")
            elif actual == reference:
                result["matched_count"] += 1
            else:
                result["mismatches"].append({
                    "field": f"{metric}.{period}",
                    "api_krw": reference, "filing_krw": actual,
                })
    if missing:
        result["status"] = "incomplete"
        result["errors"].extend(f"MissingOrInvalid:{field}" for field in missing)
    elif result["mismatches"]:
        result["status"] = "mismatched"
    else:
        result["status"] = "matched"
        result["source_verified"] = True
    return result


def review_earnings_quality(
    operating_income_krw: int | None,
    net_income_krw: int | None,
    valuation_gain_krw: int | None = None,
    *,
    materiality_ratio: float = 0.2,
) -> dict:
    """Flag material valuation gains, not assert whether earnings are repeatable."""
    result = {"status": "not_evaluated", "flags": [], "metrics": {}}
    if (not _integer(operating_income_krw) or not _integer(net_income_krw)
            or operating_income_krw <= 0 or not _integer(valuation_gain_krw)
            or not isinstance(materiality_ratio, (int, float))
            or isinstance(materiality_ratio, bool)
            or not 0 < materiality_ratio < 1):
        return result
    ratio = valuation_gain_krw / operating_income_krw
    result["metrics"] = {"valuation_gain_to_operating_income": round(ratio, 4)}
    if ratio >= materiality_ratio:
        result["status"] = "review_required"
        result["flags"].append("MaterialFinancialInstrumentValuationGain")
    else:
        result["status"] = "no_threshold_flag"
    if net_income_krw > operating_income_krw:
        result["flags"].append("NetIncomeExceedsOperatingIncome")
        result["status"] = "review_required"
    return result


def build_review_result(api_result: dict, evidence: dict,
                        valuation_gain_krw: int | None = None) -> dict:
    source = compare_filing_values(api_result, evidence)
    checks = api_result.get("checks", {}) if isinstance(api_result, dict) else {}
    op = checks.get("operating_income", {}) if isinstance(checks, dict) else {}
    net = checks.get("net_income", {}) if isinstance(checks, dict) else {}
    earnings = review_earnings_quality(
        op.get("half_cumulative_krw") if isinstance(op, dict) else None,
        net.get("half_cumulative_krw") if isinstance(net, dict) else None,
        valuation_gain_krw,
    )
    return {"source_review": source, "earnings_quality_review": earnings}
