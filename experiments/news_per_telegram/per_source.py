"""Independent PER collection; no legacy reporting/sending imports."""
from datetime import datetime
from math import isfinite
from zoneinfo import ZoneInfo

COMPANIES = (("마이크론", "MU", "USD"), ("삼성전자", "005930.KS", "KRW"), ("SK하이닉스", "000660.KS", "KRW"))

def _worker(ticker, pipe):
    try:
        import yfinance as yf
        from curl_cffi.requests import Session
        with Session(impersonate="chrome", timeout=8) as session:
            info = yf.Ticker(ticker, session=session).get_info()
        pipe.send((True, info))
    except Exception as exc:
        pipe.send((False, type(exc).__name__))
    finally:
        pipe.close()

def fetch_bounded(ticker, seconds=25):
    """Bound all provider requests/retries to 25 seconds per company."""
    import multiprocessing as mp
    ctx = mp.get_context('spawn')
    parent, child = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_worker, args=(ticker, child))
    process.start()
    child.close()
    try:
        if not parent.poll(seconds):
            raise TimeoutError('PER provider did not finish within time budget')
        ok, value = parent.recv()
        if not ok:
            raise RuntimeError(value)
        return value
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=2)
        parent.close()

def number(value):
    if isinstance(value, (bool, str)) or value is None:
        return None
    try:
        value = float(value)
        return value if isfinite(value) and value > 0 else None
    except (TypeError, ValueError, OverflowError):
        return None

def normalize(name, ticker, currency, info, at):
    row = dict(company=name, ticker=ticker, source="Yahoo Finance / yfinance",
               collected_at_kst=at, period_verified=False,
               trailing_pe=None, forward_pe=None, status="unavailable", error=None)
    if not isinstance(info, dict) or info.get("currency") != currency:
        row.update(status="error", error="CurrencyMissingOrMismatch")
        return row
    row.update(trailing_pe=number(info.get("trailingPE")), forward_pe=number(info.get("forwardPE")))
    count = sum(row[k] is not None for k in ("trailing_pe", "forward_pe"))
    row["status"] = ("unavailable", "partial", "ok")[count]
    return row

def collect(fetch=None):
    """Bounded one attempt per ticker; never reuse old data as a live value."""
    rows = []
    for name, ticker, currency in COMPANIES:
        at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
        try:
            if fetch is None:
                info = fetch_bounded(ticker)
            else:
                info = fetch(ticker)
            row = normalize(name, ticker, currency, info, at)
        except Exception as exc:
            row = normalize(name, ticker, currency, {}, at)
            row.update(status="error", error=type(exc).__name__)
        rows.append(row)
    return rows
