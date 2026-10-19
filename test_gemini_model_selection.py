import unittest
from unittest.mock import Mock, patch
from news_ai_briefing import resolve_gemini_model

class GeminiModelSelectionTests(unittest.TestCase):
    @patch("news_ai_briefing.requests.get")
    def test_fallback_to_supported_model(self, get):
        get.return_value.status_code = 200
        get.return_value.json.return_value = {"models": [
            {"name": "models/gemini-2.5-flash", "supportedGenerationMethods": ["generateContent"]},
            {"name": "models/embedding-001", "supportedGenerationMethods": ["embedContent"]}
        ]}
        self.assertEqual(resolve_gemini_model("fake", "missing-model"), "gemini-2.5-flash")

    @patch("news_ai_briefing.requests.get")
    def test_model_list_error(self, get):
        get.return_value.status_code = 403
        self.assertIsNone(resolve_gemini_model("fake", "gemini-2.5-flash"))

if __name__ == "__main__":
    unittest.main()
