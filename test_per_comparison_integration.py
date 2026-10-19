"""Offline regression checks for the three-company valuation integration."""
import unittest
from per_comparison import render_per_comparison
from valuation_collector import normalize, SYMBOLS

class PerComparisonTests(unittest.TestCase):
    def test_all_three_companies_configured(self):
        self.assertEqual(SYMBOLS, {'Micron':'MU', 'Samsung':'005930.KS', 'SK Hynix':'000660.KS'})

    def test_usd_micron_and_krw_samsung(self):
        micron = normalize({'currency':'USD','trailingPE':12.5}, 'Micron','MU',
                           collected_at='2026-10-19T10:00:00+09:00')
        samsung = normalize({'currency':'KRW','trailingPE':9.5}, 'Samsung','005930.KS',
                            collected_at='2026-10-19T10:00:00+09:00')
        self.assertEqual(micron['trailing_pe'],12.5)
        self.assertEqual(samsung['trailing_pe'],9.5)
        self.assertFalse(micron['period_verified'])
        self.assertEqual(normalize({'currency':'KRW'},'Micron','MU')['status'],'error')

    def test_report_missing_data_is_explicit(self):
        result = render_per_comparison({'Micron':{'trailing_pe':12.5,'status':'partial'}})
        self.assertIn('마이크론 | 12.50배 | 미확인',result)
        self.assertIn('삼성전자 | 미확인 | 미확인',result)
        self.assertIn('SK하이닉스 | 미확인 | 미확인',result)
        self.assertIn('독립 검증되지',result)

if __name__ == '__main__':
    unittest.main()
