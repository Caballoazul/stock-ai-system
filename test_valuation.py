import unittest
import sys
import types
try:
    import yfinance
except ImportError:
    sys.modules["yfinance"] = types.SimpleNamespace(Ticker=lambda symbol: None)

from unittest.mock import patch
from valuation_collector import normalize, collect_valuations, finite_number


class ValuationTests(unittest.TestCase):
    def test_valid_data(self):
        info = dict(currency='KRW', trailingPE=12.5, forwardPE=10.1,
                    trailingEps=1000, forwardEps=1200, returnOnEquity=.15,
                    revenueGrowth=-.05, earningsGrowth=.20, marketCap=123456789)
        row = normalize(info, 'Samsung', '005930.KS')
        self.assertEqual(row['status'], 'ok')
        self.assertEqual(row['revenue_growth'], -.05)
        self.assertEqual(row['market_cap'], 123456789)
        self.assertFalse(row['period_verified'])

    def test_missing_and_invalid(self):
        row = normalize({'currency': 'KRW', 'trailingPE': 0, 'forwardPE': float('nan')}, 'Samsung', '005930.KS')
        self.assertEqual(row['status'], 'unavailable')
        self.assertIsNone(row['trailing_pe'])
        self.assertIsNone(row['forward_pe'])
        self.assertIsNone(finite_number(float('inf')))

    def test_currency(self):
        row = normalize({'currency': 'USD', 'trailingPE': 10}, 'Samsung', '005930.KS')
        self.assertEqual(row['status'], 'error')
        self.assertIsNone(row['trailing_pe'])

    def test_partial(self):
        row = normalize({'currency': 'KRW', 'trailingEps': -100}, 'Samsung', '005930.KS')
        self.assertEqual(row['status'], 'partial')
        self.assertEqual(row['trailing_eps'], -100)

    @patch('valuation_collector.yf.Ticker')
    def test_api_failure_is_isolated(self, ticker):
        ticker.side_effect = RuntimeError('offline')
        result = collect_valuations()
        self.assertEqual(set(result), {'Micron', 'Samsung', 'SK Hynix'})
        self.assertTrue(all(v['status'] == 'error' for v in result.values()))
        self.assertTrue(all(v['error'] == 'RuntimeError' for v in result.values()))


if __name__ == '__main__':
    unittest.main()
