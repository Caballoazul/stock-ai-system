"""Send a scheduled HTML briefing summary + fresh 3-company PER to Telegram.

Gmail is sent first by the workflow. This program does not read or send Gmail.
The compact clickable link is a Gmail subject-search link, not a message permalink.
"""
import argparse
import html as html_lib
import os
from pathlib import Path
from urllib.parse import quote

from send_saved_html import load_report
from send_saved_html_channels import Extractor
from valuation_collector import collect_valuations
from per_comparison import render_per_comparison


def build_message(report_path, valuations):
    report_html, _, _ = load_report(report_path)
    parser = Extractor()
    parser.feed(report_html)
    title = next((s for tag, s in parser.parts if tag == "h1"), Path(report_path).stem)
    paragraphs = [(tag, s) for tag, s in parser.parts if tag in ("h2", "h3", "p", "li")]
    selected = []
    used = 0
    for tag, value in paragraphs:
        line = ("■ " if tag in ("h2", "h3") else "• ") + value
        if used + len(line) > 1700:
            break
        selected.append(line)
        used += len(line) + 1
    summary = "\n".join(selected) if selected else "원문 요약을 추출하지 못했습니다."
    per_text = render_per_comparison(valuations)
    subject = "[반도체 브리핑] " + Path(report_path).stem
    # Gmail web search: URL stays intact; Telegram displays only short link text.
    search_url = "https://mail.google.com/mail/u/0/#search/" + quote("subject:\"" + subject + "\"", safe="")
    body = ("📰 " + title + "\n\n" + summary +
            "\n\n" + per_text +
            "\n\n📧 <a href=\"" + html_lib.escape(search_url, quote=True) +
            "\">Gmail 상세 보고서 보기</a>")
    # Telegram counts rendered text; HTML escaping can expand the wire length.
    if len(html_lib.unescape(body)) > 3900:
        raise ValueError("Telegram summary exceeds safe limit")
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    values = collect_valuations()
    message = build_message(args.report, values)
    print("TELEGRAM_PER_SUMMARY_VALIDATED")
    if args.preview:
        print(message)
    if not args.send:
        print("TELEGRAM_DRY_RUN_OK")
        return
    from telegram_sender import send_telegram_message
    response = send_telegram_message(message, parse_mode="HTML")
    if not isinstance(response, dict) or not response.get("ok"):
        raise RuntimeError("Telegram API did not confirm send")
    print("TELEGRAM_PER_SEND_OK")


if __name__ == "__main__":
    main()
