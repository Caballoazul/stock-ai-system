"""Unit tests for direct publisher URL preference; no network."""
import unittest
from unittest.mock import patch
from market_intelligence import fetch_news

class DirectNewsTests(unittest.TestCase):
    @patch("market_intelligence.fetch_direct_news")
    def test_direct_urls_are_preferred(self, direct):
        expected = [{"title": "Micron earnings", "link": "https://publisher.example/article",
                     "source": "publisher.example", "published": "10-19 10:00 KST"}]
        direct.return_value = (expected, None)
        self.assertEqual(fetch_news()[0], expected)

    @patch("market_intelligence.requests.get")
    def test_invalid_direct_source_falls_back_to_rss(self, get):
        with patch("market_intelligence.fetch_direct_news", return_value=([], "http_error")):
            get.return_value.content = b"<rss><channel></channel></rss>"
            get.return_value.raise_for_status.return_value = None
            result, error = fetch_news()
        self.assertEqual(result, [])
        self.assertIsNone(error)

if __name__ == "__main__":
    unittest.main()
