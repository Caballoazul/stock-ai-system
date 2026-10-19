import copy
import json
import tempfile
import unittest
from pathlib import Path
from financial_daily_appendix import append_daily_financial_review

FIXTURE = {
    'financial_validation': {
        'schema_version': '1.0',
        'company': {'corp_code':'00164779','year':2026,'report_code':'11012','fs_div':'CFS'},
        'source_review': {'status':'matched','matched_count':6,'expected_count':6,'mismatches':[],'errors':[]},
        'earnings_quality_review': {'flags':['MaterialFinancialInstrumentValuationGain'],
                                    'metrics':{'valuation_gain_to_operating_income':0.6437}},
        'limitations': {}
    }
}

class DailyAppendixTests(unittest.TestCase):
    def test_default_off(self):
        self.assertEqual(append_daily_financial_review('report'), 'report')
    def test_off_ignores_missing_file(self):
        self.assertEqual(append_daily_financial_review('report', False, '/absent'), 'report')
    def test_on_renders_historical(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'fixture.json'
            p.write_text(json.dumps(FIXTURE), encoding='utf-8')
            text = append_daily_financial_review('report', True, p)
            self.assertIn('과거 공시', text)
            self.assertIn('현재 분기 검증 완료 아님', text)
            self.assertIn('64.37%', text)
    def test_on_missing_file_preserves_original(self):
        self.assertEqual(append_daily_financial_review('report', True, '/absent'), 'report')
    def test_on_invalid_json_preserves_original(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.json'; p.write_text('{bad', encoding='utf-8')
            self.assertEqual(append_daily_financial_review('report', True, p), 'report')
    def test_wrong_company_preserves_original(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'fixture.json'
            bad = copy.deepcopy(FIXTURE)
            bad['financial_validation']['company']['corp_code'] = 'bad'
            p.write_text(json.dumps(bad), encoding='utf-8')
            self.assertEqual(append_daily_financial_review('report', True, p), 'report')
    def test_wrong_type_rejected(self):
        with self.assertRaises(TypeError):
            append_daily_financial_review(None)

if __name__ == '__main__':
    unittest.main()
