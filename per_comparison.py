"""Display source-labelled Yahoo valuation data; no target prices."""
from math import isfinite

COMPANIES = (("Micron", "마이크론"), ("Samsung", "삼성전자"), ("SK Hynix", "SK하이닉스"))

def _fmt(value):
    if isinstance(value, bool):
        return "미확인"
    try:
        number = float(value)
        return f"{number:.2f}배" if isfinite(number) and number > 0 else "미확인"
    except (TypeError, ValueError, OverflowError):
        return "미확인"

def render_per_comparison(valuations):
    if not isinstance(valuations, dict):
        raise TypeError("valuations must be a dictionary")
    lines = ["[3사 PER 비교 — Yahoo 참고 지표]",
             "기업 | Trailing PER | Forward PER | 수집상태"]
    for key, label in COMPANIES:
        row = valuations.get(key)
        row = row if isinstance(row, dict) else {}
        lines.append(f"{label} | {_fmt(row.get('trailing_pe'))} | {_fmt(row.get('forward_pe'))} | {row.get('status', '미확인')}")
    lines += [
        "출처: Yahoo Finance / yfinance.",
        "주의: 기업별 EPS 회계기간 및 Forward 추정기간은 독립 검증되지 않았습니다.",
        "직접적인 저평가 판단 또는 목표주가 산출에 사용하지 않습니다."
    ]
    return "\n".join(lines)
