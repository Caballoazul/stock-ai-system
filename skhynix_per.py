"""
skhynix_per.py
Part 1
"""

from __future__ import annotations

import yfinance as yf


# ==========================================================
# Utility
# ==========================================================

def safe_float(value, default=0.0):

    try:

        if value is None:
            return default

        return float(value)

    except Exception:

        return default


def get_info_value(info, *keys):

    for key in keys:

        value = info.get(key)

        if value not in (
            None,
            "",
        ):

            return value

    return 0


# ==========================================================
# SK Hynix
# ==========================================================

def get_skhynix_data():

    try:

        ticker = yf.Ticker("000660.KS")

        info = ticker.info

        hist = ticker.history(
            period="5d",
            auto_adjust=False,
        )

        if len(hist) >= 2:

            close_today = safe_float(
                hist["Close"].iloc[-1]
            )

            close_yesterday = safe_float(
                hist["Close"].iloc[-2]
            )

            if close_yesterday != 0:

                change_pct = (
                    (
                        close_today
                        - close_yesterday
                    )
                    / close_yesterday
                ) * 100

            else:

                change_pct = 0.0

        else:

            change_pct = 0.0

        price = safe_float(
            get_info_value(
                info,
                "currentPrice",
                "regularMarketPrice",
            )
        )

        per = safe_float(
            get_info_value(
                info,
                "forwardPE",
                "trailingPE",
            )
        )

        eps = safe_float(
            get_info_value(
                info,
                "trailingEps",
                "epsCurrentYear",
            )
        )

        revenue_growth = safe_float(
            get_info_value(
                info,
                "revenueGrowth",
            )
        )

        eps_growth = safe_float(
            get_info_value(
                info,
                "earningsGrowth",
            )
        )

        roe = safe_float(
            get_info_value(
                info,
                "returnOnEquity",
            )
        )

        market_cap = safe_float(
            get_info_value(
                info,
                "marketCap",
            )
        )

        return {

            "Company": "SK Hynix",

            "Ticker": "000660.KS",

            "Price": round(price, 2),

            "ChangePct": round(
                change_pct,
                2,
            ),

            "PER": round(per, 2),

            "EPS": round(eps, 2),

            "RevenueGrowth": round(
                revenue_growth,
                4,
            ),

            "EPSGrowth": round(
                eps_growth,
                4,
            ),

            "ROE": round(
                roe,
                4,
            ),

            "MarketCap": market_cap,

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

    print()

    for key, value in data.items():

        print(
            f"{key:15} : {value}"
        )


# ==========================================================
# End of skhynix_per.py
# ==========================================================
