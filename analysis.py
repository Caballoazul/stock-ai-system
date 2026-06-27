"""
analysis.py
Part 1
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


# ==========================================================
# PER Scenario
# ==========================================================

PER_LEVELS = [

    5.0,

    6.0,

    7.0,

    8.0,

    9.0,

    10.0,

    11.0,

]


# ==========================================================
# Utility
# ==========================================================

def safe_float(

    value,

    default=np.nan,

):

    try:

        if value is None:

            return default

        if value == "":

            return default

        return float(value)

    except Exception:

        return default


def safe_divide(

    a,

    b,

):

    a = safe_float(a)

    b = safe_float(b)

    if pd.isna(a):

        return np.nan

    if pd.isna(b):

        return np.nan

    if b == 0:

        return np.nan

    return a / b


# ==========================================================
# DataFrame
# ==========================================================

def build_quant_dataframe(

    stock_data: List[Dict],

):

    df = pd.DataFrame(stock_data)

    numeric_columns = [

        "Price",

        "ChangePct",

        "PER",

        "EPS",

        "ROE",

        "RevenueGrowth",

        "EPSGrowth",

        "MarketCap",

    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(

                df[column],

                errors="coerce",

            )

    return df


# ==========================================================
# Reference PER
# ==========================================================

def get_reference_per(df):

    micron = df[

        df["Company"] == "Micron"

    ]

    if micron.empty:

        return np.nan

    return float(

        micron.iloc[0]["PER"]

    )

# ==========================================================
# Target Price
# ==========================================================

def calc_target_price(

    price,

    current_per,

    target_per,

):

    eps = safe_divide(

        price,

        current_per,

    )

    if pd.isna(eps):

        return np.nan

    return eps * target_per


# ==========================================================
# PER Scenario
# ==========================================================

def build_per_scenarios(

    current_price,

    current_per,

     micron_per,

):

    rows = []

    eps = safe_divide(

        current_price,

        current_per,

    )

    for per in PER_LEVELS:

    if per > micron_per:

        break

        target_price = eps * per

        rows.append(

            {

                "PER": per,

                "TargetPrice": round(

                    target_price,

                    0,

                ),

            }

        )

    if micron_per not in PER_LEVELS:

        rows.append(

            {

                "PER": round(

                    micron_per,

                    2,

                ),

                "TargetPrice": round(

                    eps * micron_per,

                    0,

                ),

            }

        )

    
    return pd.DataFrame(rows)


# ==========================================================
# PER Compare
# ==========================================================

def build_per_compare(df):

    result = df.copy()

    micron_per = get_reference_per(
        result
    )

    result["ReferencePER"] = micron_per

    result["AdjustedPER"] = micron_per

    result["PERGap(%)"] = np.nan

    result["TargetPrice"] = np.nan

    result["Upside(%)"] = np.nan

    result["PERScenario"] = None

    for idx, row in result.iterrows():

        price = safe_float(

            row["Price"]

        )

        per = safe_float(

            row["PER"]

        )

        if pd.isna(price):

            continue

        if pd.isna(per):

            continue

        if per <= 0:

            continue

        gap = (

            (micron_per - per)

            / micron_per

        ) * 100

        result.loc[
            idx,
            "PERGap(%)"
        ] = round(
            gap,
            2,
        )

        target = calc_target_price(

            price,

            per,

            micron_per,

        )

        result.loc[
            idx,
            "TargetPrice"
        ] = round(
            target,
            0,
        )

        result.loc[
            idx,
            "Upside(%)"
        ] = round(

            (

                (

                    target

                    / price

                )

                - 1

            ) * 100,

            2,

        )

        result.at[
            idx,
            "PERScenario"
        ] = build_per_scenarios(

            price,

            per,

            micron_per,

        )

    return result


# ==========================================================
# PER Score
# ==========================================================

def calculate_per_score(df):

    result = df.copy()

    per_min = result["PER"].min()

    per_max = result["PER"].max()

    scores = []

    for per in result["PER"]:

        if pd.isna(per):

            scores.append(np.nan)

            continue

        if per_max == per_min:

            scores.append(50.0)

            continue

        score = (

            (per_max - per)

            / (per_max - per_min)

        ) * 100

        scores.append(

            round(score, 2)

        )

    result["PERScore"] = scores

    return result


# ==========================================================
# Growth Score
# ==========================================================

def calculate_growth_score(df):

    result = df.copy()

    score_columns = [

        ("ROE", "ROEScore"),

        ("RevenueGrowth", "RevenueScore"),

        ("EPSGrowth", "EPSScore"),

    ]

    for column, score_name in score_columns:

        minimum = result[column].min()

        maximum = result[column].max()

        scores = []

        for value in result[column]:

            if pd.isna(value):

                scores.append(np.nan)

                continue

            if minimum == maximum:

                scores.append(50.0)

                continue

            score = (

                (value - minimum)

                / (maximum - minimum)

            ) * 100

            scores.append(

                round(score, 2)

            )

        result[score_name] = scores

    return result

# ==========================================================
# Quant Score
# ==========================================================

def calculate_quant_score(df):

    result = calculate_per_score(
        df
    )

    result = calculate_growth_score(
        result
    )

    result["QuantScore"] = (

        result["PERScore"] * 0.40

        + result["ROEScore"] * 0.20

        + result["RevenueScore"] * 0.20

        + result["EPSScore"] * 0.20

    ).round(2)

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
# Opinion
# ==========================================================

def investment_opinion(

    upside,

):

    upside = safe_float(

        upside

    )

    if pd.isna(upside):

        return "☆☆☆☆☆"

    if upside >= 30:

        return "★★★★★"

    if upside >= 20:

        return "★★★★☆"

    if upside >= 10:

        return "★★★☆☆"

    if upside >= 0:

        return "★★☆☆☆"

    return "★☆☆☆☆"

# ==========================================================
# Final Analysis
# ==========================================================

def make_analysis(df):

    result = build_per_compare(
        df
    )

    result = calculate_quant_score(
        result
    )

    result["Opinion"] = result[
        "Upside(%)"
    ].apply(
        investment_opinion
    )

    result = result.sort_values(

        by="QuantScore",

        ascending=False,

    ).reset_index(
        drop=True,
    )

    return result


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

        "Opinion": best["Opinion"],

    }


# ==========================================================
# End of analysis.py
# ==========================================================
