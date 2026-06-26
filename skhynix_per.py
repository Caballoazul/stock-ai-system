"""
skhynix_per.py
"""

import yfinance as yf


# ==========================================================
# SK Hynix
# ==========================================================

def get_skhynix_data():

    try:

        ticker = yf.Ticker("000660.KS")

        info = ticker.info

        hist = ticker.history(period="2d")

        close_today = float(hist["Close"].iloc[-1])
        close_yesterday = float(hist["Close"].iloc[-2])

        change_pct = (
            (close_today / close_yesterday) - 1
        ) * 100

        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or 0
        )

        per = (
            info.get("forwardPE")
            or info.get("trailingPE")
            or 0
        )

        eps = (
            info.get("trailingEps")
            or info.get("epsCurrentYear")
            or 0
        )

        revenue_growth = (
            info.get("revenueGrowth")
            or 0
        )

        eps_growth = (
            info.get("earningsGrowth")
            or 0
        )

        roe = (
            info.get("returnOnEquity")
            or 0
        )

        market_cap = (
            info.get("marketCap")
            or 0
        )

        return {

            "Company": "SK Hynix",

            "Ticker": "000660.KS",

            "Price": float(price),

            "ChangePct": round(
                change_pct,
                2,
            ),

            "PER": float(per),

            "EPS": float(eps),

            "RevenueGrowth": float(
                revenue_growth
            ),

            "EPSGrowth": float(
                eps_growth
            ),

            "ROE": float(roe),

            "MarketCap": float(
                market_cap
            ),

        }

    except Exception as e:

        print(
            f"[SK Hynix ERROR] {e}"
        )

        return {

            "Company": "SK Hynix",

            "Ticker": "000660.KS",

            "Price": 0,

            "ChangePct": 0,

            "PER": 0,

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

    data = get_skhynix_data()

    for k, v in data.items():

        print(f"{k:15} : {v}")
