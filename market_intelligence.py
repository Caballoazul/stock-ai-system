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
MARKET_MOVE_QUERY = '("Micron stock" OR "semiconductor stocks" OR "chip stocks" OR "SOX index") (fall OR drop OR selloff OR plunge OR decline OR earnings OR outlook)'


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



def fetch_publisher_rss(hours=24, limit=6):
    """Direct publisher RSS links; no Google News redirect and no API key."""
    from html import unescape
    from urllib.parse import urlparse
    feeds = [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("Tom's Hardware", "https://www.tomshardware.com/feeds/all"),
        ("Electronics Weekly", "https://www.electronicsweekly.com/news/feed/"),
        ("CNBC", "https://www.cnbc.com/id/19854910/device/rss/rss.html"),
    ]
    terms = ("micron", "nvidia", "hynix", "samsung", "hbm",
             "semiconductor", "memory chip", "dram", "tsmc")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    results, seen = [], set()
    for source, feed_url in feeds:
        try:
            response = requests.get(feed_url, timeout=12,
                                    headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
            entries = root.findall("./channel/item")
            entries += root.findall("{http://www.w3.org/2005/Atom}entry")
            count = 0
            for item in entries:
                title = unescape((item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "").strip())
                link = (item.findtext("link") or "").strip()
                if not link:
                    atom_link = item.find("{http://www.w3.org/2005/Atom}link")
                    link = atom_link.get("href", "") if atom_link is not None else ""
                date = (item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}published")
                        or item.findtext("{http://www.w3.org/2005/Atom}updated") or "")
                try:
                    published = parsedate_to_datetime(date).astimezone(timezone.utc)
                except (ValueError, TypeError, OverflowError):
                    try:
                        published = datetime.fromisoformat(date.replace("Z", "+00:00")).astimezone(timezone.utc)
                    except (ValueError, TypeError):
                        continue
                host = (urlparse(link).hostname or "").lower()
                if (published < cutoff or not link.startswith("https://")
                    or host in {"news.google.com", "google.com"}
                    or not any(term in title.lower() for term in terms)):
                    continue
                key = " ".join(title.lower().split())
                if key in seen:
                    continue
                seen.add(key)
                results.append({"title": title, "link": link, "source": source,
                                "published": published.astimezone(KST).strftime("%m-%d %H:%M KST")})
                count += 1
            print("NEWS_PUBLISHER_RSS=" + source.replace(" ", "_") + ":" + str(count))
        except (requests.RequestException, ElementTree.ParseError) as exc:
            print("NEWS_PUBLISHER_RSS_ERROR=" + source.replace(" ", "_") + ":" + type(exc).__name__)
    # Rank semiconductor relevance, not just publication recency.
    def relevance(item):
        title = item["title"].lower()
        strong = ("hbm", "nvhbm", "micron", "hynix", "dram", "memory chip")
        medium = ("samsung", "nvidia", "tsmc", "semiconductor")
        score = 3 * sum(term in title for term in strong)
        score += sum(term in title for term in medium)
        if "netflix" in title or "oracle" in title:
            score -= 4
        return score
    results = [item for item in results if relevance(item) >= 2]
    results.sort(key=lambda x: (relevance(x), x["published"]), reverse=True)
    return results[:limit]



def market_news_score(item, market=None):
    """Rank evidence candidates; a high score does NOT establish price causality."""
    title = (item.get("title") or "").lower()
    market = market or {}
    names = ("micron", "nvidia", "hynix", "samsung", "semiconductor", "chip", "hbm", "dram", "tsmc")
    catalysts = ("earnings", "guidance", "forecast", "outlook", "demand", "supply",
                 "export", "restriction", "tariff", "downgrade", "upgrade",
                 "selloff", "slump", "drop", "fall", "decline", "rally",
                 "surge", "shares", "stock", "revenue", "margin", "price")
    sector = any(word in title for word in names)
    score = sum(2 for word in names if word in title)
    score += sum(3 for word in catalysts if word in title)
    if any(word in title for word in ("hbm", "dram", "memory")):
        score += 3
    if not sector:
        score -= 8
    if any(word in title for word in ("netflix", "oracle", "stocktwits tech watch")):
        score -= 5
    movers = {"Micron": ("micron",), "NVIDIA": ("nvidia",)}
    for name, words in movers.items():
        change = market.get(name, {}).get("change")
        if isinstance(change, (int, float)) and abs(change) >= 3:
            if any(word in title for word in words):
                score += 4
    if any(isinstance(market.get(name, {}).get("change"), (int, float))
           and abs(market[name]["change"]) >= 3 for name in ("Micron", "SOX")):
        if sector and any(word in title for word in catalysts):
            score += 3
    return score


