"""
report.py
Part 1
"""

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


# ==========================================================
# Display Table
# ==========================================================

def build_display_table(df):

    table = df.copy()

    if "Price" in table.columns:
        table["Price"] = table["Price"].apply(
            format_price
        )

    if "TargetPrice" in table.columns:
        table["TargetPrice"] = table[
            "TargetPrice"
        ].apply(
            format_price
        )

    if "PER" in table.columns:
        table["PER"] = table["PER"].apply(
            format_number
        )

    if "PERGap(%)" in table.columns:
        table["PERGap(%)"] = table[
            "PERGap(%)"
        ].apply(
            format_percent
        )

    if "Upside(%)" in table.columns:
        table["Upside(%)"] = table[
            "Upside(%)"
        ].apply(
            format_percent
        )

    if "QuantScore" in table.columns:
        table["QuantScore"] = table[
            "QuantScore"
        ].apply(
            format_number
        )

    return table


# ==========================================================
# Console Print
# ==========================================================

def print_report(df):

    table = build_display_table(df)

    print("=" * 90)
    print(" Semiconductor PER Analysis ")
    print("=" * 90)

    print(table.to_string(index=False))

    print("=" * 90)

# ==========================================================
# Markdown Report
# ==========================================================

def make_markdown_report(df):

    table = build_display_table(df)

    lines = []

    lines.append("# Semiconductor PER Report")
    lines.append("")
    lines.append(table.to_markdown(index=False))
    lines.append("")

    return "\n".join(lines)


# ==========================================================
# Telegram Message
# ==========================================================

def make_telegram_message(df):

    if df.empty:
        return "No data."

    best = df.iloc[0]

    msg = []

    msg.append("📊 반도체 PER 투자 리포트")
    msg.append("")
    msg.append(f"🏆 1위 : {best['Company']}")
    msg.append(f"PER : {best['PER']:.2f}")
    msg.append(f"Quant Score : {best['QuantScore']:.2f}")
    msg.append(f"Target Price : {best['TargetPrice']:,.0f}")
    msg.append(f"Upside : {best['Upside(%)']:.2f}%")
    msg.append(f"Opinion : {best['Opinion']}")
    msg.append("")
    msg.append("전체 순위")
    msg.append("-----------------------")

    for _, row in df.iterrows():

        msg.append(
            f"{int(row['Rank'])}. "
            f"{row['Company']} "
            f"({row['QuantScore']:.2f})"
        )

    return "\n".join(msg)


# ==========================================================
# HTML Report
# ==========================================================

def make_html_report(df):

    table = build_display_table(df)

    html = []

    html.append("<html>")
    html.append("<body>")
    html.append("<h2>Semiconductor PER Report</h2>")

    html.append(
        table.to_html(
            index=False,
            border=1,
        )
    )

    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


# ==========================================================
# End of report.py
# ==========================================================
