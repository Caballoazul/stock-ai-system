"""Offline report checks: no external APIs or messages."""
import unittest
from insight_report import compose

class EvidenceReportTests(unittest.TestCase):
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
        _, detailed, _ = compose("morning", market, news, None)
        for phrase in ("[기사 근거·원문 대조 필요]", "[시장 관찰]",
                       "[가설·미검증]", "[추가 확인]"):
            self.assertIn(phrase, detailed)
        self.assertIn("주가 변동을 일으켰는지는 확인되지 않았습니다", detailed)

if __name__ == "__main__":
    unittest.main(verbosity=2)
