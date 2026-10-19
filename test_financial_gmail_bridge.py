import json
import tempfile
import unittest
from pathlib import Path
from financial_gmail_bridge import append_historical_financial_review

VALID = {'financial_validation': {
    'data_role':'historical_reference','current_period_verified':False,
    'company':{'corp_code':'00164779','year':2026,'report_code':'11012','fs_div':'CFS'},
    'source_review':{'status':'matched','matched_count':6,'expected_count':6,'mismatches':[],'errors':[],
                     'source_verified_scope':'supplied_manual_evidence_record_only'},
    'earnings_quality_review':{'flags':['MaterialFinancialInstrumentValuationGain'],
                               'metrics':{'valuation_gain_to_operating_income':0.6437}}}}

class BridgeTests(unittest.TestCase):
    def test_absent_path_keeps_report(self):
        self.assertEqual(append_historical_financial_review('original'), 'original')
    def test_missing_file_keeps_report(self):
        self.assertEqual(append_historical_financial_review('original','/does/not/exist.json'),'original')
    def test_valid_preview_adds_appendix(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'preview.json';p.write_text(json.dumps(VALID),encoding='utf-8')
            output=append_historical_financial_review('original',p)
            self.assertTrue(output.startswith('original\n\n'))
            self.assertIn('과거 공시',output)
            self.assertIn('64.37%',output)
    def test_invalid_json_keeps_report(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'preview.json';p.write_text('{bad',encoding='utf-8')
            self.assertEqual(append_historical_financial_review('original',p),'original')
    def test_wrong_period_keeps_report(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'preview.json';data=json.loads(json.dumps(VALID))
            data['financial_validation']['current_period_verified']=True
            p.write_text(json.dumps(data),encoding='utf-8')
            self.assertEqual(append_historical_financial_review('original',p),'original')
    def test_type_rejected(self):
        with self.assertRaises(TypeError):
            append_historical_financial_review(None)

if __name__=='__main__':unittest.main()
