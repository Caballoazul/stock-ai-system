import copy
import unittest
from dart_source_reviewer import compare_filing_values, review_earnings_quality, build_review_result


class ReviewerTests(unittest.TestCase):
    def setUp(self):
        self.api = {
            "status": "ok", "period_verified": True,
            "corp_code": "00126380", "year": 2026,
            "checks": {
                "revenue": {"q2_reported_krw": 171499470000000, "half_cumulative_krw": 305372914000000},
                "operating_income": {"q2_reported_krw": 89492412000000, "half_cumulative_krw": 146725209000000},
                "net_income": {"q2_reported_krw": 71624461000000, "half_cumulative_krw": 118849733000000},
            },
        }
        self.evidence = {
            "corp_code": "00126380", "year": 2026, "report_code": "11012",
            "fs_div": "CFS", "unit": "KRW", "filing_receipt_no": "20260814003699",
            "verification_method": "manual_filing_comparison", "verified_by": "human_reviewer",
            "checked_at": "2026-10-19", "source_values": {
                "revenue": {"q2": 171499470000000, "half": 305372914000000},
                "operating_income": {"q2": 89492412000000, "half": 146725209000000},
                "net_income": {"q2": 71624461000000, "half": 118849733000000},
            },
        }

    def test_all_match(self):
        result = compare_filing_values(self.api, self.evidence)
        self.assertEqual(result["status"], "matched")
        self.assertTrue(result["source_verified"])
        self.assertEqual(result["matched_count"], 6)

    def test_mismatch(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["source_values"]["revenue"]["q2"] += 1
        result = compare_filing_values(self.api, evidence)
        self.assertEqual(result["status"], "mismatched")
        self.assertFalse(result["source_verified"])

    def test_missing_value(self):
        evidence = copy.deepcopy(self.evidence)
        del evidence["source_values"]["net_income"]["half"]
        self.assertEqual(compare_filing_values(self.api, evidence)["status"], "incomplete")

    def test_wrong_company(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["corp_code"] = "wrong"
        self.assertEqual(compare_filing_values(self.api, evidence)["status"], "invalid_metadata")

    def test_wrong_period(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["year"] = 2025
        self.assertEqual(compare_filing_values(self.api, evidence)["status"], "invalid_metadata")

    def test_wrong_statement(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["fs_div"] = "OFS"
        self.assertEqual(compare_filing_values(self.api, evidence)["status"], "invalid_metadata")

    def test_missing_evidence(self):
        evidence = copy.deepcopy(self.evidence)
        evidence.pop("verified_by")
        self.assertEqual(compare_filing_values(self.api, evidence)["status"], "unverified")

    def test_bad_receipt(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["filing_receipt_no"] = "fake"
        self.assertEqual(compare_filing_values(self.api, evidence)["status"], "invalid_metadata")

    def test_invalid_boolean_amount(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["source_values"]["revenue"]["q2"] = True
        self.assertEqual(compare_filing_values(self.api, evidence)["status"], "incomplete")

    def test_api_not_verified(self):
        api = copy.deepcopy(self.api)
        api["period_verified"] = False
        self.assertEqual(compare_filing_values(api, self.evidence)["status"], "unverified")

    def test_material_gain(self):
        result = review_earnings_quality(98152891000000, 134268502000000, 63178974000000)
        self.assertEqual(result["status"], "review_required")
        self.assertIn("MaterialFinancialInstrumentValuationGain", result["flags"])

    def test_small_gain(self):
        result = review_earnings_quality(1000, 900, 50)
        self.assertEqual(result["status"], "no_threshold_flag")

    def test_missing_gain(self):
        self.assertEqual(review_earnings_quality(1000, 900)["status"], "not_evaluated")

    def test_build(self):
        result = build_review_result(self.api, self.evidence)
        self.assertEqual(result["source_review"]["status"], "matched")
        self.assertEqual(result["earnings_quality_review"]["status"], "not_evaluated")


if __name__ == "__main__":
    unittest.main()
