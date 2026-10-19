"""Collect valuation data without changing legacy report senders."""
from datetime import datetime
from math import isfinite
from zoneinfo import ZoneInfo
import yfinance as yf

KST = ZoneInfo('Asia/Seoul')
FIELDS = {
    'trailing_pe': 'trailingPE', 'forward_pe': 'forwardPE',
    'trailing_eps': 'trailingEps', 'forward_eps': 'forwardEps',
    'roe': 'returnOnEquity', 'revenue_growth': 'revenueGrowth',
    'earnings_growth': 'earningsGrowth', 'market_cap': 'marketCap',
}
SYMBOLS = {'Micron': 'MU', 'Samsung': '005930.KS', 'SK Hynix': '000660.KS'}


def finite_number(value):
    if value is None or isinstance(value, (str, bool)):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if isfinite(number) else None


def normalize(info, name, ticker, collected_at=None):
    """Preserve source values, rejecting invalid multiples and currencies."""
    collected_at = collected_at or datetime.now(KST).isoformat(timespec='seconds')
    result = {
        'ticker': ticker, 'source': 'Yahoo Finance / yfinance',
        'collected_at_kst': collected_at, 'currency': None,
        **{key: None for key in FIELDS},
        'period_verified': False, 'status': 'unavailable', 'error': None,
    }
    if not isinstance(info, dict):
        result['status'] = 'error'
        result['error'] = 'InvalidInfoResponse'
        return result
    currency = info.get('currency')
    result['currency'] = currency if isinstance(currency, str) else None
    expected_currency = 'USD' if name == 'Micron' else 'KRW'
    if currency != expected_currency:
        result['status'] = 'error'
        result['error'] = 'CurrencyMissingOrMismatch'
        return result
    for field, source_field in FIELDS.items():
        value = finite_number(info.get(source_field))
        if value is not None and field in ('trailing_pe', 'forward_pe', 'market_cap') and value <= 0:
            value = None
        if field == 'market_cap' and value is not None:
            value = int(value) if value.is_integer() else None
        result[field] = value
    count = sum(result[field] is not None for field in FIELDS)
    result['status'] = 'ok' if count == len(FIELDS) else ('partial' if count else 'unavailable')
    return result


def collect_one(name, ticker):
    try:
        info = yf.Ticker(ticker).info
        return normalize(info, name, ticker)
    except Exception as exc:
        result = normalize(None, name, ticker)
        result['error'] = type(exc).__name__
        return result


def collect_valuations():
    return {name: collect_one(name, ticker) for name, ticker in SYMBOLS.items()}
