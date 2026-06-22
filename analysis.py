# =====================================================
# analysis.py
# Semiconductor Quant Engine v2
# =====================================================

import pandas as pd


# =====================================================
# 정규화
# =====================================================

def normalize(series):

    if series.max() == series.min():
        return pd.Series([0.5] * len(series))

    return (
        series - series.min()
    ) / (
        series.max() - series.min()
    )


# =====================================================
# 기존 적정가 계산
# =====================================================

def calculate_fair_value(eps, target_pe=10):

    if not eps:
        return 0

    return eps * target_pe


def calculate_gap(price, fair_value):

    if not price or not fair_value:
        return 0

    return (fair_value - price) / price * 100


# =====================================================
# 개별 종목 분석
# =====================================================

def make_analysis(data):

    eps = data.get("eps", 0)
    price = data.get("price", 0)

    fair_value = calculate_fair_value(eps)
    gap = calculate_gap(price, fair_value)

    return {
        "name": data["name"],
        "ticker": data["ticker"],

        "price": price,
        "pe": data.get("pe", 0),
        "eps": eps,

        "eps_growth": data.get("eps_growth", 0),
        "revenue_growth": data.get("revenue_growth", 0),
        "roe": data.get("roe", 0),

        "fair_value": fair_value,
        "gap": gap
    }


# =====================================================
# 퀀트 스코어 계산
# =====================================================

def build_quant_dataframe(results):

    df = pd.DataFrame(results)

    micron = df[df["name"] == "Micron"].iloc[0]

    micron_per = micron["pe"]

    # -------------------------------------------------
    # 점수 계산
    # -------------------------------------------------

    df["per_score"] = (
        1 - (df["pe"] / micron_per)
    )

    df["eps_score"] = normalize(
        df["eps_growth"].fillna(0)
    )

    df["revenue_score"] = normalize(
        df["revenue_growth"].fillna(0)
    )

    df["roe_score"] = normalize(
        df["roe"].fillna(0)
    )

    # -------------------------------------------------
    # 최종 점수
    # -------------------------------------------------

    df["final_score"] = (

        df["per_score"] * 0.40 +

        df["eps_score"] * 0.25 +

        df["revenue_score"] * 0.20 +

        df["roe_score"] * 0.15

    )

    return df.sort_values(
        "final_score",
        ascending=False
    )


# =====================================================
# 투자 순위
# =====================================================

def get_ranking(df):

    ranking = []

    for _, row in df.iterrows():

        ranking.append({
            "name": row["name"],
            "score": round(
                row["final_score"], 3
            )
        })

    return ranking


# =====================================================
# Micron PER 기준 시나리오
# =====================================================

def build_scenario(df):

    scenarios = []

    micron = df[
        df["name"] == "Micron"
    ].iloc[0]

    micron_per = micron["pe"]

    for _, row in df.iterrows():

        if row["name"] == "Micron":
            continue

        current_price = row["price"]
        current_per = row["pe"]

        if current_per == 0:
            continue

        eps = current_price / current_per

        target_price = eps * micron_per

        upside = (
            target_price /
            current_price - 1
        ) * 100

        scenarios.append({

            "name": row["name"],

            "current_per":
                round(current_per, 2),

            "micron_per":
                round(micron_per, 2),

            "target_price":
                round(target_price, 0),

            "upside":
                round(upside, 1)

        })

    return scenarios


# =====================================================
# 단독 실행 테스트
# =====================================================

if __name__ == "__main__":

    print(
        "Semiconductor Quant Engine Ready"
    )