def rank_market_news(items, market=None, limit=6):
    """Prioritize relevant catalysts; retain title-only evidence labels downstream."""
    ranked = sorted(items, key=lambda item: market_news_score(item, market), reverse=True)
    return ranked[:limit]


def fetch_session_market_news(market, limit=12):
    """Search news around the US close date, not the report's current 24h window.

    UTC noon on session date through UTC noon the following day covers the
    US trading session and immediate post-close coverage. Headlines alone
    remain unverified; publication timing is not evidence of causality.
    """
    from datetime import date
    dates = [market.get(k, {}).get("date") for k in ("SOX", "NASDAQ", "Micron")]
    valid = []
    for raw in dates:
        try:
            if raw:
                valid.append(date.fromisoformat(raw))
        except (TypeError, ValueError):
            continue
    if not valid:
        print("NEWS_MARKET_SESSION=unavailable")
        return []
    session = max(valid)
    start = datetime.combine(session, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=12)
    end = start + timedelta(days=1)
    query = (MARKET_MOVE_QUERY + " after:" + session.isoformat()
             + " before:" + (session + timedelta(days=2)).isoformat())
    url = ("https://news.google.com/rss/search?q=" + quote(query)
           + "&hl=en-US&gl=US&ceid=US:en")
    print("NEWS_MARKET_SESSION=" + session.isoformat())
    try:
        response = requests.get(url, timeout=18, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        results = []
        for entry in root.findall("./channel/item"):
            title = (entry.findtext("title") or "").strip()
            link = (entry.findtext("link") or "").strip()
            try:
                published = parsedate_to_datetime(entry.findtext("pubDate") or "").astimezone(timezone.utc)
            except (ValueError, TypeError, OverflowError):
                continue
            if not title or not link.startswith("https://") or not start <= published < end:
                continue
            results.append({"title": title, "link": link,
                            "source": entry.findtext("source") or "Google News RSS",
                            "published": published.astimezone(KST).strftime("%m-%d %H:%M KST"),
                            "session_date": session.isoformat()})
        print("NEWS_MARKET_SESSION_FOUND=" + str(len(results)))
        return rank_market_news(results, market, limit)
    except (requests.RequestException, ElementTree.ParseError) as exc:
        print("NEWS_MARKET_SESSION_ERROR=" + type(exc).__name__)
        return []


def fetch_news(hours=24, limit=6, market=None):
    """Combine publisher RSS and GDELT; supplement with Google News when sparse."""
    publisher = fetch_publisher_rss(hours=hours, limit=max(limit * 3, 12))
    direct, direct_error = fetch_direct_news(hours=hours, limit=max(limit * 3, 12))
    combined, seen = [], set()

    def add(items, category):
        for item in items:
            title = " ".join((item.get("title") or "").lower().split())
            link = item.get("link", "")
            if not title or not link or title in seen:
                continue
            seen.add(title)
            record = dict(item)
            record["category"] = category
            combined.append(record)

    add(publisher, "semiconductor")
    add(direct, "semiconductor")
    session_news = fetch_session_market_news(market or {}, limit=max(limit * 2, 8)) if market else []
    add(session_news, "market_session")
    print("NEWS_SOURCES=publisher:" + str(len(publisher)) + ",gdelt:" + str(len(direct)))
    if len(publisher) + len(direct) < limit:
        url = ("https://news.google.com/rss/search?q="
               + quote(NEWS_QUERY + " when:1d")
               + "&hl=en-US&gl=US&ceid=US:en")
        try:
            response = requests.get(url, timeout=18, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            fallback = []
            for item in root.findall("./channel/item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                raw_date = item.findtext("pubDate") or ""
                try:
                    published = parsedate_to_datetime(raw_date).astimezone(timezone.utc)
                except (ValueError, TypeError, OverflowError):
                    continue
                if not title or not link or published < cutoff:
                    continue
                fallback.append({"title": title, "link": link,
                                 "source": item.findtext("source") or "Google News RSS",
                                 "published": published.astimezone(KST).strftime("%m-%d %H:%M KST")})
            add(fallback, "semiconductor")
            print("NEWS_GOOGLE_FALLBACK=" + str(len(fallback)))
        except (requests.RequestException, ElementTree.ParseError) as exc:
            print("NEWS_GOOGLE_FALLBACK_ERROR=" + type(exc).__name__)
    # Google News landing URLs are not verified publisher bodies. Never label them direct.
    # Reserve candidate space for market-move headlines when direct evidence is sparse.
    if not session_news and len(combined) < limit + 2:
        try:
            focused_url = ("https://news.google.com/rss/search?q="
                           + quote(MARKET_MOVE_QUERY + " when:1d")
                           + "&hl=en-US&gl=US&ceid=US:en")
            focused_response = requests.get(focused_url, timeout=18,
                                            headers={"User-Agent": "Mozilla/5.0"})
            focused_response.raise_for_status()
            focused_root = ElementTree.fromstring(focused_response.content)
            focused = []
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            for entry in focused_root.findall("./channel/item"):
                title = (entry.findtext("title") or "").strip()
                link = (entry.findtext("link") or "").strip()
                try:
                    published = parsedate_to_datetime(entry.findtext("pubDate") or "").astimezone(timezone.utc)
                except (ValueError, TypeError, OverflowError):
                    continue
                if not title or not link.startswith("https://") or published < cutoff:
                    continue
                focused.append({"title": title, "link": link,
                                "source": entry.findtext("source") or "Google News RSS",
                                "published": published.astimezone(KST).strftime("%m-%d %H:%M KST")})
            add(focused, "market")
            print("NEWS_MARKET_FOCUSED=" + str(len(focused)))
        except (requests.RequestException, ElementTree.ParseError) as exc:
            print("NEWS_MARKET_FOCUSED_ERROR=" + type(exc).__name__)
    if not combined:
        return [], direct_error or "no_articles"
    # Prefer direct publisher URLs; Google News landing links cannot provide article bodies.
    direct_links = [item for item in combined
                    if not item.get("link", "").startswith("https://news.google.com/")]
    google_links = [item for item in combined
                    if item.get("link", "").startswith("https://news.google.com/")]
    prioritized = (rank_market_news(direct_links, market, max(limit * 3, 12))
                   + rank_market_news(google_links, market, max(limit * 3, 12)))
    if session_news:
        # Preserve space for session-day market reporting even when recent
        # industry headlines are more numerous; direct links still lead.
        session_titles = {" ".join(n["title"].lower().split()) for n in session_news}
        market_candidates = [n for n in prioritized if " ".join(n["title"].lower().split()) in session_titles]
        other_candidates = [n for n in prioritized if " ".join(n["title"].lower().split()) not in session_titles]
        selected = (market_candidates[:min(2, limit)] + other_candidates)[:limit]
        if len(selected) < limit:
            selected += market_candidates[min(2, limit):limit - len(selected) + min(2, limit)]
    else:
        selected = prioritized[:limit]
    print("NEWS_SELECTED_MARKET_SESSION=" + str(sum(bool(n.get("session_date")) for n in selected)))
    print("NEWS_SELECTED_DIRECT=" + str(sum(
        not item.get("link", "").startswith("https://news.google.com/")
        for item in selected)))
    return selected, None
