"""Deliver concise Telegram/Kakao messages from the same saved HTML as Gmail.

No separate news collection, AI rewriting, or invented market values.
Dry-run by default; --send is explicit.
"""
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path

from send_saved_html import load_report


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.tag = None
        self.buf = []
        self.href = None
        self.links = []
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3", "p", "li"):
            self.tag = tag
            self.buf = []
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "a":
            url = dict(attrs).get("href", "")
            if url.startswith(("https://", "http://")):
                self.href = url

    def handle_data(self, data):
        if self.tag:
            self.buf.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href:
            if self.href not in self.links:
                self.links.append(self.href)
            self.href = None
        if tag in ("h1", "h2", "h3", "p", "li") and self.tag == tag:
            value = " ".join("".join(self.buf).split())
            if value:
                self.parts.append((tag, value))
            self.tag = None
            self.buf = []
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        if tag == "tr" and self.row is not None:
            if self.row:
                self.rows.append(self.row)
            self.row = None


def gmail_search_label(report_path):
    if Path(report_path).name.startswith("chatgpt_scheduled_briefing_"):
        return "[반도체 브리핑]"
    return "[HTML 원본 전달 테스트]"


def complete_sentence(text, max_length):
    """Return only a complete sentence, never a mid-word truncation."""
    if not text or max_length <= 0:
        return ""
    if len(text) <= max_length:
        return text
    matches = list(re.finditer(r"[.!?。](?=\\s|$)", text[:max_length + 1]))
    if matches:
        return text[:matches[-1].end()].strip()
    return ""


def summarize(html, report_path):
    parser = Extractor()
    parser.feed(html)
    title = next((v for tag, v in parser.parts if tag == "h1"), Path(report_path).stem)
    # Source text only: do not infer new facts or manufacture numbers.
    paragraphs = [(tag, val) for tag, val in parser.parts if tag in ("h2", "h3", "p", "li")]
    short = []
    total = 0
    for tag, val in paragraphs:
        # Prefer news and evidence; preserve the order of the original report.
        item = ("■ " if tag in ("h2", "h3") else "• ") + val
        if total + len(item) > 2200:
            break
        short.append(item)
        total += len(item) + 1
    table = []
    for row in parser.rows[:4]:
        table.append(" / ".join(row))
    source_links = parser.links[:2]
    telegram = "📰 " + title + "\n\n" + "\n".join(short)
    if table:
        telegram += "\n\n[원문 표 발췌]\n" + "\n".join(table)
    if source_links:
        telegram += "\n\n[출처]\n" + "\n".join(source_links)
    telegram += "\n\n📧 상세 보고서: Gmail에서 " + gmail_search_label(report_path) + " 검색"
    if len(telegram) > 3900:
        telegram = telegram[:3850].rsplit("\n", 1)[0] + "\n…(상세 내용은 Gmail 참조)"

    # Kakao: select a complete source sentence, never a partial excerpt.
    main = next((val for tag, val in paragraphs if tag == "p" and ("사실" in val or "핵심" in val)), "")
    footer = "상세: Gmail에서 " + gmail_search_label(report_path) + " 검색"
    headline = title[:48]
    remaining = 180 - len(headline) - len(footer) - 2
    fact = complete_sentence(main, min(110, remaining))
    kakao = headline + "\n" + (fact + "\n" if fact else "") + footer
    if len(kakao) > 180:
        raise ValueError("Kakao message exceeds 180 characters")
    return telegram, kakao


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--preview", action="store_true", help="Print summaries for review")
    args = ap.parse_args()
    html, _, _ = load_report(args.report)
    telegram, kakao = summarize(html, args.report)
    if not telegram.strip() or not kakao.strip():
        raise ValueError("Empty channel summary")
    print(f"CHANNEL_SUMMARY_VALIDATED telegram_chars={len(telegram)} kakao_chars={len(kakao)}")
    if args.preview:
        print("=== TELEGRAM_PREVIEW_BEGIN ===")
        print(telegram)
        print("=== TELEGRAM_PREVIEW_END ===")
        print("=== KAKAO_PREVIEW_BEGIN ===")
        print(kakao)
        print("=== KAKAO_PREVIEW_END ===")
    if not args.send:
        print("CHANNEL_DRY_RUN_OK: no Telegram/Kakao messages sent")
        return
    from telegram_sender import send_telegram_message
    from kakao_sender import send_kakao_messages
    errors = []
    try:
        result = send_telegram_message(telegram)
        if not isinstance(result, dict) or not result.get("ok"):
            raise RuntimeError("Telegram API did not confirm delivery")
        print("TELEGRAM_SEND_OK")
    except Exception as exc:
        print(f"TELEGRAM_SEND_FAILED={type(exc).__name__}")
        errors.append("telegram")
    try:
        send_kakao_messages([kakao])
        print("KAKAO_SEND_OK")
    except Exception as exc:
        print(f"KAKAO_SEND_FAILED={type(exc).__name__}")
        errors.append("kakao")
    if errors:
        raise RuntimeError("CHANNEL_DELIVERY_FAILED: " + ",".join(errors))


if __name__ == "__main__":
    main()
