"""Scheduled US/KR HTML briefing -> independent fresh PER -> Telegram.
Called only after Gmail succeeds. Does not depend on legacy daily reporting.
The Gmail link is a subject-search link, not an individual message permalink.
"""
import argparse
import html
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote

from send_saved_html import load_report

# Production PER collector: independent of legacy daily/Telegram/Kakao pipeline.
sys.path.insert(0, str(Path(__file__).resolve().parent / "experiments" / "news_per_telegram"))
from per_source import collect


class Sections(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = None
        self.depth = 0
        self.buf = []
        self.title = ""
        self.section = ""
        self.sections = {}
        self.intro = []
        self.headlines = {}

    def handle_starttag(self, tag, attrs):
        if self.active is not None:
            self.depth += 1
        elif tag in ("h1", "h2", "h3", "p"):
            self.active, self.depth, self.buf = tag, 0, []

    def handle_data(self, data):
        if self.active is not None:
            self.buf.append(data)

    def handle_endtag(self, tag):
        if self.active is None:
            return
        if self.depth > 0:
            self.depth -= 1
            return
        if tag != self.active:
            return
        value = " ".join("".join(self.buf).split())
        kind = self.active
        self.active, self.buf = None, []
        if not value:
            return
        if kind == "h1":
            self.title = value
        elif kind == "h2":
            self.section = value
            self.sections.setdefault(value, [])
        elif kind == "h3":
            self.headlines.setdefault(self.section, []).append(value)
        elif self.section:
            self.sections.setdefault(self.section, []).append(value)
        else:
            self.intro.append(value)

    def section(self, marker):
        return next((v for k, v in self.sections.items() if marker in k), [])


def section_values(parsed, marker):
    return next((v for k, v in parsed.sections.items() if marker in k), [])


def summary_lines(parsed, kind):
    if kind == "pm":
        core = section_values(parsed, "핵심 3줄")
        if core:
            return core[:3]
        intro = [x for x in parsed.intro if "핵심:" in x or x.startswith("핵심:")]
        if intro:
            return intro[:1]
        raise ValueError("PM report missing core summary")
    intro = [x for x in parsed.intro if "오늘의 판단 구조:" in x]
    headlines = next((v for k, v in parsed.headlines.items() if "시장 요약" in k), [])
    chosen = intro[:1] + headlines[:2]
    if not chosen:
        raise ValueError("AM report missing summary")
    return chosen


def insight(parsed, name):
    for heading, paragraphs in parsed.sections.items():
        if name in heading and ("뉴스" in heading or "핵심" in heading or "기업" in heading):
            selected = next((p for p in paragraphs if "해석" in p and len(p) > 25), None)
            if selected:
                return selected
    return None


def pe(value):
    return "미확인" if value is None else f"{value:.2f}배"


def build_message(report_path, rows, gmail_account=""):
    source, _, _ = load_report(report_path)
    parsed = Sections()
    parsed.feed(source)
    if not parsed.title:
        raise ValueError("Missing report title")
    filename = Path(report_path).name
    match = re.fullmatch(r"chatgpt_scheduled_briefing_(am|pm)_\d{8}\.html", filename)
    if not match:
        raise ValueError("Not an approved scheduled briefing file")
    kind = match.group(1)
    title = "🌎 미국장·반도체" if kind == "am" else "🇰🇷 국내장·반도체"
    lines = [f"<b>{title} 브리핑</b>", html.escape(parsed.title),
             "", "<b>① 핵심 뉴스</b>"]
    for item in summary_lines(parsed, kind):
        lines.append("• " + html.escape(item))
    for name in ("삼성전자", "SK하이닉스"):
        item = insight(parsed, name)
        if item:
            lines.extend(["", f"<b>{name} — 원본 해석</b>", html.escape(item)])
    if len(rows) != 3 or [r["company"] for r in rows] != ["마이크론", "삼성전자", "SK하이닉스"]:
        raise ValueError("PER company set mismatch")
    lines.extend(["", "<b>② 3사 PER 비교 (별도 실시간 조회)</b>",
                  "기업 | 과거 실적 PER | 예상 PER"])
    for row in rows:
        lines.append(html.escape(f"{row['company']} | {pe(row['trailing_pe'])} | {pe(row['forward_pe'])}"))
    lines.extend(["출처: Yahoo Finance / yfinance",
                  "조회 시도(KST): " + html.escape(rows[0]["collected_at_kst"]) + " ~ " + html.escape(rows[-1]["collected_at_kst"]),
                  "기업별 EPS 회계·예상기간 일치 미검증. 누락값은 미확인."])
    subject = "[반도체 브리핑] " + Path(report_path).stem
    # Account-specific search URL: search result may contain multiple matching emails.
    account = ("?authuser=" + quote(gmail_account, safe="")) if gmail_account else "/0/"
    link = "https://mail.google.com/mail/u/" + account + "#search/" + quote('subject:"' + subject + '"', safe="")
    lines.extend(["", "<b>③ 상세 보고서</b>",
                  '<a href="' + html.escape(link, quote=True) + '">📧 Gmail 원문 보고서 열기</a>',
                  "", "PER는 보고서 작성 후 별도로 조회한 참고값이며 Gmail 원본에는 추가되지 않았습니다."])
    message = "\n".join(lines)
    # Preserve the Gmail link and PER table if source insights are long.
    if len(message) > 3900:
        # Drop optional company commentary before dropping critical data.
        for name in ("SK하이닉스", "삼성전자"):
            marker = f"<b>{name} — 원본 해석</b>"
            if marker in lines:
                index = lines.index(marker)
                del lines[index - 1:index + 2]
                message = "\n".join(lines)
                if len(message) <= 3900:
                    break
    if len(message) > 3900:
        raise ValueError("Summary too long: no truncated/invalid Telegram message sent")
    return message


def send_one(message):
    import requests
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_CONFIG_MISSING")
    try:
        response = requests.post(
            "https://api.telegram.org/bot" + token + "/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML",
                  "disable_web_page_preview": True},
            timeout=30)
        data = response.json()
    except Exception:
        raise RuntimeError("TELEGRAM_RESULT_UNKNOWN_NO_AUTO_RETRY") from None
    if response.status_code != 200 or not data.get("ok"):
        raise RuntimeError("TELEGRAM_API_REJECTED")
    receipt = data.get("result", {})
    if not receipt.get("message_id") or str(receipt.get("chat", {}).get("id")) != str(chat_id):
        raise RuntimeError("TELEGRAM_RECEIPT_UNCONFIRMED")
    print("TELEGRAM_PER_SEND_OK message_id=" + str(receipt["message_id"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    rows = collect()
    message = build_message(args.report, rows, os.getenv("GMAIL_ADDRESS", ""))
    print("TELEGRAM_PER_SUMMARY_VALIDATED chars=" + str(len(message)))
    print("PER_COLLECTION_STATUS=" + ",".join(r["company"] + ":" + r["status"] for r in rows))
    if args.preview:
        print(message)
    if not args.send:
        print("TELEGRAM_DRY_RUN_OK")
        return
    if os.getenv("GITHUB_RUN_ATTEMPT", "1") != "1":
        raise RuntimeError("RE_RUN_SEND_DISABLED_TO_PREVENT_DUPLICATES")
    send_one(message)


if __name__ == "__main__":
    main()
