"""
report.py
Part 1
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd


# ==========================================================
# Format
# ==========================================================

def format_price(value):

    if pd.isna(value):

        return "-"

    return f"{value:,.0f}"


def format_percent(value):

    if pd.isna(value):

        return "-"

    return f"{value:.2f}%"


def format_number(value):

    if pd.isna(value):

        return "-"

    return f"{value:.2f}"


def format_market_cap(value):

    if pd.isna(value):

        return "-"

    if value >= 1_000_000_000_000:

        return f"{value/1_000_000_000_000:.2f}T"

    if value >= 1_000_000_000:

        return f"{value/1_000_000_000:.2f}B"

    return f"{value:,.0f}"


# ==========================================================
# Display Table
# ==========================================================

def build_display_table(df):

    table = df.copy()

    columns = {

        "Price": format_price,

        "TargetPrice": format_price,

        "PER": format_number,

        "EPS": format_number,

        "ROE": format_percent,

        "RevenueGrowth": format_percent,

        "EPSGrowth": format_percent,

        "PERGap(%)": format_percent,

        "Upside(%)": format_percent,

        "QuantScore": format_number,

        "MarketCap": format_market_cap,

    }

    for column, formatter in columns.items():

        if column in table.columns:

            table[column] = table[column].apply(
                formatter
            )

    return table


# ==========================================================
# Console Report
# ==========================================================

def print_report(df):

    table = build_display_table(df)

    print("=" * 100)

    print(
        " Semiconductor PER Analysis Report "
    )

    print(
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    print("=" * 100)

    print(
        table.to_string(
            index=False
        )
    )

    print("=" * 100)

# ==========================================================
# Markdown Report
# ==========================================================

def make_markdown_report(df):

    table = build_display_table(
        df
    )

    report = []

    report.append(
        "# Semiconductor PER Report"
    )

    report.append("")

    report.append(
        f"Generated : {datetime.now():%Y-%m-%d %H:%M}"
    )

    report.append("")

    report.append(
        table.to_markdown(
            index=False
        )
    )

    report.append("")

    return "\n".join(
        report
    )


# ==========================================================
# Telegram Message
# ==========================================================

def make_telegram_message(df):

    if df.empty:

        return "No data."

    best = df.iloc[0]

    msg = []

    msg.append(
        "📊 반도체 PER 투자 리포트"
    )

    msg.append("")

    msg.append(
        datetime.now().strftime(
            "🕒 %Y-%m-%d %H:%M"
        )
    )

    msg.append("")

    msg.append(
        f"🏆 투자 1위 : {best['Company']}"
    )

    msg.append(
        f"PER : {best['PER']:.2f}"
    )

    msg.append(
        f"목표가 : {best['TargetPrice']:,.0f}"
    )

    msg.append(
        f"상승여력 : {best['Upside(%)']:.2f}%"
    )

    msg.append(
        f"퀀트점수 : {best['QuantScore']:.2f}"
    )

    msg.append(
        f"투자의견 : {best['Opinion']}"
    )

    msg.append("")

    msg.append(
        "📈 전체 순위"
    )

    msg.append(
        "-------------------------"
    )

    for _, row in df.iterrows():

        msg.append(

            f"{int(row['Rank'])}. "

            f"{row['Company']}"

            f" | Score {row['QuantScore']:.2f}"

        )

    return "\n".join(
        msg
    )


# ==========================================================
# End of report.py
# ==========================================================
