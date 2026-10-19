"""Market closes and recent headlines, with timestamps and source links."""
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote
from xml.etree import ElementTree
import requests
import yfinance as yf

KST = timezone(timedelta(hours=9))
SYMBOLS = {
    "Micron": "MU", "NVIDIA": "NVDA", "NASDAQ": "^IXIC",
    "SOX": "^SOX", "Samsung": "005930.KS", "SK Hynix": "000660.KS",
}
NEWS_QUERY = '(Micron OR Nvidia OR "SK hynix" OR Samsung) (HBM OR semiconductor OR memory OR earnings)'


def fetch_market():
    results = {}
    for name, symbol in SYMBOLS.items():
        try:
            history = yf.Ticker(symbol).history(period="7d", interval="1d", auto_adjust=False)
            if history.empty or len(history) < 2:
                raise ValueError("insufficient history")
            current, previous = history.iloc[-1], history.iloc[-2]
            close, prior = float(current["Close"]), float(previous["Close"])
            if close <= 0 or prior <= 0:
                raise ValueError("invalid price")
            dt = history.index[-1]
            results[name] = {
                "price": close, "change": (close / prior - 1) * 100,
                "date": dt.strftime("%Y-%m-%d"), "volume": int(current["Volume"]),
                "source": "Yahoo Finance / yfinance", "error": None,
            }
        except Exception as exc:
            results[name] = {"error": type(exc).__name__}
    return results


def fetch_news(hours=24, limit=6):
    url = ("https://news.google.com/rss/search?q="
           + quote(NEWS_QUERY + " when:1d")
           + "&hl=en-US&gl=US&ceid=US:en")
    try:
        response = requests.get(url, timeout=18, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        articles = []
        seen = set()
        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            source = item.findtext("source") or "Google News RSS"
            raw_date = item.findtext("pubDate") or ""
            try:
                published = parsedate_to_datetime(raw_date).astimezone(timezone.utc)
            except Exception:
                continue
            if not title or not link or published < cutoff or title.lower() in seen:
                continue
            seen.add(title.lower())
            articles.append({"title": title, "link": link, "source": source,
                             "published": published.astimezone(KST).strftime("%m-%d %H:%M KST")})
            if len(articles) >= limit:
                break
        return articles, None
    except Exception as exc:
        return [], type(exc).__name__
