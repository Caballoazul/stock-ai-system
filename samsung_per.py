"""
samsung_per.py
"""

import yfinance as yf


# ==========================================================
# Samsung Electronics
# ==========================================================

def get_samsung_data():

    try:

        common = yf.Ticker("005930.KS")
        preferred = yf.Ticker("005935.KS")

        common_info = common.info
        preferred_info = preferred.info

        hist = common.history(period="2d")

        close_today = float(hist["Close"].iloc[-1])
        close_yesterday = float(hist["Close"].iloc[-2])

        change_pct = (
            (close_today / close_yesterday) - 1
        ) * 100

        common_price = (
            common_info.get("currentPrice")
            or common_info.get("regularMarketPrice")
            or 0
        )

        preferred_price = (
            preferred_info.get("currentPrice")
            or preferred_info.get("regularMarketPrice")
            or 0
        )

        per = (
            common_info.get("forwardPE")
            or common_info.get("trailingPE")
            or 0
        )

        eps = (
            common_info.get("trailingEps")
            or common_info.get("epsCurrentYear")
            or 0
        )

        revenue_growth = (
            common_info.get("revenueGrowth")
            or 0
        )

        eps_growth = (
            common_info.get("earningsGrowth")
            or 0
        )

        roe = (
            common_info.get("returnOnEquity")
            or 0
        )

        common_market_cap = (
            common_info.get("marketCap")
            or 0
        )

        preferred_market_cap = (
            preferred_info.get("marketCap")
            or 0
        )

        total_market_cap = (
            common_market_cap
            + preferred_market_cap
        )

        preferred_per = (
            preferred_price / eps
            if eps > 0
            else 0
        )

        return {

            "Company": "Samsung",

            "Ticker": "005930.KS",

            "Price": float(common_price),

            "PreferredPrice": float(
                preferred_price
            ),

            "ChangePct": round(
                change_pct,
                2,
            ),

            "PER": float(per),

            "PreferredPER": round(
                preferred_per,
                2,
            ),

            "EPS": float(eps),

            "RevenueGrowth": float(
                revenue_growth
            ),

            "EPSGrowth": float(
                eps_growth
            ),

            "ROE": float(roe),

            "MarketCap": float(
                total_market_cap
            ),

        }

    except Exception as e:

        print(
            f"[Samsung ERROR] {e}"
        )

        return {

            "Company": "Samsung",

            "Ticker": "005930.KS",

            "Price": 0,

            "PreferredPrice": 0,

            "ChangePct": 0,

            "PER": 0,

            "PreferredPER": 0,

            "EPS": 0,

            "RevenueGrowth": 0,

            "EPSGrowth": 0,

            "ROE": 0,

            "MarketCap": 0,

        }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    data = get_samsung_data()

    for k, v in data.items():

        print(f"{k:18} : {v}")
