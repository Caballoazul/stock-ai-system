"""Local offline tests; no account credentials or network needed."""
from datetime import datetime
from zoneinfo import ZoneInfo
from briefing_integration import format_briefings, select_current

now = datetime(2026, 10, 18, 17, 0, tzinfo=ZoneInfo('Asia/Seoul'))
old = {'subject': 'Fwd: 2026-09-23 06:00 삼성전자·SK하이닉스 뉴스 브리핑',
       'body': '[삼성전자]\n1. 오래된 기사\n① 핵심 내용: 테스트',
       'received_at': now.isoformat()}
new = {'subject': '2026-10-18 16:00 삼성전자·SK하이닉스 뉴스 브리핑',
       'body': '[삼성전자]\n1. 새 기사\n① 핵심 내용: 삼성 관련\n③ 원문 링크: https://example.com/a\n'
               '[SK하이닉스]\n1. SK 기사\n② 의미: SK 관련',
       'received_at': now.isoformat()}
assert select_current([old], now=now) == []
output = format_briefings([new, new, old], now=now)
assert '새 기사' in output and 'SK 기사' in output
assert '오래된 기사' not in output
assert output.count('1. 새 기사') == 1
assert 'https://example.com/a' in output
print('BRIEFING_INTEGRATION_TEST=PASS')
