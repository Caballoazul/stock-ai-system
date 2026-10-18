"""Send one HTML/text report through Gmail SMTP using GitHub Secrets."""
import os
import smtplib
from email.message import EmailMessage
from html import escape
from urllib.parse import quote


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
    html_body = '<html><body><div style="font-family:Arial,sans-serif;white-space:pre-wrap;line-height:1.65">' + escape(report_text) + '</div></body></html>'
    message.add_alternative(html_body, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(address, app_password)
        smtp.send_message(message)
    # Search link, NOT a verified direct permalink to an individual email.
    return "https://mail.google.com/mail/u/0/#search/" + quote('subject:"' + subject + '"', safe="")
