"""Offline deterministic ranking test. Does not send messages or call APIs."""
import unittest
from unittest.mock import patch
from market_intelligence import market_news_score, rank_market_news, fetch_news

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

    @patch("market_intelligence.fetch_direct_news")
    @patch("market_intelligence.fetch_publisher_rss")
    def test_sources_merge_even_when_publisher_has_article(self, rss, gdelt):
        rss.return_value = [{"title": "Samsung HBM supply outlook",
                             "link": "https://publisher.example/a", "source": "Publisher",
                             "published": "10-19 09:00 KST"}]
        gdelt.return_value = ([{"title": "Micron shares fall on memory demand",
                                "link": "https://gdelt.example/b", "source": "GDELT",
                                "published": "10-19 08:00 KST"}], None)
        items, error = fetch_news(limit=2, market={"Micron": {"change": -5}})
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual({x["source"] for x in items}, {"Publisher", "GDELT"})

    @patch("market_intelligence.requests.get")
    @patch("market_intelligence.fetch_direct_news")
    @patch("market_intelligence.fetch_publisher_rss")
    def test_direct_link_outranks_google_landing(self, rss, gdelt, get):
        rss.return_value = [{"title": "Samsung HBM supply outlook",
                             "link": "https://publisher.example/a", "source": "Publisher",
                             "published": "10-19 09:00 KST"}]
        gdelt.return_value = ([], "HTTP_429")
        from unittest.mock import Mock
        get.return_value = Mock(content=b"""<rss><channel><item>
        <title>Micron shares fall on memory demand outlook</title>
        <link>https://news.google.com/rss/articles/abc</link>
        <pubDate>Mon, 19 Oct 2026 07:00:00 GMT</pubDate>
        </item></channel></rss>""")
        items, _ = fetch_news(limit=2, market={"Micron": {"change": -5}})
        self.assertEqual(items[0]["source"], "Publisher")
        self.assertEqual(len(items), 2)

    def test_no_causality_claim(self):
        item = {"title": "Micron stock falls amid demand concerns"}
        score = market_news_score(item, {"Micron": {"change": -5.63}})
        self.assertIsInstance(score, int)
        self.assertNotIn("cause", item)

if __name__ == "__main__":
    unittest.main(verbosity=2)
