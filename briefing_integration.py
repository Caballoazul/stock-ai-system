"""Attach source-grounded Gmail briefing to detailed email only.

No AI paraphrasing: preserves original wording and URLs. Filters old forwarded
briefings by the timestamp in their original subject when present.
"""
from datetime import datetime, timedelta, timezone
import re
from zoneinfo import ZoneInfo

KST = ZoneInfo('Asia/Seoul')
ORIGINAL_DATE = re.compile(r'(?<!\d)(20\d{2})[-./](\d{1,2})[-./](\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?')
URL = re.compile(r'https?://[^\s<>\]\)]+')
SECTION = re.compile(r'^\s*\[(삼성전자|SK하이닉스|공통 산업 환경)\]\s*$')
NUMBERED = re.compile(r'^\s*(?:\d+[.)]|[①②③④⑤⑥⑦⑧⑨⑩])\s*(.*)$')


def _original_date(subject):
    match = ORIGINAL_DATE.search(subject)
    if not match:
        return None
    year, month, day, hour, minute = match.groups()
    try:
        return datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0), tzinfo=KST)
    except ValueError:
        return None


def select_current(messages, now=None, hours=24):
    """Exclude old dated reports even when forwarded within 24h."""
    now = now or datetime.now(KST)
    if now.tzinfo is None:
        raise ValueError('now must be timezone-aware')
    cutoff = now - timedelta(hours=hours)
    valid = []
    for item in messages:
        subject = item.get('subject', '')
        stamp = _original_date(subject)
        if stamp is not None and not (cutoff <= stamp <= now):
            continue
        body = item.get('body', '').strip()
        if body:
            valid.append(item)
    return valid


def _split_sections(body):
    sections = {'삼성전자': [], 'SK하이닉스': [], '공통 산업 환경': []}
    current = None
    for line in body.splitlines():
        m = SECTION.match(line)
        if m:
            current = m.group(1)
            continue
        if current:
            sections[current].append(line)
    return sections


def _items(lines):
    chunks, chunk = [], []
    for line in lines:
        m = NUMBERED.match(line)
        if m:
            if chunk:
                chunks.append('\n'.join(chunk).strip())
            chunk = [m.group(1)]
        elif chunk:
            chunk.append(line)
    if chunk:
        chunks.append('\n'.join(chunk).strip())
    return chunks


def _normalize(text):
    return re.sub(r'\s+', ' ', URL.sub('', text)).casefold().strip()[:160]


def format_briefings(messages, now=None):
    """Return a text section with preserved original news and links."""
    selected = select_current(messages, now=now)
    if not selected:
        return ('\n\n[삼성전자·SK하이닉스 뉴스 브리핑]\n'
                '최근 24시간 내 유효한 원본 브리핑 없음. '
                '전달된 과거 브리핑은 최신 뉴스로 사용하지 않습니다.')
    seen = set()
    groups = {'삼성전자': [], 'SK하이닉스': []}
    for msg in selected:
        sections = _split_sections(msg['body'])
        for company in groups:
            for item in _items(sections[company]):
                key = _normalize(item)
                if key and key not in seen:
                    seen.add(key)
                    groups[company].append(item)
    lines = ['\n\n[삼성전자·SK하이닉스 뉴스 브리핑 — 수신 메일 원문 발췌]',
             '※ 요약·시사점은 원본 브리핑의 문구를 그대로 인용하며 새 분석을 생성하지 않습니다.']
    for company, items in groups.items():
        lines.append(f'\n[{company}]')
        if not items:
            lines.append('확인된 개별 뉴스 없음')
        else:
            for idx, item in enumerate(items, 1):
                lines.append(f'{idx}. {item}')
    if not any(groups.values()):
        lines.append('\n※ 원본 메일의 항목 구조를 자동 분리하지 못했습니다. 임의 요약은 생성하지 않습니다.')
    return '\n'.join(lines)
