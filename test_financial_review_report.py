import copy
import unittest
from financial_review_report import format_financial_review

FV = {
    'financial_validation': {
        'data_role': 'historical_reference', 'current_period_verified': False,
        'company': {'corp_code': '00164779', 'year': 2026, 'report_code': '11012', 'fs_div': 'CFS'},
        'source_review': {'status': 'matched', 'matched_count': 6, 'expected_count': 6,
                          'mismatches': [], 'errors': [],
                          'source_verified_scope': 'supplied_manual_evidence_record_only'},
        'earnings_quality_review': {'flags': ['MaterialFinancialInstrumentValuationGain', 'NetIncomeExceedsOperatingIncome'],
                                    'metrics': {'valuation_gain_to_operating_income': 0.6437}},
    }
}

class FinancialReviewReportTests(unittest.TestCase):
    def test_renders_historical_scope(self):
        text = format_financial_review(FV)
        self.assertIn('과거 실적', text)
        self.assertIn('6개 항목 일치', text)
        self.assertIn('64.37%', text)
        self.assertIn('매수·매도 의견', text)
    def test_missing_section(self):
        with self.assertRaises(ValueError):
            format_financial_review({})
    def test_current_period_claim_rejected(self):
        d = copy.deepcopy(FV)
        d['financial_validation']['current_period_verified'] = True
        with self.assertRaises(ValueError):
            format_financial_review(d)
    def test_company_mismatch_rejected(self):
        d = copy.deepcopy(FV)
        d['financial_validation']['company']['corp_code'] = '00126380'
        with self.assertRaises(ValueError):
            format_financial_review(d)
    def test_unmatched_rejected(self):
        d = copy.deepcopy(FV)
        d['financial_validation']['source_review']['matched_count'] = 5
        with self.assertRaises(ValueError):
            format_financial_review(d)
    def test_input_not_mutated(self):
        d = copy.deepcopy(FV)
        format_financial_review(d)
        self.assertEqual(d, FV)
    def test_unknown_flag_is_not_ignored(self):
        d = copy.deepcopy(FV)
        d['financial_validation']['earnings_quality_review']['flags'] = ['NewReviewFlag']
        self.assertIn('NewReviewFlag', format_financial_review(d))

if __name__ == '__main__':
    unittest.main()
