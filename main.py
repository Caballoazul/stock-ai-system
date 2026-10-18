"""Time-aware semiconductor reporting (stage 3).

Stage 3 separates morning/afternoon/night execution. Existing Telegram and
Kakao integrations are preserved. Gmail, Telegram deep links and NXT price
feed are NOT implemented yet. The night run deliberately sends nothing until
verified NXT data is available, rather than reporting stale KRX prices.
"""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data
from analysis import build_quant_dataframe, make_analysis
from report import build_market_report, build_valuation_report, build_quant_report
from telegram_sender import send_telegram_message
from kakao_sender import send_kakao_messages

KST = ZoneInfo('Asia/Seoul')
MODES = {'morning', 'afternoon', 'night'}


def resolve_mode():
    mode = os.getenv('REPORT_MODE', '').strip().lower()
    if mode not in MODES:
        raise ValueError('REPORT_MODE must be morning, afternoon, or night')
    return mode


def make_kakao_summary(df, mode):
    title = '미국장 분석' if mode == 'morning' else '한국 정규장 분석'
    values = {}
    for _, row in df.iterrows():
        values[row['Company']] = row
    def price(name, unit):
        row = values.get(name)
        if row is None:
            return '확인 불가'
        try:
            value = float(row['Price'])
            if value <= 0:
                return '확인 불가'
            return f'{value:,.0f}{unit}' if unit == '원' else f'${value:,.2f}'
        except (ValueError, TypeError, KeyError):
            return '확인 불가'
    message = (f'[{title}] {datetime.now(KST):%m/%d}\n'
               f'MU {price("Micron", "USD")} / '
               f'삼성 {price("Samsung", "원")} / '
               f'SK {price("SK Hynix", "원")}\n'
               '※ 가격 기준시각·데이터 지연 확인 필요')
    if len(message) > 180:
        raise ValueError('Kakao summary exceeds 180 characters')
    return message


def main():
    mode = resolve_mode()
    print(f'Report mode: {mode} | KST: {datetime.now(KST).isoformat()}')

    if mode == 'night':
        # yfinance's Korean close is NOT a verified NXT 20:00 final trade.
        # Fail closed: no misleading after-market price notification.
        print('NIGHT_NOT_READY: verified NXT final-price source required; no messages sent')
        return {'mode': mode, 'status': 'pending_nxt_source'}

    stock_data = [get_micron_data(), get_samsung_data(), get_skhynix_data()]
    df = make_analysis(build_quant_dataframe(stock_data))
    title = '08:00 미국장 분석' if mode == 'morning' else '16:30 한국 정규장 분석'
    # Stage 3 uses existing market, valuation and quant sections.
    # These are not yet the final news/forecast/verification report.
    telegram_text = (f'[{title}]\n'
                     f'{datetime.now(KST):%Y-%m-%d %H:%M KST}\n\n'
                     + build_market_report(df) + '\n\n'
                     + build_valuation_report(df) + '\n\n'
                     + build_quant_report(df)
                     + '\n\n※ 마이크론 PER 비교는 참고 시나리오이며 매매 권고가 아닙니다.')
    kakao_text = make_kakao_summary(df, mode)
    failed = False
    try:
        send_telegram_message(telegram_text)
        print('Telegram: OK')
    except Exception as exc:
        failed = True
        print(f'Telegram: FAIL ({type(exc).__name__})')
    try:
        send_kakao_messages([kakao_text])
        print('Kakao: OK')
    except Exception as exc:
        failed = True
        print(f'Kakao: FAIL ({type(exc).__name__})')
    if failed:
        raise SystemExit(1)
    return {'mode': mode, 'status': 'sent_stage3'}


if __name__ == '__main__':
    main()
