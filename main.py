"""Semiconductor report: independent Telegram and KakaoTalk delivery."""
from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data
from analysis import build_quant_dataframe, make_analysis, build_summary
from report import print_report, make_telegram_messages
from telegram_sender import send_telegram_message
from kakao_sender import send_kakao_messages


def load_stock_data():
    return [get_micron_data(), get_samsung_data(), get_skhynix_data()]


def main():
    print('=' * 80)
    print('Semiconductor PER Analysis')
    print('=' * 80)

    df = build_quant_dataframe(load_stock_data())
    result = make_analysis(df)
    summary = build_summary(result)
    print_report(result)
    messages = make_telegram_messages(result)
    print(f"Best Company : {summary['BestCompany']}")
    print(f"Quant Score  : {summary['BestScore']}")

    telegram_failed = False
    for index, message in enumerate(messages, 1):
        try:
            send_telegram_message(message)
        except Exception as exc:
            telegram_failed = True
            print(f'Telegram report {index} failed: {type(exc).__name__}')
    print('Telegram Send : FAIL' if telegram_failed else 'Telegram Send : OK')

    kakao_failed = False
    try:
        send_kakao_messages(messages)
    except Exception as exc:
        kakao_failed = True
        # Do not print exception details that might contain credentials.
        error_code = str(exc)
        if not error_code.startswith(('KAKAO_', 'GITHUB_SECRET_')):
            error_code = type(exc).__name__
        print(f'Kakao Send : FAIL ({error_code})')
        try:
            send_telegram_message(
                '⚠️ [카카오톡 보고서 발송 장애]\n'
                f'오류 유형: {error_code}\n'
                '텔레그램 보고서는 별도로 발송했습니다.\n'
                'GitHub Actions 실행 기록을 확인해주세요.'
            )
            print('Telegram Kakao failure alert : OK')
        except Exception:
            print('Telegram Kakao failure alert : FAIL')

    if telegram_failed or kakao_failed:
        raise SystemExit(1)
    return result


if __name__ == '__main__':
    main()
