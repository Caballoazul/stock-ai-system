        f"가장 저평가 : "

        f"{company_map[best['Company']]}"

    )

    report.append(

        f"가장 고평가 : "

        f"{company_map[worst['Company']]}"

    )

    report.append("")

    report.append(

        f"투자 의견 : {best['Opinion']}"

    )

    report.append("")

    report.append(

        "오늘의 한 줄 결론"

    )

    report.append("")

    report.append(

        f"Micron PER "

        f"{format_number(micron['PER'])}배를 "

        f"기준으로 비교하면 "

        f"{company_map[best['Company']]}의 "

        f"상대가치가 가장 높습니다."

    )

    return "\n".join(

        report

    )

# ==========================================================
# Telegram
# ==========================================================

def make_telegram_messages(df):

    return [

        build_market_report(df),

        build_valuation_report(df),

        build_quant_report(df),

        build_ai_report(df),

    ]


# ==========================================================
# Console
# ==========================================================

def print_report(df):

    messages = make_telegram_messages(

        df

    )

    for idx, message in enumerate(

        messages,

        start=1,

    ):

        print("=" * 80)

        print(

            f"Report {idx}"

        )

        print("=" * 80)

        print(message)

        print()


# ==========================================================
# Backward Compatibility
# ==========================================================

def make_telegram_message(df):

    """

    기존 main.py와의 호환을 위한 함수

    """

    return "\n\n".join(

        make_telegram_messages(df)

    )


# ==========================================================
# End of report.py
# ==========================================================
