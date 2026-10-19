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


def fetch_direct_news(hours=24, limit=6):
    """GDELT DOC returns publisher URLs, unlike Google News RSS landing links."""
    from urllib.parse import urlparse
    from datetime import datetime
    query = '(Micron OR NVIDIA OR "SK Hynix" OR "Samsung Electronics") (semiconductor OR memory OR HBM OR earnings)'
    params = {"query": query, "mode": "ArtList", "format": "json",
              "maxrecords": 50, "timespan": "1d", "sort": "DateDesc"}
    try:
        response = requests.get("https://api.gdeltproject.org/api/v2/doc/doc",
                                params=params, timeout=20,
                                headers={"User-Agent": "stock-ai-system/1.0"})
        if response.status_code != 200:
            print("NEWS_DIRECT_HTTP_STATUS=" + str(response.status_code))
            return [], "HTTP_" + str(response.status_code)
        items = response.json().get("articles", [])
    except (requests.RequestException, ValueError) as exc:
        return [], type(exc).__name__
    results, seen = [], set()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    for item in items:
        title = (item.get("title") or "").strip()
        link = (item.get("url") or "").strip()
        domain = (urlparse(link).hostname or "").lower()
        if not title or not link.startswith("https://") or not domain:
            continue
        if domain in {"news.google.com", "google.com"}:
            continue
        raw = item.get("seendate", "")
        try:
            published = datetime.strptime(raw, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if published < cutoff:
            continue
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        results.append({"title": title, "link": link, "source": item.get("domain") or domain,
                        "published": published.astimezone(KST).strftime("%m-%d %H:%M KST")})
        if len(results) >= limit:
            break
    return results, None if results else "no_direct_articles"


def fetch_news(hours=24, limit=6):
    direct, direct_error = fetch_direct_news(hours=hours, limit=limit)
    if direct:
        return direct, None
    print("NEWS_DIRECT_SOURCE_UNAVAILABLE=" + str(direct_error))
    # Fallback is headlines only: Google News RSS links are NOT verified publisher bodies.
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
