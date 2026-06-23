import yfinance as yf


# =====================================================
# 삼성전자 보통주 데이터
# =====================================================
def get_samsung_common_data():

    try:
        ticker = yf.Ticker("005930.KS")
        info = ticker.info

        hist = ticker.history(period="2d")

        close_today = hist["Close"].iloc[-1]
        close_yesterday = hist["Close"].iloc[-2]

        change_pct = (close_today / close_yesterday - 1) * 100

        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0

        pe = info.get("forwardPE") or info.get("trailingPE") or 0

        eps = info.get("trailingEps") or info.get("epsCurrentYear") or 0

        return {
            "name": "Samsung Common",
            "ticker": "005930.KS",
            "price": float(price),
            "pe": float(pe),
            "eps": float(eps),

            "change_pct": float(change_pct),

            "eps_growth": float(info.get("earningsGrowth") or 0),
            "revenue_growth": float(info.get("revenueGrowth") or 0),
            "roe": float(info.get("returnOnEquity") or 0)
        }

    except Exception as e:

        print("[ERROR] Samsung Common:", e)

        return {
            "name": "Samsung Common",
            "ticker": "005930.KS",
            "price": 0,
            "pe": 0,
            "eps": 0,
            "change_pct": 0,
            "eps_growth": 0,
            "revenue_growth": 0,
            "roe": 0
        }


# =====================================================
# 삼성전자 우선주 데이터 (핵심 추가)
# =====================================================
def get_samsung_preferred_data():

    try:
        ticker = yf.Ticker("005935.KS")
        info = ticker.info

        hist = ticker.history(period="2d")

        close_today = hist["Close"].iloc[-1]
        close_yesterday = hist["Close"].iloc[-2]

        change_pct = (close_today / close_yesterday - 1) * 100

        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0

        # ⚠️ 우선주는 EPS 직접 신뢰 어려움 → 보통주 EPS 사용 구조
        eps = None

        return {
            "name": "Samsung Preferred",
            "ticker": "005935.KS",
            "price": float(price),
            "pe": 0,   # analysis.py에서 보정 계산
            "eps": 0,  # common EPS로 대체 처리 필요

            "change_pct": float(change_pct),

            "eps_growth": 0,
            "revenue_growth": 0,
            "roe": 0
        }

    except Exception as e:

        print("[ERROR] Samsung Preferred:", e)

        return {
            "name": "Samsung Preferred",
            "ticker": "005935.KS",
            "price": 0,
            "pe": 0,
            "eps": 0,
            "change_pct": 0,
            "eps_growth": 0,
            "revenue_growth": 0,
            "roe": 0
        }


# =====================================================
# 단독 테스트
# =====================================================
if __name__ == "__main__":

    common = get_samsung_common_data()
    preferred = get_samsung_preferred_data()

    print("\n=== Samsung Common ===")
    print(common)

    print("\n=== Samsung Preferred ===")
    print(preferred)
