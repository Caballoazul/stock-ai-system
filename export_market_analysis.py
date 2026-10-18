"""Export existing market data to a JSON file for ChatGPT GitHub connector testing."""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from market_intelligence import fetch_market, fetch_news

KST = ZoneInfo('Asia/Seoul')
OUTPUT = Path('reports/market_analysis.json')


def main():
    market = fetch_market()
    news, news_error = fetch_news()
    payload = {
        'schema_version': 1,
        'generated_at_kst': datetime.now(KST).isoformat(timespec='seconds'),
        'data_source': 'market_intelligence.py',
        'market': market,
        'news_headlines_unverified': news,
        'news_error': news_error,
        'limitations': [
            'Price data may reflect the latest prior trading session.',
            'RSS headlines are not verified article bodies.',
            'This file does not contain AI-generated conclusions.',
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(f'EXPORT_OK={OUTPUT} MARKET_COUNT={len(market)} NEWS_COUNT={len(news)}')


if __name__ == '__main__':
    main()
