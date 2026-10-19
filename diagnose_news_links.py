"""Standalone news-link diagnostic. No AI, Telegram, or account credentials."""
from urllib.parse import urlparse
from xml.etree import ElementTree
import json
import requests
from bs4 import BeautifulSoup

RSS = "https://news.google.com/rss/search?q=Micron%20semiconductor%20stocks&hl=en-US&gl=US&ceid=US:en"

def diagnose():
    feed = requests.get(RSS, timeout=18, headers={"User-Agent": "Mozilla/5.0"})
    feed.raise_for_status()
    root = ElementTree.fromstring(feed.content)
    entries = root.findall("./channel/item")[:5]
    results = []
    for entry in entries:
        title = (entry.findtext("title") or "").strip()
        url = (entry.findtext("link") or "").strip()
        row = {"title": title[:140], "source_host": urlparse(url).hostname}
        if not url.startswith("https://news.google.com/"):
            row["result"] = "unexpected_feed_link"
            results.append(row)
            continue
        try:
            response = requests.get(url, timeout=15, allow_redirects=True,
                                    headers={"User-Agent": "Mozilla/5.0"})
            host = (urlparse(response.url).hostname or "").lower()
            row["http_status"] = response.status_code
            row["final_host"] = host
            row["redirect_count"] = len(response.history)
            if host in ("news.google.com", "google.com"):
                row["result"] = "A_google_landing"
            elif response.status_code != 200:
                row["result"] = "C_publisher_http_error"
            else:
                soup = BeautifulSoup(response.text[:900000], "html.parser")
                article = soup.find("article") or soup.find("main")
                length = len(" ".join(article.stripped_strings)) if article else 0
                row["article_chars"] = length
                row["result"] = "success" if length >= 450 else "B_short_or_missing_body"
        except requests.RequestException as exc:
            row["result"] = "C_request_error"
            row["error_type"] = type(exc).__name__
        results.append(row)
    print("DIAGNOSTIC_ONLY_NO_MESSAGES=1")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    diagnose()
