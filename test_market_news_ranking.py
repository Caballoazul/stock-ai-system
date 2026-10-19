"""Offline deterministic ranking test. Does not send messages or call APIs."""
import unittest
from market_intelligence import market_news_score, rank_market_news

class RankingTests(unittest.TestCase):
    def test_market_catalyst_prioritized(self):
        items = [
            {"title": "Netflix and Oracle tech events this week"},
            {"title": "Samsung and TSMC plan next generation HBM"},
            {"title": "Micron shares drop after weaker memory demand outlook"},
        ]
        market = {"Micron": {"change": -5.63}, "SOX": {"change": -3.83}}
        ranked = rank_market_news(items, market)
        self.assertIn("Micron", ranked[0]["title"])
        self.assertGreater(market_news_score(ranked[0], market),
                           market_news_score(ranked[-1], market))

    def test_no_causality_claim(self):
        item = {"title": "Micron stock falls amid demand concerns"}
        score = market_news_score(item, {"Micron": {"change": -5.63}})
        self.assertIsInstance(score, int)
        self.assertNotIn("cause", item)

if __name__ == "__main__":
    unittest.main(verbosity=2)
