"""
main.py
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
    make_telegram_messages,
)

from telegram_sender import (
    send_telegram_message,
)


# ==========================================================
# Load Data
# ==========================================================

def load_stock_data():

    return [

        get_micron_data(),

        get_samsung_data(),

        get_skhynix_data(),

    ]


# ==========================================================
# Main
# ==========================================================

def main():

    print("=" * 80)

    print("Semiconductor PER Analysis")

    print("=" * 80)

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

    messages = make_telegram_messages(
        result
    )

    print()

    print(
        f"Best Company : {summary['BestCompany']}"
    )

    print(
        f"Quant Score  : {summary['BestScore']}"
    )

    try:

        for message in messages:

            send_telegram_message(
                message
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
