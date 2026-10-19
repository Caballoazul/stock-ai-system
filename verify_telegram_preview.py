"""Live data Telegram preview. NEVER send messages."""
import logging
from market_intelligence import fetch_market, fetch_news
from news_ai_briefing import enrich_news
from insight_report import compose

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main():
    market = fetch_market()
    news, error = fetch_news(hours=24, limit=6, market=market)
    enriched = enrich_news(news, limit=3)
    _, _, telegram = compose("morning", market, enriched, error)
    print("PREVIEW_ARTICLES=" + str(len(news)))
    print("PREVIEW_BODY_ANALYZED=" + str(sum(
        "본문 확보" in n.get("verification", "") for n in enriched)))
    print("PREVIEW_CHARS=" + str(len(telegram)))
    print("PREVIEW_START")
    print(telegram.replace("\\n", "\n"))
    print("PREVIEW_END")
    print("PREVIEW_MESSAGES_SENT=0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
