# =====================================================
# samsung_per.py
# 삼성전자 데이터 수집 모듈
# =====================================================

import yfinance as yf


# =====================================================
# 삼성전자 보통주
# =====================================================
def get_samsung_common_data():

    try:

        ticker = yf.Ticker("005930.KS")

        info = ticker.info

        hist = ticker.history(period="2d")

        close_today = hist["Close"].iloc[-1]
        close_yesterday = hist["Close"].iloc[-2]

        change_pct = (
            close_today / close_yesterday - 1
        ) * 100

        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or 0
        )

        pe = (
            info.get("forwardPE")
            or info.get("trailingPE")
            or 0
        )

        eps = (
            info.get("trailingEps")
            or info.get("epsCurrentYear")
            or 0
        )

        return {
            "name": "Samsung Common",
            "ticker": "005930.KS",

            "price": float(price),
            "pe": float(pe),
            "eps": float(eps),

            "change_pct": float(change_pct),

            "eps_growth": float(
                info.get("earningsGrowth") or 0
            ),

            "revenue_growth": float(
                info.get("revenueGrowth") or 0
            ),

            "roe": float(
                info.get("returnOnEquity") or 0
            ),

            "market_cap": float(
                info.get("marketCap") or 0
            )
        }

    except Exception as e:

        print(f"[ERROR] Samsung Common : {e}")

        return {
            "name": "Samsung Common",
            "ticker": "005930.KS",

            "price": 0,
            "pe": 0,
            "eps": 0,

            "change_pct": 0,

            "eps_growth": 0,
            "revenue_growth": 0,
            "roe": 0,

            "market_cap": 0
        }


# =====================================================
# 삼성전자 우선주
# =====================================================
def get_samsung_preferred_data(common_eps):

    try:

        ticker = yf.Ticker("005935.KS")

        info = ticker.info

        hist = ticker.history(period="2d")

        close_today = hist["Close"].iloc[-1]
        close_yesterday = hist["Close"].iloc[-2]

        change_pct = (
            close_today / close_yesterday - 1
        ) * 100

        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or 0
        )

        # -------------------------------------------------
        # 우선주 PER 계산
        # -------------------------------------------------

        if common_eps > 0:
            pe = price / common_eps
        else:
            pe = 0

        return {
            "name": "Samsung Preferred",
            "ticker": "005935.KS",

            "price": float(price),
            "pe": float(pe),
            "eps": float(common_eps),

            "change_pct": float(change_pct),

            "market_cap": float(
                info.get("marketCap") or 0
            )
        }

    except Exception as e:

        print(f"[ERROR] Samsung Preferred : {e}")

        return {
            "name": "Samsung Preferred",
            "ticker": "005935.KS",

            "price": 0,
            "pe": 0,
            "eps": 0,

            "change_pct": 0,

            "market_cap": 0
        }


# =====================================================
# 삼성전자 통합 시가총액
# =====================================================
def get_samsung_total_market_cap():

    common = get_samsung_common_data()

    preferred = get_samsung_preferred_data(
        common["eps"]
    )

    return (
        common["market_cap"]
        + preferred["market_cap"]
    )


# =====================================================
# 단독 실행 테스트
# =====================================================
if __name__ == "__main__":

    common = get_samsung_common_data()

    preferred = get_samsung_preferred_data(
        common["eps"]
    )

    print("\n===== 삼성전자 보통주 =====")
    for k, v in common.items():
        print(f"{k}: {v}")

    print("\n===== 삼성전자 우선주 =====")
    for k, v in preferred.items():
        print(f"{k}: {v}")

    print("\n===== 삼성전자 통합 시가총액 =====")
    print(
        f"{get_samsung_total_market_cap():,.0f}"
    )
