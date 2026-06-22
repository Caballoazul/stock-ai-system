# =====================================================
# samsung_per.py
# 삼성전자 데이터 수집 모듈
# =====================================================

import yfinance as yf


def get_samsung_data():
    """
    삼성전자(005930.KS) 데이터 수집

    Returns:
        dict
    """

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
            "name": "Samsung",
            "ticker": "005930.KS",
            "change_pct": change_pct,
            
            # 가격 지표
            "price": float(price) if price else 0,

            # 가치 지표
            "pe": float(pe) if pe else 0,
            "eps": float(eps) if eps else 0,

            # 성장성 지표
            "eps_growth": float(
                info.get("earningsGrowth") or 0
            ),

            "revenue_growth": float(
                info.get("revenueGrowth") or 0
            ),

            # 수익성 지표
            "roe": float(
                info.get("returnOnEquity") or 0
            )
        }

    except Exception as e:

        print(f"[ERROR] Samsung Data Error : {e}")

        return {
            "name": "Samsung",
            "ticker": "005930.KS",

            "price": 0,
            "pe": 0,
            "eps": 0,

            "eps_growth": 0,
            "revenue_growth": 0,
            "roe": 0
        }


# =====================================================
# 단독 실행 테스트
# =====================================================

if __name__ == "__main__":

    data = get_samsung_data()

    print("\n=== Samsung Data ===\n")

    for k, v in data.items():
        print(f"{k}: {v}")
