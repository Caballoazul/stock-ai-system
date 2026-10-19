import os
import unittest
from unittest.mock import patch
from news_ai_briefing import _analyze

class GeminiNewsTests(unittest.TestCase):
    @patch("news_ai_briefing.requests.post")
    def test_missing_key_does_not_call_api(self, post):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            self.assertIsNone(_analyze("example", "sample article"))
        post.assert_not_called()

if __name__ == "__main__":
    unittest.main()
