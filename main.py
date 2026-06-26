"""
main.py
Part 1
"""

from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data

from analysis import (
    build_quant_dataframe,
    make_analysis,
    build_summary,
)

from report import (
    print_report,
    make_html_report,
    make_telegram_message,
)

from telegram_sender import (
    send_telegram_message,
)


# ==========================================================
# Load Data
# ==========================================================

def load_stock_data():

    stocks = []

    stocks.append(
        get_micron_data()
    )

    stocks.append(
        get_samsung_data()
    )

    stocks.append(
        get_skhynix_data()
    )

    return stocks


# ==========================================================
# Main
# ==========================================================

def main():

    print("=" * 100)

    print(
        "Semiconductor PER Analysis"
    )

    print("=" * 100)

    stock_data = load_stock_data()

    df = build_quant_dataframe(
        stock_data
    )

    result = make_analysis(
        df
    )

    summary = build_summary(
        result
    )

    print_report(
        result
    )

    html_report = make_html_report(
        result
    )

    telegram_message = make_telegram_message(
        result
    )

    print()

    print("Best Company")

    print(
        summary["BestCompany"]
    )

    print("Quant Score")

    print(
        summary["BestScore"]
    )

    try:

        send_telegram_message(
            telegram_message
        )

        print()

        print(
            "Telegram Send : OK"
        )

    except Exception as e:

        print()

        print(
            "Telegram Send : FAIL"
        )

        print(e)

    return result


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()


# ==========================================================
# End of main.py
# ==========================================================
