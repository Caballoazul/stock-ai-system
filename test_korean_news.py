"""No-network checks for Korean article report integration."""
import os
import unittest
from unittest.mock import patch
from news_ai_briefing import enrich_news
from insight_report import compose

SAMPLE = {"title":"Example English headline", "link":"https://news.google.com/rss/articles/example",
          "source":"Example", "published":"10-19 10:00 KST"}

class KoreanNewsTests(unittest.TestCase):
    @patch("news_ai_briefing.extract_article", return_value=None)
    def test_unverified_news_is_not_invented(self, mock_extract):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            news = enrich_news([SAMPLE])
        self.assertNotIn("analysis", news[0])
        _, detail, _ = compose("morning", {}, news, None)
        self.assertIn("본문 미확인: 번역·요약·기업 영향 분석 보류", detail)

    def test_verified_analysis_is_displayed(self):
        sample = dict(SAMPLE, analysis={
            "headline_ko":"한국어 기사 제목", "summary_ko":"기사 근거 요약",
            "facts":["근거 1", "근거 2"], "samsung_impact":"조건부 영향",
            "hynix_impact":"확인 불가", "uncertainty":"원문 대조 필요"})
        _, detail, telegram = compose("morning", {}, [sample], None)
        self.assertIn("한국어 기사 제목", detail)
        self.assertIn("삼성전자 영향: 조건부 영향", detail)
        self.assertIn("SK하이닉스 영향: 확인 불가", detail)
        self.assertIn("한국어 기사 제목", telegram)

if __name__ == "__main__":
    unittest.main()
