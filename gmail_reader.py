"""Read matching Gmail briefings without changing mailbox read state.

Uses the same Gmail account and app password as the SMTP sender.
No third-party packages are required.
"""
from __future__ import annotations

import email
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from html import unescape
from html.parser import HTMLParser
import imaplib
import os
import re

PHRASE = '삼성전자·SK하이닉스 뉴스 브리핑'


class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag in ('br', 'p', 'div', 'li', 'tr'):
            self.parts.append('\n')
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href.startswith(('https://', 'http://')):
                self.parts.append(' [')
                self.parts.append(href)
                self.parts.append('] ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden:
            self.hidden -= 1
        if tag in ('p', 'div', 'li', 'tr'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)

    def text(self):
        return re.sub(r'\n{3,}', '\n\n', unescape(''.join(self.parts))).strip()


def _decode(value):
    try:
        return str(make_header(decode_header(value or '')))
    except (UnicodeError, LookupError, ValueError):
        return value or ''


def _payload(part):
    try:
        return part.get_content()
    except (AttributeError, LookupError, UnicodeError):
        raw = part.get_payload(decode=True) or b''
        return raw.decode(part.get_content_charset() or 'utf-8', errors='replace')


def _body(msg):
    plain, html = [], []
    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        if part.get_content_disposition() == 'attachment':
            continue
        content_type = part.get_content_type()
        if content_type == 'text/plain':
            plain.append(_payload(part))
        elif content_type == 'text/html':
            html.append(_payload(part))
    if plain:
        return '\n'.join(plain).strip()
    if html:
        parser = _HTMLText()
        parser.feed('\n'.join(html))
        return parser.text()
    return ''


def fetch_recent_briefings(hours=24, max_messages=5, now=None):
    """Return newest-first matching messages; [] means none.

    Search by recent internal date first, then enforce exact time window and
    decoded subject in Python. BODY is not logged or sent anywhere.
    """
    address = os.environ.get('GMAIL_ADDRESS', '').strip()
    password = os.environ.get('GMAIL_APP_PASSWORD', '').replace(' ', '')
    if not address or not password:
        raise RuntimeError('GMAIL_CONFIG_MISSING')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('now must be timezone-aware')
    cutoff = now - timedelta(hours=hours)
    # IMAP SINCE searches calendar days; exact 24h filtering follows.
    since = (cutoff - timedelta(days=1)).strftime('%d-%b-%Y')
    client = imaplib.IMAP4_SSL('imap.gmail.com', 993, timeout=30)
    try:
        client.login(address, password)
        status, _ = client.select('INBOX', readonly=True)
        if status != 'OK':
            raise RuntimeError('GMAIL_SELECT_FAILED')
        status, data = client.uid('search', None, 'SINCE', since)
        if status != 'OK':
            raise RuntimeError('GMAIL_SEARCH_FAILED')
        uids = (data[0] or b'').split()
        found = []
        # Scan newest first; cap scanned count to avoid huge mailboxes.
        for uid in reversed(uids[-300:]):
            status, items = client.uid('fetch', uid, '(BODY.PEEK[] INTERNALDATE)')
            if status != 'OK':
                continue
            raw = next((item[1] for item in items if isinstance(item, tuple) and isinstance(item[1], bytes)), None)
            if not raw:
                continue
            msg = email.message_from_bytes(raw, policy=email.policy.default)
            subject = _decode(msg.get('Subject'))
            if PHRASE not in subject:
                continue
            try:
                received = parsedate_to_datetime(msg.get('Date')).astimezone(timezone.utc)
            except (TypeError, ValueError, OverflowError):
                continue
            if not cutoff <= received <= now:
                continue
            found.append({'subject': subject, 'received_at': received.isoformat(),
                          'body': _body(msg), 'message_id': msg.get('Message-ID', '')})
            if len(found) >= max_messages:
                break
        return sorted(found, key=lambda x: x['received_at'], reverse=True)
    finally:
        try:
            client.logout()
        except Exception:
            pass
