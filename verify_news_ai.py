"""Single-article Gemini verification; no Gmail/Telegram/Kakao sending."""
import logging
import sys
from market_intelligence import fetch_publisher_rss
from news_ai_briefing import extract_article, _analyze

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main():
    articles = fetch_publisher_rss(hours=24, limit=10)
    print("NEWS_AI_TEST_CANDIDATES=" + str(len(articles)))
    for item in articles:
        body = extract_article(item["link"])
        if not body:
            continue
        title = item["title"]
        print("NEWS_AI_TEST_SOURCE=" + item["source"])
        print("NEWS_AI_TEST_TITLE=" + title[:180].replace("\n", " "))
        print("NEWS_AI_TEST_BODY_CHARS=" + str(len(body)))
        print("NEWS_AI_TEST_TITLE_IN_BODY=" + str(any(
            word.lower() in body.lower() for word in title.split() if len(word) >= 7
        )))
        result = _analyze(title, body)
        if not result:
            print("NEWS_AI_TEST=FAIL reason=analysis_failed")
            return 1
        for key in ("headline_ko", "summary_ko", "samsung_impact", "hynix_impact", "uncertainty"):
            print("NEWS_AI_" + key.upper() + "=" + str(result.get(key, ""))[:450].replace("\n", " "))
        facts = result.get("facts", [])
        print("NEWS_AI_FACTS_COUNT=" + str(len(facts)))
        print("NEWS_AI_TEST=PASS")
        return 0
    print("NEWS_AI_TEST=FAIL reason=no_accessible_article_body")
    return 1

if __name__ == "__main__":
    sys.exit(main())
