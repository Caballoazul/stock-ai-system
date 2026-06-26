"""
analysis.py
Part 1
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ==========================================================
# Utility
# ==========================================================

def safe_float(value, default=np.nan):
    try:
        if value is None:
            return default
        if value == "":
            return default
        return float(value)
    except Exception:
        return default


def safe_divide(a, b):
    a = safe_float(a)
    b = safe_float(b)

    if pd.isna(a) or pd.isna(b):
        return np.nan

    if b == 0:
        return np.nan

    return a / b


def safe_percent(value):
    value = safe_float(value)

    if pd.isna(value):
        return np.nan

    return value * 100


# ==========================================================
# DataFrame
# ==========================================================

def build_quant_dataframe(stock_data: List[Dict]) -> pd.DataFrame:

    df = pd.DataFrame(stock_data)

    numeric_columns = [
        "Price",
        "MarketCap",
        "PER",
        "EPS",
        "ROE",
        "RevenueGrowth",
        "EPSGrowth",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

    return df


# ==========================================================
# EPS
# ==========================================================

def calc_eps(price, per):

    return safe_divide(price, per)


# ==========================================================
# Target Price
# ==========================================================

def calc_target_price(
    current_price,
    current_per,
    target_per,
):

    eps = calc_eps(
        current_price,
        current_per,
    )

    if pd.isna(eps):
        return np.nan

    return eps * target_per


# ==========================================================
# PER GAP
# ==========================================================

def calc_per_gap(
    current_per,
    target_per,
):

    current_per = safe_float(current_per)
    target_per = safe_float(target_per)

    if pd.isna(current_per):
        return np.nan

    if current_per <= 0:
        return np.nan

    return (
        (target_per / current_per) - 1
    ) * 100


# ==========================================================
# Reference PER
# ==========================================================

def get_reference_per(
    df: pd.DataFrame,
    reference="Micron",
):

    ref = df[df["Company"] == reference]

    if ref.empty:
        return None

    return safe_float(
        ref.iloc[0]["PER"]
    )

# ==========================================================
# PER Scenario
# ==========================================================

def build_per_scenarios(
    current_price,
    current_per,
    target_per,
    step=0.5,
):

    current_price = safe_float(current_price)
    current_per = safe_float(current_per)
    target_per = safe_float(target_per)

    if pd.isna(current_price):
        return pd.DataFrame()

    if pd.isna(current_per):
        return pd.DataFrame()

    if current_per <= 0:
        return pd.DataFrame()

    eps = calc_eps(
        current_price,
        current_per,
    )

    start = min(current_per, target_per)
    end = max(current_per, target_per)

    rows = []

    for per in np.arange(
        start,
        end + step,
        step,
    ):

        target = eps * per

        upside = (
            (target / current_price) - 1
        ) * 100

        rows.append(
            {
                "PER": round(per, 2),
                "TargetPrice": round(target),
                "Upside(%)": round(upside, 2),
            }
        )

    return pd.DataFrame(rows)


# ==========================================================
# PER Compare
# ==========================================================

def build_per_compare(df):

    result = df.copy()

    micron_per = get_reference_per(result)

    if micron_per is None:
        return result

    result["ReferencePER"] = micron_per

    result["PERGap(%)"] = result["PER"].apply(
        lambda x: calc_per_gap(
            x,
            micron_per,
        )
    )

    result["TargetPrice"] = result.apply(
        lambda row: calc_target_price(
            row["Price"],
            row["PER"],
            micron_per,
        ),
        axis=1,
    )

    result["Upside(%)"] = (
        (
            result["TargetPrice"]
            / result["Price"]
        ) - 1
    ) * 100

    return result


# ==========================================================
# Opinion
# ==========================================================

def investment_opinion(upside):

    upside = safe_float(upside)

    if pd.isna(upside):
        return "N/A"

    if upside >= 30:
        return "★★★★★"

    if upside >= 15:
        return "★★★★☆"

    if upside >= 5:
        return "★★★☆☆"

    if upside >= -5:
        return "★★☆☆☆"

    return "★☆☆☆☆"

# ==========================================================
# Quant Score
# ==========================================================

def normalize_score(
    value,
    minimum,
    maximum,
):

    value = safe_float(value)

    if pd.isna(value):
        return np.nan

    if maximum == minimum:
        return 50.0

    score = (
        (value - minimum)
        / (maximum - minimum)
    ) * 100

    score = max(0, score)
    score = min(100, score)

    return round(score, 2)


# ==========================================================
# PER Score
# ==========================================================

def calculate_per_score(df):

    per_min = df["PER"].min()
    per_max = df["PER"].max()

    def score(per):

        per = safe_float(per)

        if pd.isna(per):
            return np.nan

        if per_max == per_min:
            return 50.0

        return round(
            (
                (per_max - per)
                / (per_max - per_min)
            ) * 100,
            2,
        )

    return df["PER"].apply(score)


# ==========================================================
# Growth Score
# ==========================================================

def calculate_growth_score(series):

    minimum = series.min()
    maximum = series.max()

    return series.apply(
        lambda x: normalize_score(
            x,
            minimum,
            maximum,
        )
    )


# ==========================================================
# Quant Calculation
# ==========================================================

def calculate_quant_score(df):

    result = df.copy()

    result["PERScore"] = calculate_per_score(result)

    result["EPSScore"] = calculate_growth_score(
        result["EPSGrowth"]
    )

    result["RevenueScore"] = calculate_growth_score(
        result["RevenueGrowth"]
    )

    result["ROEScore"] = calculate_growth_score(
        result["ROE"]
    )

    result["QuantScore"] = (
        result["PERScore"] * 0.40
        + result["EPSScore"] * 0.25
        + result["RevenueScore"] * 0.20
        + result["ROEScore"] * 0.15
    ).round(2)

    return result


# ==========================================================
# Rank
# ==========================================================

def append_rank(df):

    result = df.copy()

    result["Rank"] = (
        result["QuantScore"]
        .rank(
            ascending=False,
            method="dense",
        )
        .astype(int)
    )

    return result


# ==========================================================
# Analysis
# ==========================================================

def make_analysis(df):

    result = build_per_compare(df)

    result = calculate_quant_score(result)

    result = append_rank(result)

    result["Opinion"] = result["Upside(%)"].apply(
        investment_opinion
    )

    return (
        result.sort_values(
            by="QuantScore",
            ascending=False,
        )
        .reset_index(drop=True)
    )


# ==========================================================
# Summary
# ==========================================================

def build_summary(df):

    if df.empty:
        return {}

    best = df.iloc[0]

    return {
        "BestCompany": best["Company"],
        "BestScore": best["QuantScore"],
        "BestPER": best["PER"],
        "TargetPrice": best["TargetPrice"],
        "Upside": best["Upside(%)"],
    }


# ==========================================================
# End of analysis.py
# ==========================================================
