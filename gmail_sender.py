"""Send one HTML/text report through Gmail SMTP using GitHub Secrets."""
import os
import smtplib
import re
from email.message import EmailMessage
from html import escape
from urllib.parse import quote


def render_report_html(report_text):
    """Escape all report text, but show HTTP(S) article links as short anchors."""
    pattern = re.compile(r"https?://[^\s<>\"']+")
    parts = []
    start = 0
    for match in pattern.finditer(report_text):
        parts.append(escape(report_text[start:match.start()]))
        raw = match.group(0)
        url = raw.rstrip(".,);")
        suffix = raw[len(url):]
        parts.append('<a href="' + escape(url, quote=True) +
                     '" target="_blank" rel="noopener noreferrer">원문 보기</a>' +
                     escape(suffix))
        start = match.end()
    parts.append(escape(report_text[start:]))
    return ('<html><body><div style="font-family:Arial,sans-serif;'
            'white-space:pre-wrap;line-height:1.65;overflow-wrap:anywhere">'
            + ''.join(parts) + '</div></body></html>')


def send_gmail_report(subject, report_text):
    address = os.environ.get("GMAIL_ADDRESS", "").strip()
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not address or not app_password:
        raise RuntimeError("GMAIL_CONFIG_MISSING")
    if "@" not in address:
        raise RuntimeError("GMAIL_ADDRESS_INVALID")
    message = EmailMessage()
    message["From"] = address
    message["To"] = address
    message["Subject"] = subject
    message.set_content(report_text)
    html_body = render_report_html(report_text)
    message.add_alternative(html_body, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(address, app_password)
        smtp.send_message(message)
    # Search link, NOT a verified direct permalink to an individual email.
    return "https://mail.google.com/mail/u/0/#search/" + quote('subject:"' + subject + '"', safe="")
