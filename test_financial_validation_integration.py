import copy
import json
import tempfile
import unittest
from pathlib import Path
from financial_validation_integration import merge_financial_validation, build_preview

MARKET = {'schema_version': 1, 'generated_at_kst': '2026-10-18T23:38:10+09:00', 'market': {'Micron': {'price': 123}}, 'news_headlines_unverified': [{'title': 'sample'}], 'valuation': {'Samsung': {'pe': None}}, 'limitations': ['original']}
FIXTURE = {'financial_validation': {'schema_version': '1.0', 'company': {'corp_code': '00164779', 'year': 2026, 'report_code': '11012', 'fs_div': 'CFS'}, 'source_review': {'status': 'matched', 'source_verified': True, 'matched_count': 6, 'expected_count': 6, 'mismatches': [], 'errors': []}, 'earnings_quality_review': {'status': 'review_required', 'flags': []}, 'limitations': {'filing_authenticity_automatically_verified': False}}}

class IntegrationTests(unittest.TestCase):
    def test_preserves_market_and_news(self):
        m = copy.deepcopy(MARKET)
        f = copy.deepcopy(FIXTURE)
        out = merge_financial_validation(m, f)
        for key in MARKET:
            self.assertEqual(out[key], MARKET[key])
        self.assertEqual(m, MARKET)
        self.assertEqual(f, FIXTURE)
    def test_historical_not_current(self):
        fv = merge_financial_validation(MARKET, FIXTURE)['financial_validation']
        self.assertEqual(fv['data_role'], 'historical_reference')
        self.assertIs(fv['current_period_verified'], False)
        self.assertEqual(fv['source_review']['source_verified_scope'], 'supplied_manual_evidence_record_only')
    def test_reject_mismatch(self):
        f = copy.deepcopy(FIXTURE)
        f['financial_validation']['source_review']['status'] = 'mismatched'
        with self.assertRaises(ValueError):
            merge_financial_validation(MARKET, f)
    def test_reject_wrong_company(self):
        f = copy.deepcopy(FIXTURE)
        f['financial_validation']['company']['corp_code'] = '00126380'
        with self.assertRaises(ValueError):
            merge_financial_validation(MARKET, f)
    def test_reject_existing(self):
        m = copy.deepcopy(MARKET)
        m['financial_validation'] = {}
        with self.assertRaises(ValueError):
            merge_financial_validation(m, FIXTURE)
    def test_preview_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            market, fixture, output = p/'market.json', p/'fixture.json', p/'preview.json'
            market.write_text(json.dumps(MARKET))
            fixture.write_text(json.dumps(FIXTURE))
            expected = build_preview(market, fixture, output)
            self.assertEqual(json.loads(output.read_text()), expected)
            self.assertEqual(json.loads(market.read_text()), MARKET)
    def test_refuse_production_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            with self.assertRaises(ValueError):
                build_preview(p/'source.json', p/'fixture.json', p/'market_analysis.json')

if __name__ == '__main__':
    unittest.main()
