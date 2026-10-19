"""Offline report checks: no external APIs or messages."""
import unittest
from unittest.mock import patch
from news_ai_briefing import enrich_news
from insight_report import compose, news_section

class EvidenceReportTests(unittest.TestCase):
    @patch("news_ai_briefing._analyze")
    @patch("news_ai_briefing.extract_article")
    def test_scan_later_body_without_extra_title_ai(self, extract, analyze):
        items = [{"title": "Article " + str(i), "link": "https://example.com/" + str(i)}
                 for i in range(6)]
        extract.side_effect = [None, None, None, "verified article body", None, None]
        analyze.return_value = {"headline_ko": "확인된 기사"}
        enriched = enrich_news(items, limit=6, scan_for_body=True)
        self.assertEqual(extract.call_count, 6)
        self.assertEqual(analyze.call_count, 4)
        self.assertIn("본문 확보", enriched[3]["verification"])
        self.assertNotIn("analysis", enriched[4])

    def test_news_section_classification(self):
        self.assertEqual(news_section({"title": "Asian chip stocks fall on funding worries"}), "시장 변동 관련")
        self.assertEqual(news_section({"title": "Samsung HBM base die process"}), "산업·기술 동향")

    def test_verified_industry_precedes_unverified_market(self):
        market = {}
        news = [
            {"title": "Micron shares fall", "source": "Google News",
             "published": "10-19 08:00 KST", "link": "https://news.google.com/a",
             "verification": "원문 미확인", "analysis": None},
            {"title": "Samsung HBM base die process", "source": "Publisher",
             "published": "10-19 09:00 KST", "link": "https://publisher.example/a",
             "verification": "기사 본문 확보", "analysis": {
                 "headline_ko": "HBM 기술 기사", "summary_ko": "본문 분석 완료.",
                 "facts": [], "samsung_impact": "확인 불가",
                 "hynix_impact": "확인 불가", "uncertainty": "독립 검증 필요"}},
        ]
        _, _, telegram = compose("morning", market, news, None)
        self.assertLess(telegram.index("HBM 기술 기사"), telegram.index("Micron shares fall"))

    def test_unverified_news_in_reference_section(self):
        news = [
            {"title": "Micron shares fall", "source": "Headline",
             "published": "10-19 08:00 KST", "link": "https://news.google.com/a",
             "verification": "제목 번역만 완료 · 기사 본문 미확인"},
            {"title": "Samsung HBM base die process", "source": "Publisher",
             "published": "10-19 09:00 KST", "link": "https://publisher.example/a",
             "verification": "기사 본문 확보", "analysis": {
                 "headline_ko": "HBM 기술 기사", "summary_ko": "기술 관련 발표가 있었다.",
                 "facts": [], "samsung_impact": "확인 불가",
                 "hynix_impact": "확인 불가", "uncertainty": "독립 검증 필요"}},
        ]
        _, _, telegram = compose("morning", {}, news, None)
        self.assertIn("[참고 뉴스 · 본문 미확인]", telegram)
        self.assertLess(telegram.index("HBM 기술 기사"), telegram.index("Micron shares fall"))
        self.assertIn("기사 속 주가·등락률", telegram)
        self.assertNotIn("https://news.google.com/a", telegram)

    def test_telegram_market_cause_and_topic_deduplication(self):
        news = [
            {"title": "Samsung Micron Hynix TSMC 3nm NVHBM base die",
             "source": "Publisher", "published": "10-19", "link": "https://example.com/1",
             "verification": "기사 본문 확보", "analysis": {
                 "headline_ko": "HBM 기술 동향", "summary_ko": "HBM 기술 소식.",
                 "facts": [], "samsung_impact": "확인 불가",
                 "hynix_impact": "확인 불가", "uncertainty": "추가 검증 필요"}},
            {"title": "NVIDIA TSMC 3nm NVHBM base dies", "source": "Other",
             "published": "10-19", "link": "https://example.com/2",
             "verification": "본문 미확인"},
            {"title": "Micron shares fall on market worries", "source": "Other",
             "published": "10-19", "link": "https://example.com/3",
             "verification": "본문 미확인"},
        ]
        _, _, telegram = compose("morning", {}, news, None)
        self.assertIn("[미국장 변동 원인]", telegram)
        self.assertIn("미국장 하락 원인 미확인", telegram)
        self.assertIn("[국내 영향·비교]", telegram)
        self.assertIn("Micron shares fall", telegram)
        self.assertNotIn("NVIDIA TSMC 3nm NVHBM base dies", telegram)

    def test_evidence_tiers_and_no_causal_assertion(self):
        market = {
            "Micron": {"price": 100, "change": -5.0, "date": "2026-10-16"},
            "SOX": {"price": 1000, "change": -3.0, "date": "2026-10-16"},
        }
        news = [{
            "title": "Memory supply update", "source": "Example Publisher",
            "published": "10-19 08:00 KST", "link": "https://example.com/news",
            "verification": "기사 본문 확보·AI 요약 (원문 대조 권장)",
            "analysis": {
                "headline_ko": "메모리 공급 업데이트", "summary_ko": "요약",
                "facts": ["공급 관련 발표가 있었다."],
                "samsung_impact": "확인 불가", "hynix_impact": "확인 불가",
                "uncertainty": "독립 검증 필요",
            }
        }]
        _, detailed, telegram = compose("morning", market, news, None)
        for phrase in ("[기사 근거·원문 대조 필요]", "[시장 관찰]",
                       "[가설·미검증]", "[추가 확인]"):
            self.assertIn(phrase, detailed)
        self.assertIn("주가 변동을 일으켰는지는 확인되지 않았습니다", detailed)
        for phrase in ("[핵심 뉴스·근거]", "메모리 공급 업데이트",
                       "기사 본문 확보·AI 분석", "https://example.com/news",
                       "인과관계 미검증"):
            self.assertIn(phrase, telegram)

if __name__ == "__main__":
    unittest.main(verbosity=2)
