"""Offline deterministic ranking test. Does not send messages or call APIs."""
import unittest
from unittest.mock import patch
from market_intelligence import market_news_score, rank_market_news, fetch_news, fetch_session_market_news

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

    @patch("market_intelligence.requests.get")
    @patch("market_intelligence.fetch_direct_news")
    @patch("market_intelligence.fetch_publisher_rss")
    def test_market_focused_fallback_adds_relevant_headline(self, rss, gdelt, get):
        from unittest.mock import Mock
        rss.return_value = []
        gdelt.return_value = ([], "HTTP_429")
        general = b"<rss><channel></channel></rss>"
        focused = b"""<rss><channel><item>
        <title>Micron shares fall as chip stocks decline</title>
        <link>https://news.google.com/rss/articles/move</link>
        <pubDate>Mon, 19 Oct 2026 07:00:00 GMT</pubDate>
        </item></channel></rss>"""
        get.side_effect = [Mock(content=general), Mock(content=focused)]
        items, _ = fetch_news(limit=2, market={"Micron": {"change": -5.0}})
        self.assertEqual(len(items), 1)
        self.assertIn("Micron shares fall", items[0]["title"])
        self.assertTrue(items[0]["link"].startswith("https://news.google.com/"))
        self.assertEqual(get.call_count, 2)

    @patch("market_intelligence.requests.get")
    def test_session_news_uses_us_close_date_and_excludes_later_news(self, get):
        from unittest.mock import Mock
        xml = b"""<rss><channel>
        <item><title>Micron shares fall on memory outlook</title>
        <link>https://news.google.com/rss/articles/session</link>
        <pubDate>Fri, 16 Oct 2026 20:30:00 GMT</pubDate></item>
        <item><title>Micron shares fall on later news</title>
        <link>https://news.google.com/rss/articles/later</link>
        <pubDate>Mon, 19 Oct 2026 07:00:00 GMT</pubDate></item>
        </channel></rss>"""
        get.return_value = Mock(content=xml)
        market = {"SOX": {"date": "2026-10-16", "change": -3.8},
                  "Micron": {"date": "2026-10-16", "change": -5.6}}
        items = fetch_session_market_news(market)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["session_date"], "2026-10-16")
        self.assertIn("after%3A2026-10-16", get.call_args.args[0])
        self.assertIn("before%3A2026-10-18", get.call_args.args[0])

    @patch("market_intelligence.fetch_session_market_news")
    @patch("market_intelligence.requests.get")
    @patch("market_intelligence.fetch_direct_news")
    @patch("market_intelligence.fetch_publisher_rss")
    def test_session_news_reserved_even_when_industry_news_is_full(self, rss, gdelt, get, session):
        from unittest.mock import Mock
        rss.return_value = [
            {"title": "Samsung HBM supply " + str(i),
             "link": "https://publisher.example/" + str(i),
             "source": "Publisher", "published": "10-19 09:00 KST"}
            for i in range(6)]
        gdelt.return_value = ([], "HTTP_429")
        session.return_value = [
            {"title": "Micron shares fall on memory outlook",
             "link": "https://news.google.com/rss/articles/session",
             "source": "News", "published": "10-17 05:30 KST",
             "session_date": "2026-10-16"}]
        get.return_value = Mock(content=b"<rss><channel></channel></rss>")
        items, _ = fetch_news(limit=6, market={"SOX": {"date": "2026-10-16"}})
        self.assertTrue(any(x.get("session_date") == "2026-10-16" for x in items))
        self.assertEqual(len(items), 6)

    def test_no_causality_claim(self):
        item = {"title": "Micron stock falls amid demand concerns"}
        score = market_news_score(item, {"Micron": {"change": -5.63}})
        self.assertIsInstance(score, int)
        self.assertNotIn("cause", item)

if __name__ == "__main__":
    unittest.main(verbosity=2)
