"""Offline checks for short, safe Gmail article links."""
import unittest
from gmail_sender import render_report_html

class GmailLinkTests(unittest.TestCase):
    def test_long_rss_url_is_hidden_behind_link(self):
        url = "https://news.google.com/rss/articles/" + "A" * 220
        html = render_report_html("원문: " + url)
        self.assertIn('>원문 보기</a>', html)
        self.assertIn('href="' + url + '"', html)
        self.assertNotIn('원문: ' + url, html)

    def test_html_is_escaped(self):
        html = render_report_html('<script>alert(1)</script>')
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_multiple_links(self):
        html = render_report_html('https://example.com/a\nhttps://example.com/b')
        self.assertEqual(html.count('>원문 보기</a>'), 2)

if __name__ == '__main__':
    unittest.main()
