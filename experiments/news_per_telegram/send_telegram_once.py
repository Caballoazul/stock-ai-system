"""One explicitly authorized Telegram test; no Gmail or Kakao send."""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
from urllib.parse import quote
from per_source import collect

class Report(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tag = None
        self.buf = []
        self.section = ''
        self.title = ''
        self.sections = {}
    def handle_starttag(self, tag, attrs):
        if tag in ('h1', 'h2', 'p') and self.tag is None:
            self.tag, self.buf = tag, []
    def handle_data(self, data):
        if self.tag:
            self.buf.append(data)
    def handle_endtag(self, tag):
        if tag == self.tag:
            value = ' '.join(''.join(self.buf).split())
            if tag == 'h1':
                self.title = value
            elif tag == 'h2':
                self.section = value
            elif self.section:
                self.sections.setdefault(self.section, []).append(value)
            self.tag, self.buf = None, []
    def section_values(self, marker):
        return next((v for k, v in self.sections.items() if marker in k), [])

def fmt(value):
    return '미확인' if value is None else f'{value:.2f}배'

def compose(source, rows, gmail_url):
    report = Report()
    report.feed(source)
    if not report.title:
        raise ValueError('Report title missing')
    core = report.section_values('核心') or report.section_values('핵심 3줄')
    if not core:
        raise ValueError('Core summary section missing; refuse to send an empty summary')
    lines = ['🧪 <b>통합 브리핑 시험 발송 · 1회</b>', html.escape(report.title),
             '', '<b>① 핵심 뉴스</b>']
    lines += ['• ' + html.escape(v) for v in core[:3]]
    for marker, label in (('②', '삼성전자'), ('③', 'SK하이닉스')):
        values = report.section_values(marker)
        # Preserve complete source wording and distinguish original analysis.
        selected = next((v for v in values if '[해석' in v), None)
        if selected:
            lines += ['', '<b>' + label + ' — 원본 보고서 해석</b>', html.escape(selected)]
    lines += ['', '<b>② 3사 PER 비교 — 이번 실행에서 조회</b>',
              '기업 | 과거 실적 PER | 예상 PER']
    for row in rows:
        lines.append(html.escape(f"{row['company']} | {fmt(row['trailing_pe'])} | {fmt(row['forward_pe'])}"))
    lines += ['출처: Yahoo Finance / yfinance',
              '수집 시도(KST): ' + html.escape(rows[0]['collected_at_kst']) + ' ~ ' + html.escape(rows[-1]['collected_at_kst']),
              'EPS 회계기간·예상기간 일치 미검증. 없는 값은 미확인.',
              '', '<b>③ 상세 보고서</b>',
              '<a href="' + html.escape(gmail_url, quote=True) + '">📧 Gmail 원문 보고서 열기</a>',
              '', '뉴스는 오늘 15:50 원본에서 발췌. PER는 별도 조회값이며 원본 메일에 추가된 값은 아닙니다.']
    message = '\n'.join(lines)
    if len(message) > 3900:
        raise ValueError('Message exceeds conservative Telegram size limit')
    return message

def send_once(message, post=None):
    token = os.environ.get('TELEGRAM_TOKEN', '')
    chat = os.environ.get('TELEGRAM_CHAT_ID', '')
    if not token or not chat:
        raise RuntimeError('TELEGRAM_CONFIG_MISSING')
    if post is None:
        import requests
        post = requests.post
    # Exactly one POST; ambiguous timeout never retries automatically.
    try:
        response = post('https://api.telegram.org/bot' + token + '/sendMessage',
                        json={'chat_id': chat, 'text': message, 'parse_mode':'HTML',
                              'disable_web_page_preview':True}, timeout=30)
        data = response.json()
    except Exception:
        raise RuntimeError('TELEGRAM_RESPONSE_UNCONFIRMED_DO_NOT_RETRY') from None
    if response.status_code != 200 or not data.get('ok'):
        raise RuntimeError('TELEGRAM_API_REJECTED code=' + str(data.get('error_code', response.status_code)))
    result = data.get('result', {})
    if not result.get('message_id') or str(result.get('chat', {}).get('id')) != str(chat):
        raise RuntimeError('TELEGRAM_RECEIPT_UNCONFIRMED_DO_NOT_RETRY')
    return {'status':'sent', 'message_id':result['message_id'], 'telegram_date':result.get('date'),
            'recipient_matches_config':True}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', required=True)
    ap.add_argument('--message-id', required=True)
    ap.add_argument('--send-once', action='store_true')
    ap.add_argument('--output', default='test-results')
    args = ap.parse_args()
    if args.send_once and os.environ.get('GITHUB_RUN_ATTEMPT', '1') != '1':
        raise RuntimeError('RERUN_SEND_DISABLED')
    source = Path(args.report).read_text(encoding='utf-8-sig')
    rows = collect()
    account = os.environ.get('GMAIL_ADDRESS', '').strip()
    if not account:
        raise RuntimeError('GMAIL_ACCOUNT_LINK_CONFIG_MISSING')
    url = 'https://mail.google.com/mail/u/?authuser=' + quote(account, safe='') + '#all/' + quote(args.message_id, safe='')
    message = compose(source, rows, url)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output/'telegram_preview.html').write_text('<!doctype html><meta charset="utf-8"><div style="white-space:pre-wrap">' + message + '</div>', encoding='utf-8')
    (output/'per_collection.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    print('PREVIEW_VALIDATED chars=' + str(len(message)))
    print('PER_COLLECTION_STATUS=' + ','.join(r['company'] + ':' + r['status'] for r in rows))
    receipt = {'status':'dry_run', 'report_sha256':hashlib.sha256(source.encode()).hexdigest()}
    if args.send_once:
        receipt.update(send_once(message))
        print('TELEGRAM_SEND_OK message_id=' + str(receipt['message_id']))
    (output/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
