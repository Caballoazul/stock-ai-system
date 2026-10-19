"""News-only diagnostic: no Gemini API, Gmail, Telegram or Kakao sends."""
from market_intelligence import fetch_publisher_rss, fetch_direct_news
from news_ai_briefing import extract_article
from urllib.parse import urlparse

def main():
    items = fetch_publisher_rss(hours=24, limit=6)
    source = "publisher_rss"
    if not items:
        items, error = fetch_direct_news(hours=24, limit=6)
        source = "gdelt"
        if not items:
            print("NEWS_DIAGNOSTIC=FAIL reason=no_direct_articles gdelt_error=" + str(error))
            return 1
    print("NEWS_DIAGNOSTIC_SOURCE=" + source)
    print("NEWS_DIAGNOSTIC_ARTICLES=" + str(len(items)))
    successes = 0
    for i, item in enumerate(items[:3], 1):
        host = urlparse(item["link"]).hostname or "unknown"
        print(f"NEWS_ITEM_{i}_DOMAIN={host}")
        body = extract_article(item["link"])
        print(f"NEWS_ITEM_{i}_BODY_CHARS={len(body) if body else 0}")
        successes += bool(body)
    print("NEWS_DIAGNOSTIC_BODY_SUCCESS=" + str(successes))
    print("NEWS_DIAGNOSTIC=" + ("PASS" if successes else "FAIL"))
    return 0 if successes else 1

if __name__ == "__main__":
    raise SystemExit(main())
