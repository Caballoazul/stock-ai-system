"""Send an existing GitHub HTML briefing through Gmail without re-rendering it."""
import argparse
import hashlib
import os
import re
import smtplib
from email.message import EmailMessage
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_REPORT = "tests/chatgpt_scheduled_html_delivery_20261020.html"

class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = {}
        self.links = 0
        self.rows = 0
        self.cells = 0
        self.text = []
    def handle_starttag(self, tag, attrs):
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if tag == "a" and dict(attrs).get("href", "").startswith(("https://", "http://")):
            self.links += 1
        if tag == "tr":
            self.rows += 1
        if tag in ("td", "th"):
            self.cells += 1
    def handle_data(self, data):
        self.text.append(data)

def load_report(name):
    if not re.fullmatch(r"tests/[a-zA-Z0-9_.-]+\.html", name):
        raise ValueError("REPORT_PATH must be a single HTML file inside tests/")
    root = Path.cwd().resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root / "tests"):
        raise ValueError("Invalid report path")
    html = path.read_text(encoding="utf-8-sig")
    parser = ReportParser()
    parser.feed(html)
    text = " ".join(parser.text)
    if not all(parser.tags.get(tag, 0) for tag in ("html", "h1", "h2", "table", "tr", "th", "td")):
        raise ValueError("HTML is missing required report elements")
    if parser.rows < 4 or parser.cells < 12 or parser.links < 1:
        raise ValueError("HTML table or source links are incomplete")
    if "사실" not in text or "해석" not in text:
        raise ValueError("Fact/interpretation sections are missing")
    if re.search(r"<\s*(script|iframe|form)\b|\bon\w+\s*=", html, re.I):
        raise ValueError("Unsafe active HTML elements or event handlers")
    return html, text, parser

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=DEFAULT_REPORT)
    ap.add_argument("--send", action="store_true", help="Actually send one Gmail message")
    args = ap.parse_args()
    html, text, info = load_report(args.report)
    digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
    print(f"VALIDATED report={args.report} sha256={digest} rows={info.rows} links={info.links}")
    if not args.send:
        print("DRY_RUN_OK: HTML validated; no email sent")
        return

    address = os.getenv("GMAIL_ADDRESS", "").strip()
    password = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not address or not password or "@" not in address:
        raise RuntimeError("GMAIL_CONFIG_MISSING")

    msg = EmailMessage()
    msg["From"] = address
    msg["To"] = address
    label = "[반도체 브리핑]" if Path(args.report).name.startswith("chatgpt_scheduled_briefing_") else "[HTML 원본 전달 테스트]"
    msg["Subject"] = f"{label} {Path(args.report).stem}"
    msg.set_content(text)
    # Original HTML, not escaped or converted from Markdown.
    msg.add_alternative(html, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(address, password)
        smtp.send_message(msg)
    print("GMAIL_SEND_OK: one message sent to configured account")

if __name__ == "__main__":
    main()
