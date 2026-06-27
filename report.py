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

    return f"{value:,.0f}원"


def format_usd(value):

    if pd.isna(value):

        return "-"

    return f"${value:,.2f}"


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
# Company
# ==========================================================

def get_company(

    df,

    company,

):

    row = df[

        df["Company"] == company

    ]

    if row.empty:

        return None

    return row.iloc[0]


# ==========================================================
# Market Report
# ==========================================================

def build_market_report(df):

    micron = get_company(

        df,

        "Micron",

    )

    samsung = get_company(

        df,

        "Samsung",

    )

    sk = get_company(

        df,

        "SK Hynix",

    )

    report = []

    report.append(

        "📊 반도체 PER 투자 리포트"

    )

    report.append(

        "━━━━━━━━━━━━━━━━━━━━━━━━"

    )

    report.append("")

    report.append(

        f"📅 {datetime.now():%Y-%m-%d %H:%M}"

    )

    report.append("")

    report.append(

        "🇺🇸 Micron"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append(

        f"PER         {format_number(micron['PER'])}"

    )

    report.append(

        f"주가        {format_usd(micron['Price'])}"

    )

    report.append(

        f"전일대비    {format_percent(micron['ChangePct'])}"

    )

    report.append("")

    report.append(

        "🇰🇷 삼성전자"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append(

        f"PER         {format_number(samsung['PER'])}"

    )

    report.append(

        f"주가        {format_price(samsung['Price'])}"

    )

    report.append(

        f"보정 PER    {format_number(samsung['AdjustedPER'])}"

    )

    report.append("")

    report.append(

        "🇰🇷 SK하이닉스"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append(

        f"PER         {format_number(sk['PER'])}"

    )

    report.append(

        f"주가        {format_price(sk['Price'])}"

    )

    report.append(

        f"전일대비    {format_percent(sk['ChangePct'])}"

    )

    return "\n".join(report)

# ==========================================================
# PER Scenario
# ==========================================================

def build_per_scenario_text(company):

    report = []

    company_name = {

        "Samsung": "삼성전자",

        "SK Hynix": "SK하이닉스",

    }.get(

        company["Company"],

        company["Company"],

    )

    report.append("")

    report.append(

        "📊 PER 시나리오"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append("")

    report.append(

        company_name

    )

    report.append("")

    scenarios = company["PERScenario"]

    for _, row in scenarios.iterrows():

        per = row["PER"]

        if abs(

            per

            - company["ReferencePER"]

        ) < 0.01:

            report.append(

                f"PER {per:.2f} (Micron)"

                f"    적정주가 "

                f"{format_price(row['TargetPrice'])}"

            )

        else:

            report.append(

                f"PER {per:.1f}"

                f"    적정주가 "

                f"{format_price(row['TargetPrice'])}"

            )

    return report


# ==========================================================
# Valuation Report
# ==========================================================

def build_valuation_report(df):

    samsung = get_company(

        df,

        "Samsung",

    )

    sk = get_company(

        df,

        "SK Hynix",

    )

    report = []

    report.append(

        "📈 Micron PER 기준 적정주가"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append("")

    report.append(

        "삼성전자"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append(

        f"현재가      {format_price(samsung['Price'])}"

    )

    report.append(

        f"현재 PER    {format_number(samsung['PER'])}"

    )

    report.append(

        f"Micron PER  {format_number(samsung['ReferencePER'])}"

    )

    report.append(

        f"목표가      {format_price(samsung['TargetPrice'])}"

    )

    report.append(

        f"상승여력    {format_percent(samsung['Upside(%)'])}"

    )

    report.extend(

        build_per_scenario_text(

            samsung

        )

    )

    report.append("")

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append("")

    report.append(

        "SK하이닉스"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append(

        f"현재가      {format_price(sk['Price'])}"

    )

    report.append(

        f"현재 PER    {format_number(sk['PER'])}"

    )

    report.append(

        f"Micron PER  {format_number(sk['ReferencePER'])}"

    )

    report.append(

        f"목표가      {format_price(sk['TargetPrice'])}"

    )

    report.append(

        f"상승여력    {format_percent(sk['Upside(%)'])}"

    )

    report.extend(

        build_per_scenario_text(

            sk

        )

    )

    return "\n".join(

        report

    )


# ==========================================================
# Quant Report
# ==========================================================

def build_quant_report(df):

    report = []

    report.append(

        "📊 퀀트 분석"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append("")

    ranking = df.sort_values(

        by="QuantScore",

        ascending=False,

    )

    company_map = {

        "Micron": "Micron",

        "Samsung": "삼성전자",

        "SK Hynix": "SK하이닉스",

    }

    for _, row in ranking.iterrows():

        report.append(

            f"■ {company_map[row['Company']]}"

        )

        report.append(

            f"순위        {int(row['Rank'])}위"

        )

        report.append(

            f"PER 점수    {format_number(row['PERScore'])}"

        )

        report.append(

            f"ROE 점수    {format_number(row['ROEScore'])}"

        )

        report.append(

            f"EPS 점수    {format_number(row['EPSScore'])}"

        )

        report.append(

            f"매출 점수   {format_number(row['RevenueScore'])}"

        )

        report.append(

            f"종합 점수   {format_number(row['QuantScore'])}"

        )

        report.append("")

# ==========================================================
# AI Report
# ==========================================================

def build_ai_report(df):

    micron = get_company(

        df,

        "Micron",

    )

    samsung = get_company(

        df,

        "Samsung",

    )

    sk = get_company(

        df,

        "SK Hynix",

    )

    ranking = df.sort_values(

        by="QuantScore",

        ascending=False,

    )

    best = ranking.iloc[0]

    worst = ranking.iloc[-1]

    company_map = {

        "Micron": "Micron",

        "Samsung": "삼성전자",

        "SK Hynix": "SK하이닉스",

    }

    report = []

    report.append(

        "🤖 AI 투자 의견"

    )

    report.append(

        "━━━━━━━━━━━━━━━━"

    )

    report.append("")

    report.append(

        f"Micron PER : {format_number(micron['PER'])}"

    )

    report.append("")

    report.append(

        f"삼성 할인율 : "

        f"{format_percent(samsung['PERGap(%)'])}"

    )

    report.append(

        f"SK 할인율 : "

        f"{format_percent(sk['PERGap(%)'])}"

    )

    report.append("")

    report.append(

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
