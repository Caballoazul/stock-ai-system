"""Manual smoke test. Only metadata printed; no email contents in Actions logs."""
from gmail_reader import fetch_recent_briefings


def main():
    messages = fetch_recent_briefings()
    print(f'GMAIL_READER_MATCHES={len(messages)}')
    for idx, item in enumerate(messages, 1):
        print(f'MESSAGE_{idx}_DATE={item["received_at"]}')
        print(f'MESSAGE_{idx}_SUBJECT={item["subject"]}')
        print(f'MESSAGE_{idx}_BODY_CHARS={len(item["body"])}')
    if not messages:
        print('최근 24시간 이내 제목에 삼성전자·SK하이닉스 뉴스 브리핑이 포함된 메일이 없습니다.')


if __name__ == '__main__':
    main()
